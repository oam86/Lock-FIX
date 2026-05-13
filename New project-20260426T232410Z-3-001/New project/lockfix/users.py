from __future__ import annotations

import json
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
        return {"departments": departments, "users": users}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def departments(self) -> list[dict[str, Any]]:
        return list(self.load()["departments"])

    def users(self) -> list[dict[str, Any]]:
        return list(self.load()["users"])

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
            disabled=False,
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
