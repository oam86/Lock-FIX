from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LockFixConfig, bool_value, get_veeam_config
from .controller import LockFixController
from .veeam_client import (
    is_success_status,
    match_sessions,
    normalized_job_id,
    session_id,
    session_job_id,
    session_name,
    session_sort_key,
    session_status,
)
from .veeam_factory import create_veeam_client


def run_veeam_diagnostics(config: LockFixConfig, controller: LockFixController | None = None) -> dict[str, Any]:
    """Run the canonical LOCK-FIX Veeam REST 9419 diagnostic flow.

    This is the only diagnostic result used by veeam-test, /api/veeam-backup,
    and VeeamWatcher. All settings come from config["veeam"] via
    get_veeam_config(config), and all Veeam REST calls use the Python
    VeeamClient created by veeam_factory.create_veeam_client().
    """

    veeam_config = get_veeam_config(config)
    client = create_veeam_client(veeam_config)
    settings = client.settings
    state_path = veeam_watcher_state_path(config)
    watcher_state = read_runtime_state(state_path)
    result: dict[str, Any] = {
        "success": False,
        "source": "python_veeam_client",
        "enabled": bool_value(veeam_config.get("enabled", False)),
        "config_source": "config.veeam",
        "config": {
            "base_url": settings.normalized_base_url,
            "api_version": settings.api_version,
            "auto_discover": settings.auto_discover,
            "discovery_scan_local_subnet": settings.discovery_scan_local_subnet,
            "discovery_timeout_seconds": settings.discovery_timeout_seconds,
            "verify_ssl": settings.verify_ssl,
            "username": settings.username,
            "password_env": settings.password_env,
            "password_logged": False,
            "job_name": settings.job_name,
            "job_id": settings.job_id,
            "match_order": "job_id -> job_name exact -> case-insensitive -> normalized -> similar candidates",
            "require_backup_copy": settings.require_backup_copy,
            "target_repository_id": settings.target_repository_id,
            "target_repository_name": settings.target_repository_name,
            "target_repository_path": settings.target_repository_path,
            "exclude_os_repository": settings.exclude_os_repository,
            "poll_interval_seconds": settings.poll_interval_seconds,
            "post_success_delay_seconds": int(veeam_config.get("post_success_delay_seconds", 10) or 0),
            "require_repository_resync_quiet": bool_value(
                veeam_config.get("require_repository_resync_quiet", True), True
            ),
        },
        "vbr_rest_9419": {
            "required": True,
            "api_base": settings.api_base,
            "token_url": settings.token_url,
            "port": client.check_port(),
            "discovery": client.discovery_result,
        },
        "reference_only_enterprise_manager_port": {
            **client.check_enterprise_manager_port(),
            "required": False,
            "affects_lockfix_integration": False,
            "message": "Enterprise Manager 9398 is reference-only. LOCK-FIX integration success is decided by VBR REST 9419 token and sessions.",
        },
        "powershell_curl_module": {
            "required": False,
            "affects_lockfix_integration": False,
            "message": "PowerShell, curl, and Veeam PowerShell Module failures are reference diagnostics only; Python VeeamClient result is authoritative.",
        },
        "tls": {
            "verify_ssl": settings.verify_ssl,
            "poc_mode": "verify_ssl=false allows self-signed certificates for PoC validation.",
            "production_mode": "Use verify_ssl=true after registering the Veeam REST certificate in the Windows trusted root store.",
            "python_client": "LOCK-FIX validates Veeam with Python HTTPS client; PowerShell/curl Schannel failures are diagnostic only.",
        },
        "authentication": None,
        "jobs": None,
        "sessions": None,
        "backups": None,
        "repositories": None,
        "matching": None,
        "latest_configured_session": None,
        "isolate_condition": None,
        "pre_isolate_checks": None,
        "runtime_state": {
            "state_path": str(state_path),
            "processed_session_ids": watcher_state.get("processed_session_ids") or [],
            "last_isolated_session_id": watcher_state.get("last_isolated_session_id", ""),
        },
    }
    result["port"] = result["vbr_rest_9419"]["port"]

    latest_session: dict[str, Any] | None = None
    sessions: list[dict[str, Any]] = []
    jobs: list[dict[str, Any]] = []
    try:
        token = client.login()
        result["config"]["base_url"] = client.settings.normalized_base_url
        result["vbr_rest_9419"]["api_base"] = client.settings.api_base
        result["vbr_rest_9419"]["token_url"] = client.settings.token_url
        result["vbr_rest_9419"]["port"] = client.check_port()
        result["vbr_rest_9419"]["discovery"] = client.discovery_result
        result["authentication"] = {"ok": bool(token), "token_received": bool(token), "password_logged": False}

        jobs = client.get_jobs()
        result["jobs"] = {"ok": True, "count": len(jobs), "items": jobs}
        backups = client.get_backups()
        repositories = client.get_repositories()
        result["backups"] = {"ok": True, "count": len(backups), "items": backups}
        result["repositories"] = {
            "ok": True,
            "count": len(repositories),
            "items": repositories,
            "target_repository_id": settings.target_repository_id,
            "target_repository_name": settings.target_repository_name,
            "target_repository_path": settings.target_repository_path,
            "exclude_os_repository": settings.exclude_os_repository,
            "require_backup_copy": settings.require_backup_copy,
        }
        sessions = client.get_sessions()
        result["sessions"] = {"ok": True, "count": len(sessions), "items": sessions}

        wanted_job_id = normalized_job_id(settings.job_id)
        match = match_sessions(sessions, settings.job_name, wanted_job_id)
        result["matching"] = {
            "job_id": wanted_job_id,
            "job_name": settings.job_name,
            "strategy": match["strategy"],
            "matched": bool(match["matches"]),
            "similar_candidates": match["candidates"],
            "match_order": "job_id -> job_name exact -> case-insensitive -> normalized -> similar candidates",
        }
        result["latest_configured_session"] = client.get_backup_status()
        latest_session = (
            sorted(match["matches"], key=session_sort_key, reverse=True)[0] if match["matches"] else None
        )
        if not latest_session and result["latest_configured_session"].get("session_match"):
            latest_session = session_from_backup_summary(result["latest_configured_session"])
            result["matching"]["strategy"] = result["latest_configured_session"].get(
                "backup_match_strategy",
                result["latest_configured_session"].get("match_strategy", "backup_restore_point"),
            )
            result["matching"]["matched"] = True
            result["matching"]["restore_point_scope"] = result["latest_configured_session"].get("restore_point_scope")
        result["success"] = True
    except Exception as exc:
        result["error_type"] = getattr(exc, "code", exc.__class__.__name__)
        result["error"] = str(exc)

    result["isolate_condition"] = isolate_condition(
        config,
        veeam_config,
        latest_session,
        state_path,
        watcher_state,
    )
    result["pre_isolate_checks"] = pre_isolate_checks(
        config,
        veeam_config,
        latest_session,
        sessions,
        result["isolate_condition"],
    )
    if result["isolate_condition"]:
        result["isolate_condition"]["would_call_isolate"] = bool(
            result["isolate_condition"].get("would_call_isolate")
            and result["pre_isolate_checks"].get("ready")
        )
    return add_webui_shape(result)


