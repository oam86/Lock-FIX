from __future__ import annotations

import json
import io
from http import client as httpclient
from typing import Any
from urllib import error as urlerror
from urllib.parse import urlparse

from .config import LockFixConfig
from .controller import LockFixController
from .veeam_diagnostics import run_veeam_diagnostics


DEFAULT_WEBUI_URL = "http://127.0.0.1:8088"


def compare_veeam_test_with_webui(
    config: LockFixConfig,
    controller: LockFixController,
    webui_url: str = DEFAULT_WEBUI_URL,
    email: str = "admin",
    password: str = "1",
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Compare local veeam-test diagnostics with an already running Web UI.

    This diagnostic intentionally never starts lockfix-ui.exe, webui.py, or a
    Python web server. In locked-down Windows environments the Web UI must be
    run by the installed Windows service or Task Scheduler task.
    """

    veeam_test = run_veeam_diagnostics(config, controller)
    result: dict[str, Any] = {
        "source": "http_compare_only",
        "process_launch_attempted": False,
        "webui_url": webui_url.rstrip("/"),
        "veeam_test": summarize_veeam_test(veeam_test),
        "webui": {
            "running": False,
            "ok": False,
            "message": "Web UI server was not checked yet.",
        },
        "comparison": {
            "ok": False,
            "message": "Web UI response was not available.",
            "matches": {},
        },
    }

    try:
        webui_payload = fetch_webui_veeam_backup(webui_url, email, password, timeout_seconds)
    except WebUiServerNotRunning as exc:
        result["webui"] = {
            "running": False,
            "ok": False,
            "message": "Web UI server is not running",
            "detail": str(exc),
        }
        result["comparison"]["message"] = (
            "Web UI server is not running. This is not treated as a Veeam REST integration failure."
        )
        return result
    except Exception as exc:
        result["webui"] = {
            "running": True,
            "ok": False,
            "message": "Web UI HTTP check failed",
            "error_type": exc.__class__.__name__,
            "detail": str(exc),
        }
        result["comparison"]["message"] = (
            "Web UI HTTP check failed. This is separate from Veeam REST 9419 validation."
        )
        return result

    webui_summary = summarize_webui_backup(webui_payload)
    matches = compare_summaries(result["veeam_test"], webui_summary)
    result["webui"] = {
        "running": True,
        "ok": True,
        "message": "/api/veeam-backup HTTP response received.",
        **webui_summary,
    }
    result["comparison"] = {
        "ok": all(matches.values()) if matches else False,
        "message": "veeam-test and /api/veeam-backup were compared without launching a process.",
        "matches": matches,
    }
    return result


class WebUiServerNotRunning(ConnectionError):
    pass


def fetch_webui_veeam_backup(
    webui_url: str,
    email: str = "admin",
    password: str = "1",
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    base = webui_url.rstrip("/")
    try:
        login_body = json.dumps({"email": email, "password": password}).encode("utf-8")
        login_status, login_headers, _ = direct_http_request(
            base,
            "POST",
            "/api/login",
            login_body,
            {"Content-Type": "application/json", "Accept": "application/json"},
            timeout_seconds,
        )
        if login_status >= 400:
            raise urlerror.HTTPError(f"{base}/api/login", login_status, "Login failed", login_headers, None)
        cookie = login_headers.get("Set-Cookie", "").split(";", 1)[0]
        _, _, raw_bytes = direct_http_request(
            base,
            "GET",
            "/api/veeam-backup",
            None,
            {"Accept": "application/json", "Cookie": cookie},
            timeout_seconds,
        )
        raw = raw_bytes.decode("utf-8", errors="replace")
    except urlerror.HTTPError:
        raise
    except (ConnectionRefusedError, TimeoutError, OSError, httpclient.HTTPException) as exc:
        raise WebUiServerNotRunning(exc) from exc
    loaded = json.loads(raw) if raw else {}
    return loaded if isinstance(loaded, dict) else {"data": loaded}


def direct_http_request(
    base_url: str,
    method: str,
    path: str,
    body: bytes | None,
    headers: dict[str, str],
    timeout_seconds: float,
) -> tuple[int, httpclient.HTTPMessage, bytes]:
    parsed = urlparse(base_url)
    scheme = parsed.scheme or "http"
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if scheme == "https" else 80)
    connection_class = httpclient.HTTPSConnection if scheme == "https" else httpclient.HTTPConnection
    connection = connection_class(host, port, timeout=timeout_seconds)
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        if response.status >= 400:
            raise urlerror.HTTPError(
                f"{base_url}{path}",
                response.status,
                response.reason,
                response.headers,
                io.BytesIO(raw),
            )
        return response.status, response.headers, raw
    finally:
        connection.close()


def summarize_veeam_test(data: dict[str, Any]) -> dict[str, Any]:
    latest = data.get("latest_configured_session") if isinstance(data.get("latest_configured_session"), dict) else {}
    config = data.get("config") if isinstance(data.get("config"), dict) else {}
    authentication = data.get("authentication") if isinstance(data.get("authentication"), dict) else {}
    sessions = data.get("sessions") if isinstance(data.get("sessions"), dict) else {}
    jobs = data.get("jobs") if isinstance(data.get("jobs"), dict) else {}
    matching = data.get("matching") if isinstance(data.get("matching"), dict) else {}
    vbr = data.get("vbr_rest_9419") if isinstance(data.get("vbr_rest_9419"), dict) else {}
    port = vbr.get("port") if isinstance(vbr.get("port"), dict) else {}
    return {
        "source": latest.get("source") or "python_veeam_client",
        "base_url": config.get("base_url"),
        "api_version": config.get("api_version"),
        "verify_ssl": config.get("verify_ssl"),
        "port_9419_open": port.get("ok"),
        "token_ok": authentication.get("ok"),
        "sessions_ok": sessions.get("ok"),
        "sessions_count": sessions.get("count"),
        "jobs_ok": jobs.get("ok"),
        "jobs_count": jobs.get("count"),
        "job_name": config.get("job_name"),
        "job_id": config.get("job_id"),
        "matched": matching.get("matched"),
        "match_strategy": matching.get("strategy"),
        "latest_name": latest.get("name"),
        "latest_status": latest.get("status"),
        "latest_result": latest.get("result"),
        "latest_duration": latest.get("duration"),
    }


def summarize_webui_backup(data: dict[str, Any]) -> dict[str, Any]:
    api = data.get("api") if isinstance(data.get("api"), dict) else {}
    job = data.get("job") if isinstance(data.get("job"), dict) else {}
    token = api.get("token") if isinstance(api.get("token"), dict) else {}
    sessions = api.get("sessions") if isinstance(api.get("sessions"), dict) else {}
    jobs = api.get("jobs") if isinstance(api.get("jobs"), dict) else {}
    matching = api.get("matching") if isinstance(api.get("matching"), dict) else {}
    return {
        "source": data.get("source") or api.get("source"),
        "base_url": api.get("base_url"),
        "api_version": api.get("api_version"),
        "verify_ssl": api.get("verify_ssl"),
        "token_ok": token.get("ok"),
        "sessions_ok": sessions.get("ok"),
        "sessions_count": sessions.get("count"),
        "jobs_ok": jobs.get("ok"),
        "jobs_count": jobs.get("count"),
        "job_name": api.get("job_name"),
        "job_id": api.get("job_id"),
        "matched": matching.get("matched"),
        "match_strategy": matching.get("strategy"),
        "latest_name": job.get("name"),
        "latest_result": job.get("result"),
        "latest_duration": job.get("duration"),
    }


def compare_summaries(veeam_test: dict[str, Any], webui: dict[str, Any]) -> dict[str, bool]:
    keys = (
        "source",
        "base_url",
        "api_version",
        "verify_ssl",
        "token_ok",
        "sessions_ok",
        "sessions_count",
        "jobs_ok",
        "jobs_count",
        "job_name",
        "job_id",
        "matched",
        "match_strategy",
        "latest_name",
        "latest_duration",
    )
    return {key: veeam_test.get(key) == webui.get(key) for key in keys}
