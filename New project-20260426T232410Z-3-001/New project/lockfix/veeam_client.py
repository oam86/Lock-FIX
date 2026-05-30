from __future__ import annotations

import json
import os
import re
import socket
import ssl
import time
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from difflib import get_close_matches
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlencode, urlparse
from xml.etree import ElementTree

from .config import VeeamConfig
from .veeam_console_logs import latest_backup_copy_console_log_summary


SUCCESS_STATES = {"SUCCESS", "SUCCEEDED", "COMPLETED", "SUCCESSWARNING", "SUCCESS_WITH_WARNING"}
RUNNING_STATES = {"RUNNING", "WORKING", "INPROGRESS", "IN_PROGRESS"}
FAILED_STATES = {"FAILED", "FAILURE", "ERROR"}


class VeeamError(Exception):
    code = "VeeamError"


class VeeamAuthenticationError(VeeamError):
    code = "401"


class VeeamPermissionError(VeeamError):
    code = "403"


class VeeamNotFoundError(VeeamError):
    code = "404"


class VeeamConnectionError(VeeamError):
    code = "ConnectionError"


class VeeamSslError(VeeamError):
    code = "SSLError"


def veeam_base_url_candidates(settings: "VeeamSettings") -> list[str]:
    urls: list[str] = []

    def add(value: str) -> None:
        text = (value or "").strip().rstrip("/")
        if not text:
            return
        if not text.startswith(("http://", "https://")):
            text = f"https://{text}"
        if ":" not in text.rsplit("/", 1)[-1]:
            text = f"{text}:9419"
        if text not in urls:
            urls.append(text)

    add(os.environ.get("LOCKFIX_VEEAM_BASE_URL", ""))
    host = os.environ.get("LOCKFIX_VEEAM_HOST", "")
    port = os.environ.get("LOCKFIX_VEEAM_PORT", "9419")
    if host:
        add(f"{host}:{port}")
    for item in (settings.discovery_candidates or []):
        add(item)
    for item in os.environ.get("LOCKFIX_VEEAM_CANDIDATES", "").split(","):
        add(item)
    add(settings.base_url)
    if settings.discovery_scan_local_subnet:
        for host in local_ipv4_subnet_hosts():
            add(f"https://{host}:9419")
    return urls


def local_ipv4_subnet_hosts() -> list[str]:
    hosts: list[str] = []
    seen: set[str] = set()
    try:
        hostname = socket.gethostname()
        addresses = socket.gethostbyname_ex(hostname)[2]
    except OSError:
        addresses = []
    for address in addresses:
        if address.startswith(("127.", "169.254.")):
            continue
        parts = address.split(".")
        if len(parts) != 4:
            continue
        prefix = ".".join(parts[:3])
        for index in range(1, 255):
            candidate = f"{prefix}.{index}"
            if candidate == address or candidate in seen:
                continue
            seen.add(candidate)
            hosts.append(candidate)
    return hosts


def discover_veeam_base_url(settings: "VeeamSettings", candidates: list[str]) -> tuple[str, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    context = ssl.create_default_context() if settings.verify_ssl else ssl._create_unverified_context()
    preferred = candidates[:4]
    scanned = candidates[4:]
    for url in preferred:
        ok, detail = probe_veeam_candidate(url, settings, context)
        attempts.append(detail)
        if ok:
            return url, attempts
    if not scanned:
        return "", attempts
    max_workers = min(32, max(1, len(scanned)))
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        futures = {executor.submit(probe_veeam_candidate, url, settings, context): url for url in scanned}
        for future in as_completed(futures):
            ok, detail = future.result()
            attempts.append(detail)
            if ok:
                for pending in futures:
                    if pending is not future:
                        pending.cancel()
                return futures[future], attempts
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
    return "", attempts


def probe_veeam_candidate(url: str, settings: "VeeamSettings", context: ssl.SSLContext) -> tuple[bool, dict[str, Any]]:
    started = time.time()
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or 9419
    detail: dict[str, Any] = {"base_url": url, "host": host, "port": port, "ok": False}
    try:
        with socket.create_connection((host, port), timeout=settings.discovery_timeout_seconds):
            pass
        body = urlencode(
            {
                "grant_type": "password",
                "username": settings.username,
                "password": settings.password,
            }
        ).encode("utf-8")
        request = urlrequest.Request(
            f"{url.rstrip('/')}/api/oauth2/token",
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "x-api-version": settings.api_version,
            },
            method="POST",
        )
        with urlrequest.urlopen(request, timeout=settings.discovery_timeout_seconds, context=context) as response:
            raw = response.read().decode("utf-8", errors="replace")
        token = (json.loads(raw) if raw else {}).get("access_token", "")
        detail.update({"ok": bool(token), "code": "OK" if token else "NO_TOKEN"})
        return bool(token), detail
    except urlerror.HTTPError as exc:
        detail.update({"code": str(exc.code), "message": "HTTP response from candidate."})
        return False, detail
    except ssl.SSLError as exc:
        detail.update({"code": "SSLError", "message": str(exc)})
        return False, detail
    except OSError as exc:
        detail.update({"code": "ConnectionError", "message": str(exc)})
        return False, detail
    finally:
        detail["elapsed_ms"] = int((time.time() - started) * 1000)


@dataclass(frozen=True)
class VeeamSettings:
    base_url: str = "https://127.0.0.1:9419"
    enterprise_manager_url: str = "https://127.0.0.1:9398"
    auto_discover: bool = False
    discovery_candidates: list[str] | None = None
    discovery_scan_local_subnet: bool = False
    discovery_timeout_seconds: float = 0.35
    api_version: str = "1.2-rev1"
    username: str = ""
    username_env: str = "LOCKFIX_VEEAM_USER"
    password: str = ""
    password_env: str = "LOCKFIX_VEEAM_PASSWORD"
    verify_ssl: bool = False
    job_name: str = ""
    job_id: str = ""
    require_backup_copy: bool = True
    target_repository_id: str = ""
    target_repository_name: str = ""
    target_repository_path: str = ""
    exclude_os_repository: bool = True
    console_log_fallback_enabled: bool = True
    console_log_root: str = "C:\\ProgramData\\Veeam\\Backup"
    poll_interval_seconds: int = 1
    isolate_on_status: list[str] | None = None
    timeout_seconds: float = 5.0

    @classmethod
    def from_config(cls, config: VeeamConfig) -> "VeeamSettings":
        username_env = config.username_env or "LOCKFIX_VEEAM_USER"
        password_env = config.password_env or "LOCKFIX_VEEAM_PASSWORD"
        username = config.username or os.environ.get(username_env, "")
        password = os.environ.get(password_env, "")
        return cls(
            base_url=os.environ.get("LOCKFIX_VEEAM_BASE_URL", config.base_url),
            enterprise_manager_url=os.environ.get("LOCKFIX_VEEAM_EM_BASE_URL", config.enterprise_manager_url),
            auto_discover=config.auto_discover,
            discovery_candidates=config.discovery_candidates,
            discovery_scan_local_subnet=config.discovery_scan_local_subnet,
            discovery_timeout_seconds=config.discovery_timeout_seconds,
            api_version=os.environ.get("LOCKFIX_VEEAM_API_VERSION", config.api_version),
            username=username,
            username_env=username_env,
            password=password,
            password_env=password_env,
            verify_ssl=config.verify_ssl,
            job_name=os.environ.get("LOCKFIX_VEEAM_JOB_NAME", config.job_name),
            job_id=normalized_job_id(os.environ.get("LOCKFIX_VEEAM_JOB_ID", config.job_id)),
            require_backup_copy=config.require_backup_copy,
            target_repository_id=os.environ.get("LOCKFIX_VEEAM_REPOSITORY_ID", config.target_repository_id),
            target_repository_name=os.environ.get("LOCKFIX_VEEAM_REPOSITORY_NAME", config.target_repository_name),
            target_repository_path=os.environ.get("LOCKFIX_VEEAM_REPOSITORY_PATH", config.target_repository_path),
            exclude_os_repository=config.exclude_os_repository,
            console_log_fallback_enabled=config.console_log_fallback_enabled,
            console_log_root=os.environ.get("LOCKFIX_VEEAM_CONSOLE_LOG_ROOT", config.console_log_root),
            poll_interval_seconds=config.poll_interval_seconds,
            isolate_on_status=config.isolate_on_status,
        )

    @property
    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")

    @property
    def token_url(self) -> str:
        return f"{self.normalized_base_url}/api/oauth2/token"

    @property
    def api_base(self) -> str:
        return f"{self.normalized_base_url}/api/v1"

    @property
    def normalized_enterprise_manager_url(self) -> str:
        return self.enterprise_manager_url.rstrip("/")


