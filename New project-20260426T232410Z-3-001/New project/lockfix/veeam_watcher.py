from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .config import LockFixConfig
from .controller import LockFixController
from .veeam_diagnostics import run_veeam_diagnostics


class VeeamWatcher:
    def __init__(
        self,
        config: LockFixConfig,
        controller: LockFixController,
        state_path: Path | None = None,
    ) -> None:
        self.config = config
        self.controller = controller
        self.state_path = state_path or config.state_path.parent / "veeam_watcher_state.json"

    def poll_once(self, slot_id: str | None = None) -> dict[str, Any]:
        diagnostics = run_veeam_diagnostics(self.config, self.controller)
        if not self.config.veeam.enabled:
            result = {
                "ok": False,
                "action": "disabled",
                "diagnostics": diagnostics,
                "message": "Veeam watcher is disabled in config.veeam.enabled.",
            }
            self.controller.audit.write("veeam.watch.disabled", **result)
            return result

        condition = diagnostics.get("isolate_condition") if isinstance(diagnostics.get("isolate_condition"), dict) else {}
        pre_checks = diagnostics.get("pre_isolate_checks") if isinstance(diagnostics.get("pre_isolate_checks"), dict) else {}
        if diagnostics.get("error"):
            result = {
                "ok": False,
                "action": "wait",
                "error_type": diagnostics.get("error_type"),
                "message": diagnostics.get("error"),
                "diagnostics": diagnostics,
            }
            self.controller.audit.write("veeam.watch.error", **result)
            return result
        if condition.get("already_processed"):
            result = {
                "ok": True,
                "action": "already_isolated",
                "session_id": condition.get("session_id", ""),
                "job_name": condition.get("job_name", ""),
                "job_id": condition.get("job_id", ""),
                "status": condition.get("status", ""),
                "diagnostics": diagnostics,
            }
            self.controller.audit.write("veeam.watch.duplicate_skip", **result)
            return result
        if not condition.get("would_call_isolate"):
            result = {
                "ok": True,
                "action": "wait",
                "session_id": condition.get("session_id", ""),
                "job_name": condition.get("job_name", self.config.veeam.job_name),
                "job_id": condition.get("job_id", self.config.veeam.job_id),
                "status": condition.get("status", ""),
                "match_strategy": (diagnostics.get("matching") or {}).get("strategy"),
                "pre_isolate_checks": pre_checks,
                "message": "Veeam session is not ready for isolate. job_id matching, Success status, post-success delay, I/O quiet policy, and repository resync checks must all pass.",
                "diagnostics": diagnostics,
            }
            self.controller.audit.write("veeam.watch.session_wait", **result)
            return result

        latest_session = diagnostics.get("latest_configured_session") if isinstance(diagnostics.get("latest_configured_session"), dict) else {}
        restore_scope = latest_session.get("restore_point_scope") if isinstance(latest_session.get("restore_point_scope"), dict) else {}
        repository_path = str(
            latest_session.get("repository_path")
            or restore_scope.get("repository_path")
            or self.config.veeam.target_repository_path
            or ""
        )
        target_slot_id = slot_id or next(iter(self.config.slots))
        isolated_state = self.controller.isolate(target_slot_id, repository_path=repository_path)
        state = self.read_state()
        processed_session_ids = set(state.get("processed_session_ids") or [])
        current_session_id = str(condition.get("session_id") or "")
        record = {
            "last_isolated_session_id": current_session_id,
            "processed_session_ids": sorted(processed_session_ids | {current_session_id}),
            "slot_id": target_slot_id,
            "job_name": condition.get("job_name", ""),
            "job_id": condition.get("job_id", ""),
            "status": condition.get("status", ""),
            "repository_path": repository_path,
            "lockfix_state": isolated_state.value,
            "isolated_at_epoch": time.time(),
            "pre_isolate_checks": pre_checks,
        }
        self.write_state(record)
        result = {
            "ok": True,
            "action": "isolated",
            "session_id": current_session_id,
            "diagnostics": diagnostics,
            **record,
        }
        self.controller.audit.write("veeam.watch.isolated", **result)
        return result

    def run_forever(self, slot_id: str | None = None) -> None:
        while True:
            self.poll_once(slot_id=slot_id)
            time.sleep(self.config.veeam.poll_interval_seconds)

    def read_state(self) -> dict[str, Any]:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def write_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
