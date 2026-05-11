from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .audit import AuditLogger
from .rbac import Role, normalize_role


APPROVED = "APPROVED"
EXPIRED = "EXPIRED"
PENDING = "PENDING"
REJECTED = "REJECTED"


DEFAULT_APPROVER_ROLES = {
    "DISK_ONLINE": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value],
    "EMERGENCY_UNLOCK": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value],
    "POLICY_CHANGE": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value],
    "DISK_OFFLINE": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.BACKUP_OPERATOR.value],
    "HARDWARE_POWER_OFF": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value],
    "HARDWARE_POWER_ON": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value],
}


@dataclass(frozen=True)
class ApprovalPolicy:
    id: str
    requestType: str
    requiredApprovals: int
    allowedApproverRoles: list[str]
    expiresInMinutes: int
    enabled: bool


@dataclass(frozen=True)
class ApprovalDecision:
    id: str
    approvalRequestId: str
    approverUserId: str
    decision: str
    comment: str
    createdAt: str


@dataclass(frozen=True)
class ApprovalRequest:
    id: str
    requestType: str
    requesterUserId: str
    targetId: str
    status: str
    requiredApprovals: int
    allowedApproverRoles: list[str]
    expiresAt: str
    createdAt: str
    updatedAt: str
    metadata: dict[str, Any]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def default_policies() -> list[ApprovalPolicy]:
    rows = [
        ("DISK_ONLINE", 2),
        ("EMERGENCY_UNLOCK", 2),
        ("POLICY_CHANGE", 2),
        ("DISK_OFFLINE", 1),
        ("HARDWARE_POWER_OFF", 2),
        ("HARDWARE_POWER_ON", 2),
    ]
    return [
        ApprovalPolicy(
            id=request_type.lower().replace("_", "-"),
            requestType=request_type,
            requiredApprovals=required,
            allowedApproverRoles=list(DEFAULT_APPROVER_ROLES[request_type]),
            expiresInMinutes=30,
            enabled=True,
        )
        for request_type, required in rows
    ]


