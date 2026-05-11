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
    "DISK_ONLINE": [Role.SECURITY_ADMIN.value, Role.SUPER_ADMIN.value],
    "EMERGENCY_UNLOCK": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value],
    "POLICY_CHANGE": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value],
    "DISK_OFFLINE": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.BACKUP_OPERATOR.value],
    "HARDWARE_POWER_OFF": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value],
    "HARDWARE_POWER_ON": [Role.SUPER_ADMIN.value, Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value],
}

REPOSITORY_ONLINE_REVIEW_TYPES = {
    "SECURITY_LOG_REVIEW": Role.SECURITY_ADMIN.value,
    "HARDWARE_STATE_REVIEW": Role.HARDWARE_ADMIN.value,
    "MANAGER_REVIEW": Role.SUPER_ADMIN.value,
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
        normalized_type = str(policy["requestType"])
        request_metadata = dict(metadata or {})
        if normalized_type == "EMERGENCY_UNLOCK" and not str(request_metadata.get("reason") or "").strip():
            self.audit_event(
                "approval.request.rejected",
                request_type=normalized_type,
                requesterUserId=str(requester_user_id or "unknown"),
                targetId=str(target_id or ""),
                reason="emergency unlock reason is required",
            )
            raise ValueError("reason is required for EMERGENCY_UNLOCK")
        now = utc_now()
        request = ApprovalRequest(
            id=uuid.uuid4().hex,
            requestType=normalized_type,
            requesterUserId=str(requester_user_id or "unknown"),
            targetId=str(target_id or ""),
            status=PENDING,
            requiredApprovals=max(1, int(policy.get("requiredApprovals") or 1)),
            allowedApproverRoles=list(policy.get("allowedApproverRoles") or []),
            expiresAt=iso(now + timedelta(minutes=max(1, int(policy.get("expiresInMinutes") or 30)))),
            createdAt=iso(now),
            updatedAt=iso(now),
            metadata=request_metadata,
        )
        record = asdict(request)
        data["requests"].append(record)
        self.save(data)
        self.audit_event("approval.request.created", approval_request=record)
        if normalized_type == "DISK_ONLINE":
            self.audit_event(
                "approval.notification.sent",
                approval_request=record,
                recipient_roles=[Role.SECURITY_ADMIN.value, Role.HARDWARE_ADMIN.value, Role.SUPER_ADMIN.value],
                message="Repository Online approval request requires security review, hardware review, and manager confirmation.",
            )
        return record

    def create_repository_online_request(
        self,
        requester_user_id: str,
        target_id: str,
        reason: str,
        repository_path: str = "",
    ) -> dict[str, Any]:
        metadata = {
            "workflowType": "REPOSITORY_ONLINE",
            "targetResourceType": "REPOSITORY",
            "reason": str(reason or "").strip(),
            "repositoryPath": str(repository_path or "").strip(),
            "workflowStatus": "AWAITING_SECURITY_HARDWARE_REVIEW",
            "reviews": {},
        }
        request = self.create_request("DISK_ONLINE", requester_user_id, target_id=target_id, metadata=metadata)
        self.audit_event(
            "repository.online.request.created",
            approval_request=request,
            requesterUserId=str(requester_user_id or "unknown"),
            targetId=str(target_id or ""),
        )
        return request

    def review_request(
        self,
        approval_request_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        review_type: str,
        comment: str,
    ) -> dict[str, Any]:
        data = self.load()
        request = self.find_request(data, approval_request_id)
        self.expire_request_if_needed(data, request)
        if request.get("status") != PENDING:
            self.save(data)
            raise PermissionError(f"approval request is not pending: {request.get('status')}")
        reviewer = str(reviewer_user_id or "").strip()
        if not reviewer:
            raise ValueError("reviewerUserId is required")
        if reviewer == str(request.get("requesterUserId") or ""):
            raise PermissionError("request creator cannot review their own request")
        normalized_type = str(review_type or "").strip().upper()
        expected_role = REPOSITORY_ONLINE_REVIEW_TYPES.get(normalized_type)
        if not expected_role:
            raise ValueError("reviewType must be SECURITY_LOG_REVIEW, HARDWARE_STATE_REVIEW, or MANAGER_REVIEW")
        role = normalize_role(reviewer_role)
        if role.value != expected_role:
            raise PermissionError(f"reviewer role is not allowed: {role.value}")
        text = str(comment or "").strip()
        if not text:
            raise ValueError("comment is required")
        metadata = request.setdefault("metadata", {})
        reviews = metadata.setdefault("reviews", {})
        if normalized_type in reviews:
            raise PermissionError(f"duplicate review is not allowed: {normalized_type}")
        review = {
            "reviewType": normalized_type,
            "reviewerUserId": reviewer,
            "reviewerRole": role.value,
            "comment": text,
            "createdAt": iso(utc_now()),
        }
        reviews[normalized_type] = review
        metadata["workflowStatus"] = self.repository_online_workflow_status(request)
        request["updatedAt"] = review["createdAt"]
        self.save(data)
        self.audit_event("approval.review.created", approval_request=request, review=review)
        if normalized_type in {"SECURITY_LOG_REVIEW", "HARDWARE_STATE_REVIEW"}:
            self.audit_event(
                "approval.notification.sent",
                approval_request=request,
                recipient_roles=[Role.SUPER_ADMIN.value],
                message="Security and hardware review updates are ready for manager confirmation.",
            )
        if normalized_type == "MANAGER_REVIEW":
            self.audit_event(
                "approval.notification.sent",
                approval_request=request,
                recipient_roles=[Role.SECURITY_ADMIN.value, Role.SUPER_ADMIN.value],
                message="Repository Online request is ready for first and second approval.",
            )
        return {"request": dict(request), "review": review}

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
        if str(request.get("requestType") or "").upper() == "DISK_ONLINE" and normalized_decision == APPROVED:
            self.require_repository_online_reviews(request)
            self.require_repository_online_approval_order(data, request, role)
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
        if str(request.get("requestType") or "").upper() == "DISK_ONLINE":
            request.setdefault("metadata", {})["workflowStatus"] = self.repository_online_workflow_status(request, data)
        request["updatedAt"] = created_at
        self.save(data)
        self.audit_event(event, approval_request=request, decision=decision_dict)
        if request["status"] == APPROVED:
            self.audit_event("approval.request.approved", approval_request=request)
        if request["status"] == REJECTED:
            self.audit_event("approval.request.rejected", approval_request=request)
        return {"request": dict(request), "decision": decision_dict}

    def require_repository_online_reviews(self, request: dict[str, Any]) -> None:
        reviews = (request.get("metadata") or {}).get("reviews")
        if not isinstance(reviews, dict):
            reviews = {}
        required = {"SECURITY_LOG_REVIEW", "HARDWARE_STATE_REVIEW", "MANAGER_REVIEW"}
        missing = sorted(required - set(reviews))
        if missing:
            raise PermissionError(f"repository online review required: {', '.join(missing)}")

    def require_repository_online_approval_order(
        self,
        data: dict[str, Any],
        request: dict[str, Any],
        approver_role: Role,
    ) -> None:
        approved_count = self.approval_count(data, str(request.get("id") or ""))
        expected_role = Role.SECURITY_ADMIN if approved_count == 0 else Role.SUPER_ADMIN
        if approver_role != expected_role:
            raise PermissionError(f"repository online approval order requires {expected_role.value}")

    def repository_online_workflow_status(self, request: dict[str, Any], data: dict[str, Any] | None = None) -> str:
        if request.get("status") == APPROVED:
            return "APPROVED_READY_TO_EXECUTE"
        if request.get("status") == REJECTED:
            return "REJECTED"
        if request.get("status") == EXPIRED:
            return "EXPIRED"
        reviews = (request.get("metadata") or {}).get("reviews")
        if not isinstance(reviews, dict):
            reviews = {}
        if not {"SECURITY_LOG_REVIEW", "HARDWARE_STATE_REVIEW"}.issubset(reviews):
            return "AWAITING_SECURITY_HARDWARE_REVIEW"
        if "MANAGER_REVIEW" not in reviews:
            return "AWAITING_MANAGER_REVIEW"
        source = data or self.load()
        count = self.approval_count(source, str(request.get("id") or ""))
        if count == 0:
            return "AWAITING_SECURITY_ADMIN_APPROVAL"
        if count == 1:
            return "AWAITING_SUPER_ADMIN_APPROVAL"
        return "APPROVED_READY_TO_EXECUTE"

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