def build_veeam_test_result(config: LockFixConfig, controller: LockFixController | None = None) -> dict[str, Any]:
    """Backward-compatible name for older callers."""

    return run_veeam_diagnostics(config, controller)


def session_from_backup_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": summary.get("session_id") or summary.get("id"),
        "name": summary.get("name"),
        "jobId": summary.get("job_id"),
        "creationTime": summary.get("started_at"),
        "endTime": summary.get("ended_at"),
        "result": {"result": summary.get("result") or summary.get("status")},
    }


def veeam_watcher_state_path(config: LockFixConfig) -> Path:
    return config.state_path.parent / "veeam_watcher_state.json"


def read_runtime_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def isolate_condition(
    config: LockFixConfig,
    veeam_config: dict[str, Any],
    latest_session: dict[str, Any] | None,
    state_path: Path,
    watcher_state: dict[str, Any],
) -> dict[str, Any]:
    processed_session_ids = set(watcher_state.get("processed_session_ids") or [])
    current_session_id = session_id(latest_session) if latest_session else ""
    current_status = session_status(latest_session) if latest_session else ""
    isolate_on_status = [str(item) for item in veeam_config.get("isolate_on_status", ["Success"])]
    status_allowed = is_success_status(current_status, isolate_on_status) if latest_session else False
    already_processed = bool(
        current_session_id
        and (current_session_id == watcher_state.get("last_isolated_session_id") or current_session_id in processed_session_ids)
    )
    return {
        "watcher_enabled": bool_value(veeam_config.get("enabled", False)),
        "matched_session": bool(latest_session),
        "session_id": current_session_id,
        "job_name": session_name(latest_session) if latest_session else "",
        "job_id": session_job_id(latest_session) if latest_session else "",
        "status": current_status,
        "isolate_on_status": isolate_on_status,
        "status_allowed": status_allowed,
        "already_processed": already_processed,
        "would_call_isolate": bool(
            bool_value(veeam_config.get("enabled", False)) and latest_session and status_allowed and not already_processed
        ),
        "state_path": str(state_path),
    }


