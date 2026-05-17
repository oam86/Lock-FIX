from __future__ import annotations

import os
from typing import Any

from .config import bool_value
from .veeam_client import VeeamClient, VeeamSettings, normalized_job_id


def create_veeam_client(veeam_config: dict[str, Any]) -> VeeamClient:
    """Create the single LOCK-FIX Veeam REST client from config["veeam"].

    All Veeam entrypoints must use this factory so username, password_env,
    verify_ssl, base_url, api_version, job_id, and job_name are resolved in one
    place. The password value is read from the configured environment variable
    and is never returned or logged.
    """

    username_env = str(veeam_config.get("username_env") or "LOCKFIX_VEEAM_USER")
    username = str(os.getenv(username_env) or veeam_config.get("username") or "").strip()
    password_env = str(veeam_config.get("password_env") or "LOCKFIX_VEEAM_PASSWORD")
    password = os.getenv(password_env, "")

    if not username:
        raise ValueError("Veeam username is not configured")
    if not password:
        raise ValueError(f"Veeam password environment variable is not set: {password_env}")

    settings = VeeamSettings(
        base_url=str(os.getenv("LOCKFIX_VEEAM_BASE_URL") or veeam_config.get("base_url") or "https://127.0.0.1:9419").rstrip("/"),
        enterprise_manager_url=str(os.getenv("LOCKFIX_VEEAM_EM_BASE_URL") or veeam_config.get("enterprise_manager_url") or "https://127.0.0.1:9398").rstrip("/"),
        auto_discover=bool_value(veeam_config.get("auto_discover", False), False),
        discovery_candidates=[
            str(item).rstrip("/")
            for item in veeam_config.get("discovery_candidates", [])
            if str(item).strip()
        ],
        discovery_scan_local_subnet=bool_value(veeam_config.get("discovery_scan_local_subnet", False), False),
        discovery_timeout_seconds=float(veeam_config.get("discovery_timeout_seconds", 0.35)),
        api_version=str(os.getenv("LOCKFIX_VEEAM_API_VERSION") or veeam_config.get("api_version") or "1.2-rev1"),
        username=username,
        username_env=username_env,
        password=password,
        password_env=password_env,
        verify_ssl=bool_value(veeam_config.get("verify_ssl", False)),
        job_name=str(os.getenv("LOCKFIX_VEEAM_JOB_NAME") or veeam_config.get("job_name") or ""),
        job_id=normalized_job_id(str(os.getenv("LOCKFIX_VEEAM_JOB_ID") or veeam_config.get("job_id") or "")),
        require_backup_copy=bool_value(veeam_config.get("require_backup_copy", True), True),
        target_repository_id=str(os.getenv("LOCKFIX_VEEAM_REPOSITORY_ID") or veeam_config.get("target_repository_id") or ""),
        target_repository_name=str(os.getenv("LOCKFIX_VEEAM_REPOSITORY_NAME") or veeam_config.get("target_repository_name") or ""),
        target_repository_path=str(os.getenv("LOCKFIX_VEEAM_REPOSITORY_PATH") or veeam_config.get("target_repository_path") or ""),
        exclude_os_repository=bool_value(veeam_config.get("exclude_os_repository", True), True),
        console_log_fallback_enabled=bool_value(veeam_config.get("console_log_fallback_enabled", True), True),
        console_log_root=str(veeam_config.get("console_log_root") or "C:\\ProgramData\\Veeam\\Backup"),
        poll_interval_seconds=max(1, int(veeam_config.get("poll_interval_seconds", 10))),
        isolate_on_status=[str(item) for item in veeam_config.get("isolate_on_status", ["Success"])],
    )
    return VeeamClient(settings)