class VeeamClient:
    def __init__(self, settings: VeeamSettings) -> None:
        self.settings = settings
        self._access_token = ""
        self._token_expires_at = 0.0
        try:
            self._ssl_context = ssl.create_default_context() if settings.verify_ssl else ssl._create_unverified_context()
        except ssl.SSLError:
            self._ssl_context = None
        self.discovery_result: dict[str, Any] = {"enabled": settings.auto_discover, "selected": settings.base_url}
        self._discovery_done = False

    @classmethod
    def from_config(cls, config: VeeamConfig) -> "VeeamClient":
        return cls(VeeamSettings.from_config(config))

    def get_backup_status(self) -> dict[str, Any]:
        return self.latest_session_summary(self.settings.job_name, self.settings.job_id)

    def login(self) -> str:
        if not self.settings.username:
            raise VeeamAuthenticationError("401: Veeam username is not configured.")
        if not self.settings.password:
            raise VeeamAuthenticationError(
                f"401: Veeam password environment variable is not set: {self.settings.password_env}"
            )
        self.ensure_discovered_base_url()
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        body = urlencode(
            {
                "grant_type": "password",
                "username": self.settings.username,
                "password": self.settings.password,
            }
        ).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-version": self.settings.api_version,
        }
        data = self._request_json(self.settings.token_url, "POST", headers=headers, body=body, authenticated=False)
        token = str(data.get("access_token") or "").strip()
        if not token:
            raise VeeamAuthenticationError("401: /api/oauth2/token did not return access_token.")
        expires_in = int(data.get("expires_in") or 900)
        self._access_token = token
        self._token_expires_at = time.time() + expires_in
        return token

    def ensure_discovered_base_url(self) -> None:
        if self._discovery_done:
            return
        self._discovery_done = True
        if not self.settings.username or not self.settings.password:
            self.discovery_result = {
                "enabled": self.settings.auto_discover,
                "selected": self.settings.base_url,
                "skipped": "username or password is not configured",
            }
            return
        if not self.settings.auto_discover:
            self.discovery_result = {"enabled": False, "selected": self.settings.base_url}
            return
        candidates = veeam_base_url_candidates(self.settings)
        selected, attempts = discover_veeam_base_url(self.settings, candidates)
        self.discovery_result = {
            "enabled": True,
            "selected": selected or self.settings.base_url,
            "attempts": attempts,
            "candidate_count": len(candidates),
        }
        if selected and selected.rstrip("/") != self.settings.base_url.rstrip("/"):
            self.settings = replace(self.settings, base_url=selected.rstrip("/"))
            self._access_token = ""
            self._token_expires_at = 0.0

    def get_jobs(self) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/jobs?limit=200", "GET")
        return list_items(data)

    def get_job_states(self) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/jobs/states?limit=200", "GET")
        return list_items(data)

    def get_sessions(self, limit: int = 100) -> list[dict[str, Any]]:
        query = f"?limit={int(limit)}" if limit else ""
        data = self._request_json(f"{self.settings.api_base}/sessions{query}", "GET")
        return list_items(data)

    def latest_session(self, job_name: str = "", job_id: str = "") -> dict[str, Any] | None:
        wanted_name = (job_name or self.settings.job_name).strip()
        wanted_id = normalized_job_id(job_id or self.settings.job_id).lower()
        sessions = self.get_sessions()
        match = match_sessions(sessions, wanted_name, wanted_id)
        if not match["matches"]:
            return None
        return sorted(match["matches"], key=session_sort_key, reverse=True)[0]

    def get_session_logs(self, session_id_value: str) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/sessions/{session_id_value}/logs", "GET")
        return list_items(data)

    def get_session_task_sessions(self, session_id_value: str) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/sessions/{session_id_value}/taskSessions", "GET")
        return list_items(data)

    def get_task_sessions(self, limit: int = 100) -> list[dict[str, Any]]:
        query = f"?limit={int(limit)}" if limit else ""
        data = self._request_json(f"{self.settings.api_base}/taskSessions{query}", "GET")
        return list_items(data)

    def get_backups(self, limit: int = 100) -> list[dict[str, Any]]:
        query = f"?limit={int(limit)}" if limit else ""
        data = self._request_json(f"{self.settings.api_base}/backups{query}", "GET")
        return list_items(data)

    def get_repositories(self, limit: int = 100) -> list[dict[str, Any]]:
        query = f"?limit={int(limit)}" if limit else ""
        data = self._request_json(f"{self.settings.api_base}/backupInfrastructure/repositories{query}", "GET")
        return list_items(data)

    def get_backup_objects(self, backup_id: str) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/backups/{backup_id}/objects", "GET")
        return list_items(data)

    def get_restore_points(self, backup_object_id: str) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/backupObjects/{backup_object_id}/restorePoints", "GET")
        return list_items(data)

    def latest_backup_restore_point(self, job_name: str = "", job_id: str = "") -> dict[str, Any] | None:
        backups = self.get_backups()
        repositories = self.get_repositories()
        eligible_repositories = filter_target_repositories(
            repositories,
            self.settings.target_repository_id,
            self.settings.target_repository_name,
            self.settings.target_repository_path,
            self.settings.exclude_os_repository,
        )
        match = match_backups(
            backups,
            job_name or self.settings.job_name,
            job_id or self.settings.job_id,
            eligible_repositories=eligible_repositories,
            require_backup_copy=self.settings.require_backup_copy,
        )
        if not match["matches"] and self.settings.require_backup_copy:
            relaxed_repositories = filter_target_repositories(
                repositories,
                exclude_os_repository=self.settings.exclude_os_repository,
            )
            relaxed_match = match_backups(
                backups,
                eligible_repositories=relaxed_repositories,
                require_backup_copy=True,
            )
            if relaxed_match["matches"]:
                match = {
                    "matches": relaxed_match["matches"],
                    "strategy": "auto_discovered_backup_copy",
                    "candidates": relaxed_match["candidates"],
                }
                eligible_repositories = relaxed_repositories
        if not match["matches"]:
            return None
        restore_points: list[dict[str, Any]] = []
        for backup in match["matches"]:
            backup_id = item_id(backup)
            if not backup_id:
                continue
            for backup_object in self.get_backup_objects(backup_id):
                for restore_point in self.get_restore_points(item_id(backup_object)):
                    restore_point = dict(restore_point)
                    restore_point["_backup"] = backup
                    restore_point["_backup_object"] = backup_object
                    restore_point["_repository"] = repository_for_backup(backup, eligible_repositories)
                    restore_point["_configured_job_name"] = (job_name or self.settings.job_name).strip()
                    restore_point["_configured_job_id"] = normalized_job_id(job_id or self.settings.job_id)
                    restore_point["_backup_match_strategy"] = match["strategy"]
                    restore_point["_backup_match_candidates"] = match["candidates"]
                    restore_points.append(restore_point)
        if not restore_points:
            return None
        return sorted(restore_points, key=restore_point_sort_key, reverse=True)[0]

    def latest_session_summary(self, job_name: str = "", job_id: str = "") -> dict[str, Any]:
        self.ensure_discovered_base_url()
        checks: dict[str, Any] = {
            "port_9419": self.check_port(),
            "discovery": self.discovery_result,
            "token": {"ok": False, "message": "/api/oauth2/token was not requested yet."},
            "sessions": {"ok": False, "message": "/api/v1/sessions was not queried yet."},
        }
        if not checks["port_9419"]["ok"]:
            return {"api_synced": False, "source": "python_veeam_client", "checks": checks}
        try:
            started = time.time()
            self.login()
            checks["token"] = {
                "ok": True,
                "message": "/api/oauth2/token issued an access token.",
                "elapsed_ms": int((time.time() - started) * 1000),
            }
            started = time.time()
            sessions = self.get_sessions()
            sessions_elapsed_ms = int((time.time() - started) * 1000)
            checks["backups"] = {"ok": False, "message": "/api/v1/backups was not queried yet."}
            match = match_sessions(
                sessions,
                (job_name or self.settings.job_name).strip(),
                normalized_job_id(job_id or self.settings.job_id).lower(),
            )
            session = sorted(match["matches"], key=session_sort_key, reverse=True)[0] if match["matches"] else None
            checks["sessions"] = {
                "ok": True,
                "message": "/api/v1/sessions query succeeded.",
                "elapsed_ms": sessions_elapsed_ms,
                "count": len(sessions),
            }
        except VeeamError as exc:
            key = "token" if getattr(exc, "code", "") == "401" else "sessions"
            checks[key] = {"ok": False, "code": getattr(exc, "code", exc.__class__.__name__), "message": str(exc)}
            return {"api_synced": False, "source": "python_veeam_client", "checks": checks}
        if not session:
            try:
                restore_point = self.latest_backup_restore_point(job_name, job_id)
                checks["backups"] = {
                    "ok": True,
                    "message": "/api/v1/backups, repositories, and restore points query succeeded.",
                    "require_backup_copy": self.settings.require_backup_copy,
                    "target_repository_id": self.settings.target_repository_id,
                    "target_repository_name": self.settings.target_repository_name,
                    "target_repository_path": self.settings.target_repository_path,
                    "exclude_os_repository": self.settings.exclude_os_repository,
                }
            except VeeamError as exc:
                restore_point = None
                checks["backups"] = {"ok": False, "code": getattr(exc, "code", exc.__class__.__name__), "message": str(exc)}
            if restore_point:
                summary = restore_point_summary(restore_point)
                restore_session_id = str(restore_point.get("sessionId") or "").strip()
                if restore_session_id:
                    try:
                        logs = self.get_session_logs(restore_session_id)
                        tasks = self.get_session_task_sessions(restore_session_id)
                        summary = enrich_summary_with_logs(summary, logs, tasks)
                    except VeeamError as exc:
                        summary["session_logs"][0]["actions"].append(
                            f"WAIT - Restore point session detail logs could not be loaded: {exc}"
                        )
                summary = self.prefer_newer_console_log_summary(summary)
                summary["api_synced"] = True
                summary["source"] = "python_veeam_client"
                summary["session_match"] = True
                summary["match_strategy"] = summary.get("backup_match_strategy", "backup_restore_point")
                summary["checks"] = checks
                return summary
            target = (job_name or normalized_job_id(job_id) or self.settings.job_name or self.settings.job_id or "configured Veeam job").strip()
            checks["sessions"] = {
                "ok": True,
                "message": f"/api/v1/sessions query succeeded, but no VBR 9419 session matched {target}.",
                "match_strategy": match["strategy"],
                "similar_candidates": match["candidates"],
            }
            return {
                "api_synced": True,
                "source": "python_veeam_client",
                "session_match": False,
                "state_source": "veeam_rest_api",
                "name": target,
                "job": target,
                "status": "Waiting",
                "result": "WAITING",
                "progress_percent": 0,
                "current_step": 1,
                "duration": "-",
                "session_logs": [
                    {
                        "name": target,
                        "status": "Waiting",
                        "actions": [
                            "Veeam REST API token and /api/v1/sessions query are connected.",
                            f"No VBR 9419 session matched {target}. Matching order: job_id first, then exact name, case-insensitive name, normalized name.",
                            f"Similar VBR 9419 candidates: {', '.join(match['candidates']) if match['candidates'] else '-'}",
                            "Enterprise Manager 9398 is reference-only diagnostics and is not required for LOCK-FIX VBR REST validation.",
                        ],
                        "duration": "-",
                        "progress_percent": 0,
                    }
                ],
                "checks": checks,
            }
        summary = session_summary(session)
        started = time.time()
        logs = self.get_session_logs(session_id(session))
        checks["session_logs"] = {
            "ok": True,
            "message": "/api/v1/sessions/{id}/logs query succeeded.",
            "elapsed_ms": int((time.time() - started) * 1000),
            "count": len(logs),
        }
        started = time.time()
        tasks = self.get_session_task_sessions(session_id(session))
        checks["task_sessions"] = {
            "ok": True,
            "message": "/api/v1/sessions/{id}/taskSessions query succeeded.",
            "elapsed_ms": int((time.time() - started) * 1000),
            "count": len(tasks),
        }
        summary = enrich_summary_with_logs(summary, logs, tasks)
        summary = self.prefer_newer_console_log_summary(summary)
        summary["api_synced"] = True
        summary["source"] = "python_veeam_client"
        summary["session_match"] = True
        summary["match_strategy"] = match["strategy"]
        summary["checks"] = checks
        return summary

    def prefer_newer_console_log_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.console_log_fallback_enabled:
            return summary
        scope = summary.get("restore_point_scope") if isinstance(summary.get("restore_point_scope"), dict) else {}
        log_summary = latest_backup_copy_console_log_summary(
            log_root=self.settings.console_log_root,
            backup_copy_name=str(scope.get("backup_name") or ""),
            job_name=str(summary.get("name") or self.settings.job_name or ""),
            target_name=str(summary.get("target") or scope.get("backup_object_name") or ""),
            policy_job_id=str(summary.get("job_id") or self.settings.job_id or ""),
            repository_id=str(summary.get("repository_id") or self.settings.target_repository_id or ""),
            repository_name=str(summary.get("repository_name") or self.settings.target_repository_name or ""),
            repository_path=str(summary.get("repository_path") or self.settings.target_repository_path or ""),
        )
        if not log_summary:
            return summary
        current_time = veeam_latest_time_sort_key(summary)
        log_time = veeam_latest_time_sort_key(log_summary)
        if log_time < current_time:
            return summary
        merged = dict(summary)
        merged.update(log_summary)
        merged["api_synced"] = summary.get("api_synced", True)
        merged["source"] = "python_veeam_client"
        merged["session_match"] = True
        checks = summary.get("checks")
        if checks:
            merged["checks"] = checks
        return merged

    def enterprise_manager_latest_session_summary(self, job_name: str = "", job_id: str = "") -> dict[str, Any]:
        checks: dict[str, Any] = {"enterprise_manager": self.check_enterprise_manager_port()}
        if not checks["enterprise_manager"].get("ok"):
            return {"api_synced": True, "session_match": False, "checks": checks}
        em = VeeamEnterpriseManagerClient(self.settings)
        try:
            em.login()
            checks["enterprise_manager"] = {"ok": True, "message": "Enterprise Manager REST logon succeeded."}
            sessions = em.get_agent_backup_sessions() + em.get_backup_sessions()
            session = select_matching_session(sessions, job_name, job_id)
            if not session:
                checks["enterprise_manager_sessions"] = {"ok": True, "message": "Enterprise Manager REST sessions queried, but no matching Agent session was found."}
                return {"api_synced": True, "session_match": False, "checks": checks}
            details = em.get_backup_session_entity(session)
            tasks = em.get_task_sessions(session)
            summary = enterprise_session_summary(details or session, tasks)
            summary["api_synced"] = True
            summary["session_match"] = True
            summary["checks"] = checks
            return summary
        except VeeamError as exc:
            checks["enterprise_manager"] = {"ok": False, "code": getattr(exc, "code", exc.__class__.__name__), "message": str(exc)}
            return {"api_synced": True, "session_match": False, "checks": checks}

    def check_port(self) -> dict[str, Any]:
        parsed = urlparse(self.settings.normalized_base_url)
        return self._check_url_port(parsed, "Veeam REST API")

    def check_enterprise_manager_port(self) -> dict[str, Any]:
        parsed = urlparse(self.settings.normalized_enterprise_manager_url)
        return self._check_url_port(parsed, "Veeam Enterprise Manager REST API")

    def _check_url_port(self, parsed, label: str) -> dict[str, Any]:
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        started = time.time()
        try:
            with socket.create_connection((host, port), timeout=self.settings.timeout_seconds):
                return {
                    "ok": True,
                    "code": "OK",
                    "message": f"{label} port is reachable: {host}:{port}",
                    "elapsed_ms": int((time.time() - started) * 1000),
                }
        except OSError as exc:
            return {
                "ok": False,
                "code": "ConnectionError",
                "message": f"ConnectionError: {label} port/firewall/service issue: {host}:{port} - {exc}",
                "elapsed_ms": int((time.time() - started) * 1000),
            }

    def _request_json(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        request_headers = {
            "Accept": "application/json",
            "x-api-version": self.settings.api_version,
            **(headers or {}),
        }
        if authenticated:
            request_headers["Authorization"] = f"Bearer {self.login()}"
        req = urlrequest.Request(url, data=body, headers=request_headers, method=method)
        try:
            with urlrequest.urlopen(req, timeout=self.settings.timeout_seconds, context=self._ssl_context) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urlerror.HTTPError as exc:
            if authenticated and exc.code == 401:
                self._access_token = ""
                self._token_expires_at = 0.0
                request_headers["Authorization"] = f"Bearer {self.login()}"
                retry_req = urlrequest.Request(url, data=body, headers=request_headers, method=method)
                try:
                    with urlrequest.urlopen(retry_req, timeout=self.settings.timeout_seconds, context=self._ssl_context) as response:
                        raw = response.read().decode("utf-8", errors="replace")
                    loaded = json.loads(raw) if raw else {}
                    return loaded if isinstance(loaded, dict) else {"data": loaded}
                except urlerror.HTTPError as retry_exc:
                    raise map_http_error(retry_exc) from retry_exc
            raise map_http_error(exc) from exc
        except ssl.SSLError as exc:
            raise VeeamSslError(f"SSLError: Veeam certificate problem: {exc}") from exc
        except (TimeoutError, OSError, urlerror.URLError) as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, ssl.SSLError):
                raise VeeamSslError(f"SSLError: Veeam certificate problem: {reason}") from exc
            raise VeeamConnectionError(f"ConnectionError: Veeam port/firewall/service issue: {reason}") from exc
        if not raw:
            return {}
        loaded = json.loads(raw)
        return loaded if isinstance(loaded, dict) else {"data": loaded}


