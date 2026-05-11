from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .rbac import Permission, Role


SCHEMA_SQL_PATH = Path(__file__).resolve().parents[1] / "config" / "lockfix_schema.sql"

LOCKFIX_TABLE_SCHEMA: dict[str, tuple[str, ...]] = {
    "users": (
        "id",
        "email",
        "name",
        "password_hash",
        "department_id",
        "role",
        "disabled",
        "created_at",
        "updated_at",
    ),
    "departments": ("id", "name", "description", "created_at", "updated_at"),
    "role_permissions": ("id", "role", "permission"),
    "approval_requests": (
        "id",
        "request_type",
        "requested_by_user_id",
        "target_resource_type",
        "target_resource_id",
        "reason",
        "review_departments",
        "status",
        "created_at",
        "updated_at",
    ),
    "approval_policies": (
        "id",
        "request_type",
        "required_approvals",
        "allowed_approver_roles",
        "expires_in_minutes",
        "enabled",
    ),
    "department_reviews": (
        "id",
        "approval_request_id",
        "department_id",
        "reviewer_user_id",
        "status",
        "comment",
        "created_at",
        "updated_at",
    ),
    "approval_decisions": ("id", "approval_request_id", "approver_user_id", "decision", "comment", "created_at"),
    "audit_logs": (
        "id",
        "actor_user_id",
        "action",
        "resource_type",
        "resource_id",
        "ip_address",
        "user_agent",
        "result",
        "before_value",
        "after_value",
        "created_at",
    ),
}


def load_schema_sql() -> str:
    return SCHEMA_SQL_PATH.read_text(encoding="utf-8")


def users_row(user: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "users",
        {
            "id": user.get("id", ""),
            "email": user.get("email", ""),
            "name": user.get("name", ""),
            "password_hash": user.get("password_hash") or user.get("passwordHash") or "",
            "department_id": user.get("department_id") or user.get("departmentId") or "",
            "role": user.get("role", Role.AUDITOR.value),
            "disabled": bool(user.get("disabled", False)),
            "created_at": user.get("created_at") or user.get("createdAt") or "",
            "updated_at": user.get("updated_at") or user.get("updatedAt") or "",
        },
    )


def departments_row(department: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "departments",
        {
            "id": department.get("id", ""),
            "name": department.get("name", ""),
            "description": department.get("description", ""),
            "created_at": department.get("created_at") or department.get("createdAt") or "",
            "updated_at": department.get("updated_at") or department.get("updatedAt") or "",
        },
    )


def role_permissions_rows(policy: dict[Role, set[Permission]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for role, permissions in sorted(policy.items(), key=lambda item: item[0].value):
        for permission in sorted(permissions, key=lambda item: item.value):
            row_id = stable_id(role.value, permission.value)
            rows.append(pick_schema_row("role_permissions", {"id": row_id, "role": role.value, "permission": permission.value}))
    return rows


def approval_policy_row(policy: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "approval_policies",
        {
            "id": policy.get("id", ""),
            "request_type": policy.get("request_type") or policy.get("requestType") or "",
            "required_approvals": int(policy.get("required_approvals") or policy.get("requiredApprovals") or 1),
            "allowed_approver_roles": json.dumps(
                policy.get("allowed_approver_roles") or policy.get("allowedApproverRoles") or [],
                ensure_ascii=False,
            ),
            "expires_in_minutes": int(policy.get("expires_in_minutes") or policy.get("expiresInMinutes") or 30),
            "enabled": bool(policy.get("enabled", True)),
        },
    )


def approval_request_row(request: dict[str, Any]) -> dict[str, Any]:
    metadata = request.get("metadata") if isinstance(request.get("metadata"), dict) else {}
    return pick_schema_row(
        "approval_requests",
        {
            "id": request.get("id", ""),
            "request_type": request.get("request_type") or request.get("requestType") or "",
            "requested_by_user_id": request.get("requested_by_user_id") or request.get("requesterUserId") or "",
            "target_resource_type": request.get("target_resource_type") or metadata.get("targetResourceType") or "",
            "target_resource_id": request.get("target_resource_id") or request.get("targetId") or "",
            "reason": request.get("reason") or metadata.get("reason") or "",
            "review_departments": json.dumps(
                request.get("review_departments") or request.get("reviewDepartments") or [],
                ensure_ascii=False,
            ),
            "status": request.get("status", ""),
            "created_at": request.get("created_at") or request.get("createdAt") or "",
            "updated_at": request.get("updated_at") or request.get("updatedAt") or "",
        },
    )


def department_review_row(review: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "department_reviews",
        {
            "id": review.get("id", ""),
            "approval_request_id": review.get("approval_request_id") or review.get("approvalRequestId") or "",
            "department_id": review.get("department_id") or review.get("departmentId") or "",
            "reviewer_user_id": review.get("reviewer_user_id") or review.get("reviewerUserId") or "",
            "status": review.get("status", ""),
            "comment": review.get("comment", ""),
            "created_at": review.get("created_at") or review.get("createdAt") or "",
            "updated_at": review.get("updated_at") or review.get("updatedAt") or "",
        },
    )


def approval_decision_row(decision: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "approval_decisions",
        {
            "id": decision.get("id", ""),
            "approval_request_id": decision.get("approval_request_id") or decision.get("approvalRequestId") or "",
            "approver_user_id": decision.get("approver_user_id") or decision.get("approverUserId") or "",
            "decision": decision.get("decision", ""),
            "comment": decision.get("comment", ""),
            "created_at": decision.get("created_at") or decision.get("createdAt") or "",
        },
    )


def audit_log_row(log: dict[str, Any]) -> dict[str, Any]:
    return pick_schema_row(
        "audit_logs",
        {
            "id": log.get("id", ""),
            "actor_user_id": log.get("actor_user_id") or log.get("actorUserId") or "",
            "action": log.get("action", ""),
            "resource_type": log.get("resource_type") or log.get("resourceType") or "",
            "resource_id": log.get("resource_id") or log.get("resourceId") or "",
            "ip_address": log.get("ip_address") or log.get("ipAddress") or "",
            "user_agent": log.get("user_agent") or log.get("userAgent") or "",
            "result": log.get("result", ""),
            "before_value": json_text(log.get("before_value", log.get("beforeValue", ""))),
            "after_value": json_text(log.get("after_value", log.get("afterValue", ""))),
            "created_at": log.get("created_at") or log.get("createdAt") or "",
        },
    )


def pick_schema_row(table: str, values: dict[str, Any]) -> dict[str, Any]:
    return {field: values.get(field, "") for field in LOCKFIX_TABLE_SCHEMA[table]}


def json_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value or "")


def stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:32]
