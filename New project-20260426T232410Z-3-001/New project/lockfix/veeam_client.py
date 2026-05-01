from __future__ import annotations

import json
import os
import re
import socket
import ssl
import time
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime
from difflib import get_close_matches
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlencode, urlparse
from xml.etree import ElementTree

from .config import VeeamConfig


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


@dataclass(frozen=True)
class VeeamSettings:
    base_url: str = "https://127.0.0.1:9419"
    enterprise_manager_url: str = "https://127.0.0.1:9398"
    api_version: str = "1.2-rev1"
    username: str = ""
    password: str = ""
    password_env: str = "LOCKFIX_VEEAM_PASSWORD"
    verify_ssl: bool = False
    job_name: str = ""
    job_id: str = ""
    poll_interval_seconds: int = 1
    isolate_on_status: list[str] | None = None
    timeout_seconds: float = 5.0

    @classmethod
    def from_config(cls, config: VeeamConfig) -> "VeeamSettings":
        return cls(
            base_url=os.environ.get("LOCKFIX_VEEAM_BASE_URL", config.base_url),
            enterprise_manager_url=os.environ.get("LOCKFIX_VEEAM_EM_BASE_URL", config.enterprise_manager_url),
            api_version=os.environ.get("LOCKFIX_VEEAM_API_VERSION", config.api_version),
            username=os.environ.get("LOCKFIX_VEEAM_USER", config.username),
            password=os.environ.get(config.password_env, ""),
            password_env=config.password_env,
            verify_ssl=config.verify_ssl,
            job_name=os.environ.get("LOCKFIX_VEEAM_JOB_NAME", config.job_name),
            job_id=normalized_job_id(os.environ.get("LOCKFIX_VEEAM_JOB_ID", config.job_id)),
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
        self._ssl_context = ssl.create_default_context() if settings.verify_ssl else ssl._create_unverified_context()

    def login(self) -> str:
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        if not (self.settings.username and self.settings.password):
            raise VeeamAuthenticationError(
                f"401: Veeam username and environment password are required. Password env: {self.settings.password_env}"
            )

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

    def get_jobs(self) -> list[dict[str, Any]]:
        data = self._request_json(f"{self.settings.api_base}/jobs", "GET")
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

    def latest_session_summary(self, job_name: str = "", job_id: str = "") -> dict[str, Any]:
        checks: dict[str, Any] = {
            "port_9419": self.check_port(),
            "token": {"ok": False, "message": "/api/oauth2/token was not requested yet."},
            "sessions": {"ok": False, "message": "/api/v1/sessions was not queried yet."},
        }
        if not checks["port_9419"]["ok"]:
            return {"api_synced": False, "checks": checks}
        try:
            self.login()
            checks["token"] = {"ok": True, "message": "/api/oauth2/token issued an access token."}
            sessions = self.get_sessions()
            match = match_sessions(
                sessions,
                (job_name or self.settings.job_name).strip(),
                normalized_job_id(job_id or self.settings.job_id).lower(),
            )
            session = sorted(match["matches"], key=session_sort_key, reverse=True)[0] if match["matches"] else None
            checks["sessions"] = {"ok": True, "message": "/api/v1/sessions query succeeded."}
        except VeeamError as exc:
            key = "token" if getattr(exc, "code", "") == "401" else "sessions"
            checks[key] = {"ok": False, "code": getattr(exc, "code", exc.__class__.__name__), "message": str(exc)}
            return {"api_synced": False, "checks": checks}
        if not session:
            target = (job_name or normalized_job_id(job_id) or self.settings.job_name or self.settings.job_id or "configured Veeam job").strip()
            checks["sessions"] = {
                "ok": True,
                "message": f"/api/v1/sessions query succeeded, but no VBR 9419 session matched {target}.",
                "match_strategy": match["strategy"],
                "similar_candidates": match["candidates"],
            }
            return {
                "api_synced": True,
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
        logs = self.get_session_logs(session_id(session))
        tasks = self.get_session_task_sessions(session_id(session))
        summary = enrich_summary_with_logs(summary, logs, tasks)
        summary["api_synced"] = True
        summary["session_match"] = True
        summary["match_strategy"] = match["strategy"]
        summary["checks"] = checks
        return summary

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
        self._ssl_context = ssl.create_default_context() if settings.verify_ssl else ssl._create_unverified_context()

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
    if exc.code == 401:
        return VeeamAuthenticationError("401: authentication failed. Check Veeam username/password or token.")
    if exc.code == 403:
        return VeeamPermissionError("403: Veeam permission denied. Grant Veeam Backup Viewer or higher.")
    if exc.code == 404:
        return VeeamNotFoundError("404: Veeam API URL or x-api-version path is invalid.")
    return VeeamError(f"HTTP {exc.code}: Veeam API request failed.")


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


def session_sort_key(session: dict[str, Any]) -> str:
    return str(
        session.get("creationTime")
        or session.get("startTime")
        or session.get("endTime")
        or session.get("stopTime")
        or session.get("id")
        or ""
    )


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
        "session_logs": [
            {
                "name": name,
                "status": normalize_display_status(status),
                "actions": session_actions(session),
                "duration": duration,
                "progress_percent": progress,
                "started_at": started_at,
                "ended_at": ended_at,
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
            if task_name:
                task_actions.append(f"{task_name} - {task_status} - {task_progress}%")
        actions.extend(task_actions)
    if actions:
        summary["session_logs"][0]["actions"] = actions
    if logs:
        first = min(logs, key=lambda item: str(item.get("startTime") or item.get("creationTime") or item.get("time") or ""))
        last = max(logs, key=lambda item: str(item.get("updateTime") or item.get("endTime") or item.get("time") or ""))
        summary["session_logs"][0]["started_at"] = summary["started_at"] = str(first.get("startTime") or summary.get("started_at") or "-")
        if last.get("updateTime") or last.get("endTime"):
            summary["session_logs"][0]["ended_at"] = summary["ended_at"] = str(last.get("updateTime") or last.get("endTime"))
    return summary


def log_actions(logs: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for item in sorted(logs, key=lambda row: str(row.get("startTime") or row.get("time") or row.get("id") or "")):
        title = item.get("title") or item.get("message") or item.get("description")
        if not title:
            continue
        status = item.get("status") or item.get("state") or ""
        when = item.get("startTime") or item.get("time") or item.get("updateTime") or ""
        prefix = f"{status} - " if status else ""
        suffix = f" at {when}" if when else ""
        actions.append(f"{prefix}{title}{suffix}")
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
    raw = str(
        session.get("progress_percent")
        or session.get("progressPercent")
        or session.get("Progress")
        or session.get("progress")
        or session.get("percentComplete")
        or 0
    )
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
        actions.append(f"Backup copy for {name} started at {started}")
        ended = str(session.get("endTime") or session.get("stopTime") or "")
        if ended:
            actions.append(f"{name} processing finished at {ended}")
    return actions


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
    if raw:
        return str(raw)
    try:
        if not started_at or not ended_at or started_at == "-" or ended_at == "-":
            return "-"
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
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
