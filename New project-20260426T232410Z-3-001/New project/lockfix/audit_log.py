from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditLog:
    id: str
    actorUserId: str
    action: str
    resourceType: str
    resourceId: str
    ipAddress: str
    userAgent: str
    result: str
    beforeValue: Any
    afterValue: Any
    createdAt: str


AUDIT_LOG_FIELDS = tuple(AuditLog.__dataclass_fields__.keys())


def normalize_audit_log(record: dict[str, Any]) -> dict[str, Any]:
    created_at = str(record.get("createdAt") or record.get("ts") or "")
    action = str(record.get("action") or record.get("event") or "")
    log = AuditLog(
        id=str(record.get("id") or stable_audit_id(record)),
        actorUserId=str(record.get("actorUserId") or record.get("actor") or record.get("user") or ""),
        action=action,
        resourceType=str(record.get("resourceType") or infer_resource_type(action)),
        resourceId=str(
            record.get("resourceId")
            or record.get("user_id")
            or record.get("slot_id")
            or nested_id(record.get("approval_request"))
            or ""
        ),
        ipAddress=str(record.get("ipAddress") or record.get("client_ip") or ""),
        userAgent=str(record.get("userAgent") or record.get("user_agent") or ""),
        result=str(record.get("result") or infer_result(action)),
        beforeValue=record.get("beforeValue", record.get("before", {})),
        afterValue=record.get("afterValue", record.get("after", record.get("user") or record.get("approval_request") or {})),
        createdAt=created_at,
    )
    data = asdict(log)
    data["raw"] = record
    return data


def tail_text_lines(path: Path, limit: int = 1000, chunk_size: int = 64 * 1024) -> list[str]:
    limit = max(1, int(limit or 1))
    chunk_size = max(4096, int(chunk_size or 4096))
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            position = handle.tell()
            data = bytearray()
            newline_count = 0
            while position > 0 and newline_count <= limit:
                read_size = min(chunk_size, position)
                position -= read_size
                handle.seek(position)
                chunk = handle.read(read_size)
                data[:0] = chunk
                newline_count += chunk.count(b"\n")
    except OSError:
        return []
    return data.decode("utf-8", errors="replace").splitlines()[-limit:]


def read_audit_logs(path: Path, limit: int = 1000) -> list[dict[str, Any]]:
    try:
        lines = tail_text_lines(path, limit=limit)
    except OSError:
        return []
    items: list[dict[str, Any]] = []
    for line in lines:
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            raw = {"event": "parse_error", "raw": line}
        if isinstance(raw, dict):
            items.append(normalize_audit_log(raw))
    return list(reversed(items))


def audit_logs_to_csv(logs: list[dict[str, Any]]) -> bytes:
    rows = [",".join(AUDIT_LOG_FIELDS)]
    for log in logs:
        rows.append(",".join(csv_cell(log.get(field, "")) for field in AUDIT_LOG_FIELDS))
    return ("\n".join(rows) + "\n").encode("utf-8-sig")


def csv_cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value or "")
    return '"' + text.replace('"', '""') + '"'


def stable_audit_id(record: dict[str, Any]) -> str:
    seed = json.dumps(record, ensure_ascii=False, sort_keys=True)
    import hashlib

    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]


def nested_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    return ""


def infer_resource_type(action: str) -> str:
    text = str(action or "")
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


def infer_result(action: str) -> str:
    text = str(action or "").lower()
    if any(marker in text for marker in ("failed", "error", "denied", "blocked", "rejected")):
        return "FAILED"
    if "expired" in text:
        return "EXPIRED"
    if any(marker in text for marker in ("success", "approved", "completed", "created", "updated", "disabled")):
        return "SUCCESS"
    return "INFO"