class VeeamEnterpriseManagerClient:
    def __init__(self, settings: VeeamSettings) -> None:
        self.settings = settings
        self._session_id = ""
        try:
            self._ssl_context = ssl.create_default_context() if settings.verify_ssl else ssl._create_unverified_context()
        except ssl.SSLError:
            self._ssl_context = None

    @property
    def api_base(self) -> str:
        return f"{self.settings.normalized_enterprise_manager_url}/api"

    def login(self) -> str:
        if self._session_id:
            return self._session_id
        if not (self.settings.username and self.settings.password):
            raise VeeamAuthenticationError(
                f"401: Enterprise Manager username and environment password are required. Password env: {self.settings.password_env}"
            )
        raw = f"{self.settings.username}:{self.settings.password}".encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + b64encode(raw).decode("ascii"),
        }
        req = urlrequest.Request(f"{self.api_base}/sessionMngr/?v=latest", headers=headers, method="POST")
        try:
            with urlrequest.urlopen(req, timeout=self.settings.timeout_seconds, context=self._ssl_context) as response:
                self._session_id = response.headers.get("X-RestSvcSessionId", "")
                body = response.read().decode("utf-8", errors="replace")
        except urlerror.HTTPError as exc:
            raise map_http_error(exc) from exc
        except ssl.SSLError as exc:
            raise VeeamSslError(f"SSLError: Enterprise Manager certificate problem: {exc}") from exc
        except (TimeoutError, OSError, urlerror.URLError) as exc:
            reason = getattr(exc, "reason", exc)
            raise VeeamConnectionError(f"ConnectionError: Enterprise Manager port/firewall/service issue: {reason}") from exc
        if not self._session_id:
            try:
                loaded = json.loads(body) if body else {}
                self._session_id = str(loaded.get("SessionId") or loaded.get("sessionId") or "").strip()
            except json.JSONDecodeError:
                self._session_id = ""
        if not self._session_id:
            raise VeeamAuthenticationError("401: Enterprise Manager logon did not return X-RestSvcSessionId.")
        return self._session_id

    def get_agent_backup_sessions(self) -> list[dict[str, Any]]:
        return self._get_items("/agents/backupSessions")

    def get_backup_sessions(self) -> list[dict[str, Any]]:
        return self._get_items("/backupSessions")

    def get_backup_session_entity(self, session: dict[str, Any]) -> dict[str, Any]:
        href = alternate_href(session) or str(session.get("Href") or session.get("href") or "")
        if not href:
            return {}
        return self._get_object(href if href.startswith("http") else href)

    def get_task_sessions(self, session: dict[str, Any]) -> list[dict[str, Any]]:
        href = down_href(session, "taskSessions")
        if not href:
            sid = enterprise_session_id(session)
            href = f"/backupSessions/{sid}/taskSessions" if sid else ""
        return self._get_items(href) if href else []

    def _get_items(self, path_or_url: str) -> list[dict[str, Any]]:
        return list_items(self._get_object(path_or_url))

    def _get_object(self, path_or_url: str) -> dict[str, Any]:
        url = path_or_url if path_or_url.startswith("http") else f"{self.api_base}{path_or_url}"
        headers = {
            "Accept": "application/json",
            "X-RestSvcSessionId": self.login(),
        }
        req = urlrequest.Request(url, headers=headers, method="GET")
        try:
            with urlrequest.urlopen(req, timeout=self.settings.timeout_seconds, context=self._ssl_context) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urlerror.HTTPError as exc:
            raise map_http_error(exc) from exc
        except ssl.SSLError as exc:
            raise VeeamSslError(f"SSLError: Enterprise Manager certificate problem: {exc}") from exc
        except (TimeoutError, OSError, urlerror.URLError) as exc:
            reason = getattr(exc, "reason", exc)
            raise VeeamConnectionError(f"ConnectionError: Enterprise Manager port/firewall/service issue: {reason}") from exc
        if not raw:
            return {}
        try:
            loaded = json.loads(raw)
            return loaded if isinstance(loaded, dict) else {"data": loaded}
        except json.JSONDecodeError:
            return xml_to_dict(raw)


