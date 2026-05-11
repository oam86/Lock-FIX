from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Iterable


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    BACKUP_OPERATOR = "BACKUP_OPERATOR"
    HARDWARE_ADMIN = "HARDWARE_ADMIN"
    AUDITOR = "AUDITOR"
    UI_DESIGNER = "UI_DESIGNER"
    DEVELOPER = "DEVELOPER"


class Permission(str, Enum):
    DASHBOARD_VIEW = "DASHBOARD_VIEW"
    USER_MANAGE = "USER_MANAGE"
    ROLE_MANAGE = "ROLE_MANAGE"
    VEEAM_VIEW = "VEEAM_VIEW"
    VEEAM_MANAGE = "VEEAM_MANAGE"
    AIRGAP_POLICY_VIEW = "AIRGAP_POLICY_VIEW"
    AIRGAP_POLICY_MANAGE = "AIRGAP_POLICY_MANAGE"
    DISK_OFFLINE_REQUEST = "DISK_OFFLINE_REQUEST"
    DISK_OFFLINE_EXECUTE = "DISK_OFFLINE_EXECUTE"
    DISK_ONLINE_REQUEST = "DISK_ONLINE_REQUEST"
    DISK_ONLINE_APPROVE = "DISK_ONLINE_APPROVE"
    HARDWARE_CONTROL = "HARDWARE_CONTROL"
    AUDIT_LOG_VIEW = "AUDIT_LOG_VIEW"
    REPORT_EXPORT = "REPORT_EXPORT"
    SYSTEM_SETTING_MANAGE = "SYSTEM_SETTING_MANAGE"


class AuthorizationError(PermissionError):
    def __init__(self, permission: Permission, role: Role) -> None:
        super().__init__(f"forbidden: {role.value} lacks {permission.value}")
        self.permission = permission
        self.role = role


DEFAULT_ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.SECURITY_ADMIN: {
        Permission.DASHBOARD_VIEW,
        Permission.USER_MANAGE,
        Permission.ROLE_MANAGE,
        Permission.AIRGAP_POLICY_VIEW,
        Permission.AIRGAP_POLICY_MANAGE,
        Permission.DISK_OFFLINE_REQUEST,
        Permission.DISK_ONLINE_REQUEST,
        Permission.DISK_ONLINE_APPROVE,
        Permission.AUDIT_LOG_VIEW,
        Permission.REPORT_EXPORT,
        Permission.SYSTEM_SETTING_MANAGE,
    },
    Role.BACKUP_OPERATOR: {
        Permission.DASHBOARD_VIEW,
        Permission.VEEAM_VIEW,
        Permission.VEEAM_MANAGE,
        Permission.AIRGAP_POLICY_VIEW,
        Permission.DISK_OFFLINE_REQUEST,
        Permission.DISK_ONLINE_REQUEST,
        Permission.REPORT_EXPORT,
    },
    Role.HARDWARE_ADMIN: {
        Permission.DASHBOARD_VIEW,
        Permission.AIRGAP_POLICY_VIEW,
        Permission.DISK_OFFLINE_EXECUTE,
        Permission.DISK_ONLINE_APPROVE,
        Permission.HARDWARE_CONTROL,
        Permission.AUDIT_LOG_VIEW,
    },
    Role.AUDITOR: {
        Permission.DASHBOARD_VIEW,
        Permission.VEEAM_VIEW,
        Permission.AIRGAP_POLICY_VIEW,
        Permission.AUDIT_LOG_VIEW,
        Permission.REPORT_EXPORT,
    },
    Role.UI_DESIGNER: {
        Permission.DASHBOARD_VIEW,
    },
    Role.DEVELOPER: {
        Permission.DASHBOARD_VIEW,
        Permission.VEEAM_VIEW,
        Permission.AIRGAP_POLICY_VIEW,
        Permission.AUDIT_LOG_VIEW,
        Permission.REPORT_EXPORT,
        Permission.SYSTEM_SETTING_MANAGE,
    },
}


DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "rbac_policy.json"


def normalize_role(value: object) -> Role:
    text = str(value or Role.AUDITOR.value).strip().upper()
    try:
        return Role(text)
    except ValueError:
        return Role.AUDITOR


def normalize_permission(value: object) -> Permission:
    return Permission(str(value or "").strip().upper())


def default_policy_document() -> dict[str, list[str]]:
    return {
        role.value: sorted(permission.value for permission in permissions)
        for role, permissions in DEFAULT_ROLE_PERMISSIONS.items()
    }


def load_role_permissions(policy_path: Path | None = None) -> dict[Role, set[Permission]]:
    path = policy_path or DEFAULT_POLICY_PATH
    if not path.exists():
        return {role: set(permissions) for role, permissions in DEFAULT_ROLE_PERMISSIONS.items()}
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {role: set(permissions) for role, permissions in DEFAULT_ROLE_PERMISSIONS.items()}
    if not isinstance(raw, dict):
        return {role: set(permissions) for role, permissions in DEFAULT_ROLE_PERMISSIONS.items()}
    loaded: dict[Role, set[Permission]] = {}
    for role in Role:
        values = raw.get(role.value, [])
        if not isinstance(values, list):
            values = []
        permissions: set[Permission] = set()
        for value in values:
            try:
                permissions.add(normalize_permission(value))
            except ValueError:
                continue
        loaded[role] = permissions
    return loaded


def permissions_for_role(role: Role, policy: dict[Role, set[Permission]] | None = None) -> set[Permission]:
    role_policy = policy or load_role_permissions()
    return set(role_policy.get(role, set()))


def has_permission(role: Role, permission: Permission, policy: dict[Role, set[Permission]] | None = None) -> bool:
    return permission in permissions_for_role(role, policy)


def require_permission(role: Role, permission: Permission, policy: dict[Role, set[Permission]] | None = None) -> None:
    if not has_permission(role, permission, policy):
        raise AuthorizationError(permission, role)


def require_all(role: Role, permissions: Iterable[Permission], policy: dict[Role, set[Permission]] | None = None) -> None:
    role_policy = policy or load_role_permissions()
    for permission in permissions:
        require_permission(role, permission, role_policy)