class ApprovalStore:
    def __init__(self, path: Path, audit: AuditLogger | None = None) -> None:
        self.path = path
        self.audit = audit

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
        policies = data.get("policies")
        if not isinstance(policies, list) or not policies:
            policies = [asdict(policy) for policy in default_policies()]
        requests = data.get("requests")
        if not isinstance(requests, list):
            requests = []
        decisions = data.get("decisions")
        if not isinstance(decisions, list):
            decisions = []
        return {"policies": policies, "requests": requests, "decisions": decisions}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def policy_for(self, request_type: str) -> dict[str, Any]:
        data = self.load()
        wanted = str(request_type or "").strip().upper()
        for policy in data["policies"]:
            if str(policy.get("requestType") or "").upper() == wanted:
                return dict(policy)
        raise KeyError(f"approval policy not found: {request_type}")

    def create_request(
        self,
        request_type: str,
        requester_user_id: str,
        target_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = self.load()
        policy = self.policy_for(request_type)
        if not policy.get("enabled", True):
            raise PermissionError(f"approval policy disabled: {request_type}")
        now = utc_now()
        request = ApprovalRequest(
            id=uuid.uuid4().hex,
            requestType=str(policy["requestType"]),
            requesterUserId=str(requester_user_id or "unknown"),
            targetId=str(target_id or ""),
            status=PENDING,
            requiredApprovals=max(1, int(policy.get("requiredApprovals") or 1)),
            allowedApproverRoles=list(policy.get("allowedApproverRoles") or []),
            expiresAt=iso(now + timedelta(minutes=max(1, int(policy.get("expiresInMinutes") or 30)))),
            createdAt=iso(now),
            updatedAt=iso(now),
            metadata=dict(metadata or {}),
        )
        record = asdict(request)
        data["requests"].append(record)
        self.save(data)
        self.audit_event("approval.request.created", approval_request=record)
        return record

    def decide(
        self,
        approval_request_id: str,
        approver_user_id: str,
        approver_role: Role | str,
        decision: str,
        comment: str = "",
    ) -> dict[str, Any]:
        data = self.load()
        request = self.find_request(data, approval_request_id)
        self.expire_request_if_needed(data, request)
        if request.get("status") != PENDING:
            self.save(data)
            raise PermissionError(f"approval request is not pending: {request.get('status')}")
        approver = str(approver_user_id or "").strip()
        if not approver:
            raise ValueError("approverUserId is required")
        if approver == str(request.get("requesterUserId") or ""):
            raise PermissionError("request creator cannot approve their own request")
        role = normalize_role(approver_role)
        if role.value not in set(request.get("allowedApproverRoles") or []):
            raise PermissionError(f"approver role is not allowed: {role.value}")
        if any(
            item.get("approvalRequestId") == approval_request_id and item.get("approverUserId") == approver
            for item in data["decisions"]
        ):
            raise PermissionError("duplicate approval decision is not allowed")
        normalized_decision = str(decision or "").strip().upper()
        if normalized_decision not in {APPROVED, REJECTED}:
            raise ValueError("decision must be APPROVED or REJECTED")
        created_at = iso(utc_now())
        decision_record = ApprovalDecision(
            id=uuid.uuid4().hex,
            approvalRequestId=approval_request_id,
            approverUserId=approver,
            decision=normalized_decision,
            comment=str(comment or ""),
            createdAt=created_at,
        )
        decision_dict = asdict(decision_record)
        data["decisions"].append(decision_dict)
        event = "approval.decision.approved" if normalized_decision == APPROVED else "approval.decision.rejected"
        if normalized_decision == REJECTED:
            request["status"] = REJECTED
        elif self.approval_count(data, approval_request_id) >= int(request.get("requiredApprovals") or 1):
            request["status"] = APPROVED
        request["updatedAt"] = created_at
        self.save(data)
        self.audit_event(event, approval_request=request, decision=decision_dict)
        if request["status"] == APPROVED:
            self.audit_event("approval.request.approved", approval_request=request)
        if request["status"] == REJECTED:
            self.audit_event("approval.request.rejected", approval_request=request)
        return {"request": dict(request), "decision": decision_dict}

    def approved_request_for(self, request_type: str, target_id: str = "") -> dict[str, Any] | None:
        data = self.load()
        changed = False
        for request in data["requests"]:
            before = request.get("status")
            if self.expire_request_if_needed(data, request):
                changed = True
            if before != request.get("status"):
                changed = True
        if changed:
            self.save(data)
        wanted_type = str(request_type or "").strip().upper()
        wanted_target = str(target_id or "")
        approved = [
            request
            for request in data["requests"]
            if str(request.get("requestType") or "").upper() == wanted_type
            and str(request.get("targetId") or "") == wanted_target
            and request.get("status") == APPROVED
        ]
        if not approved:
            return None
        return sorted(approved, key=lambda item: str(item.get("updatedAt") or ""), reverse=True)[0]

    def require_approved(self, request_type: str, target_id: str = "") -> dict[str, Any]:
        request = self.approved_request_for(request_type, target_id)
        if not request:
            self.audit_event("approval.execution.blocked", request_type=request_type, target_id=target_id)
            raise PermissionError(f"approval required: {request_type}")
        return request

    def expire_pending_requests(self) -> list[dict[str, Any]]:
        data = self.load()
        expired: list[dict[str, Any]] = []
        for request in data["requests"]:
            if self.expire_request_if_needed(data, request):
                expired.append(dict(request))
        if expired:
            self.save(data)
        return expired

    def expire_request_if_needed(self, data: dict[str, Any], request: dict[str, Any]) -> bool:
        if request.get("status") != PENDING:
            return False
        expires_at = parse_time(str(request.get("expiresAt") or ""))
        if utc_now() <= expires_at:
            return False
        request["status"] = EXPIRED
        request["updatedAt"] = iso(utc_now())
        self.audit_event("approval.request.expired", approval_request=request)
        return True

    def approval_count(self, data: dict[str, Any], approval_request_id: str) -> int:
        return sum(
            1
            for item in data["decisions"]
            if item.get("approvalRequestId") == approval_request_id and item.get("decision") == APPROVED
        )

    def find_request(self, data: dict[str, Any], approval_request_id: str) -> dict[str, Any]:
        for request in data["requests"]:
            if request.get("id") == approval_request_id:
                return request
        raise KeyError(f"approval request not found: {approval_request_id}")

    def audit_event(self, event: str, **payload: Any) -> None:
        if self.audit:
            self.audit.write(event, **payload)


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return utc_now() - timedelta(seconds=1)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