def map_http_error(exc: urlerror.HTTPError) -> VeeamError:
    body = ""
    try:
        body = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:
        body = ""
    if exc.code == 401:
        detail = f" Veeam response: {body}" if body else ""
        return VeeamAuthenticationError(f"401: authentication failed. Check Veeam username/password or token.{detail}")
    if exc.code == 403:
        if "product edition" in body.lower():
            return VeeamPermissionError(
                "403: Veeam accepted the account, but this product edition/license does not allow the REST API. "
                f"Veeam response: {body}"
            )
        detail = f" Veeam response: {body}" if body else ""
        return VeeamPermissionError(f"403: Veeam permission denied. Grant Veeam Backup Viewer or higher.{detail}")
    if exc.code == 404:
        detail = f" Veeam response: {body}" if body else ""
        return VeeamNotFoundError(f"404: Veeam API URL or x-api-version path is invalid.{detail}")
    detail = f" Veeam response: {body}" if body else ""
    return VeeamError(f"HTTP {exc.code}: Veeam API request failed.{detail}")


def list_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("data", "items", "results", "value", "records", "Refs", "refs", "sessions", "jobs"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = list_items(value)
            if nested:
                return nested
    return [data] if data else []


def session_name(session: dict[str, Any]) -> str:
    return str(
        session.get("jobName")
        or session.get("name")
        or session.get("Name")
        or session.get("displayName")
        or session.get("job", {}).get("name")
        or ""
    )


def session_job_id(session: dict[str, Any]) -> str:
    job = session.get("job") if isinstance(session.get("job"), dict) else {}
    return str(
        session.get("jobId")
        or session.get("JobId")
        or session.get("job_id")
        or session.get("jobUid")
        or job.get("id")
        or job.get("uid")
        or ""
    )


def session_id(session: dict[str, Any]) -> str:
    return str(
        session.get("id")
        or session.get("Id")
        or session.get("uid")
        or session.get("sessionId")
        or session.get("instanceUid")
        or "|".join([session_name(session), str(session.get("creationTime") or session.get("startTime") or "")])
    )


def item_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("Id") or item.get("uid") or item.get("instanceUid") or "")