def pre_isolate_checks(
    config: LockFixConfig,
    veeam_config: dict[str, Any],
    latest_session: dict[str, Any] | None,
    sessions: list[dict[str, Any]],
    condition: dict[str, Any],
) -> dict[str, Any]:
    delay_seconds = max(0, int(veeam_config.get("post_success_delay_seconds", 10) or 0))
    ended_at = session_end_text(latest_session)
    end_epoch = parse_time_epoch(ended_at)
    age_seconds = int(time.time() - end_epoch) if end_epoch else None
    delay_ok = bool(age_seconds is not None and age_seconds >= delay_seconds)
    if delay_seconds == 0 and condition.get("status_allowed"):
        delay_ok = True

    active_resync = active_repository_resync_sessions(sessions)
    require_resync_quiet = bool_value(veeam_config.get("require_repository_resync_quiet", True), True)
    repository_resync_ok = not (require_resync_quiet and active_resync)
    io_quiet_seconds = max(0, int(config.io_quiet_seconds))
    io_quiet_ok = io_quiet_seconds >= 0

    ready = bool(condition.get("status_allowed") and delay_ok and repository_resync_ok and io_quiet_ok)
    return {
        "ready": ready,
        "post_success_delay": {
            "ok": delay_ok,
            "required_seconds": delay_seconds,
            "age_seconds": age_seconds,
            "ended_at": ended_at or "-",
            "message": (
                "Post-success delay satisfied."
                if delay_ok
                else "Waiting until successful Veeam session is older than post_success_delay_seconds."
            ),
        },
        "io_quiet": {
            "ok": io_quiet_ok,
            "required_seconds": io_quiet_seconds,
            "enforced_by": "LockFixController.isolate",
            "message": "I/O quiet check is enforced immediately before unmount inside LOCK-FIX isolate.",
        },
        "repository_resync": {
            "ok": repository_resync_ok,
            "required": require_resync_quiet,
            "active_count": len(active_resync),
            "active_sessions": active_resync,
            "message": (
                "No active repository/configuration resync session detected."
                if repository_resync_ok
                else "Repository/configuration resync is active; isolate is blocked."
            ),
        },
    }


