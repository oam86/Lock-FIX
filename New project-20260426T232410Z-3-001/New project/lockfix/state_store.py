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
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, slot_id: str):
        state = self.read_all().get(slot_id)
        return LockFixState(state) if state else None

    def set(self, slot_id: str, state: LockFixState) -> None:
        data = self.read_all()
        data[slot_id] = state.value
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