def session_status(session: dict[str, Any]) -> str:
    result = session.get("result") or session.get("Result")
    if isinstance(result, dict):
        return str(result.get("result") or result.get("message") or "")
    return str(
        result
        or session.get("status")
        or session.get("Status")
        or session.get("state")
        or session.get("State")
        or session.get("sessionState")
        or ""
    )


def is_success_status(value: str, allowed: list[str]) -> bool:
    normalized = value.strip().lower()
    return normalized in {item.strip().lower() for item in allowed}


def normalized_job_id(value: str) -> str:
    cleaned = (value or "").strip()
    lowered = cleaned.lower()
    placeholders = {
        "",
        "actual veeam job id",
        "real veeam job id",
        "veeam job id",
        "실제 veeam job id",
        "실제 veeam job id 입력",
    }
    if lowered in placeholders or "실제" in cleaned or "job id" == lowered:
        return ""
    return cleaned


def normalize_match_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def match_sessions(sessions: list[dict[str, Any]], job_name: str = "", job_id: str = "") -> dict[str, Any]:
    wanted_id = normalized_job_id(job_id).lower()
    wanted_name = (job_name or "").strip()
    if wanted_id:
        matches = [
            session
            for session in sessions
            if wanted_id == session_job_id(session).lower()
            or wanted_id == session_id(session).lower()
            or wanted_id in session_job_id(session).lower()
        ]
        if matches:
            return {"matches": matches, "strategy": "job_id", "candidates": []}

    if wanted_name:
        exact = [session for session in sessions if wanted_name == session_name(session)]
        if exact:
            return {"matches": exact, "strategy": "job_name_exact", "candidates": []}

        wanted_lower = wanted_name.lower()
        insensitive = [session for session in sessions if wanted_lower == session_name(session).lower()]
        if insensitive:
            return {"matches": insensitive, "strategy": "job_name_case_insensitive", "candidates": []}

        wanted_normalized = normalize_match_name(wanted_name)
        normalized = [session for session in sessions if wanted_normalized == normalize_match_name(session_name(session))]
        if normalized:
            return {"matches": normalized, "strategy": "job_name_normalized", "candidates": []}

        names = sorted({session_name(session) for session in sessions if session_name(session)})
        candidates = get_close_matches(wanted_name, names, n=8, cutoff=0.35)
        if not candidates and wanted_normalized:
            candidates = [
                name for name in names
                if wanted_normalized in normalize_match_name(name) or normalize_match_name(name) in wanted_normalized
            ][:8]
        return {"matches": [], "strategy": "no_match", "candidates": candidates}

    return {"matches": sessions, "strategy": "latest_session_no_filter", "candidates": []}


def match_backups(
    backups: list[dict[str, Any]],
    job_name: str = "",
    job_id: str = "",
    eligible_repositories: list[dict[str, Any]] | None = None,
    require_backup_copy: bool = True,
) -> dict[str, Any]:
    if eligible_repositories is not None:
        repository_ids = {item_id(repository).lower() for repository in eligible_repositories}
        backups = [backup for backup in backups if str(backup.get("repositoryId") or "").lower() in repository_ids]
    if require_backup_copy:
        backups = [backup for backup in backups if is_backup_copy_backup(backup)]
    wanted_id = normalized_job_id(job_id).lower()
    wanted_name = (job_name or "").strip()
    if wanted_id:
        matches = [
            backup
            for backup in backups
            if wanted_id in str(backup.get("jobId") or "").lower()
            or wanted_id in str(backup.get("policyUniqueId") or "").lower()
            or wanted_id == item_id(backup).lower()
        ]
        if matches:
            return {"matches": matches, "strategy": "backup_job_id", "candidates": []}

    if wanted_name:
        exact = [backup for backup in backups if wanted_name == session_name(backup)]
        if exact:
            return {"matches": exact, "strategy": "backup_name_exact", "candidates": []}

        wanted_lower = wanted_name.lower()
        contains = [backup for backup in backups if wanted_lower in session_name(backup).lower()]
        if contains:
            return {"matches": contains, "strategy": "backup_name_contains", "candidates": []}

        wanted_normalized = normalize_match_name(wanted_name)
        normalized = [backup for backup in backups if wanted_normalized and wanted_normalized in normalize_match_name(session_name(backup))]
        if normalized:
            return {"matches": normalized, "strategy": "backup_name_normalized", "candidates": []}

        names = sorted({session_name(backup) for backup in backups if session_name(backup)})
        candidates = get_close_matches(wanted_name, names, n=8, cutoff=0.35)
        if require_backup_copy and eligible_repositories is not None and backups:
            return {"matches": backups, "strategy": "target_repository_backup_copy", "candidates": candidates}
        return {"matches": [], "strategy": "no_backup_match", "candidates": candidates}

    return {"matches": backups, "strategy": "latest_backup_no_filter", "candidates": []}


def is_backup_copy_backup(backup: dict[str, Any]) -> bool:
    name = session_name(backup).lower()
    return "copy" in name or "backup copy" in name


def repository_path(repository: dict[str, Any]) -> str:
    details = repository.get("repository") if isinstance(repository.get("repository"), dict) else {}
    return str(repository.get("path") or details.get("path") or "")


def is_os_repository(repository: dict[str, Any]) -> bool:
    path = repository_path(repository).strip().replace("/", "\\").lower()
    return path == "c:" or path.startswith("c:\\")


def filter_target_repositories(
    repositories: list[dict[str, Any]],
    target_id: str = "",
    target_name: str = "",
    target_path: str = "",
    exclude_os_repository: bool = True,
) -> list[dict[str, Any]]:
    filtered = [repository for repository in repositories if not (exclude_os_repository and is_os_repository(repository))]
    wanted_id = (target_id or "").strip().lower()
    wanted_name = (target_name or "").strip().lower()
    wanted_path = (target_path or "").strip().replace("/", "\\").lower()
    if wanted_id:
        filtered = [repository for repository in filtered if wanted_id == item_id(repository).lower()]
    if wanted_name:
        filtered = [repository for repository in filtered if wanted_name == session_name(repository).lower()]
    if wanted_path:
        filtered = [repository for repository in filtered if repository_path(repository).strip().replace("/", "\\").lower() == wanted_path]
    return filtered


def repository_for_backup(backup: dict[str, Any], repositories: list[dict[str, Any]]) -> dict[str, Any]:
    repository_id = str(backup.get("repositoryId") or "").lower()
    for repository in repositories:
        if item_id(repository).lower() == repository_id:
            return repository
    return {}


def local_timezone():
    return datetime.now().astimezone().tzinfo or timezone.utc


def parse_veeam_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text or text == "-":
        return None
    korean_match = re.search(
        r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(오전|오후)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?",
        text,
    )
    if korean_match:
        year, month, day, meridiem, hour, minute, second = korean_match.groups()
        hour_int = int(hour)
        if meridiem == "오후" and hour_int != 12:
            hour_int += 12
        if meridiem == "오전" and hour_int == 12:
            hour_int = 0
        return datetime(
            int(year),
            int(month),
            int(day),
            hour_int,
            int(minute),
            int(second or 0),
            tzinfo=local_timezone(),
        )
    candidates = [text]
    if text.endswith("Z"):
        candidates.append(text[:-1] + "+00:00")
    if " " in text and "T" not in text:
        candidates.append(text.replace(" ", "T", 1))
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=local_timezone())
            return parsed
        except ValueError:
            continue
    return None


