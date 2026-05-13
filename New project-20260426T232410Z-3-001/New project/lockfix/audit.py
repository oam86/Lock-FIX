from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: str, **payload: Any) -> None:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": str(payload.pop("id", "") or uuid.uuid4().hex),
            "ts": now,
            "createdAt": str(payload.pop("createdAt", "") or now),
            "event": event,
            "action": str(payload.pop("action", "") or event),
            "actorUserId": str(payload.pop("actorUserId", "") or payload.get("actor") or payload.get("user") or ""),
            "resourceType": str(payload.pop("resourceType", "") or infer_resource_type(event)),
            "resourceId": str(
                payload.pop("resourceId", "")
                or payload.get("user_id")
                or payload.get("slot_id")
                or payload.get("approvalRequestId")
                or nested_id(payload.get("approval_request"))
                or ""
            ),
            "ipAddress": str(payload.pop("ipAddress", "") or payload.get("client_ip") or ""),
            "userAgent": str(payload.pop("userAgent", "") or payload.get("user_agent") or ""),
            "result": str(payload.pop("result", "") or infer_result(event, payload)),
            "beforeValue": payload.pop("beforeValue", payload.get("before", {})),
            "afterValue": payload.pop("afterValue", payload.get("after", payload.get("user") or payload.get("approval_request") or {})),
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def nested_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    return ""


def infer_resource_type(event: str) -> str:
    text = str(event or "")
    if text.startswith("auth."):
        return "AUTH"
    if text.startswith("admin.user."):
        return "USER"
    if "role" in text:
        return "ROLE"
    if text.startswith("approval."):
        return "APPROVAL"
    if text.startswith("disk."):
        return "DISK"
    if text.startswith("power."):
        return "HARDWARE_POWER"
    if "policy" in text:
        return "POLICY"
    if text.startswith("emergency."):
        return "EMERGENCY"
    return "SYSTEM"


def infer_result(event: str, payload: dict[str, Any]) -> str:
    if "result" in payload:
        return str(payload.get("result") or "")
    text = str(event or "").lower()
    if any(marker in text for marker in ("failed", "error", "denied", "blocked", "rejected")):
        return "FAILED"
    if "expired" in text:
        return "EXPIRED"
    if any(marker in text for marker in ("success", "approved", "completed", "created", "updated", "disabled")):
        return "SUCCESS"
    return "INFO"
