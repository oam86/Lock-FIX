from __future__ import annotations

import json
import os
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from lockfix.config import VeeamConfig


@dataclass(frozen=True)
class VeeamApiClient:
    config: VeeamConfig

    @property
    def base_url(self) -> str:
        return f"https://{self.config.host}:{self.config.port}"

    def summary(self) -> dict:
        if not self.config.enabled:
            return self.mock_summary("DISABLED", "Veeam API integration is configured but disabled.", interlock_ready=False)
        if not self.config.host:
            return self.mock_summary("NOT_CONFIGURED", "Veeam API host is not configured.", interlock_ready=False)

        username = os.environ.get(self.config.username_env, "")
        password = os.environ.get(self.config.password_env, "")
        if not username or not password:
            return self.mock_summary(
                "WAITING_FOR_CREDENTIALS",
                f"Set {self.config.username_env} and {self.config.password_env} to enable live Veeam API polling.",
                interlock_ready=False,
            )

        try:
            token = self.access_token(username, password)
            server_time = self.get_json("/api/v1/serverTime", token)
            try:
                sessions = self.get_json("/api/v1/sessions?limit=5", token)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                sessions = {"data": [], "error": str(exc)}
            try:
                jobs = self.get_json("/api/v1/jobs/states?limit=200", token)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                jobs = {"data": [], "error": str(exc)}
            try:
                job_defs = self.get_json("/api/v1/jobs?limit=200", token)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError):
                job_defs = {"data": []}
            try:
                repositories = self.get_json("/api/v1/backupInfrastructure/repositories/states?limit=200", token)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                repositories = {"data": [], "error": str(exc)}
            return self.live_summary(server_time, sessions, jobs, job_defs, repositories)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            return self.mock_summary("ERROR", f"Veeam API polling failed: {exc}", interlock_ready=False)

    def access_token(self, username: str, password: str) -> str:
        data = urlencode(
            {
                "grant_type": "password",
                "username": username,
                "password": password,
            }
        ).encode("utf-8")
        response = self.request(
            "/api/oauth2/token",
            method="POST",
            body=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = response.get("access_token")
        if not token:
            raise ValueError("missing access_token in Veeam response")
        return str(token)

    def get_json(self, path: str, token: str) -> dict:
        return self.request(path, headers={"Authorization": f"Bearer {token}"})

    def request(self, path: str, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None) -> dict:
        request_headers = {
            "Accept": "application/json",
            "x-api-version": self.config.api_version,
        }
        request_headers.update(headers or {})
        request = Request(f"{self.base_url}{path}", data=body, headers=request_headers, method=method)
        context = None if self.config.verify_tls else ssl._create_unverified_context()
        with urlopen(request, timeout=self.config.timeout_seconds, context=context) as response:
            payload = response.read()
        return json.loads(payload.decode("utf-8")) if payload else {}

    def live_summary(self, server_time: dict, sessions: dict, jobs: dict, job_defs: dict, repositories: dict) -> dict:
        items = sessions.get("data") or sessions.get("items") or []
        job_names = self.job_name_map(job_defs.get("data") or [])
        normalized = [self.normalize_session(item, job_names) for item in items[:5]]
        job_states = [self.normalize_job_state(item, job_names) for item in (jobs.get("data") or [])]
        policy_monitor = self.policy_monitor(job_states)
        if jobs.get("error"):
            policy_monitor["status"] = "ERROR"
            policy_monitor["message"] = f"Job states polling failed: {jobs['error']}"
        repository_states = [self.normalize_repository(item) for item in (repositories.get("data") or [])]
        repository_monitor = self.repository_monitor(repository_states)
        if repositories.get("error"):
            repository_monitor["status"] = "ERROR"
            repository_monitor["message"] = f"Repository states polling failed: {repositories['error']}"
        session_error = sessions.get("error")
        active = next((item for item in normalized if self.session_running(item)), None)
        latest = active or (normalized[0] if normalized else None)
        completed = bool(latest and latest["result"] == "Success" and self.session_complete(latest))
        ready = bool(completed and not active)
        backup_monitor = self.backup_monitor(latest, ready)
        session_result_monitor = self.session_result_monitor(normalized)
        if session_error:
            backup_monitor = {
                "state": "ERROR",
                "title": f"Veeam session polling failed: {session_error}",
                "progress": 0,
                "completed": False,
                "running": False,
                "started_at": "-",
                "ended_at": "-",
                "result": "Forbidden" if "403" in str(session_error) else "Error",
            }
            session_result_monitor["status"] = "ERROR"
            session_result_monitor["message"] = f"Veeam session polling failed: {session_error}"
        return {
            "mode": "LIVE",
            "status": "CONNECTED",
            "endpoint": self.base_url,
            "api_version": self.config.api_version,
            "server_time": server_time.get("serverTime") or server_time.get("time") or "-",
            "message": "Veeam authentication is valid. Some data endpoints may still require Veeam role permissions.",
            "last_backup": latest or {},
            "backup_monitor": backup_monitor,
            "session_result_monitor": session_result_monitor,
            "policy_monitor": policy_monitor,
            "repository_monitor": repository_monitor,
            "interlock_ready": ready,
            "interlock_policy": "Trigger LOCK-FIX isolation only after a successful Veeam backup session.",
            "sessions": normalized,
        }

    def session_result_monitor(self, sessions: list[dict]) -> dict:
        success = sum(1 for item in sessions if item["result"] == "Success")
        warning = sum(1 for item in sessions if item["result"] == "Warning")
        failed = sum(1 for item in sessions if item["result"] == "Failed")
        running = sum(1 for item in sessions if self.session_running(item))
        return {
            "status": "LIVE" if sessions else "NO_DATA",
            "message": "Veeam session result data is available." if sessions else "No Veeam session result data returned.",
            "session_count": len(sessions),
            "success_count": success,
            "warning_count": warning,
            "failed_count": failed,
            "running_count": running,
        }

    def job_name_map(self, jobs: list[dict[str, Any]]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for item in jobs:
            name = self.pick_text(item, "name", "jobName", "displayName")
            for key in ("id", "jobId", "uid", "uniqueId"):
                value = item.get(key)
                if value and name:
                    mapping[str(value)] = name
        return mapping

    def normalize_job_state(self, item: dict[str, Any], job_names: dict[str, str] | None = None) -> dict:
        last_result = item.get("lastResult")
        if isinstance(last_result, dict):
            last_result_value = last_result.get("result") or last_result.get("message") or "Unknown"
        else:
            last_result_value = last_result or item.get("result") or "Unknown"
        job_id = self.pick_text(item, "id", "jobId", "uid", "uniqueId")
        name = self.pick_text(item, "name", "jobName", "displayName") or (job_names or {}).get(job_id, "")
        return {
            "id": job_id or "-",
            "name": name or "Backup Policy",
            "type": item.get("type") or item.get("jobType") or "-",
            "status": item.get("status") or item.get("state") or "Unknown",
            "last_result": last_result_value,
            "last_run": item.get("lastRun") or item.get("lastStartTime") or item.get("creationTime") or "-",
            "next_run": item.get("nextRun") or "-",
            "is_enabled": item.get("isEnabled", item.get("scheduleEnabled", True)),
        }

    def policy_monitor(self, policies: list[dict]) -> dict:
        success = sum(1 for item in policies if item["last_result"] == "Success")
        warning = sum(1 for item in policies if item["last_result"] == "Warning")
        failed = sum(1 for item in policies if item["last_result"] == "Failed")
        running = sum(1 for item in policies if str(item["status"]).lower() == "running")
        return {
            "status": "LIVE" if policies else "NO_DATA",
            "message": "Backup policy states are available." if policies else "No backup policy state data returned.",
            "policy_count": len(policies),
            "success_count": success,
            "warning_count": warning,
            "failed_count": failed,
            "running_count": running,
            "policies": policies,
        }

    def normalize_repository(self, item: dict[str, Any]) -> dict:
        capacity = self.float_value(item.get("capacityGB"))
        free = self.float_value(item.get("freeGB"))
        used = self.float_value(item.get("usedSpaceGB"))
        if used <= 0 and capacity > 0:
            used = max(0.0, capacity - free)
        usage = round((used / capacity) * 100, 1) if capacity > 0 else 0.0
        return {
            "id": item.get("id") or "-",
            "name": item.get("name") or "Repository",
            "type": item.get("type") or "-",
            "host": item.get("hostName") or "-",
            "path": item.get("path") or "-",
            "capacity_gb": round(capacity, 1),
            "free_gb": round(free, 1),
            "used_gb": round(used, 1),
            "usage_percent": usage,
            "is_online": bool(item.get("isOnline", False)),
            "is_out_of_date": bool(item.get("isOutOfDate", False)),
        }

    def repository_monitor(self, repositories: list[dict]) -> dict:
        total_capacity = sum(item["capacity_gb"] for item in repositories if item["capacity_gb"] > 0)
        total_free = sum(item["free_gb"] for item in repositories if item["free_gb"] > 0)
        total_used = sum(item["used_gb"] for item in repositories if item["used_gb"] > 0)
        usage = round((total_used / total_capacity) * 100, 1) if total_capacity > 0 else 0.0
        online = sum(1 for item in repositories if item["is_online"])
        return {
            "status": "LIVE" if repositories else "NO_DATA",
            "message": "Repository capacity data is available." if repositories else "No repository capacity data returned.",
            "repository_count": len(repositories),
            "online_count": online,
            "total_capacity_gb": round(total_capacity, 1),
            "total_used_gb": round(total_used, 1),
            "total_free_gb": round(total_free, 1),
            "usage_percent": usage,
            "repositories": repositories,
        }

    def float_value(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def normalize_session(self, item: dict[str, Any], job_names: dict[str, str] | None = None) -> dict:
        result = item.get("result")
        if isinstance(result, dict):
            result_value = result.get("result") or result.get("message") or "Unknown"
        else:
            result_value = result or item.get("status") or "Unknown"
        job_id = self.pick_text(item, "jobId", "jobUid", "job_id")
        name = self.pick_text(item, "name", "jobName", "displayName") or (job_names or {}).get(job_id, "")
        return {
            "name": name or "Veeam session",
            "job_id": job_id or "-",
            "session_type": item.get("sessionType") or item.get("type") or "-",
            "state": item.get("state") or item.get("status") or "Unknown",
            "result": result_value,
            "creation_time": item.get("creationTime") or item.get("startTime") or "-",
            "end_time": item.get("endTime") or item.get("stopTime") or "-",
            "progress": item.get("progressPercent", 100 if result_value == "Success" else 0),
        }

    def pick_text(self, item: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = item.get(key)
            if value:
                return str(value)
        return ""

    def backup_monitor(self, session: dict | None, interlock_ready: bool) -> dict:
        if not session:
            return {
                "state": "NO_SESSION",
                "title": "No backup session detected",
                "progress": 0,
                "completed": False,
                "running": False,
                "started_at": "-",
                "ended_at": "-",
                "result": "Unknown",
            }
        running = self.session_running(session)
        completed = self.session_complete(session) and session["result"] == "Success"
        if running:
            state = "RUNNING"
            title = "Backup in progress"
        elif completed and interlock_ready:
            state = "COMPLETED"
            title = "Backup completed"
        elif completed:
            state = "COMPLETED_WAITING"
            title = "Backup completed, waiting for interlock"
        else:
            state = "ATTENTION"
            title = "Backup requires attention"
        return {
            "state": state,
            "title": title,
            "progress": max(0, min(100, int(session.get("progress") or 0))),
            "completed": completed,
            "running": running,
            "started_at": session.get("creation_time") or "-",
            "ended_at": session.get("end_time") or "-",
            "result": session.get("result") or "Unknown",
        }

    def session_running(self, session: dict) -> bool:
        return str(session.get("state", "")).lower() in {"running", "working", "inprogress", "in_progress", "starting", "stopping"}

    def session_complete(self, session: dict) -> bool:
        return str(session.get("state", "")).lower() in {"stopped", "success", "completed", "finished"}

    def mock_summary(self, status: str, message: str, interlock_ready: bool = True) -> dict:
        sessions = self.mock_sessions()
        latest = sessions[0]
        monitor = self.backup_monitor(latest, interlock_ready) if interlock_ready else {
            "state": "NO_LIVE_DATA",
            "title": "Live Veeam credentials required",
            "progress": 0,
            "completed": False,
            "running": False,
            "started_at": "-",
            "ended_at": "-",
            "result": "Unknown",
        }
        return {
            "mode": "MOCK",
            "status": status,
            "endpoint": self.base_url if self.config.host else "https://<veeam-host>:9419",
            "api_version": self.config.api_version,
            "server_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "message": message,
            "last_backup": latest,
            "backup_monitor": monitor,
            "session_result_monitor": self.session_result_monitor(sessions if interlock_ready else []),
            "policy_monitor": self.mock_policy_monitor(interlock_ready),
            "repository_monitor": self.mock_repository_monitor(interlock_ready),
            "interlock_ready": interlock_ready,
            "interlock_policy": "Mock mode assumes the latest backup completed before LOCK-FIX isolation.",
            "sessions": sessions,
        }

    def mock_sessions(self) -> list[dict]:
        return [
            {
                "name": "Daily_Backup_VM_01",
                "state": "Stopped",
                "result": "Success",
                "creation_time": "2026-04-25T17:00:00+09:00",
                "end_time": "2026-04-25T18:25:00+09:00",
                "progress": 100,
            },
            {
                "name": "Repository_Verification",
                "state": "Stopped",
                "result": "Success",
                "creation_time": "2026-04-25T18:26:00+09:00",
                "end_time": "2026-04-25T18:31:00+09:00",
                "progress": 100,
            },
        ]

    def mock_policy_monitor(self, include_sample: bool = True) -> dict:
        policies = [
            {
                "id": "mock-job-01",
                "name": "Daily_Backup_VM_01",
                "type": "Backup",
                "status": "inactive",
                "last_result": "Success",
                "last_run": "2026-04-25T17:00:00+09:00",
                "next_run": "2026-04-26T17:00:00+09:00",
                "is_enabled": True,
            },
            {
                "id": "mock-job-02",
                "name": "Repository_Verification",
                "type": "BackupCopy",
                "status": "inactive",
                "last_result": "Success",
                "last_run": "2026-04-25T18:26:00+09:00",
                "next_run": "-",
                "is_enabled": True,
            },
        ] if include_sample else []
        return self.policy_monitor(policies)

    def mock_repository_monitor(self, include_sample: bool = True) -> dict:
        repositories = [
            {
                "id": "mock-repo-01",
                "name": "Default Backup Repository",
                "type": "WinLocal",
                "host": self.config.host or "veeam-backup",
                "path": "C:\\Backup Repository",
                "capacity_gb": 512.0,
                "used_gb": 286.4,
                "free_gb": 225.6,
                "usage_percent": 55.9,
                "is_online": include_sample,
                "is_out_of_date": False,
            }
        ] if include_sample else []
        return self.repository_monitor(repositories)