def active_repository_resync_sessions(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active: list[dict[str, Any]] = []
    active_states = {"working", "running", "inprogress", "in_progress"}
    for item in sessions:
        if not isinstance(item, dict):
            continue
        text = " ".join(
            str(item.get(key) or "")
            for key in ("sessionType", "name", "type", "state")
        ).lower()
        state = str(item.get("state") or item.get("status") or "").strip().lower()
        is_resync = "resynchron" in text or "resync" in text or "repository" in text and "sync" in text
        if is_resync and normalize_state(state) in active_states:
            active.append(
                {
                    "id": item.get("id") or item.get("sessionId") or "",
                    "name": item.get("name") or item.get("sessionType") or "Repository resync",
                    "state": item.get("state") or item.get("status") or "",
                }
            )
    return active


def normalize_state(value: str) -> str:
    return value.replace("-", "_").replace(" ", "_").lower()


def session_end_text(session: dict[str, Any] | None) -> str:
    if not session:
        return ""
    result = str(
        session.get("endTime")
        or session.get("ended_at")
        or session.get("end_time")
        or session.get("stopTime")
        or ""
    ).strip()
    nested = session.get("result")
    if not result and isinstance(nested, dict):
        result = str(nested.get("endTime") or "").strip()
    return result


def parse_time_epoch(value: str) -> float | None:
    text = (value or "").strip()
    if not text or text == "-":
        return None
    candidates = [text]
    if text.endswith("Z"):
        candidates.append(text[:-1] + "+00:00")
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.timestamp()
        except ValueError:
            continue
    return None


def add_webui_shape(result: dict[str, Any]) -> dict[str, Any]:
    latest = result.get("latest_configured_session") if isinstance(result.get("latest_configured_session"), dict) else {}
    config = result.get("config") if isinstance(result.get("config"), dict) else {}
    status = str(latest.get("result") or latest.get("status") or "Waiting")
    progress = int(latest.get("progress_percent") or latest.get("progress") or (100 if status.lower() == "success" else 0))
    current_step = int(latest.get("current_step") or (2 if status.lower() == "success" else 1))
    current_step = max(1, min(5, current_step))
    started_at = latest.get("started_at") or latest.get("start_time") or "-"
    ended_at = latest.get("ended_at") or latest.get("end_time") or "-"
    duration = latest.get("duration") or "-"
    session_logs = latest.get("session_logs") if isinstance(latest.get("session_logs"), list) else []
    if not session_logs:
        session_logs = [
            {
                "name": latest.get("name") or config.get("job_name") or "Veeam API",
                "status": status,
                "actions": webui_actions(result, latest),
                "duration": duration,
                "progress_percent": progress,
                "started_at": started_at,
                "ended_at": ended_at,
                "backup_size": latest.get("backup_size") or "-",
                "transferred": latest.get("transferred") or "-",
                "speed": latest.get("speed") or "-",
            }
        ]

    result["api"] = {
        "source": "python_veeam_client",
        "poll_interval_seconds": config.get("poll_interval_seconds", 10),
        "server": host_from_base_url(config.get("base_url") or "https://127.0.0.1:9419"),
        "port": port_from_base_url(config.get("base_url") or "https://127.0.0.1:9419"),
        "connected": bool(result.get("success") and latest.get("api_synced", result.get("success"))),
        "api_synced": bool(result.get("success") and latest.get("api_synced", result.get("success"))),
        "port_open": bool((result.get("vbr_rest_9419") or {}).get("port", {}).get("ok")),
        "api_checks": latest.get("checks") if isinstance(latest.get("checks"), dict) else {},
        "vbr_rest_9419": result.get("vbr_rest_9419"),
        "base_url": config.get("base_url"),
        "api_version": config.get("api_version"),
        "verify_ssl": config.get("verify_ssl"),
        "username": config.get("username"),
        "password_env": config.get("password_env"),
        "password_logged": False,
        "token": result.get("authentication"),
        "jobs": {"ok": (result.get("jobs") or {}).get("ok", False), "count": (result.get("jobs") or {}).get("count", 0)},
        "sessions": {
            "ok": (result.get("sessions") or {}).get("ok", False),
            "count": (result.get("sessions") or {}).get("count", 0),
        },
        "matching": result.get("matching"),
        "job_name": config.get("job_name"),
        "job_id": config.get("job_id"),
        "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
        "state_source": latest.get("state_source") or "veeam_rest_api",
        "message": "Veeam API is connected." if result.get("success") else result.get("error", "Veeam API is not connected."),
    }
    result["job"] = {
        "name": latest.get("name") or latest.get("job") or config.get("job_name") or "Veeam API",
        "session_state": latest.get("session_state") or latest.get("state") or ("BACKUP_COMPLETED" if progress >= 100 else "WAITING"),
        "current_step": current_step,
        "progress_percent": progress,
        "result": "SUCCESS" if status.lower() == "success" else status.upper(),
        "started_at": started_at,
        "ended_at": ended_at,
        "duration": duration,
    }
    result["steps"] = webui_steps(current_step, progress, result.get("success", False))
    result["session_logs"] = session_logs
    result["auto_isolate"] = {
        "enabled": bool((result.get("isolate_condition") or {}).get("watcher_enabled")),
        "triggered": False,
        "ready": bool((result.get("pre_isolate_checks") or {}).get("ready")),
        "message": "VeeamWatcher uses this same diagnostics result before isolate.",
    }
    result["veeam_client_result"] = latest
    result["logs"] = [
        {"time": item["time"], "level": "INFO" if item["transition_allowed"] else "WAIT", "step": item["step"], "message": item["detail"], "source": item["source"]}
        for item in result["steps"]
    ]
    result["diagnostics"] = {
        key: result.get(key)
        for key in (
            "success",
            "source",
            "enabled",
            "config_source",
            "config",
            "vbr_rest_9419",
            "reference_only_enterprise_manager_port",
            "powershell_curl_module",
            "tls",
            "authentication",
            "jobs",
            "sessions",
            "backups",
            "repositories",
            "matching",
            "latest_configured_session",
            "isolate_condition",
            "pre_isolate_checks",
            "runtime_state",
            "error_type",
            "error",
        )
    }
    return result


def webui_actions(result: dict[str, Any], latest: dict[str, Any]) -> list[str]:
    if latest:
        actions = []
        for log in latest.get("session_logs", []) if isinstance(latest.get("session_logs"), list) else []:
            if isinstance(log, dict):
                actions.extend([str(item) for item in log.get("actions", [])])
        if actions:
            return actions
    if result.get("success"):
        return ["Veeam REST 9419 token, jobs, sessions, and backup copy evidence were queried by Python VeeamClient."]
    return [
        f"ERROR - {result.get('error_type', 'VeeamError')}: {result.get('error', 'Veeam REST API is not synced.')}",
        "PowerShell/curl/Veeam PowerShell Module diagnostics are reference-only.",
    ]


def webui_steps(current_step: int, progress: int, connected: bool) -> list[dict[str, Any]]:
    labels = ["백업 완료", "Flush 실행", "I/O 종료 확인", "Unmount", "전원 OFF"]
    codes = ["BACKUP_COMPLETED", "FLUSHING", "IO_CHECKING", "UNMOUNTING", "POWERING_OFF"]
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    steps = []
    for index, label in enumerate(labels, start=1):
        state = "DONE" if index < current_step else "ACTIVE" if index == current_step and connected else "PENDING"
        steps.append(
            {
                "step": index,
                "label": label,
                "code": codes[index - 1],
                "state": state,
                "time": now,
                "source": "Python VeeamClient" if connected else "Veeam API 대기",
                "detail": (
                    f"{label} 단계가 Veeam REST 결과 기준으로 확인되었습니다."
                    if index <= current_step and connected
                    else "실제 Veeam REST 단계 전환 전까지 대기합니다."
                ),
                "progress_percent": progress if index <= current_step else "",
                "api_verification_percent": 100 if connected and index == 1 else "",
                "transition_allowed": bool(connected and index <= current_step),
            }
        )
    return steps


def host_from_base_url(base_url: str) -> str:
    text = str(base_url or "")
    if "://" in text:
        text = text.split("://", 1)[1]
    return text.split(":", 1)[0].split("/", 1)[0] or "127.0.0.1"


def port_from_base_url(base_url: str) -> int:
    text = str(base_url or "")
    if "://" in text:
        text = text.split("://", 1)[1]
    if ":" not in text:
        return 9419
    try:
        return int(text.split(":", 1)[1].split("/", 1)[0])
    except ValueError:
        return 9419
