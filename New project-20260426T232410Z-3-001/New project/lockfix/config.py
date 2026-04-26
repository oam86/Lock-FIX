from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PowerConfig:
    type: str
    off_command: list[str]
    on_command: list[str]


@dataclass(frozen=True)
class SlotConfig:
    slot_id: str
    device: str
    mount_point: Path
    expected_uid: str
    identity: dict[str, str]
    manifest_path: str
    power: PowerConfig


@dataclass(frozen=True)
class LockFixConfig:
    dry_run: bool
    state_path: Path
    audit_log_path: Path
    io_quiet_seconds: int
    disk_wait_seconds: int
    slots: dict[str, SlotConfig]

    def slot(self, slot_id: str) -> SlotConfig:
        try:
            return self.slots[slot_id]
        except KeyError as exc:
            raise ValueError(f"unknown slot: {slot_id}") from exc


def load_config(path) -> LockFixConfig:
    base = Path(path).resolve().parent
    raw = json.loads(Path(path).read_text(encoding="utf-8"))

    def resolve_path(value: str) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else base.parent / candidate

    slots: dict[str, SlotConfig] = {}
    for item in raw.get("slots", []):
        power_raw: dict[str, Any] = item["power"]
        slot = SlotConfig(
            slot_id=item["slot_id"],
            device=item["device"],
            mount_point=Path(item["mount_point"]),
            expected_uid=item.get("expected_uid", ""),
            identity=dict(item.get("identity", {})),
            manifest_path=item.get("manifest_path", ".lockfix_manifest.sha256"),
            power=PowerConfig(
                type=power_raw.get("type", "mock"),
                off_command=list(power_raw.get("off_command", [])),
                on_command=list(power_raw.get("on_command", [])),
            ),
        )
        slots[slot.slot_id] = slot

    return LockFixConfig(
        dry_run=bool(raw.get("dry_run", True)),
        state_path=resolve_path(raw.get("state_path", "runtime/state.json")),
        audit_log_path=resolve_path(raw.get("audit_log_path", "runtime/audit.jsonl")),
        io_quiet_seconds=int(raw.get("io_quiet_seconds", 30)),
        disk_wait_seconds=int(raw.get("disk_wait_seconds", 60)),
        slots=slots,
    )