def veeam_time_sort_key(*values: Any) -> float:
    for value in values:
        parsed = parse_veeam_time(value)
        if parsed:
            return parsed.timestamp()
    return 0.0


def veeam_latest_time_sort_key(summary: dict[str, Any]) -> float:
    """Return the newest visible Veeam timestamp from REST or console evidence."""
    values: list[Any] = [
        summary.get("job_finished_at"),
        summary.get("updated_at"),
        summary.get("updateTime"),
        summary.get("ended_at"),
        summary.get("endTime"),
        summary.get("stopTime"),
        summary.get("started_at"),
        summary.get("startTime"),
        summary.get("creationTime"),
    ]
    logs = summary.get("session_logs") if isinstance(summary.get("session_logs"), list) else []
    for log in logs:
        if isinstance(log, dict):
            values.extend(
                [
                    log.get("job_finished_at"),
                    log.get("updated_at"),
                    log.get("ended_at"),
                    log.get("endTime"),
                    log.get("started_at"),
                    log.get("startTime"),
                ]
            )
    return max((veeam_time_sort_key(value) for value in values), default=0.0)


def display_veeam_time(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return "-"
    parsed = parse_veeam_time(text)
    if not parsed:
        return text
    return parsed.astimezone(local_timezone()).strftime("%Y-%m-%d %H:%M:%S")


def normalize_embedded_veeam_times(text: str) -> str:
    def replace_korean(match: re.Match) -> str:
        return display_veeam_time(match.group(0))

    return re.sub(
        r"\d{4}-\d{1,2}-\d{1,2}\s+(?:오전|오후)\s+\d{1,2}:\d{2}(?::\d{2})?",
        replace_korean,
        text,
    )


def session_sort_key(session: dict[str, Any]) -> float:
    return veeam_time_sort_key(
        session.get("creationTime"),
        session.get("startTime"),
        session.get("endTime"),
        session.get("stopTime"),
        session.get("id"),
    )


def restore_point_sort_key(restore_point: dict[str, Any]) -> float:
    return veeam_time_sort_key(
        restore_point.get("creationTime"),
        restore_point.get("createdTime"),
        restore_point.get("time"),
        restore_point.get("startTime"),
        restore_point.get("endTime"),
        item_id(restore_point),
    )


def restore_point_summary(restore_point: dict[str, Any]) -> dict[str, Any]:
    backup = restore_point.get("_backup") if isinstance(restore_point.get("_backup"), dict) else {}
    backup_object = restore_point.get("_backup_object") if isinstance(restore_point.get("_backup_object"), dict) else {}
    repository = restore_point.get("_repository") if isinstance(restore_point.get("_repository"), dict) else {}
    configured_job_name = str(restore_point.get("_configured_job_name") or "").strip()
    backup_name = configured_job_name or session_name(backup) or session_name(backup_object) or session_name(restore_point)
    backup_target = session_name(backup_object) or str(backup_object.get("hostName") or backup_object.get("platformName") or "").strip()
    restore_point_id = item_id(restore_point)
    restore_session_id = str(restore_point.get("sessionId") or "").strip()
    current_id = restore_session_id if restore_session_id and restore_session_id != "00000000-0000-0000-0000-000000000000" else restore_point_id
    created = str(restore_point.get("creationTime") or "-")
    status = "Success" if restore_point_id else "Waiting"
    repo_name = session_name(repository) or "-"
    repo_path = repository_path(repository) or "-"
    backup_size = transfer_size(restore_point)
    transferred = transferred_size(restore_point)
    speed = transfer_speed(restore_point)
    backup_match_strategy = str(restore_point.get("_backup_match_strategy") or "backup_restore_point")
    backup_match_candidates = list(restore_point.get("_backup_match_candidates") or [])
    if backup_size == "-":
        backup_size = transfer_size(backup_object)
    if transferred == "-":
        transferred = backup_size
    target_suffix = f" - {backup_target}" if backup_target and backup_target != backup_name else ""
    finished_line = (
        f"{backup_name}{target_suffix} ({transferred if transferred != '-' else '0 B'}) processing finished at {created}: "
        f"{transferred if transferred != '-' else '0 B'} transferred"
        f"{' at ' + speed if speed != '-' else ''}"
    )
    summary = {
        "state_source": "veeam_rest_backup_restore_point",
        "id": current_id,
        "session_id": current_id,
        "name": backup_name,
        "job": backup_name,
        "job_id": str(restore_point.get("_configured_job_id") or backup.get("jobId") or backup.get("policyUniqueId") or ""),
        "target": backup_target,
        "status": status,
        "result": status,
        "session_state": "BACKUP_COMPLETED",
        "progress_percent": 100 if status == "Success" else 0,
        "current_step": 2 if status == "Success" else 1,
        "started_at": created,
        "ended_at": created,
        "duration": "-",
        "backup_size": backup_size,
        "transferred": transferred,
        "speed": speed,
        "repository_id": item_id(repository),
        "repository_name": repo_name,
        "repository_path": repo_path,
        "backup_match_strategy": backup_match_strategy,
        "backup_match_candidates": backup_match_candidates,
        "restore_point_scope": {
            "backup_id": item_id(backup),
            "backup_name": session_name(backup) or "-",
            "backup_job_id": str(backup.get("jobId") or ""),
            "backup_policy_unique_id": str(backup.get("policyUniqueId") or ""),
            "backup_object_id": item_id(backup_object),
            "backup_object_name": session_name(backup_object) or backup_target or "-",
            "restore_point_id": restore_point_id,
            "restore_point_session_id": restore_session_id,
            "repository_id": item_id(repository),
            "repository_name": repo_name,
            "repository_path": repo_path,
        },
        "veeam_console_actions": [
            f"Backup copy for {backup_name}{target_suffix} started at {display_veeam_time(created)}",
            (
                f"{backup_name}{target_suffix} ({transferred if transferred != '-' else '0 B'}) processing finished at "
                f"{display_veeam_time(created)}: {transferred if transferred != '-' else '0 B'} transferred"
                f"{' at ' + speed if speed != '-' else ''}"
            ),
        ],
        "session_logs": [
            {
                "name": backup_name,
                "status": status,
                "actions": [],
                "duration": "-",
                "progress_percent": 100 if status == "Success" else 0,
                "started_at": display_veeam_time(created),
                "ended_at": display_veeam_time(created),
                "backup_size": backup_size,
                "transferred": transferred,
                "speed": speed,
            }
        ],
    }
    summary["session_logs"][0]["actions"] = [
        *summary["veeam_console_actions"],
        f"Backup Copy match strategy: {backup_match_strategy}.",
        f"Veeam Backup Copy object matched from /api/v1/backups: {session_name(backup) or backup_name}",
        f"Target repository confirmed: {repo_name} ({repo_path}).",
        "C:\\ OS repository guard passed: target repository is not on C:\\.",
        f"Latest restore point detected at {display_veeam_time(created)}.",
        f"Restore point id: {restore_point_id}",
    ]
    return summary


def backup_copy_console_actions(summary: dict[str, Any]) -> list[str]:
    name = str(summary.get("name") or summary.get("job") or "Veeam Backup").strip()
    target = str(summary.get("target") or "").strip()
    target_suffix = f" - {target}" if target and target != name else ""
    started = display_veeam_time(summary.get("started_at"))
    ended = display_veeam_time(summary.get("ended_at") or summary.get("started_at"))
    transferred = str(summary.get("transferred") or "").strip()
    if not transferred or transferred == "-":
        transferred = "0 B"
    speed = str(summary.get("speed") or "").strip()
    return [
        f"Backup copy for {name}{target_suffix} started at {started}",
        (
            f"{name}{target_suffix} ({transferred}) processing finished at {ended}: "
            f"{transferred} transferred"
            f"{' at ' + speed if speed and speed != '-' else ''}"
        ),
    ]


def select_matching_session(sessions: list[dict[str, Any]], job_name: str = "", job_id: str = "") -> dict[str, Any] | None:
    wanted_name = (job_name or "").strip().lower()
    wanted_id = normalized_job_id(job_id).lower()
    candidates = sessions
    if wanted_id:
        candidates = [
            session for session in candidates
            if wanted_id in session_job_id(session).lower() or wanted_id == session_id(session).lower() or wanted_id in enterprise_session_id(session).lower()
        ]
    elif wanted_name:
        candidates = [session for session in candidates if wanted_name in session_name(session).lower()]
    if not candidates:
        return None
    return sorted(candidates, key=session_sort_key, reverse=True)[0]


def session_summary(session: dict[str, Any]) -> dict[str, Any]:
    status = session_status(session) or "Running"
    progress = session_progress(session)
    normalized = status.upper()
    if normalized in SUCCESS_STATES or status.lower() == "success":
        progress = 100
    name = session_name(session) or "Veeam Backup"
    started_at = str(session.get("creationTime") or session.get("startTime") or session.get("started_at") or "-")
    ended_at = str(session.get("endTime") or session.get("stopTime") or session.get("ended_at") or "-")
    duration = session_duration(session, started_at, ended_at)
    backup_size = transfer_size(session)
    transferred = transferred_size(session)
    speed = transfer_speed(session)
    actions = session_actions(session)
    if backup_size != "-" or transferred != "-" or speed != "-":
        actions.append(
            f"Realtime transfer: {transferred if transferred != '-' else '0 B'} / {backup_size if backup_size != '-' else '-'}"
            f"{' at ' + speed if speed != '-' else ''}"
        )
    return {
        "state_source": "veeam_rest_api",
        "session_id": session_id(session),
        "name": name,
        "job": name,
        "status": normalize_display_status(status),
        "result": normalize_display_status(status).upper(),
        "progress_percent": progress,
        "current_step": 2 if progress >= 100 or normalize_display_status(status) == "Success" else 1,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration": duration,
        "backup_size": backup_size,
        "transferred": transferred,
        "speed": speed,
        "session_logs": [
            {
                "name": name,
                "status": normalize_display_status(status),
                "actions": actions,
                "duration": duration,
                "progress_percent": progress,
                "started_at": display_veeam_time(started_at),
                "ended_at": display_veeam_time(ended_at),
                "backup_size": backup_size,
                "transferred": transferred,
                "speed": speed,
            }
        ],
    }


def enrich_summary_with_logs(summary: dict[str, Any], logs: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    actions = log_actions(logs)
    if tasks:
        task_actions = []
        for task in tasks:
            task_name = session_name(task) or str(task.get("objectName") or task.get("displayName") or "")
            task_status = normalize_display_status(session_status(task))
            task_progress = session_progress(task)
            task_size = transfer_size(task)
            task_transferred = transferred_size(task)
            task_speed = transfer_speed(task)
            if task_name:
                task_actions.append(
                    f"{task_name} - {task_status} - {task_progress}%"
                    f"{' - ' + task_transferred + ' / ' + task_size if task_size != '-' or task_transferred != '-' else ''}"
                    f"{' at ' + task_speed if task_speed != '-' else ''}"
                )
        actions.extend(task_actions)
        task_progress_values = [session_progress(task) for task in tasks]
        if task_progress_values:
            progress = max(task_progress_values)
            if progress > int(summary.get("progress_percent") or 0):
                summary["progress_percent"] = progress
                summary["session_logs"][0]["progress_percent"] = progress
    metrics_source = latest_metric_source([*logs, *tasks])
    if metrics_source:
        size = transfer_size(metrics_source)
        transferred = transferred_size(metrics_source)
        speed = transfer_speed(metrics_source)
        if size != "-":
            summary["backup_size"] = size
            summary["session_logs"][0]["backup_size"] = size
        if transferred != "-":
            summary["transferred"] = transferred
            summary["session_logs"][0]["transferred"] = transferred
        if speed != "-":
            summary["speed"] = speed
            summary["session_logs"][0]["speed"] = speed
    if logs:
        first = min(logs, key=lambda item: veeam_time_sort_key(item.get("startTime"), item.get("creationTime"), item.get("time")))
        last = max(logs, key=lambda item: veeam_time_sort_key(item.get("updateTime"), item.get("endTime"), item.get("time"), item.get("startTime")))
        summary["session_logs"][0]["started_at"] = summary["started_at"] = str(first.get("startTime") or summary.get("started_at") or "-")
        if last.get("updateTime") or last.get("endTime"):
            summary["session_logs"][0]["ended_at"] = summary["ended_at"] = str(last.get("updateTime") or last.get("endTime"))
        duration = session_duration(summary, str(summary.get("started_at") or "-"), str(summary.get("ended_at") or "-"))
        summary["duration"] = duration
        summary["session_logs"][0]["duration"] = duration
        summary["session_logs"][0]["started_at"] = display_veeam_time(summary.get("started_at"))
        summary["session_logs"][0]["ended_at"] = display_veeam_time(summary.get("ended_at"))
    if actions:
        if summary.get("state_source") == "veeam_rest_backup_restore_point":
            console_actions = backup_copy_console_actions(summary)
            summary["veeam_console_actions"] = console_actions
        else:
            console_actions = [
                normalize_embedded_veeam_times(str(item))
                for item in summary.get("veeam_console_actions", [])
                if str(item).strip()
            ]
        merged_actions = [*console_actions]
        for action in actions:
            if action not in merged_actions:
                merged_actions.append(action)
        summary["session_logs"][0]["actions"] = merged_actions
    return summary


def log_actions(logs: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for item in sorted(logs, key=lambda row: veeam_time_sort_key(row.get("startTime"), row.get("time"), row.get("id"))):
        title = item.get("title") or item.get("message") or item.get("description")
        if not title:
            continue
        status = item.get("status") or item.get("state") or ""
        when = item.get("startTime") or item.get("time") or item.get("updateTime") or ""
        prefix = f"{status} - " if status else ""
        normalized_title = normalize_embedded_veeam_times(str(title))
        suffix = ""
        if when and not re.search(r"\d{4}-\d{1,2}-\d{1,2}", normalized_title):
            suffix = f" at {display_veeam_time(when)}"
        actions.append(f"{prefix}{normalized_title}{suffix}")
    return actions


def enterprise_session_summary(session: dict[str, Any], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    name = session_name(session) or "Veeam Backup"
    if "@" in name:
        name = name.split("@", 1)[0]
    status = normalize_display_status(session_status(session))
    progress = session_progress(session)
    if status == "Success":
        progress = 100
    started_at = str(session.get("CreationTime") or session.get("creationTime") or session.get("StartTime") or session.get("startTime") or "-")
    ended_at = str(session.get("EndTime") or session.get("endTime") or session.get("StopTime") or session.get("stopTime") or "-")
    duration = session_duration(session, started_at, ended_at)
    target = ""
    task_actions: list[str] = []
    for task in tasks:
        task_name = session_name(task)
        if task_name and task_name != name:
            target = task_name.split("@", 1)[0]
        task_status = normalize_display_status(session_status(task))
        if task_name:
            task_actions.append(f"{task_name} - {task_status}")
    if not task_actions:
        task_actions = session_actions(session)
    if not target:
        target = str(session.get("ComputerName") or session.get("hostName") or session.get("name") or "")
    actions = [
        f"Backup copy for {name}{' - ' + target if target else ''} started at {started_at}",
        *task_actions,
    ]
    if ended_at and ended_at != "-":
        actions.append(f"{name}{' - ' + target if target else ''} processing finished at {ended_at}")
    return {
        "state_source": "veeam_enterprise_manager_rest_api",
        "session_id": enterprise_session_id(session),
        "name": name,
        "job": name,
        "status": status,
        "result": status.upper(),
        "progress_percent": progress,
        "current_step": 2 if progress >= 100 or status == "Success" else 1,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration": duration,
        "session_logs": [
            {
                "name": name,
                "status": status,
                "actions": actions,
                "duration": duration,
                "progress_percent": progress,
                "started_at": started_at,
                "ended_at": ended_at,
            }
        ],
    }


def normalize_display_status(value: str) -> str:
    upper = value.strip().upper()
    if upper in {"SUCCEEDED"}:
        return "Success"
    if upper in SUCCESS_STATES or value.strip().lower() == "success":
        return "Success"
    if upper in FAILED_STATES:
        return "Failed"
    if upper in RUNNING_STATES:
        return "Running"
    return value or "Running"


def session_progress(session: dict[str, Any]) -> int:
    raw_value = first_nested_value(
        session,
        (
            "progress_percent",
            "progressPercent",
            "Progress",
            "progress",
            "percentComplete",
            "processedPercent",
            "workloadProgress",
        ),
    )
    raw = str(raw_value or 0)
    raw = raw.replace("%", "")
    try:
        return max(0, min(100, int(float(raw))))
    except (TypeError, ValueError):
        return 0


def session_actions(session: dict[str, Any]) -> list[str]:
    raw_actions = session.get("actions") or session.get("log") or session.get("logs") or session.get("messages")
    actions: list[str] = []
    if isinstance(raw_actions, list):
        for item in raw_actions:
            if isinstance(item, dict):
                text = item.get("action") or item.get("message") or item.get("title") or item.get("description")
                if text:
                    actions.append(str(text))
            elif item:
                actions.append(str(item))
    elif raw_actions:
        actions.append(str(raw_actions))
    if not actions:
        name = session_name(session) or "Veeam Backup"
        started = str(session.get("creationTime") or session.get("startTime") or "-")
        actions.append(f"Backup copy for {name} started at {display_veeam_time(started)}")
        ended = str(session.get("endTime") or session.get("stopTime") or "")
        if ended:
            actions.append(f"{name} processing finished at {display_veeam_time(ended)}")
    return actions


def first_nested_value(data: Any, keys: tuple[str, ...]) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    for value in data.values():
        if isinstance(value, dict):
            found = first_nested_value(value, keys)
            if found not in (None, ""):
                return found
        elif isinstance(value, list):
            for item in value:
                found = first_nested_value(item, keys)
                if found not in (None, ""):
                    return found
    return None


def latest_metric_source(items: list[dict[str, Any]]) -> dict[str, Any]:
    metric_keys = (
        "backupSize",
        "totalSize",
        "totalBytes",
        "totalDataSize",
        "processedSize",
        "processedDataSize",
        "sourceSize",
        "transferred",
        "transferredSize",
        "transferredBytes",
        "processedBytes",
        "readSize",
        "readBytes",
        "speed",
        "transferSpeed",
        "processingRate",
        "readRate",
        "throughput",
    )
    valid = [
        item for item in items
        if isinstance(item, dict)
        and (
            first_nested_value(item, metric_keys) not in (None, "")
            or text_size_value(item)
            or text_transfer_value(item)
            or text_speed_value(item)
        )
    ]
    if not valid:
        return {}
    return max(
        valid,
        key=lambda item: veeam_time_sort_key(
            item.get("updateTime"),
            item.get("endTime"),
            item.get("time"),
            item.get("startTime"),
        ),
    )


def transfer_size(item: dict[str, Any]) -> str:
    raw = first_nested_value(
        item,
        (
            "backupSize",
            "totalSize",
            "totalBytes",
            "totalDataSize",
            "processedSize",
            "processedDataSize",
            "sourceSize",
            "size",
        ),
    )
    if raw in (None, ""):
        raw = text_size_value(item)
    return format_size(raw)


def transferred_size(item: dict[str, Any]) -> str:
    raw = first_nested_value(
        item,
        (
            "transferred",
            "transferredSize",
            "transferredBytes",
            "processedBytes",
            "processedDataSize",
            "readSize",
            "readBytes",
        ),
    )
    if raw in (None, ""):
        raw = text_transfer_value(item)
    return format_size(raw)


def transfer_speed(item: dict[str, Any]) -> str:
    raw = first_nested_value(item, ("speed", "transferSpeed", "processingRate", "readRate", "throughput"))
    if raw in (None, ""):
        raw = text_speed_value(item)
    if raw in (None, ""):
        return "-"
    if isinstance(raw, (int, float)):
        return f"{format_size(raw)}/s"
    text = str(raw).strip()
    return text if text else "-"


def text_metric_blob(item: dict[str, Any]) -> str:
    parts = []
    for key in ("title", "message", "description", "action", "detail"):
        value = item.get(key)
        if value not in (None, ""):
            parts.append(str(value))
    return " ".join(parts)


def text_size_value(item: dict[str, Any]) -> str:
    text = text_metric_blob(item)
    match = re.search(r"(?:total\s+size|backup\s+size|size)\s*:\s*([0-9][0-9.,]*\s*[KMGTPE]?B)", text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else ""


def text_transfer_value(item: dict[str, Any]) -> str:
    text = text_metric_blob(item)
    match = re.search(r"([0-9][0-9.,]*\s*[KMGTPE]?B)\s+transferred", text, re.IGNORECASE)
    if not match:
        match = re.search(r"(?:transferred|processed)\s*:\s*([0-9][0-9.,]*\s*[KMGTPE]?B)", text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else ""


def text_speed_value(item: dict[str, Any]) -> str:
    text = text_metric_blob(item)
    match = re.search(r"(?:at|speed\s*:)\s*([0-9][0-9.,]*\s*[KMGTPE]?B/s)", text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else ""


def format_size(raw: Any) -> str:
    if raw in (None, ""):
        return "-"
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return "-"
        if re.search(r"[a-zA-Z가-힣/]", text):
            return text
        try:
            raw = float(text)
        except ValueError:
            return text
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return str(raw)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    if index == 0:
        return f"{int(value)} {units[index]}"
    return f"{value:.1f} {units[index]}"


def enterprise_session_id(session: dict[str, Any]) -> str:
    raw = str(session.get("UID") or session.get("uid") or session.get("id") or session.get("Id") or "")
    return raw.rsplit(":", 1)[-1] if raw else ""


def alternate_href(session: dict[str, Any]) -> str:
    return link_href(session, rel="Alternate")


def down_href(session: dict[str, Any], contains: str = "") -> str:
    return link_href(session, rel="Down", contains=contains)


def link_href(session: dict[str, Any], rel: str = "", contains: str = "") -> str:
    links = session.get("Links") or session.get("links") or []
    if isinstance(links, dict):
        links = links.get("Link") or links.get("links") or []
    if isinstance(links, dict):
        links = [links]
    if not isinstance(links, list):
        return ""
    for link in links:
        if not isinstance(link, dict):
            continue
        link_rel = str(link.get("Rel") or link.get("rel") or "")
        href = str(link.get("Href") or link.get("href") or "")
        if rel and link_rel.lower() != rel.lower():
            continue
        if contains and contains.lower() not in href.lower():
            continue
        if href:
            return href
    return ""


def session_duration(session: dict[str, Any], started_at: str, ended_at: str) -> str:
    raw = session.get("duration") or session.get("Duration") or session.get("elapsedTime") or session.get("durationText")
    if raw and str(raw).strip() != "-":
        return str(raw)
    try:
        if not started_at or not ended_at or started_at == "-" or ended_at == "-":
            return "-"
        start = parse_veeam_time(started_at)
        end = parse_veeam_time(ended_at)
        if not start or not end:
            return "-"
        seconds = max(0, int((end - start).total_seconds()))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
    except ValueError:
        return "-"


def xml_to_dict(raw: str) -> dict[str, Any]:
    root = ElementTree.fromstring(raw)
    return xml_element_to_dict(root)


def xml_element_to_dict(element) -> dict[str, Any]:
    name = element.tag.split("}", 1)[-1]
    result: dict[str, Any] = {key: value for key, value in element.attrib.items()}
    children = list(element)
    for child in children:
        child_name = child.tag.split("}", 1)[-1]
        child_value = xml_element_to_dict(child)
        existing = result.get(child_name)
        if existing is None:
            result[child_name] = child_value
        elif isinstance(existing, list):
            existing.append(child_value)
        else:
            result[child_name] = [existing, child_value]
    text = (element.text or "").strip()
    if text and not children:
        result["text"] = text
    if name in {"EntityReferences", "Refs"} and "Ref" in result:
        refs = result["Ref"]
        result["Refs"] = refs if isinstance(refs, list) else [refs]
    return result
