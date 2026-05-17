from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .rbac import Role, normalize_role


DEFAULT_DEPARTMENTS: tuple[tuple[str, str], ...] = (
    ("Management", "Executive and business owner accounts."),
    ("Security", "Security operations and policy administrators."),
    ("Backup Operation", "Backup monitoring and Veeam operators."),
    ("Hardware Control", "Physical disk and isolation hardware operators."),
    ("Audit", "Audit log, compliance, and report reviewers."),
    ("Development", "LOCK-FIX implementation and integration engineers."),
    ("Web Design", "Web UI design and experience contributors."),
)


@dataclass(frozen=True)
class Department:
    id: str
    name: str
    description: str
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class User:
    id: str
    email: str
    name: str
    departmentId: str
    role: str
    disabled: bool
    deleted: bool
    deletedAt: str
    deletedBy: str
    passwordHash: str
    passwordChangeRequired: bool
    temporaryPasswordExpiresAt: str
    temporaryPasswordUsedAt: str
    passwordUpdatedAt: str
    createdAt: str
    updatedAt: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def department_id_for(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def default_departments(now: str | None = None) -> list[Department]:
    timestamp = now or utc_now()
    return [
        Department(
            id=department_id_for(name),
            name=name,
            description=description,
            createdAt=timestamp,
            updatedAt=timestamp,
        )
        for name, description in DEFAULT_DEPARTMENTS
    ]


class UserDirectory:
    def __init__(self, path: Path) -> None:
        self.path = path

    def normalize_user_record(self, user: dict[str, Any]) -> dict[str, Any]:
        record = dict(user)
        record.setdefault("id", "")
        record.setdefault("email", "")
        record.setdefault("name", "")
        record.setdefault("departmentId", "")
        record.setdefault("role", Role.AUDITOR.value)
        record["disabled"] = bool(record.get("disabled", False))
        record["deleted"] = bool(record.get("deleted", False))
        record.setdefault("deletedAt", "")
        record.setdefault("deletedBy", "")
        record.setdefault("passwordHash", "")
        record["passwordChangeRequired"] = bool(record.get("passwordChangeRequired", False))
        record.setdefault("temporaryPasswordExpiresAt", "")
        record.setdefault("temporaryPasswordUsedAt", "")
        record.setdefault("passwordUpdatedAt", "")
        record.setdefault("createdAt", "")
        record.setdefault("updatedAt", record.get("createdAt", ""))
        return record

    def load(self) -> dict[str, Any]:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                data = {}
        else:
            data = {}
        if not isinstance(data, dict):
            data = {}
        departments = data.get("departments")
        if not isinstance(departments, list) or not departments:
            departments = [asdict(department) for department in default_departments()]
        users = data.get("users")
        if not isinstance(users, list):
            users = []
        users = [self.normalize_user_record(user) for user in users if isinstance(user, dict)]
        return {"departments": departments, "users": users}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def departments(self) -> list[dict[str, Any]]:
        return list(self.load()["departments"])

    def users(self, include_deleted: bool = True) -> list[dict[str, Any]]:
        users = list(self.load()["users"])
        if include_deleted:
            return users
        return [user for user in users if not bool(user.get("deleted", False))]

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self.load()
        now = utc_now()
        department_id = self.require_department(data, str(payload.get("departmentId") or ""))
        email = str(payload.get("email") or "").strip()
        name = str(payload.get("name") or "").strip()
        if not email:
            raise ValueError("email is required")
        if not name:
            raise ValueError("name is required")
        if any(str(user.get("email") or "").lower() == email.lower() for user in data["users"]):
            raise ValueError("user email already exists")
        user = User(
            id=str(payload.get("id") or uuid.uuid4().hex),
            email=email,
            name=name,
            departmentId=department_id,
            role=normalize_role(payload.get("role") or Role.AUDITOR.value).value,
            disabled=bool(payload.get("disabled", False)),
            deleted=False,
            deletedAt="",
            deletedBy="",
            passwordHash=str(payload.get("passwordHash") or ""),
            passwordChangeRequired=bool(payload.get("passwordChangeRequired", False)),
            temporaryPasswordExpiresAt=str(payload.get("temporaryPasswordExpiresAt") or ""),
            temporaryPasswordUsedAt="",
            passwordUpdatedAt=str(payload.get("passwordUpdatedAt") or ""),
            createdAt=now,
            updatedAt=now,
        )
        record = asdict(user)
        data["users"].append(record)
        self.save(data)
        return record

    def update_user(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = self.load()
        user = self.find_user(data, user_id)
        before_email = str(user.get("email") or "")
        if "email" in payload:
            email = str(payload.get("email") or "").strip()
            if not email:
                raise ValueError("email is required")
            if any(
                str(item.get("id") or "") != user_id and str(item.get("email") or "").lower() == email.lower()
                for item in data["users"]
            ):
                raise ValueError("user email already exists")
            user["email"] = email
        if "name" in payload:
            name = str(payload.get("name") or "").strip()
            if not name:
                raise ValueError("name is required")
            user["name"] = name
        if "departmentId" in payload:
            user["departmentId"] = self.require_department(data, str(payload.get("departmentId") or ""))
        if "role" in payload:
            user["role"] = normalize_role(payload.get("role")).value
        if "disabled" in payload:
            user["disabled"] = bool(payload.get("disabled"))
        if "passwordHash" in payload:
            user["passwordHash"] = str(payload.get("passwordHash") or "")
        if "passwordChangeRequired" in payload:
            user["passwordChangeRequired"] = bool(payload.get("passwordChangeRequired"))
        if "temporaryPasswordExpiresAt" in payload:
            user["temporaryPasswordExpiresAt"] = str(payload.get("temporaryPasswordExpiresAt") or "")
        if "temporaryPasswordUsedAt" in payload:
            user["temporaryPasswordUsedAt"] = str(payload.get("temporaryPasswordUsedAt") or "")
        if "passwordUpdatedAt" in payload:
            user["passwordUpdatedAt"] = str(payload.get("passwordUpdatedAt") or "")
        user["updatedAt"] = utc_now()
        self.save(data)
        user["previousEmail"] = before_email
        return dict(user)

    def disable_user(self, user_id: str) -> dict[str, Any]:
        data = self.load()
        user = self.find_user(data, user_id)
        user["disabled"] = True
        user["updatedAt"] = utc_now()
        self.save(data)
        return dict(user)

    def archive_user(self, user_id: str, deleted_by: str) -> dict[str, Any]:
        data = self.load()
        user = self.find_user(data, user_id)
        now = utc_now()
        user["disabled"] = True
        user["deleted"] = True
        user["deletedAt"] = now
        user["deletedBy"] = str(deleted_by or "unknown")
        user["updatedAt"] = now
        self.save(data)
        return dict(user)

    def set_temporary_password(self, user_id: str, password_hash: str, expires_at: str) -> dict[str, Any]:
        data = self.load()
        user = self.find_user(data, user_id)
        now = utc_now()
        user["passwordHash"] = str(password_hash or "")
        user["passwordChangeRequired"] = True
        user["temporaryPasswordExpiresAt"] = str(expires_at or "")
        user["temporaryPasswordUsedAt"] = ""
        user["passwordUpdatedAt"] = ""
        user["updatedAt"] = now
        self.save(data)
        return dict(user)

    def change_password(self, user_id: str, password_hash: str) -> dict[str, Any]:
        data = self.load()
        user = self.find_user(data, user_id)
        now = utc_now()
        user["passwordHash"] = str(password_hash or "")
        user["passwordChangeRequired"] = False
        user["temporaryPasswordExpiresAt"] = ""
        user["temporaryPasswordUsedAt"] = ""
        user["passwordUpdatedAt"] = now
        user["updatedAt"] = now
        self.save(data)
        return dict(user)

    def find_user_by_email(self, data: dict[str, Any], email: str) -> dict[str, Any]:
        lookup = str(email or "").strip().lower()
        for user in data["users"]:
            if str(user.get("email") or "").strip().lower() == lookup:
                return user
        raise KeyError(f"user not found: {email}")

    def authenticate_password(self, email: str, password_hash: str) -> dict[str, Any]:
        data = self.load()
        try:
            user = self.find_user_by_email(data, email)
        except KeyError:
            return {"ok": False, "reason": "not_found", "known_user": False}
        if bool(user.get("deleted", False)):
            return {"ok": False, "reason": "deleted", "known_user": True, "user": dict(user)}
        if bool(user.get("disabled", False)):
            return {"ok": False, "reason": "disabled", "known_user": True, "user": dict(user)}
        stored_hash = str(user.get("passwordHash") or "")
        if not stored_hash:
            return {"ok": False, "reason": "password_not_set", "known_user": True, "user": dict(user)}
        if not secrets.compare_digest(stored_hash, str(password_hash or "")):
            return {"ok": False, "reason": "password_mismatch", "known_user": True, "user": dict(user)}
        if bool(user.get("passwordChangeRequired", False)):
            expires_at = str(user.get("temporaryPasswordExpiresAt") or "")
            if expires_at:
                try:
                    expires = datetime.fromisoformat(expires_at)
                    if expires.tzinfo is None:
                        expires = expires.replace(tzinfo=timezone.utc)
                    if expires <= datetime.now(timezone.utc):
                        return {"ok": False, "reason": "temporary_password_expired", "known_user": True, "user": dict(user)}
                except ValueError:
                    return {"ok": False, "reason": "temporary_password_expired", "known_user": True, "user": dict(user)}
            if str(user.get("temporaryPasswordUsedAt") or ""):
                return {"ok": False, "reason": "temporary_password_used", "known_user": True, "user": dict(user)}
            now = utc_now()
            user["temporaryPasswordUsedAt"] = now
            user["updatedAt"] = now
            self.save(data)
        return {"ok": True, "known_user": True, "user": dict(user)}

    def find_user(self, data: dict[str, Any], user_id: str) -> dict[str, Any]:
        for user in data["users"]:
            if str(user.get("id") or "") == str(user_id):
                return user
        raise KeyError(f"user not found: {user_id}")

    def require_department(self, data: dict[str, Any], department_id: str) -> str:
        text = department_id.strip()
        if not text:
            raise ValueError("departmentId is required")
        if any(str(department.get("id") or "") == text for department in data["departments"]):
            return text
        raise ValueError(f"department not found: {department_id}")
