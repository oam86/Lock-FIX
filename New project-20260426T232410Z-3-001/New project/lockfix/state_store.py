from __future__ import annotations

import json
from pathlib import Path

from .states import LockFixState


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_all(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        raw = self.path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = self._recover_corrupt_state(raw)
        if not isinstance(data, dict):
            return {}
        return {str(key): str(value) for key, value in data.items()}

    def _recover_corrupt_state(self, raw: str) -> dict[str, str]:
        decoder = json.JSONDecoder()
        try:
            data, _ = decoder.raw_decode(raw.lstrip("\ufeff \t\r\n"))
        except json.JSONDecodeError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        try:
            backup_path = self.path.with_suffix(self.path.suffix + ".corrupt")
            backup_path.write_text(raw, encoding="utf-8")
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
        return {str(key): str(value) for key, value in data.items()}

    def get(self, slot_id: str):
        state = self.read_all().get(slot_id)
        return LockFixState(state) if state else None

    def set(self, slot_id: str, state: LockFixState) -> None:
        data = self.read_all()
        data[slot_id] = state.value
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
