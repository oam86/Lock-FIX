from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .config import LockFixConfig
from .controller import LockFixController
from .veeam_client import (
    VeeamClient,
    VeeamError,
    VeeamSettings,
    is_success_status,
    match_sessions,
    session_id,
    session_job_id,
    session_name,
    session_sort_key,
    session_status,
)


class VeeamWatcher:
    def __init__(
        self,
        config: LockFixConfig,
        controller: LockFixController,
        state_path: Path | None = None,
    ) -> None:
        self.config = config
        self.controller = controller
        self.settings = VeeamSettings.from_config(config.veeam)
        self.client = VeeamClient(self.settings)
        self.state_path = state_path or config.state_path.parent / "veeam_watcher_state.json"

    def poll_once(self, slot_id: str | None = None) -> dict[str, Any]:
        if not self.config.veeam.enabled:
            result = {"ok": False, "action": "disabled", "message": "Veeam watcher is disabled in config.veeam.enabled."}
            self.controller.audit.write("veeam.watch.disabled", **result)
            return result

        port_check = self.client.check_port()
        if not port_check["ok"]:
            self.controller.audit.write("veeam.watch.error", **port_check)
            return {"ok": False, "action": "wait", "error_type": "ConnectionError", "checks": {"port": port_check}}

        try:
            self.client.login()
            jobs = self.client.get_jobs()
            sessions = self.client.get_sessions()
            match = match_sessions(sessions, self.settings.job_name, self.settings.job_id)
            session = sorted(match["matches"], key=session_sort_key, reverse=True)[0] if match["matches"] else None
        except VeeamError as exc:
            result = {
                "ok": False,
                "action": "wait",
                "error_type": getattr(exc, "code", exc.__class__.__name__),
                "message": str(exc),
            }
            self.controller.audit.write("veeam.watch.error", **result)
            return result

        if not session:
            result = {
                "ok": True,
                "action": "wait",
                "message": "No Veeam session found for configured job.",
                "job_name": self.settings.job_name,
                "job_id": self.settings.job_id,
                "jobs_count": len(jobs),
                "sessions_count": len(sessions),
                "match_strategy": match["strategy"],
                "similar_candidates": match["candidates"],
            }
            self.controller.audit.write("veeam.watch.no_session", **result)
            return result

        current_session_id = session_id(session)
        current_status = session_status(session)
        current_name = session_name(session)
        current_job_id = session_job_id(session)
        if not is_success_status(current_status, self.config.veeam.isolate_on_status):
            result = {
                "ok": True,
                "action": "wait",
                "session_id": current_session_id,
                "job_name": current_name,
                "job_id": current_job_id,
                "status": current_status,
                "message": "Latest Veeam session is not in isolate_on_status.",
            }
            self.controller.audit.write("veeam.watch.session_wait", **result)
            return result

        state = self.read_state()
        processed_session_ids = set(state.get("processed_session_ids") or [])
        if state.get("last_isolated_session_id") == current_session_id or current_session_id in processed_session_ids:
            result = {
                "ok": True,
                "action": "already_isolated",
                "session_id": current_session_id,
                "job_name": current_name,
                "job_id": current_job_id,
                "status": current_status,
            }
            self.controller.audit.write("veeam.watch.duplicate_skip", **result)
            return result

        target_slot_id = slot_id or next(iter(self.config.slots))
        isolated_state = self.controller.isolate(target_slot_id)
        record = {
            "last_isolated_session_id": current_session_id,
            "processed_session_ids": sorted(processed_session_ids | {current_session_id}),
            "slot_id": target_slot_id,
            "job_name": current_name,
            "job_id": current_job_id,
            "status": current_status,
            "lockfix_state": isolated_state.value,
            "isolated_at_epoch": time.time(),
        }
        self.write_state(record)
        result = {"ok": True, "action": "isolated", "session_id": current_session_id, **record}
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
