from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .audit import AuditLogger
from .rbac import Role, normalize_role
from .users import department_id_for


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

DEPARTMENT_REVIEW_ASSIGNMENTS = {
    "DISK_ONLINE": ["Security", "Hardware Control"],
    "DISK_OFFLINE": ["Backup Operation", "Security"],
    "POLICY_CHANGE": ["Security", "Audit"],
    "EMERGENCY_UNLOCK": ["Security", "Hardware Control", "Audit"],
    "HARDWARE_POWER_ON": ["Hardware Control", "Security"],
    "HARDWARE_POWER_OFF": ["Hardware Control", "Security"],
}

DEPARTMENT_REVIEW_STATUSES = {"PENDING", "IN_REVIEW", "REVIEWED", "NEEDS_CHANGES", "BLOCKED"}

ROLE_REVIEW_DEPARTMENTS = {
    Role.SECURITY_ADMIN.value: ["security"],
    Role.BACKUP_OPERATOR.value: ["backup-operation"],
    Role.HARDWARE_ADMIN.value: ["hardware-control"],
    Role.AUDITOR.value: ["audit"],
    Role.SUPER_ADMIN.value: ["management", "security", "backup-operation", "hardware-control", "audit"],
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
class DepartmentReview:
    id: str
    approvalRequestId: str
    departmentId: str
    reviewerUserId: str
    status: str
    comment: str
    createdAt: str
    updatedAt: str


@dataclass(frozen=True)
class ApprovalRequest:
    id: str
    requestType: str
    requesterUserId: str
    targetId: str
    status: str
    requiredApprovals: int
    allowedApproverRoles: list[str]
    reviewDepartments: list[str]
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
        department_reviews = data.get("departmentReviews")
        if not isinstance(department_reviews, list):
            department_reviews = []
        notifications = data.get("notifications")
        if not isinstance(notifications, list):
            notifications = []
        review_comments = data.get("reviewComments")
        if not isinstance(review_comments, list):
            review_comments = []
            for review in department_reviews:
                legacy_comments = review.get("comments") if isinstance(review.get("comments"), list) else []
                for comment in legacy_comments:
                    review_comments.append(
                        {
                            "id": comment.get("id") or uuid.uuid4().hex,
                            "approvalRequestId": review.get("approvalRequestId", ""),
                            "departmentReviewId": review.get("id", ""),
                            "authorUserId": comment.get("authorUserId") or comment.get("reviewerUserId") or "",
                            "comment": comment.get("comment", ""),
                            "createdAt": comment.get("createdAt") or review.get("updatedAt") or "",
                            "status": comment.get("status") or review.get("status") or "",
                        }
                    )
        for request in requests:
            if not isinstance(request, dict):
                continue
            request_type = str(request.get("requestType") or "").upper()
            departments = request.get("reviewDepartments")
            if not isinstance(departments, list):
                request["reviewDepartments"] = self.review_departments_for(request_type)
        return {
            "policies": policies,
            "requests": requests,
            "decisions": decisions,
            "departmentReviews": department_reviews,
            "reviewComments": review_comments,
            "notifications": notifications,
        }

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

    def review_departments_for(self, request_type: str) -> list[str]:
        return list(DEPARTMENT_REVIEW_ASSIGNMENTS.get(str(request_type or "").strip().upper(), []))

    def create_department_review_records(self, request: dict[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
        timestamp = iso(now or utc_now())
        records: list[dict[str, Any]] = []
        for department in request.get("reviewDepartments") or []:
            department_id = department_id_for(str(department or ""))
            records.append(
                asdict(
                    DepartmentReview(
                        id=uuid.uuid4().hex,
                        approvalRequestId=str(request.get("id") or ""),
                        departmentId=department_id,
                        reviewerUserId="",
                        status="PENDING",
                        comment="",
                        createdAt=timestamp,
                        updatedAt=timestamp,
                    )
                )
            )
        return records

    def create_department_notifications(self, request: dict[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
        timestamp = iso(now or utc_now())
        notifications: list[dict[str, Any]] = []
        for department in request.get("reviewDepartments") or []:
            department_id = department_id_for(str(department or ""))
            notifications.append(
                {
                    "id": uuid.uuid4().hex,
                    "userId": f"department:{department_id}",
                    "title": f"{request.get('requestType')} department review required",
                    "message": f"{request.get('requestType')} requires {department} department review before approval.",
                    "targetType": "APPROVAL_REQUEST",
                    "targetId": str(request.get("id") or ""),
                    "readAt": "",
                    "createdAt": timestamp,
                    "approvalRequestId": str(request.get("id") or ""),
                    "departmentId": department_id,
                }
            )
        return notifications

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
        review_departments = self.review_departments_for(normalized_type)
        request = ApprovalRequest(
            id=uuid.uuid4().hex,
            requestType=normalized_type,
            requesterUserId=str(requester_user_id or "unknown"),
            targetId=str(target_id or ""),
            status=PENDING,
            requiredApprovals=max(1, int(policy.get("requiredApprovals") or 1)),
            allowedApproverRoles=list(policy.get("allowedApproverRoles") or []),
            reviewDepartments=review_departments,
            expiresAt=iso(now + timedelta(minutes=max(1, int(policy.get("expiresInMinutes") or 30)))),
            createdAt=iso(now),
            updatedAt=iso(now),
            metadata=request_metadata,
        )
        record = asdict(request)
        data["requests"].append(record)
        data.setdefault("departmentReviews", []).extend(self.create_department_review_records(record, now))
        data.setdefault("reviewComments", [])
        data.setdefault("notifications", []).extend(self.create_department_notifications(record, now))
        self.save(data)
        self.audit_event("approval.request.created", approval_request=record)
        if review_departments:
            self.audit_event(
                "department.review.assigned",
                approval_request=record,
                reviewDepartments=review_departments,
            )
            self.audit_event(
                "department.review.notification.created",
                approvalRequestId=record["id"],
                reviewDepartments=review_departments,
                notifications=[item for item in data["notifications"] if item.get("approvalRequestId") == record["id"]],
            )
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
        self.sync_legacy_department_review(data, request, normalized_type, reviewer, text, role)
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

    def department_reviews_for(self, approval_request_id: str) -> list[dict[str, Any]]:
        data = self.load()
        comments_by_review: dict[str, list[dict[str, Any]]] = {}
        for comment in data.get("reviewComments", []):
            if str(comment.get("approvalRequestId") or "") != str(approval_request_id):
                continue
            comments_by_review.setdefault(str(comment.get("departmentReviewId") or ""), []).append(dict(comment))
        return [
            {**dict(review), "comments": comments_by_review.get(str(review.get("id") or ""), [])}
            for review in data.get("departmentReviews", [])
            if str(review.get("approvalRequestId") or "") == str(approval_request_id)
        ]

    def comment_department_review(
        self,
        approval_request_id: str,
        review_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        comment: str,
    ) -> dict[str, Any]:
        return self.update_department_review(
            approval_request_id,
            review_id,
            reviewer_user_id,
            reviewer_role,
            "IN_REVIEW",
            comment,
            "department.review.comment.created",
        )

    def mark_department_reviewed(
        self,
        approval_request_id: str,
        review_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        comment: str = "",
    ) -> dict[str, Any]:
        return self.update_department_review(
            approval_request_id,
            review_id,
            reviewer_user_id,
            reviewer_role,
            "REVIEWED",
            comment,
            "department.review.marked_reviewed",
        )

    def mark_department_needs_changes(
        self,
        approval_request_id: str,
        review_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        comment: str,
    ) -> dict[str, Any]:
        return self.update_department_review(
            approval_request_id,
            review_id,
            reviewer_user_id,
            reviewer_role,
            "NEEDS_CHANGES",
            comment,
            "department.review.needs_changes",
        )

    def block_department_review(
        self,
        approval_request_id: str,
        review_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        comment: str,
    ) -> dict[str, Any]:
        return self.update_department_review(
            approval_request_id,
            review_id,
            reviewer_user_id,
            reviewer_role,
            "BLOCKED",
            comment,
            "department.review.blocked",
        )

    def update_department_review(
        self,
        approval_request_id: str,
        review_id: str,
        reviewer_user_id: str,
        reviewer_role: Role | str,
        status: str,
        comment: str,
        event: str,
    ) -> dict[str, Any]:
        data = self.load()
        request = self.find_request(data, approval_request_id)
        self.expire_request_if_needed(data, request)
        if request.get("status") != PENDING:
            self.save(data)
            raise PermissionError(f"approval request is not pending: {request.get('status')}")
        review = self.find_department_review(data, approval_request_id, review_id)
        role = normalize_role(reviewer_role)
        if review.get("status") == "BLOCKED" and role != Role.SUPER_ADMIN:
            raise PermissionError("blocked department review requires Super Admin exception review")
        self.require_department_reviewer(review, reviewer_user_id, role)
        normalized_status = str(status or "").strip().upper()
        if normalized_status not in DEPARTMENT_REVIEW_STATUSES:
            raise ValueError("invalid department review status")
        text = str(comment or "").strip()
        if normalized_status in {"IN_REVIEW", "NEEDS_CHANGES", "BLOCKED"} and not text:
            raise ValueError("comment is required")
        now = iso(utc_now())
        review["reviewerUserId"] = str(reviewer_user_id or "").strip()
        review["status"] = normalized_status
        if text:
            review["comment"] = text
        review["updatedAt"] = now
        if text:
            data.setdefault("reviewComments", []).append(
                {
                    "id": uuid.uuid4().hex,
                    "approvalRequestId": str(approval_request_id),
                    "departmentReviewId": str(review_id),
                    "authorUserId": review["reviewerUserId"],
                    "comment": text,
                    "createdAt": now,
                    "status": normalized_status,
                }
            )
        request.setdefault("metadata", {})["departmentReviewStatus"] = self.department_review_status(request, data)
        request["updatedAt"] = now
        self.save(data)
        self.audit_event(event, approval_request=request, departmentReview=review, comment=text)
        return {"request": dict(request), "review": dict(review), "reviews": self.department_reviews_for(approval_request_id)}

    def find_department_review(self, data: dict[str, Any], approval_request_id: str, review_id: str) -> dict[str, Any]:
        for review in data.get("departmentReviews", []):
            if (
                str(review.get("approvalRequestId") or "") == str(approval_request_id)
                and str(review.get("id") or "") == str(review_id)
            ):
                return review
        raise KeyError(f"department review not found: {review_id}")

    def require_department_reviewer(self, review: dict[str, Any], reviewer_user_id: str, reviewer_role: Role) -> None:
        reviewer = str(reviewer_user_id or "").strip()
        if not reviewer:
            raise ValueError("reviewerUserId is required")
        department_id = str(review.get("departmentId") or "")
        allowed = ROLE_REVIEW_DEPARTMENTS.get(reviewer_role.value, [])
        if department_id not in allowed:
            raise PermissionError(f"reviewer role is not assigned to department: {department_id}")

    def sync_legacy_department_review(
        self,
        data: dict[str, Any],
        request: dict[str, Any],
        review_type: str,
        reviewer: str,
        comment: str,
        role: Role,
    ) -> None:
        department_by_review_type = {
            "SECURITY_LOG_REVIEW": "security",
            "HARDWARE_STATE_REVIEW": "hardware-control",
        }
        department_id = department_by_review_type.get(review_type)
        if not department_id:
            return
        for review in data.get("departmentReviews", []):
            if review.get("approvalRequestId") == request.get("id") and review.get("departmentId") == department_id:
                now = iso(utc_now())
                review["reviewerUserId"] = reviewer
                review["status"] = "REVIEWED"
                review["comment"] = comment
                review["updatedAt"] = now
                data.setdefault("reviewComments", []).append(
                    {
                        "id": uuid.uuid4().hex,
                        "approvalRequestId": str(request.get("id") or ""),
                        "departmentReviewId": str(review.get("id") or ""),
                        "authorUserId": reviewer,
                        "comment": comment,
                        "createdAt": now,
                        "status": "REVIEWED",
                        "legacyReviewType": review_type,
                    }
                )
                self.audit_event("department.review.marked_reviewed", approval_request=request, departmentReview=review)
                break

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
        if normalized_decision == APPROVED:
            self.require_department_reviews_completed(data, request, role)
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

    def department_review_status(self, request: dict[str, Any], data: dict[str, Any] | None = None) -> str:
        reviews = [
            review
            for review in (data or self.load()).get("departmentReviews", [])
            if str(review.get("approvalRequestId") or "") == str(request.get("id") or "")
        ]
        if not reviews:
            return "NOT_REQUIRED"
        statuses = {str(review.get("status") or "PENDING").upper() for review in reviews}
        if "BLOCKED" in statuses:
            return "BLOCKED"
        if "NEEDS_CHANGES" in statuses:
            return "NEEDS_CHANGES"
        if statuses == {"REVIEWED"}:
            return "REVIEWED"
        if "IN_REVIEW" in statuses:
            return "IN_REVIEW"
        return "PENDING"

    def require_department_reviews_completed(self, data: dict[str, Any], request: dict[str, Any], approver_role: Role) -> None:
        status = self.department_review_status(request, data)
        if status == "NOT_REQUIRED":
            return
        if status == "BLOCKED":
            if approver_role != Role.SUPER_ADMIN:
                raise PermissionError("blocked department review requires Super Admin exception review")
            return
        if status == "NEEDS_CHANGES":
            raise PermissionError("department review needs changes before approval")
        if status != "REVIEWED":
            raise PermissionError("department review required before approval")

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
