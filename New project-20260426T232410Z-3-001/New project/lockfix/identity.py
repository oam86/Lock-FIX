from __future__ import annotations

import hashlib

from .config import SlotConfig


def compute_uid(serial: str, model: str, wwn: str, slot_id: str) -> str:
    raw = "|".join([serial.strip(), model.strip(), wwn.strip(), slot_id.strip()])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def slot_uid(slot: SlotConfig) -> str:
    identity = slot.identity
    return compute_uid(
        identity.get("serial", ""),
        identity.get("model", ""),
        identity.get("wwn", ""),
        slot.slot_id,
    )


def verify_uid(slot: SlotConfig) -> tuple[bool, str]:
    current_uid = slot_uid(slot)
    expected = slot.expected_uid
    if not expected or expected == "replace-with-registered-uid":
        return True, current_uid
    return current_uid == expected, current_uid
