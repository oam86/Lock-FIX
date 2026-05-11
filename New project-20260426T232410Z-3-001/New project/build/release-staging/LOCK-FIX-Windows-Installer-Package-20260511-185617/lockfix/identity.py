from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from typing import Callable

from .config import SlotConfig


@dataclass(frozen=True)
class FingerprintField:
    key: str
    label: str
    aliases: tuple[str, ...]
    fallback: Callable[[SlotConfig], str] | None = None
    hash_input: bool = True


FINGERPRINT_FIELDS: tuple[FingerprintField, ...] = (
    FingerprintField("serial", "Serial Number", ("serial", "serial_number")),
    FingerprintField("wwn", "WWN / NAA / EUI", ("wwn", "naa", "eui")),
    FingerprintField(
        "unique_id",
        "Device Unique ID",
        ("unique_id", "device_unique_id", "device_id", "pnp_device_id"),
        lambda slot: slot.slot_id,
    ),
    FingerprintField(
        "size",
        "Disk Size",
        ("size", "disk_size", "size_bytes", "capacity", "capacity_bytes"),
        lambda slot: disk_size_label(slot),
    ),
    FingerprintField("model", "Model", ("model", "disk_model")),
    FingerprintField("firmware", "Firmware Revision", ("firmware", "firmware_revision", "revision")),
    FingerprintField(
        "controller_location",
        "Controller Location",
        ("controller_location", "controller", "location", "bus_location"),
        lambda slot: slot.slot_id,
    ),
)


def disk_size_label(slot: SlotConfig) -> str:
    for candidate in (slot.mount_point, slot.device):
        if not candidate:
            continue
        try:
            total_bytes = shutil.disk_usage(str(candidate)).total
        except (OSError, ValueError):
            continue
        total_gb = max(1, round(total_bytes / (1024**3)))
        return f"{total_gb:,} GB"
    return ""


def _field_value(slot: SlotConfig, field: FingerprintField) -> str:
    identity = slot.identity
    for alias in field.aliases:
        value = identity.get(alias)
        if value not in (None, ""):
            return str(value).strip()
    if field.fallback:
        return str(field.fallback(slot)).strip()
    return ""


def fingerprint_parts(slot: SlotConfig) -> list[dict[str, str]]:
    return [
        {
            "key": field.key,
            "label": field.label,
            "value": _field_value(slot, field),
            "hash_input": field.hash_input,
        }
        for field in FINGERPRINT_FIELDS
    ]


def fingerprint_raw(parts: list[dict[str, str]]) -> str:
    return "|".join(str(part.get("value", "")).strip() for part in parts if part.get("hash_input", True))


def compute_fingerprint(parts: list[dict[str, str]]) -> str:
    return hashlib.sha256(fingerprint_raw(parts).encode("utf-8")).hexdigest()


def fingerprint_formula(parts: list[dict[str, str]]) -> str:
    labels = [str(part.get("label", "")) for part in parts if part.get("hash_input", True)]
    return "SHA256(" + " + ".join(labels) + ")"


def compute_uid(
    serial: str,
    model: str,
    wwn: str,
    slot_id: str,
    size: str = "",
    firmware: str = "",
    controller_location: str = "",
) -> str:
    raw = "|".join(
        [
            serial.strip(),
            wwn.strip(),
            slot_id.strip(),
            size.strip(),
            model.strip(),
            firmware.strip(),
            controller_location.strip(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def slot_uid(slot: SlotConfig) -> str:
    return compute_fingerprint(fingerprint_parts(slot))


def verify_uid(slot: SlotConfig) -> tuple[bool, str]:
    current_uid = slot_uid(slot)
    expected = slot.expected_uid
    if not expected or expected == "replace-with-registered-uid":
        return True, current_uid
    return current_uid == expected, current_uid
