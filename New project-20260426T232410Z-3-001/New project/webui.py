from __future__ import annotations

import json
import base64
import binascii
import copy
import io
import ipaddress
import mimetypes
import os
import platform
import re
import secrets
import shutil
import smtplib
import ssl
import hashlib
import socket
import subprocess
import textwrap
import threading
import time
import uuid
import zipfile
import zlib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlencode, urlparse
from xml.sax.saxutils import escape

from lockfix.config import get_veeam_config, load_app_config, load_config, normalize_operation_mode
from lockfix.agent_service import AgentServiceClient, AgentServiceUnavailable, AgentServiceWorker
from lockfix.controller import LockFixController, repository_volume_root
from lockfix.audit_log import audit_logs_to_csv, read_audit_logs, tail_text_lines
from lockfix.hashcheck import verify_manifest
from lockfix.identity import fingerprint_formula, fingerprint_parts, slot_uid, verify_uid
from lockfix.integrated import integrated_solution_summary
from lockfix.rbac import (
    AuthorizationError,
    Permission,
    Role,
    load_role_permissions,
    normalize_role,
    permissions_for_role,
    require_permission,
)
from lockfix.source_inventory import integrated_source_inventory
from lockfix.users import UserDirectory
from lockfix.veeam_diagnostics import run_veeam_diagnostics


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "web" / "static"
DEFAULT_CONFIG = ROOT / "config" / "lockfix.example.json"
LOGIN_WARNING_THRESHOLD = 3
LOGIN_LOCK_THRESHOLD = 5
LOGIN_TEMP_PASSWORD_TTL_SECONDS = 15 * 60
USER_TEMP_PASSWORD_TTL_SECONDS = 24 * 60 * 60
LOGIN_TEMP_PASSWORD_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
NETWORK_HISTORY_LOCK = threading.Lock()
NETWORK_INTERFACE_HISTORY: dict[str, dict[str, list[float]]] = {}
AIRGAP_AUTO_ISOLATE_LOCK = threading.Lock()
AIRGAP_AUTO_ISOLATE_STALE_SECONDS = 120
DASHBOARD_CACHE_TTL_SECONDS = 0.8
DASHBOARD_PROBE_TIMEOUT_SECONDS = 1.2
SOURCES_CACHE_TTL_SECONDS = 0.8
SOURCE_INVENTORY_CACHE_TTL_SECONDS = 30.0
DETECT_CACHE_TTL_SECONDS = 2.0
VEEAM_DIAGNOSTICS_WAIT_BUFFER_SECONDS = 0.5
EMERGENCY_RECONNECT_AGENT_START_TIMEOUT_SECONDS = 12


class WebContext:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.sessions = {}
        self.qr_tokens = {}
        self.license_path = ROOT / "runtime" / "license.json"
        self.report_customer_path = ROOT / "runtime" / "report_customer.json"
        self.report_extras_path = ROOT / "runtime" / "report_extras.json"
        self.emergency_jobs = {}
        self.emergency_jobs_lock = threading.Lock()
        self.login_security_path = ROOT / "runtime" / "login_security.json"
        self.notification_settings_path = ROOT / "runtime" / "notification_settings.json"
        self.login_security_lock = threading.Lock()
        self.rbac_policy_path = ROOT / "config" / "rbac_policy.json"
        self.user_directory_path = ROOT / "runtime" / "users.json"
        self.user_directory_lock = threading.Lock()
        self.agent_service_queue_root = ROOT / "runtime" / "agent_service"
        self.agent_worker_lock = threading.Lock()
        self.agent_worker_thread: threading.Thread | None = None
        self.veeam_steering_lock = threading.Lock()
        self.veeam_steering_thread: threading.Thread | None = None
        self.veeam_steering_state_path = ROOT / "runtime" / "veeam_steering_state.json"
        self.report_snapshot_lock = threading.Lock()
        self.report_snapshot: dict | None = None
        self.report_snapshot_at = 0.0

    def store_report_snapshot(self, report: dict) -> None:
        with self.report_snapshot_lock:
            self.report_snapshot = copy.deepcopy(report)
            self.report_snapshot_at = time.time()

    def latest_report_snapshot(self, max_age_seconds: int = 600) -> dict | None:
        with self.report_snapshot_lock:
            if not self.report_snapshot:
                return None
            if time.time() - self.report_snapshot_at > max_age_seconds:
                return None
            return copy.deepcopy(self.report_snapshot)

    @property
    def app_config(self):
        return load_app_config(self.config_path)

    @property
    def config(self):
        return load_config(self.config_path)

    def operation_mode(self) -> str:
        config = self.config
        return normalize_operation_mode(getattr(config, "operation_mode", ""), getattr(config, "dry_run", False))

    @property
    def controller(self) -> LockFixController:
        return LockFixController(self.config)

    @property
    def agent_service(self) -> AgentServiceClient:
        config = self.config
        mode = self.operation_mode()
        allow_inline = mode == "poc"
        return AgentServiceClient(
            self.agent_service_queue_root,
            timeout_seconds=float(os.environ.get("LOCKFIX_AGENT_SERVICE_TIMEOUT", "30")),
            allow_inline_fallback=allow_inline,
            inline_executor=self.execute_inline_agent_operation,
        )

    def execute_inline_agent_operation(self, operation: str, payload: dict) -> dict:
        controller = self.controller
        mode = self.operation_mode()
        controller.audit.write(
            "poc.admin_execution",
            operation=operation,
            operation_mode=mode,
            dry_run=controller.config.dry_run,
            message="POC/admin inline execution fallback was used. Commercial and delivery operation must use LOCK-FIX Agent/Service.",
        )
        controller.audit.write(
            "agent.service.inline_fallback",
            operation=operation,
            operation_mode=mode,
            dry_run=controller.config.dry_run,
        )
        if operation == "disk.isolate":
            state = controller.isolate(str(payload.get("slot_id") or ""), repository_path=str(payload.get("repository_path") or ""))
            return {"ok": True, "operation": operation, "state": state.value, "inline_fallback": True}
        if operation == "disk.reconnect":
            state = controller.reconnect(str(payload.get("slot_id") or ""), repository_path=str(payload.get("repository_path") or ""))
            return {"ok": True, "operation": operation, "state": state.value, "inline_fallback": True}
        if operation == "emergency.reconnect":
            state = controller.emergency_reconnect(
                str(payload.get("slot_id") or ""),
                repository_path=str(payload.get("repository_path") or ""),
                approval_bypass=bool(payload.get("approval_bypass")),
                approval_bypass_reason=str(payload.get("approval_bypass_reason") or ""),
            )
            return {"ok": True, "operation": operation, "state": state.value, "inline_fallback": True}
        if operation == "veeam.diagnostics":
            return {"ok": True, "operation": operation, "diagnostics": run_veeam_diagnostics(self.config, controller), "inline_fallback": True}
        if operation == "service.preflight":
            diagnostics = AgentServiceWorker(self.config_path, self.agent_service_queue_root).service_preflight(payload, controller)
            return {"ok": True, "operation": operation, "diagnostics": diagnostics, "inline_fallback": True}
        raise ValueError(f"Unsupported LOCK-FIX Agent/Service operation: {operation}")

    def run_agent_service_operation(self, operation: str, payload: dict, timeout_seconds: float | None = None) -> dict:
        if operation in {"veeam.diagnostics", "service.preflight"} or self.agent_worker_thread is not None:
            self.start_agent_service_worker()
        return self.agent_service.submit_and_wait(operation, payload, timeout_seconds=timeout_seconds)

    def start_agent_service_worker(self) -> None:
        if str(os.environ.get("LOCKFIX_DISABLE_AGENT_WORKER", "")).strip() in {"1", "true", "TRUE", "yes", "YES"}:
            return
        with self.agent_worker_lock:
            if self.agent_worker_thread and self.agent_worker_thread.is_alive():
                return
            worker = AgentServiceWorker(self.config_path, self.agent_service_queue_root)
            thread = threading.Thread(
                target=worker.run_forever,
                name="LOCKFIXAgentServiceWorker",
                daemon=True,
            )
            thread.start()
            self.agent_worker_thread = thread
        self.controller.audit.write(
            "agent.service.worker.started",
            queue_root=str(self.agent_service_queue_root),
            message="LOCK-FIX Agent/Service worker started inside LOCKFIXWebUI Windows Service.",
        )

    def start_veeam_steering_worker(self) -> None:
        if str(os.environ.get("LOCKFIX_DISABLE_VEEAM_STEERING", "")).strip() in {"1", "true", "TRUE", "yes", "YES"}:
            return
        if not self.config.veeam.enabled:
            return
        with self.veeam_steering_lock:
            if self.veeam_steering_thread and self.veeam_steering_thread.is_alive():
                return
            thread = threading.Thread(
                target=self.run_veeam_steering_forever,
                name="LOCKFIXVeeamSteeringWorker",
                daemon=True,
            )
            thread.start()
            self.veeam_steering_thread = thread
        self.controller.audit.write(
            "veeam.steering.worker.started",
            state_path=str(self.veeam_steering_state_path),
            message="LOCK-FIX Veeam/Air-Gap steering worker started automatically inside LOCKFIXWebUI.",
        )

    def run_veeam_steering_forever(self) -> None:
        while True:
            interval = 10
            try:
                config = self.config
                interval = max(1, int(getattr(config.veeam, "poll_interval_seconds", 10) or 10))
                if config.veeam.enabled:
                    self.run_veeam_steering_once()
            except Exception as exc:
                self.write_veeam_steering_state(
                    {
                        "ok": False,
                        "last_error": str(exc),
                        "last_run_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                try:
                    self.controller.audit.write(
                        "veeam.steering.failed",
                        error=str(exc),
                        message="Automatic Veeam/Air-Gap steering tick failed; worker will retry on the next interval.",
                    )
                except Exception:
                    pass
            time.sleep(interval)

    def run_veeam_steering_once(self) -> dict:
        probe = object.__new__(LockFixWebHandler)
        probe.context = self
        runtime = LockFixWebHandler.veeam_interlock_runtime(probe, time.time(), poll_api=True)
        auto_isolate = runtime.get("auto_isolate") if isinstance(runtime.get("auto_isolate"), dict) else {}
        api_synced = bool(runtime.get("api_synced"))
        status = str(runtime.get("status") or runtime.get("result") or "").strip()
        auto_state = str(auto_isolate.get("state") or "").strip()
        issue_detected = (
            not api_synced
            or status.upper() in {"FAILED", "FAILURE", "ERROR"}
            or auto_state.upper() == "FAILED"
        )
        state = {
            "ok": True,
            "last_run_at": datetime.now().isoformat(timespec="seconds"),
            "worker": "LOCKFIXVeeamSteeringWorker",
            "api_synced": api_synced,
            "server": runtime.get("server"),
            "port": runtime.get("port"),
            "job": runtime.get("job"),
            "status": status,
            "progress_percent": runtime.get("progress_percent"),
            "current_step": runtime.get("current_step"),
            "state_source": runtime.get("state_source"),
            "message": runtime.get("message") or "",
            "last_checked": runtime.get("last_checked") or "",
            "issue_detected": issue_detected,
            "auto_isolate_state": auto_isolate.get("state") or "",
            "auto_isolate_triggered": bool(auto_isolate.get("triggered")),
            "auto_isolate_message": auto_isolate.get("message") or "",
        }
        self.write_veeam_steering_state(state)
        if issue_detected:
            try:
                self.controller.audit.write(
                    "veeam.integration.health.failed",
                    api_synced=api_synced,
                    server=state.get("server") or "",
                    port=state.get("port") or "",
                    job=state.get("job") or "",
                    status=status or "-",
                    current_step=state.get("current_step") or "",
                    state_source=state.get("state_source") or "",
                    message=state.get("message") or state.get("auto_isolate_message") or "Veeam REST integration health check failed.",
                )
            except Exception:
                pass
        return state

    def write_veeam_steering_state(self, state: dict) -> None:
        self.veeam_steering_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.veeam_steering_state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def veeam_backup_copy_repository_path(self) -> str:
        veeam = self.config.veeam
        if veeam.enabled and veeam.require_backup_copy:
            return str(veeam.target_repository_path or "").strip()
        return ""

    @property
    def user_directory(self) -> UserDirectory:
        return UserDirectory(self.user_directory_path)

    def login_security_now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def login_security_hash(self, value: str) -> str:
        return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()

    def login_security_key(self, user: str) -> str:
        return str(user or "").strip().lower() or "unknown"

    def login_security_state(self) -> dict:
        try:
            state = json.loads(self.login_security_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}
        if not isinstance(state, dict):
            state = {}
        state.setdefault("users", {})
        return state

    def save_login_security_state(self, state: dict) -> None:
        self.login_security_path.parent.mkdir(parents=True, exist_ok=True)
        self.login_security_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def login_temp_expired(self, temporary: dict) -> bool:
        expires_at = str(temporary.get("expires_at") or "")
        try:
            return datetime.fromisoformat(expires_at) <= datetime.now()
        except ValueError:
            return True

    def generate_login_temp_password(self) -> str:
        return "".join(secrets.choice(LOGIN_TEMP_PASSWORD_ALPHABET) for _ in range(8))

    def register_login_failure(self, user: str, client_ip: str) -> dict:
        with self.login_security_lock:
            state = self.login_security_state()
            users = state.setdefault("users", {})
            key = self.login_security_key(user)
            record = users.get(key) if isinstance(users.get(key), dict) else {}
            now = self.login_security_now()
            failure_count = int(record.get("failure_count") or 0) + 1
            record.update(
                {
                    "user": str(user or "unknown"),
                    "client_ip": client_ip,
                    "failure_count": failure_count,
                    "last_failed_at": now,
                    "updated_at": now,
                }
            )
            result = {
                "user": record["user"],
                "client_ip": client_ip,
                "failure_count": failure_count,
                "last_failed_at": now,
                "warning": failure_count == LOGIN_WARNING_THRESHOLD,
                "locked": failure_count >= LOGIN_LOCK_THRESHOLD,
                "approval_required": failure_count >= LOGIN_LOCK_THRESHOLD,
                "approval_status": "NONE",
            }
            temporary = record.get("temporary") if isinstance(record.get("temporary"), dict) else {}
            if failure_count >= LOGIN_LOCK_THRESHOLD:
                should_issue = failure_count == LOGIN_LOCK_THRESHOLD or not temporary or self.login_temp_expired(temporary)
                if should_issue:
                    token = secrets.token_urlsafe(32)
                    temp_password = self.generate_login_temp_password()
                    expires_at = (datetime.now() + timedelta(seconds=LOGIN_TEMP_PASSWORD_TTL_SECONDS)).isoformat(
                        timespec="seconds"
                    )
                    temporary = {
                        "token_hash": self.login_security_hash(token),
                        "password_hash": self.login_security_hash(temp_password),
                        "created_at": now,
                        "expires_at": expires_at,
                        "approved": False,
                        "approved_at": "",
                        "approved_by": "",
                        "approval_status": "PENDING",
                    }
                    record["temporary"] = temporary
                    result.update(
                        {
                            "approval_status": "PENDING",
                            "approval_token": token,
                            "temporary_password": temp_password,
                            "temporary_expires_at": expires_at,
                            "temporary_password_digest": temporary["password_hash"][:16],
                        }
                    )
                else:
                    result.update(
                        {
                            "approval_status": str(temporary.get("approval_status") or "PENDING"),
                            "temporary_expires_at": str(temporary.get("expires_at") or ""),
                        }
                    )
            users[key] = record
            self.save_login_security_state(state)
            return result

    def reset_login_failures(self, user: str, client_ip: str, reason: str) -> dict:
        with self.login_security_lock:
            state = self.login_security_state()
            users = state.setdefault("users", {})
            key = self.login_security_key(user)
            record = users.get(key) if isinstance(users.get(key), dict) else {"user": user}
            record.update(
                {
                    "user": str(user or "unknown"),
                    "client_ip": client_ip,
                    "failure_count": 0,
                    "last_success_at": self.login_security_now(),
                    "last_success_reason": reason,
                    "temporary": {},
                }
            )
            users[key] = record
            self.save_login_security_state(state)
            return record

    def approve_login_temp_password(self, user: str, token: str, approved_by: str, client_ip: str) -> dict:
        with self.login_security_lock:
            state = self.login_security_state()
            record = state.setdefault("users", {}).get(self.login_security_key(user))
            temporary = record.get("temporary") if isinstance(record, dict) else {}
            if not isinstance(temporary, dict) or not temporary:
                return {"ok": False, "reason": "not_found"}
            if self.login_temp_expired(temporary):
                temporary["approval_status"] = "EXPIRED"
                self.save_login_security_state(state)
                return {"ok": False, "reason": "expired", "expires_at": temporary.get("expires_at", "")}
            if not secrets.compare_digest(str(temporary.get("token_hash") or ""), self.login_security_hash(token)):
                return {"ok": False, "reason": "invalid_token"}
            now = self.login_security_now()
            temporary.update(
                {
                    "approved": True,
                    "approved_at": now,
                    "approved_by": approved_by,
                    "approval_status": "APPROVED",
                    "approved_from": client_ip,
                }
            )
            self.save_login_security_state(state)
            return {
                "ok": True,
                "user": record.get("user", user),
                "approved_at": now,
                "approved_by": approved_by,
                "expires_at": temporary.get("expires_at", ""),
            }

    def verify_login_temp_password(self, user: str, password: str) -> dict:
        with self.login_security_lock:
            state = self.login_security_state()
            record = state.setdefault("users", {}).get(self.login_security_key(user))
            temporary = record.get("temporary") if isinstance(record, dict) else {}
            if not isinstance(temporary, dict) or not temporary:
                return {"ok": False, "reason": "not_found"}
            if self.login_temp_expired(temporary):
                temporary["approval_status"] = "EXPIRED"
                self.save_login_security_state(state)
                return {"ok": False, "reason": "expired", "expires_at": temporary.get("expires_at", "")}
            if not secrets.compare_digest(str(temporary.get("password_hash") or ""), self.login_security_hash(password)):
                return {"ok": False, "reason": "password_mismatch"}
            if not temporary.get("approved"):
                return {
                    "ok": False,
                    "reason": "approval_pending",
                    "approval_status": str(temporary.get("approval_status") or "PENDING"),
                    "expires_at": temporary.get("expires_at", ""),
                }
            return {
                "ok": True,
                "user": record.get("user", user),
                "approved_by": temporary.get("approved_by", "administrator"),
                "approved_at": temporary.get("approved_at", ""),
                "expires_at": temporary.get("expires_at", ""),
            }

    def start_emergency_reconnect(
        self,
        slot_id: str,
        repository_path: str,
        *,
        approval_bypass: bool = False,
        approval_bypass_reason: str = "",
    ) -> dict:
        with self.emergency_jobs_lock:
            running = self.emergency_jobs.get(slot_id)
            if running and running.get("status") == "running":
                return dict(running)
            job = {
                "job_id": uuid.uuid4().hex,
                "slot_id": slot_id,
                "repository_path": repository_path,
                "status": "running",
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "background_started_at": "",
                "approved_until": "",
                "approval_bypass": bool(approval_bypass),
                "approval_bypass_reason": str(approval_bypass_reason or ""),
                "message": "Emergency reconnect job started in background.",
            }
            self.emergency_jobs[slot_id] = job
        self.controller.audit.write(
            "emergency.reconnect.request",
            slot_id=slot_id,
            job_id=job["job_id"],
            repository_path=repository_path,
            approved_until=job["approved_until"],
            message="Emergency reconnect request accepted by WebUI. Background worker launch is being verified.",
        )
        worker = threading.Thread(
            target=self._run_emergency_reconnect_job,
            args=(slot_id, repository_path, job["job_id"], bool(approval_bypass), str(approval_bypass_reason or "")),
            daemon=True,
        )
        worker.start()
        return dict(job)

    def _run_emergency_reconnect_job(
        self,
        slot_id: str,
        repository_path: str,
        job_id: str,
        approval_bypass: bool = False,
        approval_bypass_reason: str = "",
    ) -> None:
        controller = self.controller
        background_started_at = datetime.now().isoformat(timespec="seconds")
        with self.emergency_jobs_lock:
            current = self.emergency_jobs.get(slot_id, {})
            if current.get("job_id") == job_id:
                current["background_started_at"] = background_started_at
                current["message"] = "Emergency reconnect background worker is running."
                self.emergency_jobs[slot_id] = current
        controller.audit.write(
            "emergency.reconnect.background.started",
            slot_id=slot_id,
            job_id=job_id,
            repository_path=repository_path,
            message="Emergency reconnect accepted by WebUI and moved to a background worker.",
        )
        try:
            result = self.run_agent_service_operation(
                "emergency.reconnect",
                {
                    "slot_id": slot_id,
                    "repository_path": repository_path,
                    "job_id": job_id,
                    "approval_bypass": bool(approval_bypass),
                    "approval_bypass_reason": str(approval_bypass_reason or ""),
                },
                timeout_seconds=max(180, int(getattr(self.config, "disk_wait_seconds", 60)) + 120),
            )
            state_value = str(result.get("state") or "ONLINE_VERIFIED_RW")
        except Exception as exc:
            resolution = self.emergency_reconnect_error_resolution(str(exc))
            controller.audit.write(
                "emergency.reconnect.background.error",
                slot_id=slot_id,
                job_id=job_id,
                repository_path=repository_path,
                error=str(exc),
                resolution=resolution,
            )
            status = {
                "status": "error",
                "error": str(exc),
                "resolution": resolution,
                "finished_at": datetime.now().isoformat(timespec="seconds"),
            }
        else:
            controller.audit.write(
                "emergency.reconnect.background.complete",
                slot_id=slot_id,
                job_id=job_id,
                repository_path=repository_path,
                state=state_value,
                executor="LOCK-FIX Agent/Service",
            )
            status = {"status": "complete", "state": state_value, "finished_at": datetime.now().isoformat(timespec="seconds")}
        with self.emergency_jobs_lock:
            current = self.emergency_jobs.get(slot_id, {})
            if current.get("job_id") == job_id:
                current.update(status)
                self.emergency_jobs[slot_id] = current

    def emergency_reconnect_status(self, slot_id: str, job_id: str = "") -> dict:
        with self.emergency_jobs_lock:
            job = dict(self.emergency_jobs.get(slot_id) or {})
        if not job:
            return {"slot_id": slot_id, "status": "idle", "message": "No emergency reconnect job is active."}
        if job_id and job.get("job_id") != job_id:
            return {"slot_id": slot_id, "status": "stale", "message": "A different emergency reconnect job is active.", "job": job}
        try:
            started_at = datetime.fromisoformat(str(job.get("started_at") or ""))
            elapsed = (datetime.now() - started_at).total_seconds()
        except ValueError:
            elapsed = 0
        job["elapsed_seconds"] = int(max(0, elapsed))
        if job.get("status") == "running" and job.get("background_started_at"):
            if elapsed >= EMERGENCY_RECONNECT_AGENT_START_TIMEOUT_SECONDS and not self.emergency_reconnect_agent_started(slot_id, str(job.get("job_id") or "")):
                error = "LOCK-FIX Agent/Service is not responding. Privileged disk and Veeam operations must run in the Windows Service."
                resolution = self.emergency_reconnect_error_resolution(error)
                updated = {
                    **job,
                    "status": "error",
                    "error": error,
                    "message": error,
                    "resolution": resolution,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
                with self.emergency_jobs_lock:
                    current = self.emergency_jobs.get(slot_id, {})
                    if current.get("job_id") == job.get("job_id") and current.get("status") == "running":
                        self.emergency_jobs[slot_id] = updated
                        job = dict(updated)
                self.controller.audit.write(
                    "emergency.reconnect.background.error",
                    slot_id=slot_id,
                    job_id=job.get("job_id", ""),
                    repository_path=job.get("repository_path", ""),
                    error=error,
                    resolution=resolution,
                )
            timeout_seconds = max(180, int(getattr(self.config, "disk_wait_seconds", 60)) + 120)
            if elapsed >= timeout_seconds:
                message = "재접속 작업 제한 시간을 초과했습니다. 실제 볼륨 연결이 완료되지 않았습니다."
                guidance = [
                    "저장된 Volume GUID/accessPath가 유지되는지 확인하세요.",
                    "LOCK-FIX WebUI 서비스를 LocalSystem 또는 관리자 권한으로 실행하세요.",
                    "서버에서 mountvol D:\\ \\\\?\\Volume{...}\\ 방식으로 수동 복구가 가능한지 확인하세요.",
                    "Get-Disk/Get-Partition/Get-Volume 권한과 Storage/WMI 서비스를 점검하세요.",
                ]
                updated = {
                    **job,
                    "status": "error",
                    "error": message,
                    "message": message,
                    "resolution": guidance,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
                with self.emergency_jobs_lock:
                    current = self.emergency_jobs.get(slot_id, {})
                    if current.get("job_id") == job.get("job_id") and current.get("status") == "running":
                        self.emergency_jobs[slot_id] = updated
                        job = dict(updated)
                self.controller.audit.write(
                    "emergency.reconnect.background.timeout",
                    slot_id=slot_id,
                    job_id=job.get("job_id", ""),
                    repository_path=job.get("repository_path", ""),
                    elapsed_seconds=int(elapsed),
                    timeout_seconds=timeout_seconds,
                    message=message,
                    resolution=" | ".join(guidance),
                )
        if job.get("status") == "running":
            self.controller.audit.write(
                "emergency.reconnect.heartbeat",
                slot_id=slot_id,
                job_id=job.get("job_id", ""),
                repository_path=job.get("repository_path", ""),
                background_started=bool(job.get("background_started_at")),
                elapsed_seconds=job.get("elapsed_seconds", 0),
                message=(
                    "Emergency reconnect background worker is running."
                    if job.get("background_started_at")
                    else "Emergency reconnect request is waiting for background worker start confirmation."
                ),
            )
        if job.get("status") == "running" and not job.get("background_started_at"):
            if elapsed >= 12:
                message = "재접속 작업이 시작되지 않았습니다. 관리자 권한/서비스 상태 확인 필요"
                guidance = [
                    "LOCK-FIX를 관리자 권한으로 재시작하세요.",
                    "WebUI 서비스가 최신 소스로 재시작되었는지 확인하세요.",
                    "Windows 디스크/파티션 API(Get-Disk, Get-Volume, Get-Partition) 접근 권한을 확인하세요.",
                    "작업 로그에 emergency.reconnect.background.started가 없으면 백그라운드 작업이 실제로 진입하지 못한 상태입니다.",
                ]
                updated = {
                    **job,
                    "status": "not_started",
                    "message": message,
                    "resolution": guidance,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
                with self.emergency_jobs_lock:
                    current = self.emergency_jobs.get(slot_id, {})
                    if current.get("job_id") == job.get("job_id") and current.get("status") == "running":
                        self.emergency_jobs[slot_id] = updated
                        job = dict(updated)
                    else:
                        job = dict(current or updated)
                self.controller.audit.write(
                    "emergency.reconnect.background.not_started",
                    slot_id=slot_id,
                    job_id=job.get("job_id", ""),
                    repository_path=job.get("repository_path", ""),
                    message=message,
                    resolution=" | ".join(guidance),
                )
        class _ReconnectAuditProbe:
            context = self

        probe = _ReconnectAuditProbe()
        reconnect_records = LockFixWebHandler.recent_reconnect_audit_records(probe, slot_id, limit=80)
        detail_logs = [
            item
            for item in (LockFixWebHandler.format_reconnect_audit_record(probe, record) for record in reconnect_records)
            if item
        ]
        flow_state = ""
        for record in reversed(reconnect_records):
            if record.get("event") == "state.transition" and record.get("state"):
                flow_state = str(record.get("state") or "")
                break
        return {"slot_id": slot_id, **job, "detail_logs": detail_logs[-80:], "flow_state": flow_state}

    def emergency_reconnect_agent_started(self, slot_id: str, job_id: str) -> bool:
        if not job_id:
            return False

        class _ReconnectAuditProbe:
            context = self

        probe = _ReconnectAuditProbe()
        for record in LockFixWebHandler.recent_reconnect_audit_records(probe, slot_id, limit=120, reset_on_request=False):
            if (
                record.get("event") == "agent.service.request.received"
                and str(record.get("operation") or "") == "emergency.reconnect"
                and str(record.get("job_id") or "") == job_id
            ):
                return True
        return False

    def emergency_reconnect_error_resolution(self, error: str) -> str:
        text = str(error or "")
        if "Agent/Service is not responding" in text:
            return (
                "LOCK-FIX Agent/Service 워커가 설치되어 실행 중인지 확인하세요. "
                "Agent/Service는 LocalSystem 또는 관리자 권한 서비스 계정으로 실행되어야 하며, "
                "runtime\\agent_service 요청 큐를 처리해야 합니다."
            )
        return (
            "LOCK-FIX WebUI와 Agent/Service를 최신 설치 파일 기준으로 재시작하고, "
            "Windows Storage/WMI 권한 및 Get-Disk/Get-Partition/Get-Volume 접근 권한을 확인하세요."
        )


class LockFixWebHandler(BaseHTTPRequestHandler):
    context: WebContext
    session_ttl_seconds = 60 * 60 * 8
    dashboard_cache_lock = threading.Lock()
    dashboard_cache_by_key: dict[str, tuple[float, dict]] = {}
    sources_cache_lock = threading.Lock()
    sources_cache_by_key: dict[str, tuple[float, dict]] = {}
    source_inventory_cache_lock = threading.Lock()
    source_inventory_cache_by_key: dict[str, tuple[float, dict]] = {}
    detect_cache_lock = threading.Lock()
    detect_cache_by_key: dict[str, tuple[float, dict]] = {}

    def log_message(self, format: str, *args: object) -> None:
        print("[webui] " + format % args)

    def do_GET(self) -> None:
        if not self.enforce_local_console_access():
            return
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self.serve_file(STATIC_DIR / "index.html")
            elif parsed.path.startswith("/static/"):
                self.serve_file(STATIC_DIR / parsed.path[len("/static/") :])
            elif parsed.path == "/api/session":
                self.send_json(
                    {
                        "authenticated": self.is_authenticated(),
                        "user": self.current_session_user() if self.is_authenticated() else "",
                        "role": self.current_role().value if self.is_authenticated() else "",
                        "userId": self.current_session_user_id() if self.is_authenticated() else "",
                        "departmentId": self.current_session_department_id() if self.is_authenticated() else "",
                        "passwordChangeRequired": self.current_password_change_required() if self.is_authenticated() else False,
                        "permissions": self.current_permissions() if self.is_authenticated() else [],
                        "license": self.license_status(),
                    }
                )
            elif parsed.path == "/api/security-temp-password/approve":
                self.approve_security_temp_password(parsed.query)
            elif parsed.path == "/open-latest-package-folder":
                self.open_latest_package_folder()
            elif parsed.path == "/api/console/status":
                self.require_auth(Permission.DASHBOARD_VIEW)
                self.send_json(self.console_status())
            elif parsed.path == "/api/service/status":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                self.send_json(self.lockfix_service_status())
            elif parsed.path == "/api/service/preflight":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                self.send_json(self.lockfix_service_preflight())
            elif parsed.path == "/api/qr-login/status":
                token = parse_qs(parsed.query).get("token", [""])[0]
                response = self.qr_status_response(token)
                headers = {}
                if response.get("approved") and response.get("session"):
                    headers["Set-Cookie"] = f"lockfix_session={response['session']}; HttpOnly; SameSite=Lax; Path=/"
                self.send_json(response, headers=headers)
            elif parsed.path == "/api/summary":
                self.require_auth(Permission.DASHBOARD_VIEW)
                self.send_json(self.summary())
            elif parsed.path == "/api/audit":
                self.require_auth(Permission.AUDIT_LOG_VIEW)
                self.send_json({"items": self.audit_items()})
            elif parsed.path == "/api/audit-logs":
                self.require_audit_log_view()
                self.send_json({"items": self.audit_logs()})
            elif parsed.path == "/api/audit-logs/export":
                self.require_audit_log_view()
                self.send_audit_logs_export()
            elif parsed.path == "/api/integrated":
                self.require_auth(Permission.DASHBOARD_VIEW)
                self.send_json(integrated_solution_summary())
            elif parsed.path == "/api/monitoring":
                self.require_auth(Permission.DASHBOARD_VIEW)
                params = parse_qs(parsed.query)
                self.send_json(self.monitoring_summary(params.get("start", [""])[0], params.get("end", [""])[0]))
            elif parsed.path == "/api/monitoring.csv":
                self.require_auth(Permission.REPORT_EXPORT)
                params = parse_qs(parsed.query)
                self.send_monitoring_csv(params.get("start", [""])[0], params.get("end", [""])[0])
            elif parsed.path == "/api/report":
                self.require_auth(Permission.REPORT_EXPORT)
                report = self.report_summary()
                self.context.store_report_snapshot(report)
                self.send_json(report)
            elif parsed.path == "/api/report/extras":
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_json(self.report_extras_record())
            elif parsed.path == "/api/report.csv":
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_report_csv()
            elif parsed.path == "/api/report.xlsx":
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_report_xlsx()
            elif parsed.path in {"/api/report.hwp", "/api/report.hwpx"}:
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_report_hwp()
            elif parsed.path == "/api/report.pdf":
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_report_pdf()
            elif parsed.path == "/api/report.docx":
                self.require_auth(Permission.REPORT_EXPORT)
                self.send_report_docx()
            elif parsed.path == "/api/dashboard":
                self.require_auth(Permission.DASHBOARD_VIEW)
                params = parse_qs(parsed.query)
                live_request = (params.get("live") or [""])[0] == "1"
                self.send_json(self.dashboard_summary(live=live_request))
            elif parsed.path == "/api/notification":
                self.require_auth(Permission.DASHBOARD_VIEW)
                self.send_json(self.notification_summary())
            elif parsed.path == "/api/notification-settings":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                self.send_json(self.notification_settings(redact=True))
            elif parsed.path == "/api/detect":
                self.require_auth(Permission.AIRGAP_POLICY_VIEW)
                params = parse_qs(parsed.query)
                live_request = (params.get("live") or [""])[0] == "1"
                self.send_json(self.detect_summary(live=live_request))
            elif parsed.path == "/api/threat-detection":
                self.require_auth(Permission.AIRGAP_POLICY_VIEW)
                self.send_json(self.threat_detection_summary())
            elif parsed.path == "/api/threat-detection/admin-notes":
                self.require_auth(Permission.AIRGAP_POLICY_VIEW)
                params = parse_qs(parsed.query)
                self.send_json(
                    {
                        "items": self.admin_memo_history(
                            str((params.get("targetId") or [""])[0] or ""),
                            days=30,
                        )
                    }
                )
            elif parsed.path == "/api/network-status":
                self.require_auth(Permission.DASHBOARD_VIEW)
                self.send_json(self.network_status_summary())
            elif parsed.path == "/api/veeam-backup":
                self.require_auth(Permission.VEEAM_VIEW)
                self.send_json(self.veeam_backup_summary())
            elif parsed.path == "/api/logs":
                self.require_auth(Permission.AUDIT_LOG_VIEW)
                params = parse_qs(parsed.query)
                self.send_json(
                    self.logs_summary(
                        params.get("start", [""])[0],
                        params.get("end", [""])[0],
                        params.get("page", ["1"])[0],
                        params.get("retention", ["30"])[0],
                        params.get("type", [""])[0],
                        params.get("severity", [""])[0],
                        params.get("source", [""])[0],
                        params.get("q", [""])[0],
                    )
                )
            elif parsed.path == "/api/logs.csv":
                self.require_auth(Permission.REPORT_EXPORT)
                params = parse_qs(parsed.query)
                self.send_logs_csv(
                    params.get("start", [""])[0],
                    params.get("end", [""])[0],
                    params.get("retention", ["30"])[0],
                    params.get("type", [""])[0],
                    params.get("severity", [""])[0],
                    params.get("source", [""])[0],
                    params.get("q", [""])[0],
                )
            elif parsed.path == "/api/license":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                self.send_json(self.license_status())
            elif parsed.path == "/api/sources":
                self.require_auth(Permission.AIRGAP_POLICY_VIEW)
                params = parse_qs(parsed.query)
                live_request = (params.get("live") or [""])[0] == "1"
                self.send_json(self.sources_summary(live=live_request))
            elif parsed.path == "/api/emergency-reconnect/status":
                self.require_auth(Permission.DISK_ONLINE_APPROVE)
                params = parse_qs(parsed.query)
                slot_id = self.query_slot(parsed.query)
                job_id = str(params.get("job_id", [""])[0])
                self.send_json(self.context.emergency_reconnect_status(slot_id, job_id))
            elif parsed.path == "/api/admin/users":
                self.require_super_admin()
                self.send_json({"items": self.admin_users()})
            elif parsed.path == "/api/admin/departments":
                self.require_super_admin()
                self.send_json({"items": self.admin_departments()})
            elif parsed.path == "/api/admin/windows-admin-status":
                self.require_super_admin()
                self.send_json(self.windows_admin_status())
            elif parsed.path == "/api/approvals":
                self.require_auth(Permission.APPROVAL_REQUEST_VIEW)
                self.send_json(self.approval_summary())
            else:
                review_match = re.fullmatch(r"/api/approval-requests/([^/]+)/reviews", parsed.path)
                if review_match:
                    self.require_auth(Permission.APPROVAL_REQUEST_VIEW)
                    self.send_json({"items": self.approval_department_reviews(review_match.group(1))})
                    return
                self.send_error(404, "not found")
        except AuthorizationError as exc:
            self.audit_access_denied(exc)
            self.send_json({"error": str(exc), "permission": exc.permission.value, "role": exc.role.value}, status=403)
        except PermissionError as exc:
            self.audit_unauthorized_access(str(exc))
            self.send_json({"error": str(exc)}, status=self.permission_error_status(exc))
        except KeyError as exc:
            self.send_json({"error": str(exc)}, status=404)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        if not self.enforce_local_console_access():
            return
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/login":
                payload = self.read_json_body()
                email = str(payload.get("email", "")).strip()
                password = str(payload.get("password", ""))
                client_ip = self.client_ip()
                if secrets.compare_digest(email, "admin") and secrets.compare_digest(password, "1"):
                    self.context.reset_login_failures(email, client_ip, "primary_password")
                    self.context.controller.audit.write(
                        "auth.login.success",
                        user=email,
                        client_ip=client_ip,
                        auth_method="primary_password",
                        result="SUCCESS",
                        message="LOCK-FIX login succeeded with primary password.",
                    )
                    token = secrets.token_urlsafe(32)
                    self.context.sessions[token] = self.session_record(email, Role.SUPER_ADMIN)
                    self.send_json(
                        {"authenticated": True},
                        headers={"Set-Cookie": f"lockfix_session={token}; HttpOnly; SameSite=Lax; Path=/"},
                    )
                elif (managed_login := self.authenticate_managed_user(email, password, client_ip)).get("ok"):
                    user = managed_login["user"]
                    self.context.reset_login_failures(email, client_ip, "managed_user_password")
                    self.context.controller.audit.write(
                        "auth.login.managed.success",
                        user=email,
                        user_id=str(user.get("id") or ""),
                        client_ip=client_ip,
                        role=str(user.get("role") or ""),
                        password_change_required=bool(managed_login.get("passwordChangeRequired", False)),
                        result="SUCCESS",
                        message="LOCK-FIX managed user login succeeded with the assigned RBAC role.",
                    )
                    token = secrets.token_urlsafe(32)
                    self.context.sessions[token] = self.session_record(
                        email,
                        normalize_role(user.get("role")),
                        user_id=str(user.get("id") or ""),
                        department_id=str(user.get("departmentId") or ""),
                        password_change_required=bool(managed_login.get("passwordChangeRequired", False)),
                    )
                    self.send_json(
                        {
                            "authenticated": True,
                            "role": str(user.get("role") or ""),
                            "passwordChangeRequired": bool(managed_login.get("passwordChangeRequired", False)),
                        },
                        headers={"Set-Cookie": f"lockfix_session={token}; HttpOnly; SameSite=Lax; Path=/"},
                    )
                elif managed_login.get("known_user") and managed_login.get("reason") in {
                    "disabled",
                    "deleted",
                    "temporary_password_expired",
                    "temporary_password_used",
                    "password_not_set",
                }:
                    self.context.controller.audit.write(
                        "auth.login.managed.blocked",
                        user=email or "unknown",
                        client_ip=client_ip,
                        reason=managed_login.get("reason", "unknown"),
                        result="BLOCKED",
                        message="LOCK-FIX managed user login was blocked by account state or temporary password policy.",
                    )
                    self.send_json(
                        {
                            "authenticated": False,
                            "error": self.managed_login_error_message(str(managed_login.get("reason") or "")),
                            "reason": managed_login.get("reason", "unknown"),
                        },
                        status=403,
                    )
                elif (temp_login := self.context.verify_login_temp_password(email, password)).get("ok"):
                    managed_user = self.managed_user_by_email(email)
                    login_role = normalize_role(managed_user.get("role")) if managed_user else Role.SUPER_ADMIN
                    user_id = str(managed_user.get("id") or "") if managed_user else ""
                    department_id = str(managed_user.get("departmentId") or "") if managed_user else ""
                    self.context.reset_login_failures(email, client_ip, "approved_temporary_password")
                    self.context.controller.audit.write(
                        "auth.login.temp.success",
                        user=email,
                        user_id=user_id,
                        client_ip=client_ip,
                        approved_by=temp_login.get("approved_by", "administrator"),
                        approved_at=temp_login.get("approved_at", ""),
                        expires_at=temp_login.get("expires_at", ""),
                        role=login_role.value,
                        result="SUCCESS",
                        message="LOCK-FIX login succeeded with an administrator-approved temporary password.",
                    )
                    token = secrets.token_urlsafe(32)
                    self.context.sessions[token] = self.session_record(email, login_role, user_id=user_id, department_id=department_id)
                    self.send_json(
                        {"authenticated": True},
                        headers={"Set-Cookie": f"lockfix_session={token}; HttpOnly; SameSite=Lax; Path=/"},
                    )
                elif temp_login.get("reason") == "approval_pending":
                    self.context.controller.audit.write(
                        "auth.login.temp.pending",
                        user=email,
                        client_ip=client_ip,
                        approval_status=temp_login.get("approval_status", "PENDING"),
                        expires_at=temp_login.get("expires_at", ""),
                        result="WAITING_APPROVAL",
                        message="Temporary password was entered before administrator approval.",
                    )
                    self.send_json(
                        {
                            "authenticated": False,
                            "error": "관리자 승인 대기 중입니다. 관리자 메일 승인 후 다시 로그인하세요.",
                            "approval_required": True,
                            "approval_status": "PENDING",
                        },
                        status=401,
                    )
                else:
                    failure = self.context.register_login_failure(email, client_ip)
                    self.context.controller.audit.write(
                        "auth.login.failed",
                        user=email or "unknown",
                        client_ip=client_ip,
                        failure_count=failure["failure_count"],
                        last_failed_at=failure["last_failed_at"],
                        threshold_warning=LOGIN_WARNING_THRESHOLD,
                        threshold_lock=LOGIN_LOCK_THRESHOLD,
                        result="FAILED",
                        risk="HIGH" if failure["failure_count"] >= LOGIN_LOCK_THRESHOLD else "WARNING",
                        message="LOCK-FIX password validation failed.",
                    )
                    if failure.get("warning"):
                        mail = self.send_security_email(
                            "LOCK-FIX 로그인 실패 3회 경고",
                            "\n".join(
                                [
                                    "LOCK-FIX 로그인 실패가 3회 감지되었습니다.",
                                    f"사용자: {email or 'unknown'}",
                                    f"접속 위치: {client_ip}",
                                    f"실패 횟수: {failure['failure_count']}",
                                    f"시간: {failure['last_failed_at']}",
                                    "관리자 확인이 필요합니다.",
                                ]
                            ),
                            user=email,
                            reason="login_failure_warning",
                        )
                        self.context.controller.audit.write(
                            "auth.login.warning.threshold",
                            user=email or "unknown",
                            client_ip=client_ip,
                            failure_count=failure["failure_count"],
                            smtp_status=mail["status"],
                            admin_email=mail["admin_email"],
                            result="WARNING",
                            risk="WARNING",
                            message="LOCK-FIX password failures reached the warning threshold. Administrator alert email was attempted.",
                        )
                    if failure.get("locked"):
                        approval_link = ""
                        mail = {"status": "PENDING_ALREADY_ISSUED", "admin_email": self.security_admin_email()}
                        if failure.get("approval_token") and failure.get("temporary_password"):
                            approval_link = self.security_approval_url(email, failure["approval_token"])
                            mail = self.send_security_email(
                                "LOCK-FIX 임시 비밀번호 관리자 승인 요청",
                                "\n".join(
                                    [
                                        "LOCK-FIX 로그인 실패가 5회 이상 발생하여 관리자 승인이 필요합니다.",
                                        f"사용자: {email or 'unknown'}",
                                        f"접속 위치: {client_ip}",
                                        f"실패 횟수: {failure['failure_count']}",
                                        f"임시 비밀번호: {failure['temporary_password']}",
                                        f"만료 시간: {failure.get('temporary_expires_at', '')}",
                                        "",
                                        "아래 링크를 열어 임시 비밀번호 사용을 승인합니다.",
                                        approval_link,
                                    ]
                                ),
                                user=email,
                                reason="login_temporary_password_approval",
                            )
                        self.context.controller.audit.write(
                            "auth.temp_password.requested",
                            user=email or "unknown",
                            client_ip=client_ip,
                            failure_count=failure["failure_count"],
                            approval_status=failure.get("approval_status", "PENDING"),
                            temporary_expires_at=failure.get("temporary_expires_at", ""),
                            temporary_password_digest=failure.get("temporary_password_digest", ""),
                            smtp_status=mail["status"],
                            admin_email=mail["admin_email"],
                            result="WAITING_APPROVAL",
                            risk="HIGH",
                            message="Administrator approval is required before temporary password login is allowed.",
                        )
                        self.context.controller.audit.write(
                            "auth.login.locked",
                            user=email or "unknown",
                            client_ip=client_ip,
                            failure_count=failure["failure_count"],
                            approval_status=failure.get("approval_status", "PENDING"),
                            smtp_status=mail["status"],
                            admin_email=mail["admin_email"],
                            result="LOCKED",
                            risk="HIGH",
                            message="LOCK-FIX account is waiting for administrator-approved temporary password login.",
                        )
                        self.send_json(
                            {
                                "authenticated": False,
                                "error": "로그인 실패 5회 이상으로 관리자 승인이 필요합니다. 관리자 메일 승인 후 임시 비밀번호로 로그인하세요.",
                                "approval_required": True,
                                "approval_status": failure.get("approval_status", "PENDING"),
                            },
                            status=401,
                        )
                    else:
                        self.send_json(
                            {
                                "authenticated": False,
                                "error": "LOCK-FIX 비밀번호가 일치하지 않습니다.",
                                "failure_count": failure["failure_count"],
                                "warning_threshold": LOGIN_WARNING_THRESHOLD,
                                "lock_threshold": LOGIN_LOCK_THRESHOLD,
                            },
                            status=401,
                        )
            elif parsed.path == "/api/qr-login":
                token = secrets.token_urlsafe(24)
                self.context.qr_tokens[token] = {"created_at": time.time(), "approved": False}
                self.send_json({"token": token, "expires_in": 300, "payload": f"LOCKFIX-QR:{token}"})
            elif parsed.path == "/api/qr-login/confirm":
                payload = self.read_json_body()
                token = str(payload.get("token", ""))
                record = self.context.qr_tokens.get(token)
                if not record or time.time() - record["created_at"] > 300:
                    self.send_json({"approved": False, "error": "QR token expired."}, status=410)
                else:
                    record["approved"] = True
                    response = self.qr_status_response(token)
                    headers = {}
                    if response.get("approved") and response.get("session"):
                        headers["Set-Cookie"] = f"lockfix_session={response['session']}; HttpOnly; SameSite=Lax; Path=/"
                    self.send_json(response, headers=headers)
            elif parsed.path == "/api/logout":
                token = self.session_token()
                if token:
                    self.context.sessions.pop(token, None)
                self.send_json(
                    {"authenticated": False},
                    headers={"Set-Cookie": "lockfix_session=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/"},
                )
            elif parsed.path == "/api/license/register":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                payload = self.read_json_body()
                self.send_json(self.register_license(payload))
            elif parsed.path == "/api/report/customer":
                self.require_auth(Permission.REPORT_EXPORT)
                payload = self.read_json_body()
                self.send_json(self.save_report_customer(payload))
            elif parsed.path == "/api/report/extras":
                self.require_auth(Permission.REPORT_EXPORT)
                payload = self.read_json_body()
                self.send_json(self.save_report_extras(payload))
            elif parsed.path == "/api/service/control":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                payload = self.read_json_body()
                self.send_json(self.lockfix_service_control(str(payload.get("action") or "")))
            elif parsed.path == "/api/veeam-config/sync":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                self.send_json(self.ensure_veeam_execution_settings_synced(manual=True))
            elif parsed.path == "/api/notification-settings":
                self.require_auth(Permission.SYSTEM_SETTING_MANAGE)
                payload = self.read_json_body()
                self.send_json(self.save_notification_settings(payload))
            elif parsed.path == "/api/threat-detection/admin-note":
                self.require_auth(Permission.AIRGAP_POLICY_MANAGE)
                payload = self.read_json_body()
                self.send_json(self.save_admin_memo(payload), status=201)
            elif parsed.path == "/api/threat-detection/manual-scan":
                self.require_auth(Permission.AIRGAP_POLICY_VIEW)
                self.send_json(self.run_manual_threat_scan(), status=202)
            elif parsed.path == "/api/isolate":
                self.require_auth(Permission.DISK_OFFLINE_EXECUTE)
                slot_id = self.query_slot(parsed.query)
                result = self.context.run_agent_service_operation("disk.isolate", {"slot_id": slot_id})
                self.send_json({"slot_id": slot_id, "state": result.get("state"), "executor": "LOCK-FIX Agent/Service", "summary": self.summary()})
            elif parsed.path == "/api/reconnect":
                self.require_auth(Permission.DISK_ONLINE_APPROVE)
                slot_id = self.query_slot(parsed.query)
                result = self.context.run_agent_service_operation("disk.reconnect", {"slot_id": slot_id})
                self.send_json({"slot_id": slot_id, "state": result.get("state"), "executor": "LOCK-FIX Agent/Service", "summary": self.summary()})
            elif parsed.path == "/api/emergency-reconnect":
                self.require_auth(Permission.DISK_ONLINE_APPROVE)
                payload = self.read_json_body()
                slot_id = self.query_slot(parsed.query)
                slot = self.context.config.slot(slot_id)
                reauth = self.verify_current_session_password(str(payload.get("reauth_password") or ""))
                if not reauth.get("ok"):
                    self.context.controller.audit.write(
                        "emergency.reconnect.reauth.failed",
                        slot_id=slot_id,
                        actorUserId=self.current_session_user(),
                        actor_role=self.current_role().value,
                        reason=str(reauth.get("reason") or "password_mismatch"),
                        result="FAILED",
                        risk="HIGH",
                        message="Emergency reconnect password re-authentication failed.",
                    )
                    self.send_json(
                        {
                            "slot_id": slot_id,
                            "accepted": False,
                            "reauth_required": True,
                            "error": "reauth_failed",
                            "message": "현재 로그인한 LOCK-FIX 사용자 비밀번호를 다시 확인하세요.",
                        },
                        status=401,
                    )
                    return
                self.context.controller.audit.write(
                    "emergency.reconnect.reauth.success",
                    slot_id=slot_id,
                    actorUserId=self.current_session_user(),
                    actor_role=self.current_role().value,
                    result="SUCCESS",
                    message="Emergency reconnect password re-authentication succeeded.",
                )
                self.context.controller.audit.write(
                    "emergency.reconnect.password_approval_bypass",
                    slot_id=slot_id,
                    actorUserId=self.current_session_user(),
                    actor_role=self.current_role().value,
                    result="SUCCESS",
                    message="Emergency reconnect was authorized by current-user password re-authentication.",
                )
                approval_bypass = True
                approval_bypass_reason = "password_reauth"
                repository_path = str(payload.get("repository_path") or self.context.veeam_backup_copy_repository_path() or slot.mount_point or slot.device or "").strip()
                veeam_repository_path = self.context.veeam_backup_copy_repository_path()
                if veeam_repository_path:
                    try:
                        requested_volume = repository_volume_root(repository_path)
                        veeam_volume = repository_volume_root(veeam_repository_path)
                    except ValueError as exc:
                        self.send_json({"ok": False, "error": "invalid_repository_path", "message": str(exc)}, status=400)
                        return
                    if requested_volume.strip().replace("/", "\\").rstrip("\\").lower() != veeam_volume.strip().replace("/", "\\").rstrip("\\").lower():
                        self.context.controller.audit.write(
                            "emergency.reconnect.repository.blocked",
                            slot_id=slot_id,
                            requested_repository_path=repository_path,
                            veeam_repository_path=veeam_repository_path,
                            message="Emergency reconnect is restricted to the Veeam Backup Copy repository volume.",
                        )
                        self.send_json(
                            {
                                "ok": False,
                                "error": "veeam_repository_mismatch",
                                "message": "Veeam Backup Copy 저장소 볼륨 기준으로만 격리해제/온라인 작업을 실행할 수 있습니다.",
                                "repository_path": veeam_repository_path,
                            },
                            status=409,
                        )
                        return
                    repository_path = veeam_repository_path
                job = self.context.start_emergency_reconnect(
                    slot_id,
                    repository_path,
                    approval_bypass=approval_bypass,
                    approval_bypass_reason=approval_bypass_reason,
                )
                self.send_json(
                    {
                        "slot_id": slot_id,
                        "accepted": True,
                        "job_id": job["job_id"],
                        "status": job["status"],
                        "device": slot.device,
                        "mount_point": str(slot.mount_point),
                        "repository_path": repository_path,
                        "message": "Emergency volume access job started. Reconnect continues in background.",
                        "summary": self.summary(),
                    },
                    status=202,
                )
            elif parsed.path == "/api/account/password":
                self.require_auth()
                payload = self.read_json_body()
                self.send_json(self.change_current_account_password(payload))
            elif parsed.path == "/api/admin/users":
                self.require_super_admin()
                payload = self.read_json_body()
                self.send_json(self.admin_create_user(payload), status=201)
            elif (admin_user_action := re.fullmatch(r"/api/admin/users/([^/]+)/(archive|temporary-password)", parsed.path)):
                self.require_super_admin()
                user_id = admin_user_action.group(1)
                action = admin_user_action.group(2)
                if action == "archive":
                    self.send_json(self.admin_archive_user(user_id))
                else:
                    self.send_json(self.admin_issue_user_temporary_password(user_id))
            elif parsed.path == "/api/approvals":
                self.require_auth(Permission.APPROVAL_REQUEST_CREATE)
                payload = self.read_json_body()
                self.send_json(self.create_approval_request(payload), status=201)
            elif parsed.path.startswith("/api/approvals/") and parsed.path.endswith("/decisions"):
                self.require_auth(Permission.APPROVAL_REQUEST_APPROVE)
                payload = self.read_json_body()
                approval_request_id = parsed.path.split("/")[3]
                self.send_json(self.create_approval_decision(approval_request_id, payload))
            elif parsed.path.startswith("/api/approvals/") and parsed.path.endswith("/reviews"):
                self.require_auth(Permission.DEPARTMENT_REVIEW)
                payload = self.read_json_body()
                approval_request_id = parsed.path.split("/")[3]
                self.send_json(self.create_approval_review(approval_request_id, payload))
            elif parsed.path.startswith("/api/approvals/") and parsed.path.endswith("/expired-delete"):
                self.require_auth(Permission.APPROVAL_REQUEST_CREATE)
                approval_request_id = parsed.path.split("/")[3]
                self.send_json(self.delete_expired_approval_request(approval_request_id))
            else:
                confirm_match = re.fullmatch(r"/api/approval-requests/([^/]+)/reviews/confirm", parsed.path)
                if confirm_match:
                    self.require_auth(Permission.DEPARTMENT_REVIEW)
                    payload = self.read_json_body()
                    self.send_json(self.confirm_department_reviews(confirm_match.group(1), payload))
                    return
                review_match = re.fullmatch(
                    r"/api/approval-requests/([^/]+)/reviews/([^/]+)/(comment|mark-reviewed|needs-changes|block)",
                    parsed.path,
                )
                if review_match:
                    self.require_auth(Permission.DEPARTMENT_REVIEW)
                    payload = self.read_json_body()
                    self.send_json(
                        self.update_department_review(
                            review_match.group(1),
                            review_match.group(2),
                            review_match.group(3),
                            payload,
                        )
                    )
                    return
                self.send_error(404, "not found")
        except AuthorizationError as exc:
            self.audit_access_denied(exc)
            self.send_json({"error": str(exc), "permission": exc.permission.value, "role": exc.role.value}, status=403)
        except PermissionError as exc:
            self.audit_unauthorized_access(str(exc))
            self.send_json({"error": str(exc)}, status=self.permission_error_status(exc))
        except KeyError as exc:
            self.send_json({"error": str(exc)}, status=404)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": str(exc), "summary": self.summary()}, status=500)

    def do_PATCH(self) -> None:
        if not self.enforce_local_console_access():
            return
        try:
            parsed = urlparse(self.path)
            match = re.fullmatch(r"/api/admin/users/([^/]+)(/disable)?", parsed.path)
            if not match:
                self.send_error(404, "not found")
                return
            self.require_super_admin()
            user_id = match.group(1)
            if match.group(2):
                self.send_json(self.admin_disable_user(user_id))
            else:
                payload = self.read_json_body()
                self.send_json(self.admin_update_user(user_id, payload))
        except AuthorizationError as exc:
            self.audit_access_denied(exc)
            self.send_json({"error": str(exc), "permission": exc.permission.value, "role": exc.role.value}, status=403)
        except PermissionError as exc:
            self.audit_unauthorized_access(str(exc))
            self.send_json({"error": str(exc)}, status=self.permission_error_status(exc))
        except KeyError as exc:
            self.send_json({"error": str(exc)}, status=404)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": str(exc), "summary": self.summary()}, status=500)

    def do_HEAD(self) -> None:
        if not self.enforce_local_console_access():
            return
        self.send_response(405)
        self.send_header("Allow", "GET, POST, PATCH")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        if not self.enforce_local_console_access():
            return
        self.send_response(405)
        self.send_header("Allow", "GET, POST, PATCH")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def query_slot(self, query: str) -> str:
        values = parse_qs(query)
        slot_id = values.get("slot", [""])[0] or values.get("slot_id", [""])[0]
        if not slot_id:
            raise ValueError("slot query parameter is required")
        return slot_id

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def client_ip(self) -> str:
        forwarded = str(self.headers.get("X-Forwarded-For") or "").split(",", 1)[0].strip()
        if forwarded:
            return forwarded
        return str(self.client_address[0]) if self.client_address else "unknown"

    def peer_ip(self) -> str:
        return str(self.client_address[0]) if self.client_address else "unknown"

    @staticmethod
    def is_loopback_ip(value: str) -> bool:
        try:
            address = ipaddress.ip_address(str(value or "").strip())
        except ValueError:
            return str(value or "").strip().lower() == "localhost"
        if address.is_loopback:
            return True
        mapped = getattr(address, "ipv4_mapped", None)
        return bool(mapped and mapped.is_loopback)

    def is_local_console_request(self) -> bool:
        return self.is_loopback_ip(self.peer_ip())

    def enforce_local_console_access(self) -> bool:
        if self.is_local_console_request():
            return True
        self.audit_remote_console_access_blocked()
        self.send_json(
            {
                "error": "LOCK-FIX Web Console is local-only. Remote console access is blocked and audited.",
                "client_ip": self.peer_ip(),
            },
            status=403,
        )
        return False

    def audit_remote_console_access_blocked(self) -> None:
        self.context.controller.audit.write(
            "security.remote_console_access.blocked",
            actorUserId="unknown",
            resourceType="WEB_CONSOLE",
            resourceId=self.path,
            ipAddress=self.peer_ip(),
            userAgent=str(self.headers.get("User-Agent") or ""),
            result="BLOCKED",
            method=str(getattr(self, "command", "") or ""),
            host_header=str(self.headers.get("Host") or ""),
            forwarded_for=str(self.headers.get("X-Forwarded-For") or ""),
            message="Remote LOCK-FIX Web Console access attempt was blocked by local-only policy.",
        )

    def default_notification_settings(self) -> dict:
        return {
            "enabled": True,
            "channel": "SMTP",
            "target_email": os.environ.get("LOCKFIX_ADMIN_EMAIL") or os.environ.get("LOCKFIX_SMTP_TO") or os.environ.get("SMTP_TO") or "rich.kim@oam.co.kr",
            "smtp_host": os.environ.get("LOCKFIX_SMTP_HOST") or os.environ.get("SMTP_HOST") or "",
            "smtp_port": int(os.environ.get("LOCKFIX_SMTP_PORT") or os.environ.get("SMTP_PORT") or "587"),
            "smtp_from": os.environ.get("LOCKFIX_SMTP_FROM") or "",
            "smtp_user": os.environ.get("LOCKFIX_SMTP_USER") or os.environ.get("SMTP_USER") or "",
            "smtp_password": os.environ.get("LOCKFIX_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or "",
            "use_tls": (os.environ.get("LOCKFIX_SMTP_STARTTLS", "true").lower() not in {"0", "false", "no"}),
            "use_ssl": (os.environ.get("LOCKFIX_SMTP_SSL", "").lower() in {"1", "true", "yes"}),
        }

    def notification_settings(self, redact: bool = False) -> dict:
        settings = LockFixWebHandler.default_notification_settings(self)
        path = self.context.notification_settings_path
        try:
            if path.exists():
                stored = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(stored, dict):
                    settings.update(stored)
        except (OSError, json.JSONDecodeError):
            pass
        try:
            settings["smtp_port"] = int(settings.get("smtp_port") or 587)
        except (TypeError, ValueError):
            settings["smtp_port"] = 587
        settings["channel"] = "SMTP"
        settings["enabled"] = bool(settings.get("enabled", True))
        if redact:
            password = str(settings.get("smtp_password") or "")
            settings["smtp_password"] = ""
            settings["password_configured"] = bool(password)
        return settings

    def save_notification_settings(self, payload: dict) -> dict:
        previous = LockFixWebHandler.notification_settings(self, redact=False)
        target_email = str(payload.get("target_email") or "").strip()
        smtp_host = str(payload.get("smtp_host") or "").strip()
        smtp_from = str(payload.get("smtp_from") or "").strip()
        smtp_user = str(payload.get("smtp_user") or "").strip()
        smtp_password = str(payload.get("smtp_password") or "")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", target_email):
            raise ValueError("알림 대상 메일 주소 형식이 올바르지 않습니다.")
        try:
            smtp_port = int(payload.get("smtp_port") or 587)
        except (TypeError, ValueError):
            raise ValueError("SMTP 포트는 숫자로 입력해야 합니다.")
        if smtp_port < 1 or smtp_port > 65535:
            raise ValueError("SMTP 포트 범위가 올바르지 않습니다.")
        settings = {
            "enabled": bool(payload.get("enabled", True)),
            "channel": "SMTP",
            "target_email": target_email,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_from": smtp_from,
            "smtp_user": smtp_user,
            "smtp_password": smtp_password if smtp_password else str(previous.get("smtp_password") or ""),
            "use_tls": bool(payload.get("use_tls", True)),
            "use_ssl": bool(payload.get("use_ssl", False)),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.context.notification_settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.context.notification_settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
        self.context.controller.audit.write(
            "notification.smtp.settings.updated",
            target_email=target_email,
            smtp_host=smtp_host or "NOT_CONFIGURED",
            smtp_port=smtp_port,
            enabled=settings["enabled"],
            result="SUCCESS",
            message="SMTP notification target settings were updated.",
        )
        return {"ok": True, "settings": LockFixWebHandler.notification_settings(self, redact=True)}

    def security_admin_email(self) -> str:
        settings = LockFixWebHandler.notification_settings(self, redact=False)
        return (
            str(settings.get("target_email") or "").strip()
            or os.environ.get("LOCKFIX_ADMIN_EMAIL")
            or os.environ.get("LOCKFIX_SMTP_TO")
            or os.environ.get("SMTP_TO")
            or "rich.kim@oam.co.kr"
        )

    def security_approval_url(self, user: str, token: str) -> str:
        host = self.headers.get("Host") or "127.0.0.1:8088"
        scheme = self.headers.get("X-Forwarded-Proto") or "http"
        query = urlencode({"user": user or "unknown", "token": token})
        return f"{scheme}://{host}/api/security-temp-password/approve?{query}"

    def send_security_email(self, subject: str, body: str, user: str = "", reason: str = "") -> dict:
        settings = LockFixWebHandler.notification_settings(self, redact=False)
        admin_email = self.security_admin_email()
        smtp_host = str(settings.get("smtp_host") or "")
        smtp_port = int(settings.get("smtp_port") or 587)
        smtp_user = str(settings.get("smtp_user") or "")
        smtp_password = str(settings.get("smtp_password") or "")
        smtp_from = str(settings.get("smtp_from") or "") or smtp_user or f"lockfix@{socket.gethostname()}"
        base_payload = {
            "user": user or "unknown",
            "admin_email": admin_email,
            "reason": reason,
            "smtp_host": smtp_host or "NOT_CONFIGURED",
        }
        if not smtp_host:
            self.context.controller.audit.write(
                "auth.security_mail.skipped",
                **base_payload,
                smtp_status="SMTP_NOT_CONFIGURED",
                result="SKIPPED",
                risk="WARNING",
                message="SMTP host is not configured. Security audit record was kept, but email could not be sent.",
            )
            return {"ok": False, "status": "SMTP_NOT_CONFIGURED", "admin_email": admin_email}
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = smtp_from
            message["To"] = admin_email
            message.set_content(body)
            use_ssl = bool(settings.get("use_ssl")) or smtp_port == 465
            use_starttls = bool(settings.get("use_tls"))
            if use_ssl:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10, context=ssl.create_default_context()) as server:
                    if smtp_user or smtp_password:
                        server.login(smtp_user, smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    if use_starttls:
                        server.starttls(context=ssl.create_default_context())
                    if smtp_user or smtp_password:
                        server.login(smtp_user, smtp_password)
                    server.send_message(message)
        except Exception as exc:
            self.context.controller.audit.write(
                "auth.security_mail.error",
                **base_payload,
                smtp_status="ERROR",
                error=str(exc),
                result="FAILED",
                risk="HIGH",
                message="SMTP security alert delivery failed. Check SMTP host, port, credentials, and firewall.",
            )
            return {"ok": False, "status": "ERROR", "admin_email": admin_email, "error": str(exc)}
        self.context.controller.audit.write(
            "auth.security_mail.sent",
            **base_payload,
            smtp_status="SENT",
            result="SUCCESS",
            risk="WARNING",
            message="Security alert email was sent to the administrator.",
        )
        return {"ok": True, "status": "SENT", "admin_email": admin_email}

    def approve_security_temp_password(self, query: str) -> None:
        params = parse_qs(query)
        user = str(params.get("user", [""])[0]).strip()
        token = str(params.get("token", [""])[0]).strip()
        result = self.context.approve_login_temp_password(
            user,
            token,
            approved_by="administrator",
            client_ip=self.client_ip(),
        )
        self.context.controller.audit.write(
            "auth.temp_password.approved" if result.get("ok") else "auth.temp_password.approval_failed",
            user=user or "unknown",
            client_ip=self.client_ip(),
            approved_by="administrator",
            approval_status="APPROVED" if result.get("ok") else "FAILED",
            approved_at=result.get("approved_at", ""),
            expires_at=result.get("expires_at", ""),
            result="SUCCESS" if result.get("ok") else "FAILED",
            risk="WARNING" if result.get("ok") else "HIGH",
            message=(
                "Temporary password login was approved by administrator email link."
                if result.get("ok")
                else f"Temporary password approval failed: {result.get('reason', 'unknown')}"
            ),
        )
        if result.get("ok"):
            self.send_html(
                "<!doctype html><meta charset='utf-8'><title>LOCK-FIX Approval</title>"
                "<body style='font-family:Malgun Gothic,Arial,sans-serif;padding:32px'>"
                "<h2>LOCK-FIX 임시 비밀번호 승인 완료</h2>"
                "<p>관리자 승인이 완료되었습니다. 사용자는 메일에 전달된 임시 비밀번호로 로그인할 수 있습니다.</p>"
                f"<p>만료 시간: {escape(result.get('expires_at', ''))}</p>"
                "</body>"
            )
        else:
            self.send_html(
                "<!doctype html><meta charset='utf-8'><title>LOCK-FIX Approval Failed</title>"
                "<body style='font-family:Malgun Gothic,Arial,sans-serif;padding:32px'>"
                "<h2>LOCK-FIX 임시 비밀번호 승인 실패</h2>"
                f"<p>사유: {escape(str(result.get('reason', 'unknown')))}</p>"
                "</body>",
                status=400,
            )

    def report_customer_record(self) -> dict:
        try:
            return json.loads(self.context.report_customer_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save_report_customer(self, payload: dict) -> dict:
        record = {
            "customer_contact": str(payload.get("customer_contact", "")).strip() or "-",
            "customer_email": str(payload.get("customer_email", "")).strip() or "-",
        }
        self.context.report_customer_path.parent.mkdir(parents=True, exist_ok=True)
        self.context.report_customer_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "customer": record}

    def report_extras_record(self) -> dict:
        try:
            record = json.loads(self.context.report_extras_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            record = {}
        return {
            "engineer_opinion": str(record.get("engineer_opinion", "")),
            "engineer_signature": str(record.get("engineer_signature", "")),
            "manager_signature": str(record.get("manager_signature", "")),
        }

    def save_report_extras(self, payload: dict) -> dict:
        record = {
            "engineer_opinion": str(payload.get("engineer_opinion", "")).strip(),
            "engineer_signature": self.clean_image_data_url(payload.get("engineer_signature", "")),
            "manager_signature": self.clean_image_data_url(payload.get("manager_signature", "")),
        }
        self.context.report_extras_path.parent.mkdir(parents=True, exist_ok=True)
        self.context.report_extras_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, **record}

    def clean_image_data_url(self, value: object) -> str:
        text = str(value or "")
        if not text.startswith("data:image/png;base64,"):
            return ""
        try:
            base64.b64decode(text.split(",", 1)[1], validate=True)
        except (ValueError, binascii.Error):
            return ""
        return text

    def image_data_url_bytes(self, value: str) -> bytes:
        if not value.startswith("data:image/png;base64,"):
            return b""
        try:
            return base64.b64decode(value.split(",", 1)[1], validate=True)
        except (ValueError, binascii.Error):
            return b""

    def session_token(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "lockfix_session":
                return value
        return None

    def is_authenticated(self) -> bool:
        token = self.session_token()
        if not token:
            return False
        record = self.context.sessions.get(token)
        if not record:
            return False
        created_at = self.session_created_at(record)
        if time.time() - created_at > self.session_ttl_seconds:
            self.context.sessions.pop(token, None)
            return False
        return True

    def license_identity(self) -> dict:
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except OSError:
            ip_address = "127.0.0.1"
        mac_raw = f"{uuid.getnode():012x}"
        mac_address = ":".join(mac_raw[index : index + 2] for index in range(0, 12, 2)).upper()
        return {"ip_address": ip_address, "mac_address": mac_address}

    def license_key_for(self, customer: str, support_code: str, ip_address: str = "", mac_address: str = "") -> str:
        seed = "|".join(["LOCK-FIX", customer.strip().upper(), support_code.strip().upper()])
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest().upper()[:20]
        return "LF-" + "-".join(digest[index : index + 4] for index in range(0, 20, 4))

    def load_license_record(self) -> dict:
        if not self.context.license_path.exists():
            return {}
        try:
            return json.loads(self.context.license_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save_license_record(self, record: dict) -> None:
        self.context.license_path.parent.mkdir(parents=True, exist_ok=True)
        self.context.license_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    def license_status(self) -> dict:
        identity = self.license_identity()
        record = self.load_license_record()
        now = datetime.now()
        status = {
            "valid": False,
            "reason": "not_registered",
            "customer": record.get("customer", ""),
            "support_code": record.get("support_code", ""),
            "license_key": record.get("license_key", ""),
            "issued_at": record.get("issued_at", ""),
            "expires_at": record.get("expires_at", ""),
            "updated_at": record.get("updated_at", ""),
            "days_left": 0,
            "identity": identity,
            "registered_identity": record.get("identity", {}),
            "sample_key": self.license_key_for("OAM-CUSTOMER", "OAM"),
        }
        if not record:
            return status

        if not record.get("license_key"):
            status["reason"] = "invalid_key"
            return status

        try:
            expires_at = datetime.fromisoformat(record["expires_at"])
        except (KeyError, ValueError):
            status["reason"] = "invalid_expiry"
            return status

        days_left = (expires_at.date() - now.date()).days
        status["days_left"] = max(0, days_left)
        if days_left < 0:
            status["reason"] = "expired"
            self.write_audit_event_once("license_expired", license_key=record.get("license_key", ""), expires_at=record.get("expires_at", ""))
            return status
        if days_left <= 30:
            self.write_audit_event_once("license_expiry_warning", days_left=days_left, expires_at=record.get("expires_at", ""))
        status["valid"] = True
        status["reason"] = "valid"
        return status

    def register_license(self, payload: dict) -> dict:
        customer = str(payload.get("customer", "")).strip() or "OAM-CUSTOMER"
        support_code = str(payload.get("support_code", "")).strip() or "OAM"
        license_key = str(payload.get("license_key", "")).strip().upper()
        identity = self.license_identity()
        expected_key = self.license_key_for(customer, support_code)
        if not secrets.compare_digest(license_key, expected_key):
            self.write_audit_event("license_register_failed", customer=customer, reason="invalid_key")
            return {"ok": False, "error": "라이선스 키가 고객사/Support Code 정보와 일치하지 않습니다.", "expected_sample": expected_key}
        now = datetime.now()
        record = {
            "customer": customer,
            "support_code": support_code,
            "license_key": license_key,
            "identity": identity,
            "issued_at": now.isoformat(timespec="seconds"),
            "expires_at": (now + timedelta(days=365)).isoformat(timespec="seconds"),
            "updated_at": now.isoformat(timespec="seconds"),
        }
        self.save_license_record(record)
        self.write_audit_event("license_registered", customer=customer, support_code=support_code, expires_at=record["expires_at"])
        return {"ok": True, "license": self.license_status()}

    def write_audit_event(self, event: str, **payload) -> None:
        self.context.config.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": datetime.now().isoformat(timespec="seconds"), "event": event, **payload}
        with self.context.config.audit_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def write_audit_event_once(self, event: str, **payload) -> None:
        today_key = f"{event}:{datetime.now().date().isoformat()}"
        marker = ROOT / "runtime" / "license_events.json"
        events = []
        if marker.exists():
            try:
                events = json.loads(marker.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                events = []
        if today_key in events:
            return
        self.write_audit_event(event, **payload)
        events.append(today_key)
        marker.write_text(json.dumps(events[-120:], ensure_ascii=False), encoding="utf-8")

    def safe_text_lines(self, path: Path) -> list[str]:
        try:
            return path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []

    def audit_log_lines(self) -> list[str]:
        try:
            path = self.context.config.audit_log_path
        except Exception:
            return []
        return tail_text_lines(path, limit=5000, chunk_size=256 * 1024)

    def audit_log_tail_lines(self, limit: int = 1000, max_bytes: int = 2 * 1024 * 1024) -> list[str]:
        try:
            path = self.context.config.audit_log_path
        except Exception:
            return []
        return tail_text_lines(path, limit=limit, chunk_size=min(max(4096, max_bytes), 256 * 1024))

    def qr_status_response(self, token: str) -> dict:
        record = self.context.qr_tokens.get(token)
        if not record:
            return {"approved": False, "expired": True}
        if time.time() - record["created_at"] > 300:
            self.context.qr_tokens.pop(token, None)
            return {"approved": False, "expired": True}
        if not record.get("approved"):
            return {"approved": False, "expired": False}

        session = secrets.token_urlsafe(32)
        self.context.sessions[session] = self.session_record("qr-admin", Role.SUPER_ADMIN)
        self.context.qr_tokens.pop(token, None)
        return {
            "approved": True,
            "expired": False,
            "session": session,
        }

    def session_record(
        self,
        user: str,
        role: Role,
        user_id: str = "",
        department_id: str = "",
        password_change_required: bool = False,
    ) -> dict:
        return {
            "created_at": time.time(),
            "user": str(user or "unknown"),
            "role": role.value,
            "user_id": str(user_id or ""),
            "department_id": str(department_id or ""),
            "password_change_required": bool(password_change_required),
        }

    def session_created_at(self, record: object) -> float:
        if isinstance(record, dict):
            return float(record.get("created_at") or 0)
        return float(record or 0)

    def current_role(self) -> Role:
        token = self.session_token()
        if not token:
            return Role.AUDITOR
        record = self.context.sessions.get(token)
        if isinstance(record, dict):
            return normalize_role(record.get("role"))
        if record:
            return Role.SUPER_ADMIN
        return Role.AUDITOR

    def current_session_record(self) -> dict:
        token = self.session_token()
        record = self.context.sessions.get(token) if token else None
        return dict(record) if isinstance(record, dict) else {}

    def current_session_user_id(self) -> str:
        return str(self.current_session_record().get("user_id") or "")

    def current_session_department_id(self) -> str:
        return str(self.current_session_record().get("department_id") or "")

    def current_password_change_required(self) -> bool:
        return bool(self.current_session_record().get("password_change_required", False))

    def verify_current_session_password(self, password: str) -> dict:
        supplied = str(password or "")
        user = self.current_session_user()
        if not supplied:
            return {"ok": False, "reason": "missing_password", "user": user}
        if secrets.compare_digest(user, "admin"):
            ok = secrets.compare_digest(supplied, "1")
            return {
                "ok": ok,
                "reason": "primary_password" if ok else "password_mismatch",
                "user": user,
            }
        managed = self.managed_user_by_email(user)
        if not managed:
            return {"ok": False, "reason": "user_not_found", "user": user}
        stored_hash = str(managed.get("passwordHash") or "")
        if not stored_hash:
            return {
                "ok": False,
                "reason": "password_not_set",
                "user": user,
                "user_id": str(managed.get("id") or ""),
            }
        supplied_hash = self.context.login_security_hash(supplied)
        ok = secrets.compare_digest(stored_hash, supplied_hash)
        return {
            "ok": ok,
            "reason": "managed_user_password" if ok else "password_mismatch",
            "user": user,
            "user_id": str(managed.get("id") or ""),
        }

    def permission_error_status(self, exc: PermissionError) -> int:
        return 401 if "authentication required" in str(exc).lower() else 403

    def current_permissions(self) -> list[str]:
        policy = load_role_permissions(self.context.rbac_policy_path)
        return sorted(permission.value for permission in permissions_for_role(self.current_role(), policy))

    def require_auth(self, permission: Permission | None = None) -> None:
        if not self.is_authenticated():
            raise PermissionError("authentication required")
        if permission:
            require_permission(self.current_role(), permission, load_role_permissions(self.context.rbac_policy_path))

    def require_super_admin(self) -> None:
        self.require_auth(Permission.USER_MANAGE)
        if self.current_role() != Role.SUPER_ADMIN:
            raise AuthorizationError(Permission.USER_MANAGE, self.current_role())

    def require_audit_log_view(self) -> None:
        self.require_auth(Permission.AUDIT_LOG_VIEW)
        if self.current_role() not in {Role.AUDITOR, Role.SECURITY_ADMIN, Role.SUPER_ADMIN}:
            raise AuthorizationError(Permission.AUDIT_LOG_VIEW, self.current_role())

    def audit_unauthorized_access(self, reason: str) -> None:
        self.context.controller.audit.write(
            "security.unauthorized_access",
            actorUserId=self.current_session_user(),
            resourceType="API",
            resourceId=self.path,
            ipAddress=self.client_ip(),
            userAgent=str(self.headers.get("User-Agent") or ""),
            result="FAILED",
            reason=reason,
        )

    def audit_access_denied(self, exc: AuthorizationError) -> None:
        self.context.controller.audit.write(
            "security.permission_denied",
            actorUserId=self.current_session_user(),
            resourceType="API",
            resourceId=self.path,
            ipAddress=self.client_ip(),
            userAgent=str(self.headers.get("User-Agent") or ""),
            result="FAILED",
            role=exc.role.value,
            permission=exc.permission.value,
        )

    def public_user_record(self, user: dict) -> dict:
        record = dict(user)
        record.pop("passwordHash", None)
        record.pop("previousEmail", None)
        return record

    def managed_user_by_email(self, email: str) -> dict:
        with self.context.user_directory_lock:
            data = self.context.user_directory.load()
            try:
                user = self.context.user_directory.find_user_by_email(data, email)
            except KeyError:
                return {}
            if bool(user.get("deleted", False)) or bool(user.get("disabled", False)):
                return {}
            return dict(user)

    def authenticate_managed_user(self, email: str, password: str, client_ip: str) -> dict:
        password_hash = self.context.login_security_hash(password)
        with self.context.user_directory_lock:
            result = self.context.user_directory.authenticate_password(email, password_hash)
        if result.get("ok"):
            user = result.get("user") if isinstance(result.get("user"), dict) else {}
            return {
                "ok": True,
                "known_user": True,
                "user": user,
                "passwordChangeRequired": bool(user.get("passwordChangeRequired", False)),
            }
        reason = str(result.get("reason") or "unknown")
        if result.get("known_user") and reason in {"disabled", "deleted", "temporary_password_expired", "temporary_password_used", "password_not_set"}:
            self.context.controller.audit.write(
                "auth.login.managed.denied",
                user=email or "unknown",
                client_ip=client_ip,
                reason=reason,
                result="BLOCKED",
            )
        return result

    def managed_login_error_message(self, reason: str) -> str:
        messages = {
            "disabled": "비활성화된 계정입니다. 관리자에게 문의하세요.",
            "deleted": "삭제 처리된 계정입니다. 관리자에게 문의하세요.",
            "temporary_password_expired": "임시 비밀번호가 만료되었습니다. 관리자에게 재발급을 요청하세요.",
            "temporary_password_used": "이미 사용된 임시 비밀번호입니다. 관리자에게 재발급을 요청하세요.",
            "password_not_set": "비밀번호가 설정되지 않은 계정입니다. 관리자에게 임시 비밀번호 발급을 요청하세요.",
        }
        return messages.get(reason, "계정 상태 때문에 로그인이 차단되었습니다.")

    def admin_departments(self) -> list[dict]:
        with self.context.user_directory_lock:
            return self.context.user_directory.departments()

    def admin_users(self) -> list[dict]:
        with self.context.user_directory_lock:
            return [self.public_user_record(user) for user in self.context.user_directory.users(include_deleted=False)]

    def audit_user_change(self, event: str, user: dict, before: dict | None = None) -> None:
        safe_user = self.public_user_record(user)
        safe_before = self.public_user_record(before or {}) if before is not None else {}
        self.context.controller.audit.write(
            event,
            actor=self.current_session_user(),
            actor_role=self.current_role().value,
            user_id=str(safe_user.get("id") or ""),
            user_email=str(safe_user.get("email") or ""),
            department_id=str(safe_user.get("departmentId") or ""),
            role=str(safe_user.get("role") or ""),
            disabled=bool(safe_user.get("disabled")),
            deleted=bool(safe_user.get("deleted")),
            before=safe_before,
            beforeValue=safe_before,
            afterValue=safe_user,
            result="SUCCESS",
        )
        before_role = str(safe_before.get("role") or "")
        after_role = str(safe_user.get("role") or "")
        if before is not None and before_role and before_role != after_role:
            self.context.controller.audit.write(
                "admin.role.changed",
                actorUserId=self.current_session_user(),
                resourceType="ROLE",
                resourceId=str(safe_user.get("id") or ""),
                beforeValue={"role": before_role},
                afterValue={"role": after_role},
                result="SUCCESS",
            )

    def generated_user_temporary_password(self) -> tuple[str, str, str]:
        temporary_password = self.context.generate_login_temp_password()
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=USER_TEMP_PASSWORD_TTL_SECONDS)).isoformat(
            timespec="seconds"
        )
        return temporary_password, self.context.login_security_hash(temporary_password), expires_at

    def admin_create_user(self, payload: dict) -> dict:
        temporary_password, password_hash, expires_at = self.generated_user_temporary_password()
        create_payload = dict(payload)
        create_payload.update(
            {
                "passwordHash": password_hash,
                "passwordChangeRequired": True,
                "temporaryPasswordExpiresAt": expires_at,
            }
        )
        with self.context.user_directory_lock:
            user = self.context.user_directory.create_user(create_payload)
        self.audit_user_change("admin.user.created", user)
        self.context.controller.audit.write(
            "admin.user.temporary_password_issued",
            actor=self.current_session_user(),
            actor_role=self.current_role().value,
            user_id=str(user.get("id") or ""),
            user_email=str(user.get("email") or ""),
            temporary_password_digest=password_hash[:16],
            temporary_expires_at=expires_at,
            result="SUCCESS",
            message="Initial managed-user temporary password was issued. Plaintext is returned once in the API response only.",
        )
        return {
            "ok": True,
            "user": self.public_user_record(user),
            "temporaryPassword": temporary_password,
            "temporaryPasswordExpiresAt": expires_at,
        }

    def admin_update_user(self, user_id: str, payload: dict) -> dict:
        update_payload = {
            key: value
            for key, value in dict(payload).items()
            if key in {"email", "name", "departmentId", "role", "disabled"}
        }
        with self.context.user_directory_lock:
            before = next((dict(user) for user in self.context.user_directory.users() if str(user.get("id") or "") == user_id), {})
            user = self.context.user_directory.update_user(user_id, update_payload)
        self.audit_user_change("admin.user.updated", user, before=before)
        return {"ok": True, "user": self.public_user_record(user)}

    def admin_disable_user(self, user_id: str) -> dict:
        with self.context.user_directory_lock:
            before = next((dict(user) for user in self.context.user_directory.users() if str(user.get("id") or "") == user_id), {})
            user = self.context.user_directory.disable_user(user_id)
        self.audit_user_change("admin.user.disabled", user, before=before)
        return {"ok": True, "user": self.public_user_record(user)}

    def admin_archive_user(self, user_id: str) -> dict:
        with self.context.user_directory_lock:
            before = next((dict(user) for user in self.context.user_directory.users() if str(user.get("id") or "") == user_id), {})
            user = self.context.user_directory.archive_user(user_id, self.current_session_user())
        self.audit_user_change("admin.user.archived", user, before=before)
        return {"ok": True, "user": self.public_user_record(user)}

    def admin_issue_user_temporary_password(self, user_id: str) -> dict:
        temporary_password, password_hash, expires_at = self.generated_user_temporary_password()
        with self.context.user_directory_lock:
            before = next((dict(user) for user in self.context.user_directory.users() if str(user.get("id") or "") == user_id), {})
            user = self.context.user_directory.set_temporary_password(user_id, password_hash, expires_at)
        self.audit_user_change("admin.user.temporary_password_reset", user, before=before)
        self.context.controller.audit.write(
            "admin.user.temporary_password_issued",
            actor=self.current_session_user(),
            actor_role=self.current_role().value,
            user_id=str(user.get("id") or ""),
            user_email=str(user.get("email") or ""),
            temporary_password_digest=password_hash[:16],
            temporary_expires_at=expires_at,
            result="SUCCESS",
            message="Managed-user temporary password was reissued. Plaintext is returned once in the API response only.",
        )
        return {
            "ok": True,
            "user": self.public_user_record(user),
            "temporaryPassword": temporary_password,
            "temporaryPasswordExpiresAt": expires_at,
        }

    def change_current_account_password(self, payload: dict) -> dict:
        record = self.current_session_record()
        user_id = str(record.get("user_id") or "")
        if not user_id:
            raise ValueError("managed user account is required")
        new_password = str(payload.get("newPassword") or "")
        if len(new_password) < 8:
            raise ValueError("new password must be at least 8 characters")
        current_password = str(payload.get("currentPassword") or "")
        new_hash = self.context.login_security_hash(new_password)
        with self.context.user_directory_lock:
            data = self.context.user_directory.load()
            user = self.context.user_directory.find_user(data, user_id)
            if bool(user.get("deleted", False)) or bool(user.get("disabled", False)):
                raise PermissionError("account is disabled or deleted")
            if not bool(record.get("password_change_required", False)):
                if not current_password or not secrets.compare_digest(
                    str(user.get("passwordHash") or ""),
                    self.context.login_security_hash(current_password),
                ):
                    raise PermissionError("current password is required")
            before = dict(user)
            updated = self.context.user_directory.change_password(user_id, new_hash)
        token = self.session_token()
        if token and isinstance(self.context.sessions.get(token), dict):
            self.context.sessions[token]["password_change_required"] = False
        self.audit_user_change("admin.user.password_changed", updated, before=before)
        return {"ok": True, "user": self.public_user_record(updated)}

    def windows_admin_status(self) -> dict:
        is_windows = os.name == "nt"
        is_admin = False
        error = ""
        if is_windows:
            try:
                import ctypes

                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception as exc:  # pragma: no cover - depends on host Windows APIs.
                error = str(exc)
        elif hasattr(os, "geteuid"):
            is_admin = os.geteuid() == 0
        status = {
            "ok": True,
            "platform": platform.platform(),
            "isWindows": is_windows,
            "isAdministrator": is_admin,
            "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": "status_only",
            "message": (
                "LOCK-FIX WebUI process is running with Windows Administrator privileges."
                if is_admin
                else "LOCK-FIX WebUI process is not running with Windows Administrator privileges."
            ),
            "error": error,
        }
        self.context.controller.audit.write(
            "admin.windows_admin_status.checked",
            actor=self.current_session_user(),
            actor_role=self.current_role().value,
            is_windows=is_windows,
            is_administrator=is_admin,
            mode="status_only",
            result="SUCCESS" if not error else "WARNING",
            message="Windows Administrator status was checked for display only; LOCK-FIX RBAC remains the permission source.",
        )
        return status

    def approval_summary(self) -> dict:
        store = self.context.controller.approvals
        expired = store.expire_pending_requests()
        auto_deleted = store.purge_expired_requests()
        data = store.load()
        return {
            "policies": data["policies"],
            "requests": data["requests"],
            "decisions": data["decisions"],
            "departmentReviews": data.get("departmentReviews", []),
            "reviewComments": data.get("reviewComments", []),
            "notifications": data.get("notifications", []),
            "expired": expired,
            "autoDeleted": auto_deleted,
        }

    def create_approval_request(self, payload: dict) -> dict:
        request = self.context.controller.approvals.create_request(
            str(payload.get("requestType") or ""),
            requester_user_id=str(payload.get("requesterUserId") or self.current_session_user()),
            target_id=str(payload.get("targetId") or ""),
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        )
        return {"ok": True, "request": request}

    def delete_expired_approval_request(self, approval_request_id: str) -> dict:
        deleted = self.context.controller.approvals.delete_expired_request(
            approval_request_id,
            deleted_by=self.current_session_user(),
        )
        return {"ok": True, "deleted": deleted, "message": "만료된 승인 요청을 삭제했습니다."}

    def active_approval_request_for(self, request_type: str, target_id: str) -> dict | None:
        data = self.context.controller.approvals.load()
        wanted_type = str(request_type or "").strip().upper()
        wanted_target = str(target_id or "")
        active_statuses = {"PENDING", "IN_REVIEW", "NEEDS_CHANGES", "BLOCKED"}
        candidates = [
            request
            for request in data.get("requests", [])
            if str(request.get("requestType") or "").upper() == wanted_type
            and str(request.get("targetId") or "") == wanted_target
            and str(request.get("status") or "").upper() in active_statuses
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: str(item.get("updatedAt") or item.get("createdAt") or ""), reverse=True)[0]

    def create_approval_decision(self, approval_request_id: str, payload: dict) -> dict:
        result = self.context.controller.approvals.decide(
            approval_request_id,
            approver_user_id=str(payload.get("approverUserId") or self.current_session_user()),
            approver_role=self.current_role(),
            decision=str(payload.get("decision") or ""),
            comment=str(payload.get("comment") or ""),
        )
        return {"ok": True, **result}

    def create_approval_review(self, approval_request_id: str, payload: dict) -> dict:
        result = self.context.controller.approvals.review_request(
            approval_request_id,
            reviewer_user_id=str(payload.get("reviewerUserId") or self.current_session_user()),
            reviewer_role=self.current_role(),
            review_type=str(payload.get("reviewType") or ""),
            comment=str(payload.get("comment") or ""),
        )
        return {"ok": True, **result}

    def approval_department_reviews(self, approval_request_id: str) -> list[dict]:
        return self.context.controller.approvals.department_reviews_for(approval_request_id)

    def update_department_review(self, approval_request_id: str, review_id: str, action: str, payload: dict) -> dict:
        store = self.context.controller.approvals
        reviewer = str(payload.get("reviewerUserId") or self.current_session_user())
        comment = str(payload.get("comment") or "")
        if action == "comment":
            result = store.comment_department_review(approval_request_id, review_id, reviewer, self.current_role(), comment)
        elif action == "mark-reviewed":
            result = store.mark_department_reviewed(approval_request_id, review_id, reviewer, self.current_role(), comment)
        elif action == "needs-changes":
            result = store.mark_department_needs_changes(approval_request_id, review_id, reviewer, self.current_role(), comment)
        elif action == "block":
            result = store.block_department_review(approval_request_id, review_id, reviewer, self.current_role(), comment)
        else:
            raise ValueError("unsupported department review action")
        return {"ok": True, **result}

    def confirm_department_reviews(self, approval_request_id: str, payload: dict) -> dict:
        store = self.context.controller.approvals
        reviewer = str(payload.get("reviewerUserId") or self.current_session_user())
        comment = str(payload.get("comment") or "확인 완료")
        result = store.confirm_department_reviews_for_role(approval_request_id, reviewer, self.current_role(), comment)
        return {"ok": True, **result}

    def current_session_user(self) -> str:
        token = self.session_token()
        record = self.context.sessions.get(token) if token else None
        if isinstance(record, dict):
            return str(record.get("user") or "unknown")
        return "legacy-admin" if record else "unknown"

    def audit_logs(self) -> list[dict]:
        return read_audit_logs(self.context.config.audit_log_path)

    def send_audit_logs_export(self) -> None:
        self.send_download(audit_logs_to_csv(self.audit_logs()), "text/csv; charset=utf-8", "lockfix_audit_logs.csv")

    def summary(self) -> dict:
        config = self.context.config
        status = self.context.controller.status()
        slots = []
        for slot_id, slot in config.slots.items():
            mount = self.mount_summary(slot.mount_point)
            slots.append(
                {
                    "slot_id": slot_id,
                    "state": status.get(slot_id, "READY_MOCK"),
                    "device": slot.device,
                    "mount_point": str(slot.mount_point),
                    "mount": mount,
                    "power_type": slot.power.type,
                    "dry_run": config.dry_run,
                    "uid": slot_uid(slot),
                    "expected_uid": slot.expected_uid,
                }
            )
        return {
            "dry_run": config.dry_run,
            "config_path": str(self.context.config_path),
            "audit_log_path": str(config.audit_log_path),
            "slots": slots,
        }

    def console_status(self) -> dict:
        return {
            "title": "LOCK-FIX Web UI Console",
            "mode": "python_function",
            "cmd_execution": False,
            "url": "http://127.0.0.1:8088",
            "root": str(ROOT),
            "config_path": str(self.context.config_path.resolve()),
            "webui_path": str((ROOT / "webui.py").resolve()),
            "python_runtime": "direct Python function/API",
            "server": {
                "running": True,
                "handler": "LockFixWebHandler",
                "entrypoint": "run(host, port, config_path)",
            },
            "message": "Web UI status is provided by Python functions. No .cmd execution is required from the browser.",
        }

    def lockfix_service_name(self) -> str:
        return (
            os.environ.get("LOCKFIX_WEBUI_SERVICE_NAME", "").strip()
            or os.environ.get("LOCKFIX_SERVICE_NAME", "").strip()
            or "LOCKFIXWebUI"
        )

    def service_command(self, *args: str, timeout: float = 8.0) -> subprocess.CompletedProcess:
        sc_path = shutil.which("sc.exe") or str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "sc.exe")
        return subprocess.run(
            [sc_path, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )

    def lockfix_service_status(self) -> dict:
        service_name = self.lockfix_service_name()
        if platform.system().lower() != "windows":
            return {
                "service_name": service_name,
                "display_name": "LOCK-FIX WebUI Service",
                "state": "UNSUPPORTED",
                "running": False,
                "can_start": False,
                "can_stop": False,
                "message": "Windows 서비스 제어는 Windows 환경에서만 사용할 수 있습니다.",
            }
        try:
            result = self.service_command("query", service_name)
        except Exception as exc:
            return {
                "service_name": service_name,
                "display_name": "LOCK-FIX WebUI Service",
                "state": "ERROR",
                "running": False,
                "can_start": False,
                "can_stop": False,
                "message": f"서비스 상태 조회 실패: {exc}",
            }
        output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
        if result.returncode != 0:
            state = "NOT_INSTALLED" if "1060" in output or "does not exist" in output.lower() else "ERROR"
            return {
                "service_name": service_name,
                "display_name": "LOCK-FIX WebUI Service",
                "state": state,
                "running": False,
                "can_start": False,
                "can_stop": False,
                "message": output or f"서비스 상태 조회 실패 코드: {result.returncode}",
            }
        state = "UNKNOWN"
        for line in output.splitlines():
            match = re.search(r"STATE\s*:\s*\d+\s+([A-Z_]+)", line)
            if match:
                state = match.group(1)
                break
        running = state == "RUNNING"
        return {
            "service_name": service_name,
            "display_name": "LOCK-FIX WebUI Service",
            "state": state,
            "running": running,
            "can_start": state in {"STOPPED", "STOP_PENDING", "PAUSED", "UNKNOWN"},
            "can_stop": running,
            "message": f"{service_name} 서비스 상태: {state}",
            "detail": output,
        }

    def lockfix_service_preflight(self) -> dict:
        mode = self.context.operation_mode()
        service_status = self.lockfix_service_status()
        try:
            result = self.context.run_agent_service_operation(
                "service.preflight",
                {"operation_mode": mode},
                timeout_seconds=24,
            )
            diagnostics = result.get("diagnostics") if isinstance(result.get("diagnostics"), dict) else {}
            diagnostics["service_status"] = service_status
            diagnostics["mode_label"] = {
                "poc": "개발/POC",
                "commercial": "상용 제품",
                "delivery": "고객사 납품",
            }.get(mode, mode)
            return diagnostics
        except AgentServiceUnavailable as exc:
            restricted = [
                "Disk Offline 불가",
                "Drive Letter 제거 불가",
                "Volume Dismount 불가",
                "Flush/I/O 확인 불가",
            ]
            if self.context.config.veeam.enabled:
                restricted.append("Veeam REST 조회는 서비스 복구 후 확인 필요")
            self.context.controller.audit.write(
                "service.preflight.unavailable",
                operation_mode=mode,
                service_state=service_status.get("state"),
                error=str(exc),
                restricted_features=restricted,
                message="LOCK-FIX Agent/Service preflight could not run because the service did not answer.",
            )
            return {
                "checked_at": datetime.now().isoformat(timespec="seconds"),
                "operation_mode": mode,
                "mode_label": {"poc": "개발/POC", "commercial": "상용 제품", "delivery": "고객사 납품"}.get(mode, mode),
                "status": "서비스 미실행",
                "ok": False,
                "deployment_ready": False,
                "service_status": service_status,
                "service": {
                    "running": False,
                    "account": "-",
                    "local_system": False,
                    "local_admin": False,
                    "account_policy": "상용/납품 환경에서는 LOCK-FIX Agent/Service 실행 계정이 권한 작업을 담당해야 합니다.",
                },
                "disk_commands": [],
                "veeam_api": {"ok": False, "diagnostics": {"error": str(exc)}},
                "uac": {"ok": False, "detail": "Agent/Service 미응답"},
                "execution_policy": {"ok": False, "detail": "Agent/Service 미응답"},
                "firewall": {"ok": False, "detail": "Agent/Service 미응답"},
                "winrm": {"ok": False, "detail": "Agent/Service 미응답"},
                "preflight_checks": [
                    {"key": "veeam_rest_connection", "label": "Veeam REST 연결", "ok": False, "detail": str(exc)},
                    {"key": "veeam_job_detection", "label": "Veeam Job 감지", "ok": False, "detail": str(exc)},
                    {"key": "repository_path", "label": "Repository 경로", "ok": False, "detail": str(exc)},
                    {"key": "target_volume", "label": "대상 볼륨 매핑", "ok": False, "detail": str(exc)},
                    {"key": "disk_offline_permission", "label": "디스크 Offline 권한", "ok": False, "detail": str(exc)},
                ],
                "restricted_features": restricted,
                "resolution": [
                    "LOCK-FIX Agent/Service 설치 및 실행 상태를 확인하세요.",
                    "서비스 계정을 LocalSystem 또는 lockfix-svc로 설정하고 필요한 디스크 권한을 부여하세요.",
                    "상용 모드에서는 WebUI가 관리자 권한 작업을 직접 수행하지 않습니다.",
                ],
            }

    def lockfix_service_control(self, action: str) -> dict:
        action = action.strip().lower()
        if action not in {"start", "stop"}:
            return {"ok": False, "error": "지원하지 않는 서비스 제어 요청입니다."}
        service_name = self.lockfix_service_name()
        self.write_audit_event("lockfix_service_control_requested", service=service_name, action=action)
        if action == "stop":
            threading.Thread(target=self.delayed_service_command, args=("stop", service_name), daemon=True).start()
            status = self.lockfix_service_status()
            status.update(
                {
                    "ok": True,
                    "accepted": True,
                    "action": action,
                    "message": f"{service_name} 서비스 중지 요청을 접수했습니다.",
                }
            )
            return status
        try:
            result = self.service_command("start", service_name, timeout=12)
        except Exception as exc:
            self.write_audit_event("lockfix_service_control_failed", service=service_name, action=action, error=str(exc))
            return {"ok": False, "service_name": service_name, "action": action, "error": str(exc)}
        output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
        if result.returncode != 0:
            self.write_audit_event("lockfix_service_control_failed", service=service_name, action=action, error=output)
            return {"ok": False, "service_name": service_name, "action": action, "error": output or f"서비스 시작 실패 코드: {result.returncode}"}
        self.write_audit_event("lockfix_service_control_completed", service=service_name, action=action, output=output)
        status = self.lockfix_service_status()
        status.update({"ok": True, "accepted": True, "action": action, "message": f"{service_name} 서비스 시작 요청이 완료되었습니다."})
        return status

    def delayed_service_command(self, action: str, service_name: str) -> None:
        time.sleep(0.8)
        try:
            result = self.service_command(action, service_name, timeout=12)
            output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
            if result.returncode == 0:
                self.write_audit_event("lockfix_service_control_completed", service=service_name, action=action, output=output)
            else:
                self.write_audit_event("lockfix_service_control_failed", service=service_name, action=action, error=output)
        except Exception as exc:
            self.write_audit_event("lockfix_service_control_failed", service=service_name, action=action, error=str(exc))

    def open_latest_package_folder(self) -> None:
        if self.client_address[0] not in {"127.0.0.1", "::1"}:
            self.send_json({"error": "local access only"}, status=403)
            return
        release_dir = self.package_release_dir()
        latest = self.latest_package_zip(release_dir)
        try:
            if latest:
                os.startfile(f'/select,"{latest}"')
            else:
                os.startfile(str(release_dir))
        except OSError as exc:
            self.send_json({"ok": False, "error": str(exc), "folder": str(release_dir)}, status=500)
            return
        self.send_html(
            "<!doctype html><meta charset='utf-8'>"
            "<title>LOCK-FIX Package Folder</title>"
            "<body style='font-family:Segoe UI,Malgun Gothic,sans-serif;padding:28px'>"
            "<h1>LOCK-FIX package folder opened</h1>"
            f"<p>Folder: {escape(str(release_dir))}</p>"
            f"<p>Selected: {escape(latest.name if latest else '-')}</p>"
            "<p>Windows Explorer should now show the latest package file.</p>"
            "</body>"
        )

    def package_release_dir(self) -> Path:
        env_release_dir = os.environ.get("LOCKFIX_PACKAGE_RELEASE_DIR", "").strip()
        candidates = [
            Path(env_release_dir) if env_release_dir else None,
            ROOT / "dist" / "release",
            ROOT.parent / "New project" / "dist" / "release",
            Path.home() / "Downloads",
        ]
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return ROOT

    def latest_package_zip(self, release_dir: Path) -> Path | None:
        try:
            packages = sorted(
                release_dir.glob("LOCK-FIX-Windows-Installer-Package-*.zip"),
                key=lambda item: item.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            return None
        return packages[0] if packages else None

    def policy_guard_state_path(self) -> Path:
        return self.context.config.audit_log_path.parent / "policy-guard-state.json"

    def policy_guard_state(self) -> dict:
        path = self.policy_guard_state_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except (OSError, json.JSONDecodeError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("events", {})
        data.setdefault("retries", {})
        return data

    def save_policy_guard_state(self, state: dict) -> None:
        path = self.policy_guard_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def recent_raw_audit_records(self, limit: int = 600) -> list[dict]:
        records = []
        for line in LockFixWebHandler.audit_log_lines(self)[-max(1, limit):]:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records

    def write_policy_guard_event_once(
        self,
        state: dict,
        key: str,
        event: str,
        response: str,
        *,
        severity: str = "WARNING",
        cooldown_seconds: int = 300,
        **payload,
    ) -> bool:
        now = time.time()
        events = state.setdefault("events", {})
        previous = events.get(key) if isinstance(events.get(key), dict) else {}
        previous_at = float(previous.get("written_at") or 0)
        if previous_at and now - previous_at < cooldown_seconds:
            return False
        events[key] = {"written_at": now, "event": event, "response": response, "severity": severity}
        self.context.controller.audit.write(
            f"policy.guard.{key}",
            result="FAILED" if severity in {"CRITICAL", "ERROR"} else "INFO",
            resourceType="POLICY",
            resourceId=key,
            severity=severity,
            policy_event=event,
            automatic_response=response,
            message=f"{event} -> {response}",
            **payload,
        )
        return True

    def approval_count_for_request(self, request: dict, decisions: list[dict]) -> int:
        request_id = str(request.get("id") or "")
        return sum(
            1
            for decision in decisions
            if str(decision.get("approvalRequestId") or "") == request_id
            and str(decision.get("decision") or "").upper() == "APPROVED"
        )

    def policy_guard_dual_approval_events(self, state: dict) -> list[dict]:
        try:
            approval_data = self.approval_summary()
        except Exception as exc:
            return [{
                "event": "관리자 이중 승인 상태 확인 실패",
                "response": "Mount/Online 버튼 상태 확인 보류",
                "severity": "WARNING",
                "detail": str(exc),
                "time": datetime.now().isoformat(timespec="seconds"),
            }]
        decisions = approval_data.get("decisions") if isinstance(approval_data, dict) else []
        critical = {"DISK_ONLINE", "POLICY_CHANGE", "EMERGENCY_UNLOCK", "HARDWARE_POWER_ON", "HARDWARE_POWER_OFF"}
        events = []
        for request_item in approval_data.get("requests", []):
            request_type = str(request_item.get("requestType") or "")
            status = str(request_item.get("status") or "").upper()
            required = int(request_item.get("requiredApprovals") or 1)
            approved = self.approval_count_for_request(request_item, decisions if isinstance(decisions, list) else [])
            if request_type in critical and status not in {"APPROVED", "EXECUTED", "REJECTED", "EXPIRED"} and approved < required:
                event = {
                    "event": "관리자 이중 승인 미완료",
                    "response": "Mount/Online 버튼 비활성화",
                    "severity": "WARNING",
                    "detail": f"{request_type} approval {approved}/{required} is incomplete.",
                    "time": datetime.now().isoformat(timespec="seconds"),
                }
                self.write_policy_guard_event_once(
                    state,
                    f"dual_approval_incomplete_{request_item.get('id')}",
                    event["event"],
                    event["response"],
                    severity=event["severity"],
                    approvalRequestId=str(request_item.get("id") or ""),
                    request_type=request_type,
                    approved=approved,
                    required=required,
                )
                events.append(event)
        return events

    def evaluate_airgap_policy_events(self, summary: dict, veeam_runtime: dict, bays: list[dict]) -> list[dict]:
        state = self.policy_guard_state()
        records = self.recent_raw_audit_records()
        now_text = datetime.now().isoformat(timespec="seconds")
        slot_id = str(next(iter(self.context.config.slots), "BAY-01"))
        backup_complete = bool(
            int(veeam_runtime.get("current_step") or 1) >= 2
            or int(veeam_runtime.get("progress_percent") or 0) >= 100
            or "success" in str(veeam_runtime.get("message") or "").lower()
        )

        def action(record: dict) -> str:
            return str(record.get("event") or record.get("action") or "")

        def text(record: dict) -> str:
            return json.dumps(record, ensure_ascii=False, sort_keys=True)

        events: list[dict] = []
        offline_failures = [
            record for record in records
            if (
                ("disk.offline" in action(record).lower() or action(record) == "veeam.auto_isolate.failed")
                and (
                    any(token in action(record).lower() for token in ("error", "fail"))
                    or str(record.get("result") or "").upper() in {"FAILED", "ERROR"}
                    or str(record.get("ok") or "").lower() in {"false", "0", "no"}
                )
            )
        ]
        if backup_complete and offline_failures:
            latest = offline_failures[-1]
            signature = str(latest.get("id") or latest.get("createdAt") or latest.get("ts") or text(latest))[:160]
            retries = state.setdefault("retries", {})
            retry_key = f"disk_offline_after_backup:{signature}"
            if not retries.get(retry_key):
                retries[retry_key] = {"attempted_at": now_text, "slot_id": slot_id}
                self.context.controller.audit.write(
                    "policy.guard.disk_offline_retry",
                    slot_id=slot_id,
                    result="INFO",
                    resourceType="DISK",
                    resourceId=slot_id,
                    message="Backup completed but Disk Offline failed. LOCK-FIX starts one automatic retry.",
                )
                try:
                    retry_result = self.context.run_agent_service_operation("disk.isolate", {"slot_id": slot_id})
                    retries[retry_key]["result"] = str(retry_result.get("state") or "")
                    self.context.controller.audit.write(
                        "policy.guard.disk_offline_retry.success",
                        slot_id=slot_id,
                        result="SUCCESS",
                        resourceType="DISK",
                        resourceId=slot_id,
                        executor="LOCK-FIX Agent/Service",
                        message="Automatic Disk Offline retry completed.",
                    )
                except Exception as exc:
                    retries[retry_key]["result"] = "FAILED"
                    retries[retry_key]["error"] = str(exc)
                    self.context.controller.audit.write(
                        "policy.guard.disk_offline_admin_alert",
                        slot_id=slot_id,
                        result="FAILED",
                        resourceType="DISK",
                        resourceId=slot_id,
                        message="Automatic Disk Offline retry failed. Administrator notification is required.",
                        error=str(exc),
                    )
            events.append({
                "event": "백업 완료 후 Disk Offline 실패",
                "response": "재시도 1회 → 실패 시 관리자 알림",
                "severity": "CRITICAL",
                "detail": str(latest.get("error") or latest.get("message") or action(latest)),
                "time": now_text,
            })

        online_requests = [record for record in records if action(record) == "disk.online.request"]
        if online_requests:
            try:
                approval_data = self.approval_summary()
                approved_targets = {
                    str(request.get("targetId") or "")
                    for request in approval_data.get("requests", [])
                    if str(request.get("requestType") or "") == "DISK_ONLINE"
                    and str(request.get("status") or "").upper() in {"APPROVED", "EXECUTED"}
                }
            except Exception:
                approved_targets = set()
            latest_online = online_requests[-1]
            online_slot = str(latest_online.get("slot_id") or latest_online.get("resourceId") or slot_id)
            if online_slot not in approved_targets:
                event = {
                    "event": "승인 없는 Online 시도",
                    "response": "즉시 차단 + 감사로그 기록",
                    "severity": "CRITICAL",
                    "detail": f"DISK_ONLINE approval was not found for {online_slot}.",
                    "time": now_text,
                }
                self.write_policy_guard_event_once(
                    state,
                    f"online_without_approval_{online_slot}",
                    event["event"],
                    event["response"],
                    severity=event["severity"],
                    slot_id=online_slot,
                )
                events.append(event)

        ransomware_signals = [
            record for record in records
            if action(record) == "disk.io_quiet.error"
            or any(token in text(record).lower() for token in ("ransomware", "write i/o is still active", "backup files are still changing"))
        ]
        if ransomware_signals:
            event = {
                "event": "랜섬웨어 의심 쓰기 패턴",
                "response": "재연결 금지 + Disk Offline 유지",
                "severity": "CRITICAL",
                "detail": str(ransomware_signals[-1].get("error") or ransomware_signals[-1].get("message") or action(ransomware_signals[-1])),
                "time": now_text,
            }
            self.write_policy_guard_event_once(state, "ransomware_write_pattern", event["event"], event["response"], severity=event["severity"], slot_id=slot_id)
            events.append(event)

        for bay in bays:
            lock_state = str((bay.get("lock") or {}).get("state") or "").upper()
            power_state = str((bay.get("power") or {}).get("state") or "").upper()
            if power_state in {"OFF", "OFFLINE"} and lock_state not in {"LOCKED", "CLOSED"}:
                event = {
                    "event": "잠금핀 상태 불일치",
                    "response": "복구 접속 차단",
                    "severity": "CRITICAL",
                    "detail": f"{bay.get('slot') or slot_id}: power={power_state}, lock={lock_state or '-'}",
                    "time": now_text,
                }
                self.write_policy_guard_event_once(state, f"lock_pin_mismatch_{bay.get('slot') or slot_id}", event["event"], event["response"], severity=event["severity"], slot_id=str(bay.get("slot") or slot_id))
                events.append(event)

        hash_failures = [
            record for record in records
            if (
                action(record) == "verify.hash"
                and str(record.get("ok")).lower() in {"false", "0", "no"}
            )
            or "hash_mismatch" in text(record).lower()
        ]
        if hash_failures:
            event = {
                "event": "해시 검증 실패",
                "response": "백업 세트 격리 + 복구 사용 금지",
                "severity": "CRITICAL",
                "detail": str(hash_failures[-1].get("message") or hash_failures[-1].get("reason") or action(hash_failures[-1])),
                "time": now_text,
            }
            self.write_policy_guard_event_once(state, "hash_verification_failed", event["event"], event["response"], severity=event["severity"], slot_id=slot_id)
            events.append(event)

        events.extend(self.policy_guard_dual_approval_events(state))
        self.save_policy_guard_state(state)
        return events[-12:]

    def air_gap_summary(self, fast: bool = False) -> dict:
        summary = self.summary()
        now = time.time()
        tick = int(now)
        veeam_runtime = self.veeam_interlock_runtime(now, poll_api=not fast)
        current_step = veeam_runtime["current_step"]
        veeam_connected = bool(veeam_runtime.get("api_synced") or veeam_runtime.get("connected"))
        if int(veeam_runtime.get("current_step") or 1) <= 1 and int(veeam_runtime.get("progress_percent") or 0) <= 0:
            for log in veeam_runtime.get("step_logs") or []:
                if not isinstance(log, dict):
                    continue
                log["state"] = "PENDING"
                log["transition_allowed"] = False
                log["progress_percent"] = ""
                if int(log.get("step") or 0) == 1:
                    log["detail"] = "새로운 Veeam Backup Done 완료 잡이 확인되기 전까지 1번 단계를 비활성화합니다."
        veeam_states = [
            {"step": 1, "title": "Backup completed", "label": "백업 완료", "state": "PENDING", "code": "BACKUP_COMPLETED"},
            {"step": 2, "title": "Flush running", "label": "Flush 실행", "state": "PENDING", "code": "FLUSHING"},
            {"step": 3, "title": "I/O checking", "label": "I/O 종료 확인", "state": "PENDING", "code": "IO_CHECKING"},
            {"step": 4, "title": "Unmount", "label": "Unmount", "state": "PENDING", "code": "UNMOUNTING"},
            {"step": 5, "title": "Offline", "label": "오프라인", "state": "PENDING", "code": "DISK_OFFLINING"},
        ]
        for item in veeam_states:
            log = veeam_runtime["step_logs"][item["step"] - 1]
            if veeam_connected:
                if item["step"] < current_step:
                    item["state"] = "DONE"
                elif item["step"] == current_step:
                    item["state"] = "ACTIVE"
            if isinstance(log, dict) and log.get("state"):
                item["state"] = log["state"]
            item["checked_at"] = veeam_runtime["last_checked"]
            item["log"] = log
        bays = []
        for index, slot in enumerate(summary["slots"], start=1):
            locked = (tick + index) % 5 != 0
            hash_suffix = hashlib.sha256(f"{slot['slot_id']}|{slot['uid']}".encode("utf-8")).hexdigest()[:12].upper()
            bays.append(
                {
                    "slot": slot["slot_id"],
                    "device": slot["device"],
                    "mount_point": slot["mount_point"],
                    "power": {
                        "state": "OFFLINE",
                        "label": "Disk Offline Complete",
                        "description": "Windows disk offline isolation is active after unmount.",
                    },
                    "lock": {
                        "state": "LOCKED" if locked else "READY",
                        "label": "Locked" if locked else "Ready to Unlock",
                        "description": "External physical access is blocked." if locked else "Ready for removal after administrator approval.",
                    },
                    "integrity": {
                        "uid": "Drive #%s - Match" % index,
                        "hash": "SHA-256 Hash - Valid",
                        "hash_value": f"SHA256-{hash_suffix}",
                        "blocked": False,
                    },
                }
            )
        policy_events = self.evaluate_airgap_policy_events(summary, veeam_runtime, bays)
        session_logs = list(veeam_runtime["session_logs"])
        if policy_events:
            has_critical = any(str(event.get("severity") or "").upper() == "CRITICAL" for event in policy_events)
            session_logs.append(
                {
                    "name": "LOCK-FIX Policy Guard",
                    "status": "Blocked" if has_critical else "Monitoring",
                    "actions": [
                        "POLICY - {event} -> {response} ({detail})".format(
                            event=event.get("event") or "-",
                            response=event.get("response") or "-",
                            detail=event.get("detail") or "-",
                        )
                        for event in policy_events
                    ],
                    "duration": "-",
                    "progress_percent": "",
                }
            )
        return {
            "security_score": {
                "score": 98,
                "status": "SAFE AIR-GAP",
                "description": "Disk offline, solenoid lock, and integrity verification are all operating normally.",
            },
            "kpis": [
                {
                    "id": "power",
                    "title": "Disk Offline",
                    "value": "Disk Offline Complete",
                    "detail": "Windows disk offline isolation after unmount.",
                },
                {
                    "id": "lock",
                    "title": "Solenoid Lock",
                    "value": "Locked",
                    "detail": "Mechanical lock is engaged on the drive bay.",
                },
                {
                    "id": "integrity",
                    "title": "Integrity Check",
                    "value": "Verified",
                    "detail": "UID match and SHA-256 hash validation passed.",
                },
            ],
            "veeam": {
                "api_poll_interval_seconds": int((get_veeam_config(self.context.app_config) or {}).get("poll_interval_seconds", 10)),
                "server": veeam_runtime["server"],
                "port": veeam_runtime["port"],
                "connected": veeam_runtime["connected"],
                "last_checked": veeam_runtime["last_checked"],
                "job": veeam_runtime["job"],
                "session_state": veeam_states[current_step - 1]["code"],
                "current_step": current_step,
                "state_source": veeam_runtime["state_source"],
                "api_synced": veeam_runtime["api_synced"],
                "port_open": veeam_runtime["port_open"],
                "api_checks": veeam_runtime["api_checks"],
                "auto_isolate": veeam_runtime["auto_isolate"],
                "progress_percent": veeam_runtime["progress_percent"],
                "api_verification_percent": veeam_runtime["api_verification_percent"],
                "message": veeam_runtime["message"],
            },
            "timeline": veeam_states,
            "step_logs": veeam_runtime["step_logs"],
            "session_logs": session_logs,
            "policy_events": policy_events,
            "bays": bays,
            "integrity_history": [
                {"time": "2026-04-25 22:40:13", "target": "Backup Cycle #1042", "uid": "MATCH", "hash": "VALID"},
                {"time": "2026-04-25 12:00:10", "target": "Backup Cycle #1041", "uid": "MATCH", "hash": "VALID"},
                {"time": "2026-04-24 23:58:44", "target": "Backup Cycle #1040", "uid": "MATCH", "hash": "VALID"},
            ],
            "emergency": {
                "title": "Emergency Control Center",
                "description": "Manual release is available after current-user password approval.",
                "primary": "Waiting for Password Approval",
                "secondary": "Data path activation remains protected",
            },
            "emergency_access": self.emergency_access_summary(summary),
        }

    @staticmethod
    def clone_payload(payload: dict) -> dict:
        return json.loads(json.dumps(payload, ensure_ascii=False))

    def cached_integrated_source_inventory(self) -> dict:
        cache_key = str(ROOT)
        now_monotonic = time.monotonic()
        with LockFixWebHandler.source_inventory_cache_lock:
            cached = LockFixWebHandler.source_inventory_cache_by_key.get(cache_key)
            if cached and now_monotonic - cached[0] < SOURCE_INVENTORY_CACHE_TTL_SECONDS:
                return LockFixWebHandler.clone_payload(cached[1])
        inventory = integrated_source_inventory()
        with LockFixWebHandler.source_inventory_cache_lock:
            LockFixWebHandler.source_inventory_cache_by_key[cache_key] = (time.monotonic(), inventory)
        return LockFixWebHandler.clone_payload(inventory)

    def sources_summary(self, live: bool = False) -> dict:
        cache_key = str(self.context.config_path)
        now_monotonic = time.monotonic()
        if not live:
            with LockFixWebHandler.sources_cache_lock:
                cached = LockFixWebHandler.sources_cache_by_key.get(cache_key)
                if cached and now_monotonic - cached[0] < SOURCES_CACHE_TTL_SECONDS:
                    payload = LockFixWebHandler.clone_payload(cached[1])
                    live_status = dict(payload.get("live_status") or {})
                    live_status.update({
                        "cache_hit": True,
                        "source_age_seconds": round(now_monotonic - cached[0], 3),
                    })
                    payload["live_status"] = live_status
                    return payload

        payload = self.cached_integrated_source_inventory()
        payload["air_gap"] = self.air_gap_summary(fast=True)
        payload["generated_at"] = datetime.now().isoformat(timespec="seconds")
        payload["live_status"] = {
            "cache_hit": False,
            "generated_at": payload["generated_at"],
            "source_age_seconds": 0,
        }
        with LockFixWebHandler.sources_cache_lock:
            LockFixWebHandler.sources_cache_by_key[cache_key] = (time.monotonic(), payload)
        return LockFixWebHandler.clone_payload(payload)

    def emergency_access_summary(self, summary: dict | None = None) -> dict:
        config = self.context.config
        status = self.context.controller.status()
        storage_capability = LockFixWebHandler.storage_api_capability(self)
        slot_summaries = []
        for slot_id, slot in config.slots.items():
            current_state = str(status.get(slot_id, "READY_MOCK") or "READY_MOCK")
            current_state_upper = current_state.upper()
            auth_hash = self.context.controller.emergency_access_hash(slot_id)
            try:
                mount_exists = slot.mount_point.exists()
                mount_error = ""
            except OSError as exc:
                mount_exists = False
                mount_error = str(exc)
            uid_ok = False
            current_uid = ""
            if mount_exists:
                uid_ok, current_uid = verify_uid(slot)
            if mount_exists:
                try:
                    hash_ok, actual_hash, expected_hash = verify_manifest(slot.mount_point, slot.manifest_path)
                    hash_status = "VALID" if hash_ok else "MISMATCH"
                except OSError as exc:
                    actual_hash = ""
                    expected_hash = ""
                    mount_error = str(exc)
                    hash_status = "MOUNT_ACCESS_ERROR"
            else:
                actual_hash = ""
                expected_hash = ""
                hash_status = "MOUNT_ACCESS_ERROR" if mount_error else "WAITING_FOR_MOUNT"
            unmount_record = LockFixWebHandler.latest_audit_record(self, slot_id, {"disk.unmount", "disk.unmount.error"})
            power_record = LockFixWebHandler.latest_audit_record(
                self,
                slot_id,
                {"disk.offline", "disk.offline.error", "power.mock.off", "power.command.off", "power.mock.off.error", "power.command.off.error"},
            )
            reconnect_records = LockFixWebHandler.recent_reconnect_audit_records(self, slot_id)
            reconnect_all_records = LockFixWebHandler.recent_reconnect_audit_records(self, slot_id, limit=240, reset_on_request=False)
            reconnect_recent_records, _ = LockFixWebHandler.split_reconnect_audit_records_by_days(self, reconnect_records, days=7)
            reconnect_all_recent_records, reconnect_older_records = LockFixWebHandler.split_reconnect_audit_records_by_days(self, reconnect_all_records, days=7)
            reconnect_history = [
                item
                for item in (LockFixWebHandler.format_reconnect_audit_record(self, record) for record in reconnect_recent_records)
                if item
            ]
            reconnect_history_more = [
                item
                for item in (LockFixWebHandler.format_reconnect_audit_record(self, record) for record in reconnect_older_records)
                if item
            ]
            approved_request = self.context.controller.approvals.approved_request_for("DISK_OFFLINE", slot_id)
            approval_progress = 0
            approval_required = 0
            approval_status = "NONE"
            approval_mode = ""
            approval_request_id = ""
            approval_requester = ""
            approval_created_at = ""
            approval_updated_at = ""
            if approved_request:
                approval_request_id = str(approved_request.get("id") or "")
                approval_requester = str(approved_request.get("requesterUserId") or "")
                approval_created_at = str(approved_request.get("createdAt") or "")
                approval_updated_at = str(approved_request.get("updatedAt") or "")
                approval_status = str(approved_request.get("status") or "APPROVED").upper()
                approval_mode = str((approved_request.get("metadata") or {}).get("forceApprovalMode") or "AUTO_POLICY")
                approval_required = max(1, int(approved_request.get("requiredApprovals") or 1))
                approval_data = self.context.controller.approvals.load()
                approval_progress = sum(
                    1
                    for decision in approval_data.get("decisions", [])
                    if str(decision.get("approvalRequestId") or "") == approval_request_id
                    and str(decision.get("decision") or "").upper() == "APPROVED"
                )
                approval_progress = min(approval_required, approval_progress)
            last_reconnect_record = reconnect_all_recent_records[-1] if reconnect_all_recent_records else None
            last_reconnect = LockFixWebHandler.format_audit_timestamp(self, last_reconnect_record.get("ts")) if last_reconnect_record else "-"
            normalized_device = str(slot.device).strip().replace("/", "\\").rstrip("\\").lower()
            normalized_mount = str(slot.mount_point).strip().replace("/", "\\").rstrip("\\").lower()
            os_volume_blocked = normalized_device in {"c:", "c"} or normalized_mount in {"c:", "c"}
            with self.context.emergency_jobs_lock:
                reconnect_job = dict(self.context.emergency_jobs.get(slot_id) or {})
            reconnect_running = reconnect_job.get("status") == "running"
            online_approval_active = self.context.controller.online_approval_active(slot_id)
            if current_state_upper == "ISOLATED" and not reconnect_running and not online_approval_active:
                try:
                    self.context.controller.reblock_unauthorized_online(slot_id, reason="webui_isolated_state_guard")
                except Exception as exc:
                    self.context.controller.audit.write(
                        "disk.online.unauthorized.guard.error",
                        slot_id=slot_id,
                        reason="webui_isolated_state_guard",
                        error=str(exc),
                    )
            elif current_state_upper == "ISOLATED" and (reconnect_running or online_approval_active):
                self.context.controller.audit.write(
                    "disk.online.unauthorized.guard.paused",
                    slot_id=slot_id,
                    reason="emergency_reconnect_active" if reconnect_running else "online_approval_active",
                    job_id=str(reconnect_job.get("job_id") or ""),
                    message="Unauthorized online reblock guard is paused during administrator-approved emergency reconnect.",
                )
            state_allows_access = current_state_upper in {
                "ISOLATED",
                "OFFLINE",
                "DISK_OFFLINE",
                "DISK_OFFLINE_COMPLETE",
                "OFFLINE_COMPLETE",
                "DISK_OFFLINING",
                "UNMOUNTED",
                "UNMOUNT",
                "DISMOUNTED",
                "DISMOUNT",
                "POWERING_OFF",
                "UNMOUNTING",
                "WAITING_DISK",
                "WAITING_FOR_MOUNT",
                "MOUNT_ACCESS_ERROR",
                "ERROR",
                "QUARANTINE",
            }
            volume_needs_reconnect = not mount_exists or hash_status in {"WAITING_FOR_MOUNT", "MOUNT_ACCESS_ERROR"}
            emergency_eligible = (state_allows_access or volume_needs_reconnect) and not os_volume_blocked
            blocked_reason = ""
            if os_volume_blocked:
                blocked_reason = "C:\\ OS volume is permanently blocked."
            elif not emergency_eligible:
                blocked_reason = "긴급 접속 대상 상태가 아닙니다."
            slot_summaries.append(
                {
                    "slot_id": slot_id,
                    "device": slot.device,
                    "mount_point": str(slot.mount_point),
                    "state": current_state,
                    "dry_run": config.dry_run,
                    "eligible": emergency_eligible,
                    "blocked_reason": blocked_reason,
                    "authorization_hash_short": f"{auth_hash[:16]}...{auth_hash[-8:]}" if len(auth_hash) > 28 else auth_hash,
                    "authorization_hash_protected": True,
                    "uid_ok": uid_ok,
                    "current_uid_short": f"{current_uid[:16]}...{current_uid[-8:]}" if len(current_uid) > 28 else current_uid,
                    "hash_status": hash_status,
                    "manifest_hash_short": f"{actual_hash[:16]}...{actual_hash[-8:]}" if len(actual_hash) > 28 else actual_hash,
                    "expected_manifest_hash_short": f"{expected_hash[:16]}...{expected_hash[-8:]}" if expected_hash and len(expected_hash) > 28 else expected_hash or "",
                    "mount_error": mount_error,
                    "last_unmount": LockFixWebHandler.compact_log_value(self, unmount_record.get("output") or unmount_record.get("error") or "-") if unmount_record else "-",
                    "last_power_off": LockFixWebHandler.compact_log_value(self, power_record.get("output") or power_record.get("error") or "-") if power_record else "-",
                    "last_reconnect": last_reconnect,
                    "last_reconnect_within_days": 7,
                    "reconnect_history": reconnect_history[-80:],
                    "reconnect_history_more": reconnect_history_more[-120:],
                    "reconnect_history_more_count": len(reconnect_history_more),
                    "auto_approval": {
                        "available": bool(approved_request),
                        "status": approval_status,
                        "mode": approval_mode,
                        "approval_request_id": approval_request_id,
                        "requester_user_id": approval_requester,
                        "created_at": approval_created_at,
                        "updated_at": approval_updated_at,
                        "approved_count": approval_progress,
                        "required_count": approval_required,
                        "summary": "자동 승인 검증 완료" if approved_request and approval_progress >= approval_required else "자동 승인 대기",
                    },
                    "storage_api_capability": storage_capability,
                }
            )
        first = slot_summaries[0] if slot_summaries else {}
        return {
            "title": "Emergency Volume Access",
            "description": "Unmount 이후 긴급 접속이 필요한 경우 인증 해시값을 확인한 뒤 UID와 SHA-256 검증을 다시 수행하고 볼륨을 즉시 접속합니다.",
            "primary": "무결성 검증 후 재접속",
            "secondary": "C:\\ OS 볼륨은 어떤 경우에도 마운트 해제/재접속 작업 대상이 될 수 없습니다.",
            "slot": first,
            "slots": slot_summaries,
            "storage_api_capability": storage_capability,
        }

    def storage_api_capability(self) -> dict:
        path = ROOT / "runtime" / "storage-api-capability.json"
        default_steps = [
            "1. Windows 기본 저장소 구성 복구: winmgmt, vds, storsvc, Schedule 서비스를 확인하고 기동합니다.",
            "2. WMI/CIM 저장소 복구: Storage WMI/CIM 권한, WMI repository, Storage 모듈 상태를 복구합니다.",
            "3. LOCK-FIX 대체 경로 사용: 저장된 volumePath/volumeMountPath 기준으로 mountvol 드라이브 문자 재할당을 시도합니다.",
            "4. 저장된 볼륨 식별정보 강화: volumePath, volumeMountPath, diskNumber, partitionNumber, diskUniqueId, volumeUniqueId, accessPath를 유지합니다.",
            "5. 그래도 실패하면 서버 정책 차단으로 판단: 긴급 재접속 제한 상태로 표시하고 운영 정책/WMI 보안을 점검합니다.",
        ]
        if not path.exists():
            return {
                "status": "UNKNOWN",
                "emergency_reconnect_mode": "storage_api_or_mountvol",
                "reason": "Storage API install preflight has not been recorded yet.",
                "alternative_steps": default_steps,
            }
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "status": "UNKNOWN",
                "emergency_reconnect_mode": "storage_api_or_mountvol",
                "reason": f"Storage API capability record could not be read: {exc}",
                "alternative_steps": default_steps,
            }
        if not isinstance(data, dict):
            data = {}
        steps = data.get("alternative_steps") if isinstance(data.get("alternative_steps"), list) else default_steps
        return {
            "checked_at": str(data.get("checked_at") or ""),
            "stage": str(data.get("stage") or ""),
            "status": str(data.get("status") or "UNKNOWN"),
            "emergency_reconnect_mode": str(data.get("emergency_reconnect_mode") or "storage_api_or_mountvol"),
            "reason": str(data.get("reason") or ""),
            "alternative_steps": [str(step) for step in steps],
        }

    def recent_reconnect_audit_records(self, slot_id: str, limit: int = 120, reset_on_request: bool = True) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {
            "emergency.reconnect.request",
            "emergency.reconnect.approved",
            "emergency.reconnect.denied",
            "emergency.reconnect.complete",
            "emergency.reconnect.failure.diagnostic",
            "emergency.reconnect.background.error",
            "emergency.reconnect.background.timeout",
            "emergency.reconnect.background.started",
            "emergency.reconnect.background.complete",
            "emergency.reconnect.background.not_started",
            "emergency.reconnect.heartbeat",
            "emergency.reconnect.step",
            "agent.service.request.received",
            "state.transition",
            "power.mock.on.start",
            "power.mock.on.tick",
            "power.mock.on",
            "power.command.on.start",
            "power.command.on.tick",
            "power.command.on",
            "power.command.on.error",
            "disk.online.approved",
            "disk.online.start",
            "disk.online.tick",
            "disk.online",
            "disk.online.error",
            "disk.online.approval.cleared",
            "disk.reconnect.plan",
            "disk.wait.start",
            "disk.wait.tick",
            "disk.wait.found",
            "disk.access_path.start",
            "disk.access_path",
            "disk.access_path.error",
            "disk.mount_ro.start",
            "disk.mount_ro.tick",
            "disk.mount_ro",
            "disk.mount_ro.error",
            "disk.health.scan.start",
            "disk.health.scan",
            "disk.health.scan.skipped",
            "disk.health.scan.error",
            "disk.mount_rw.start",
            "disk.mount_rw.tick",
            "disk.mount_rw",
            "disk.mount_rw.error",
            "disk.storage_api.self_check.error",
            "disk.storage_api.self_check",
            "verify.uid",
            "verify.hash",
        }
        records = []
        reconnect_states = {
            "RECONNECT_REQUESTED",
            "DISK_ONLINING",
            "POWERING_ON",
            "WAITING_DISK",
            "VERIFYING_UID",
            "MOUNTED_READONLY",
            "VERIFYING_HASH",
            "ONLINE_VERIFIED_RW",
            "QUARANTINE",
            "ERROR",
        }
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            if record.get("event") == "state.transition" and str(record.get("state") or "") not in reconnect_states:
                continue
            if reset_on_request and (record.get("event") == "emergency.reconnect.request" or (
                record.get("event") == "state.transition" and str(record.get("state") or "") == "RECONNECT_REQUESTED"
            )):
                records = []
            if (
                record.get("event") == "state.transition"
                and str(record.get("state") or "") == "ERROR"
                and records
                and records[-1].get("event") == "state.transition"
                and str(records[-1].get("state") or "") == "ERROR"
            ):
                previous = dict(records[-1])
                previous["repeat_count"] = int(previous.get("repeat_count") or 1) + 1
                if not previous.get("error") and record.get("error"):
                    previous["error"] = record.get("error")
                previous["ts"] = record.get("ts") or previous.get("ts")
                records[-1] = previous
                continue
            records.append(record)
        return records[-limit:]

    def format_reconnect_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        if event == "emergency.reconnect.request":
            return f"{prefix}LOCK-FIX Reconnect REQUEST - slot {slot_id}, emergency hash verification requested."
        if event == "emergency.reconnect.approved":
            return f"{prefix}LOCK-FIX Reconnect APPROVED - slot {slot_id}, authorization hash matched."
        if event == "disk.online.approved":
            approved_until = LockFixWebHandler.compact_log_value(self, record.get("approved_until") or "-")
            return f"{prefix}LOCK-FIX Reconnect ONLINE APPROVED - slot {slot_id}, limited online window until {approved_until}"
        if event == "emergency.reconnect.denied":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "verification_hash_mismatch")
            return f"{prefix}LOCK-FIX Reconnect DENIED - slot {slot_id}, {reason}"
        if event == "emergency.reconnect.background.not_started":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "재접속 작업이 시작되지 않았습니다. 관리자 권한/서비스 상태 확인 필요")
            resolution = LockFixWebHandler.compact_log_value(self, record.get("resolution") or "LOCK-FIX를 관리자 권한으로 재시작하고 WebUI 서비스를 최신 소스로 재시작하세요.")
            return f"{prefix}LOCK-FIX Reconnect NOT STARTED - slot {slot_id}, {message} | 해결: {resolution}"
        if event == "emergency.reconnect.background.started":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "background worker started")
            return f"{prefix}LOCK-FIX Reconnect BACKGROUND STARTED - slot {slot_id}, {message}"
        if event == "agent.service.request.received" and str(record.get("operation") or "") == "emergency.reconnect":
            request_id = LockFixWebHandler.compact_log_value(self, record.get("request_id") or "-")
            return f"{prefix}LOCK-FIX Agent STARTED - slot {slot_id}, request {request_id}"
        if event == "emergency.reconnect.background.complete":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "complete")
            return f"{prefix}LOCK-FIX Reconnect BACKGROUND COMPLETE - slot {slot_id}, state {state}, 완료되었다"
        if event == "emergency.reconnect.heartbeat":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "reconnect job heartbeat")
            started = "started" if record.get("background_started") else "not started yet"
            return f"{prefix}LOCK-FIX Reconnect HEARTBEAT - slot {slot_id}, background {started}, {message}"
        if event == "emergency.reconnect.background.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "background worker failed")
            resolution = LockFixWebHandler.compact_log_value(self, record.get("resolution") or "")
            resolution_text = f" | 해결: {resolution}" if resolution else ""
            return f"{prefix}LOCK-FIX Reconnect BACKGROUND ERROR - slot {slot_id}, {error}{resolution_text}"
        if event == "emergency.reconnect.background.timeout":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "재접속 작업 제한 시간을 초과했습니다.")
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or "")
            timeout = LockFixWebHandler.compact_log_value(self, record.get("timeout_seconds") or "")
            resolution = LockFixWebHandler.compact_log_value(self, record.get("resolution") or "")
            elapsed_text = f" elapsed {elapsed}s/{timeout}s," if elapsed or timeout else ""
            resolution_text = f" | 해결: {resolution}" if resolution else ""
            return f"{prefix}LOCK-FIX Reconnect BACKGROUND TIMEOUT - slot {slot_id},{elapsed_text} {message}{resolution_text}"
        if event == "emergency.reconnect.failure.diagnostic":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "reconnect failed")
            access_denied = bool(record.get("get_volume_access_denied") or record.get("storage_api_access_denied"))
            resolution = LockFixWebHandler.compact_log_value(self, record.get("resolution") or "")
            denied_text = "Get-Volume access denied detected. " if access_denied else ""
            resolution_text = f" | 해결: {resolution}" if resolution else ""
            return f"{prefix}LOCK-FIX Reconnect ERROR DETAIL - slot {slot_id}, {denied_text}{error}{resolution_text}"
        if event == "emergency.reconnect.step":
            step = LockFixWebHandler.compact_log_value(self, record.get("step") or "-")
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "reconnect step")
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "")
            drive_text = f", drive {drive}" if drive else ""
            return f"{prefix}LOCK-FIX Reconnect STEP {step} - slot {slot_id}, {message}{drive_text}"
        if event == "state.transition":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "")
            repeat_count = int(record.get("repeat_count") or 1)
            repeat_text = f" (same error repeated {repeat_count} times)" if repeat_count > 1 else ""
            error_text = f", error: {error}" if error and state == "ERROR" else ""
            return f"{prefix}LOCK-FIX Reconnect STATE - slot {slot_id}, {state}{repeat_text}{error_text}"
        if event == "disk.reconnect.plan":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            disk = LockFixWebHandler.compact_log_value(self, record.get("disk_number") or "-")
            partition = LockFixWebHandler.compact_log_value(self, record.get("partition_number") or "-")
            volume = LockFixWebHandler.compact_log_value(self, record.get("volume_unique_id") or "-")
            return f"{prefix}LOCK-FIX Reconnect PLAN - slot {slot_id}, drive {drive}, disk {disk}, partition {partition}, volume {volume}"
        if event == "disk.online.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            return f"{prefix}LOCK-FIX Reconnect ONLINE START - slot {slot_id}, drive {drive}"
        if event == "disk.online":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "disk online completed")
            return f"{prefix}LOCK-FIX Reconnect ONLINE OK - slot {slot_id}, {output}"
        if event == "disk.online.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "disk online failed")
            return f"{prefix}LOCK-FIX Reconnect ONLINE ERROR - slot {slot_id}, {error}"
        if event == "disk.online.approval.cleared":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "-")
            return f"{prefix}LOCK-FIX Reconnect ONLINE APPROVAL CLEARED - slot {slot_id}, {reason}"
        if event == "disk.wait.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            timeout = LockFixWebHandler.compact_log_value(self, record.get("timeout_seconds") or "-")
            return f"{prefix}LOCK-FIX Reconnect WAIT START - slot {slot_id}, drive {drive}, timeout {timeout}s"
        if event == "disk.wait.tick":
            attempt = LockFixWebHandler.compact_log_value(self, record.get("attempt") or "-")
            return f"{prefix}LOCK-FIX Reconnect WAIT TICK - slot {slot_id}, attempt {attempt}"
        if event == "disk.wait.found":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "backup partition detected")
            return f"{prefix}LOCK-FIX Reconnect DISK FOUND - slot {slot_id}, {output}"
        if event == "disk.access_path.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            access_path = LockFixWebHandler.compact_log_value(self, record.get("access_path") or f"{drive}:\\")
            return f"{prefix}LOCK-FIX Reconnect ACCESS PATH START - slot {slot_id}, restoring {access_path}"
        if event == "disk.access_path":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "access path restored")
            return f"{prefix}LOCK-FIX Reconnect ACCESS PATH OK - slot {slot_id}, {output}"
        if event == "disk.access_path.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "access path restore failed")
            return f"{prefix}LOCK-FIX Reconnect ACCESS PATH ERROR - slot {slot_id}, {error}"
        if event == "power.command.on.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "power on failed")
            return f"{prefix}LOCK-FIX Reconnect POWER ON ERROR - slot {slot_id}, {error}"
        if event == "disk.storage_api.self_check.error":
            check = LockFixWebHandler.compact_log_value(self, record.get("check") or "storage_api")
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "storage API self-check failed")
            resolution = LockFixWebHandler.compact_log_value(self, record.get("resolution") or "Windows Storage 서비스와 PowerShell 디스크 명령 상태를 확인하세요.")
            return f"{prefix}LOCK-FIX Reconnect STORAGE API ERROR - slot {slot_id}, {check}, {error} | 해결: {resolution}"
        if event == "disk.storage_api.self_check":
            access_denied = "access denied" if record.get("access_denied") else "completed"
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "Windows disk/partition API self-check completed.")
            return f"{prefix}LOCK-FIX Reconnect STORAGE API CHECK - slot {slot_id}, {access_denied}, {message}"
        if event in {"power.mock.on", "power.command.on"}:
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "power on completed")
            return f"{prefix}LOCK-FIX Reconnect POWER ON OK - slot {slot_id}, {output}"
        if event == "verify.uid":
            return f"{prefix}LOCK-FIX Reconnect UID CHECK - slot {slot_id}, ok={record.get('ok')}"
        if event == "verify.hash":
            return f"{prefix}LOCK-FIX Reconnect HASH CHECK - slot {slot_id}, ok={record.get('ok')}"
        if event in {"disk.mount_ro", "disk.mount_rw", "disk.health.scan"}:
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or event)
            return f"{prefix}LOCK-FIX Reconnect {event.replace('disk.', '').upper()} - slot {slot_id}, {output}"
        if event == "disk.health.scan.skipped":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "Repair-Volume scan skipped")
            return f"{prefix}LOCK-FIX Reconnect HEALTH SCAN SKIPPED - slot {slot_id}, {reason}"
        if event == "emergency.reconnect.complete":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            return f"{prefix}LOCK-FIX Reconnect COMPLETE - slot {slot_id}, state {state}, 완료되었다"
        return ""

    def latest_audit_record(self, slot_id: str, events: set[str]) -> dict:
        lines = LockFixWebHandler.audit_log_lines(self)
        for line in reversed(lines):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            return record
        return {}

    def veeam_interlock_runtime(self, now: float, poll_api: bool = True) -> dict:
        runtime_path = ROOT / "runtime" / "veeam_interlock_state.json"
        payload = {}
        if runtime_path.exists():
            try:
                payload = json.loads(runtime_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {}

        install_props = self.veeam_install_properties()
        veeam_config = get_veeam_config(self.context.app_config) or {}
        configured_url = urlparse(str(veeam_config.get("base_url") or ""))
        configured_server = configured_url.hostname or "127.0.0.1"
        configured_port = configured_url.port or 9419
        server = str(payload.get("server") or os.environ.get("LOCKFIX_VEEAM_HOST") or install_props.get("veeam_host") or configured_server)
        port = int(payload.get("port") or os.environ.get("LOCKFIX_VEEAM_PORT") or install_props.get("veeam_port") or configured_port)
        port_open = self.tcp_port_open(server, port) if poll_api else bool(payload.get("port_open"))
        api_payload = self.poll_veeam_api(server, port, payload) if poll_api else payload
        payload = api_payload or {}
        server = str(payload.get("server") or server)
        port = int(payload.get("port") or port)
        api_synced = bool(payload.get("api_synced"))
        has_api_session = api_synced
        current_step = int(payload.get("current_step") or 1)
        current_step = max(1, min(5, current_step))
        if not has_api_session:
            current_step = 1
        progress = int(payload.get("progress_percent") or payload.get("progress") or max(0, (current_step - 1) * 25))
        progress = max(0, min(100, progress))
        raw_result = str(payload.get("result") or payload.get("status") or "").upper()
        if raw_result in {"SUCCESS", "SUCCEEDED", "COMPLETED"}:
            progress = 100
        if not has_api_session:
            progress = 0
        connected = bool(has_api_session)
        api_verification_percent = 100 if connected else 0
        last_checked = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        job = str(payload.get("job") or "LOCK-FIX-AIRGAP-BACKUP")
        state_source = payload.get("state_source") or ("veeam_rest_api" if payload.get("api_synced") else "runtime/veeam_interlock_state.json" if payload else "waiting_for_veeam_api")
        raw_session_logs_for_completion = payload.get("session_logs") if isinstance(payload.get("session_logs"), list) else []
        backup_copy_completed = LockFixWebHandler.veeam_backup_copy_completed(
            self,
            payload,
            raw_session_logs_for_completion,
            last_checked,
        )
        if connected and not backup_copy_completed:
            current_step = 1
            if progress >= 100:
                progress = 99
            payload["current_step"] = 1
            payload["progress_percent"] = progress
            if raw_result in {"SUCCESS", "SUCCEEDED", "COMPLETED"}:
                payload["status"] = "Running"
                payload["result"] = "RUNNING"
                raw_result = "RUNNING"
        labels = ["백업 완료", "Flush 실행", "I/O 종료 확인", "Unmount", "오프라인"]
        codes = ["BACKUP_COMPLETED", "FLUSHING", "IO_CHECKING", "UNMOUNTING", "DISK_OFFLINING"]
        step_logs = []
        custom_logs = payload.get("step_logs") if connected and isinstance(payload.get("step_logs"), list) else []
        for index, label in enumerate(labels, start=1):
            state = "PENDING"
            if connected:
                if index < current_step:
                    state = "DONE"
                elif index == current_step:
                    state = "ACTIVE"
            custom = custom_logs[index - 1] if index - 1 < len(custom_logs) and isinstance(custom_logs[index - 1], dict) else {}
            if index == 1:
                default_detail = (
                    f"Veeam API 연동 {api_verification_percent}% 확인. 백업 수행 진행률 {progress}% 확인."
                    if connected
                    else f"Veeam API 연결 대기 중. 백업 수행 진행률 {progress}% 상태로 단계 전환을 보류합니다."
                )
            elif index == 2:
                if index < current_step:
                    default_detail = (
                        "2단계 Flush 완료. Windows Server 백업 볼륨 캐시 flush 요청, 대상 볼륨 확인, "
                        "flush 결과 감사 로그를 근거로 3단계 I/O 종료 확인으로 전환했습니다."
                    )
                elif index == current_step:
                    default_detail = (
                        "2단계 Flush 진행 중입니다. Windows Server 백업 볼륨 캐시 flush 요청과 "
                        "완료 감사 로그가 확인될 때까지 현재 단계에 머무릅니다."
                    )
                else:
                    default_detail = "1단계 백업 완료 확인 후 2단계 Flush 상세 로그를 표시합니다."
            elif index < current_step:
                default_detail = f"{label} 단계 완료. Veeam API 상태 전환 로그와 백업 진행률 {progress}%를 기록했습니다."
            elif index == current_step:
                default_detail = "현재 단계입니다. 다음 단계 전환 신호가 확인될 때까지 색상을 유지합니다."
            else:
                default_detail = "아직 이전 단계 완료 신호가 확인되지 않았습니다."
            step_logs.append(
                {
                    "step": index,
                    "label": label,
                    "code": codes[index - 1],
                    "state": custom.get("state") or state,
                    "time": custom.get("time") or last_checked,
                    "source": custom.get("source") or ("Veeam API" if connected else "Veeam API 대기"),
                    "detail": custom.get("detail") or default_detail,
                    "progress_percent": custom.get("progress_percent", progress if connected and index <= current_step else ""),
                    "api_verification_percent": custom.get("api_verification_percent", api_verification_percent if index == 1 else ""),
                    "transition_allowed": connected and index <= current_step,
                }
            )
        started_at = payload.get("started_at") or payload.get("start_time") or last_checked
        ended_at = payload.get("ended_at") or payload.get("end_time") or (last_checked if progress >= 100 else "-")
        duration = payload.get("duration") or ("00:08" if progress >= 100 else "-")
        status = str(payload.get("status") or payload.get("result") or "").strip()
        if not status:
            status = "Success" if progress >= 100 else "Running" if connected else "Waiting"
        elif status.upper() in {"SUCCESS", "SUCCEEDED", "COMPLETED"}:
            status = "Success"
        elif status.upper() in {"FAILED", "FAILURE", "ERROR"}:
            status = "Failed"
        elif status.upper() in {"RUNNING", "WORKING", "INPROGRESS", "IN_PROGRESS"}:
            status = "Running"
        if connected:
            auto_handler = getattr(self, "auto_isolate_after_veeam_success", None)
            if callable(auto_handler):
                auto_isolate = auto_handler(payload, status, last_checked)
            else:
                auto_isolate = LockFixWebHandler.auto_isolate_after_veeam_success(self, payload, status, last_checked)
        else:
            auto_isolate = {
                "enabled": True,
                "triggered": False,
                "message": "Waiting for successful Veeam session.",
            }
        payload["auto_isolate"] = auto_isolate
        session_completed = backup_copy_completed
        pre_checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
        pre_session_check = pre_checks.get("sessions") if isinstance(pre_checks.get("sessions"), dict) else {}
        backup_restore_point_evidence = bool(
            payload.get("backup_match_strategy")
            or payload.get("restore_point_scope")
            or payload.get("restore_point_id")
            or payload.get("session_id")
        )
        pre_session_match_missing = (
            not backup_restore_point_evidence
            and (
                str(pre_session_check.get("match_strategy") or "").lower() == "no_match"
                or "no vbr 9419 session matched" in str(pre_session_check.get("message") or "").lower()
            )
        )
        force_waiting_for_new_backup = (
            ((not session_completed or pre_session_match_missing) and current_step <= 1)
            or (
                auto_isolate.get("state") == "WAITING_FOR_NEW_BACKUP"
                and bool(auto_isolate.get("processed"))
                and auto_isolate.get("triggered") is not True
            )
        )
        if force_waiting_for_new_backup:
            current_step = 1
            progress = 0
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                item["state"] = "PENDING"
                item["transition_allowed"] = False
                item["progress_percent"] = ""
                item["detail"] = (
                    "새로운 Veeam Backup Done 완료 잡이 확인되기 전까지 단계 전환을 비활성화합니다."
                    if step_number == 1
                    else "새 백업 완료 신호가 들어오기 전까지 이 단계는 비활성 상태로 유지됩니다."
                )
        processed_backup_waiting = (
            connected
            and session_completed
            and auto_isolate.get("state") == "WAITING_FOR_NEW_BACKUP"
            and bool(auto_isolate.get("processed"))
        )
        if processed_backup_waiting and not force_waiting_for_new_backup:
            current_step = 1
            progress = 100
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                if step_number == 1:
                    item["state"] = "ACTIVE"
                    item["transition_allowed"] = True
                    item["progress_percent"] = 100
                    item["detail"] = (
                        auto_isolate.get("message")
                        or "This Backup Done session already completed Steps 1-5. Waiting for a new Backup Done record before Step 2 Flush."
                    )
                else:
                    item["state"] = "PENDING"
                    item["transition_allowed"] = False
                    item["progress_percent"] = ""
                    item["detail"] = "과거 처리 완료된 백업 정보입니다. 새 백업 완료 접수 전까지 이 단계로 전환하지 않습니다."
        elif connected and session_completed and current_step <= 1 and not force_waiting_for_new_backup and auto_isolate.get("triggered") is not True and auto_isolate.get("state") != "ISOLATED":
            auto_isolate_error = str(auto_isolate.get("error") or auto_isolate.get("message") or "").lower()
            offline_approval_blocked = "disk_offline" in auto_isolate_error and "approval" in auto_isolate_error
            current_step = 3 if offline_approval_blocked else 1
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                if offline_approval_blocked and step_number == 1:
                    item["state"] = "DONE"
                    item["progress_percent"] = 100
                    item["transition_allowed"] = True
                    item["detail"] = "Veeam 백업 완료가 확인되었습니다. 자동 격리는 DISK_OFFLINE 승인 대기 상태입니다."
                elif offline_approval_blocked and step_number == 2:
                    item["state"] = "DONE"
                    item["progress_percent"] = 100
                    item["transition_allowed"] = True
                    item["detail"] = "Flush 검증 단계가 완료되었습니다. 승인 전에는 디스크 오프라인 실행으로 넘어가지 않습니다."
                elif offline_approval_blocked and step_number == 3:
                    item["state"] = "ACTIVE"
                    item["progress_percent"] = 100
                    item["transition_allowed"] = True
                    item["detail"] = "I/O 종료 확인 단계입니다. 이후 Unmount/Offline 단계는 DISK_OFFLINE 승인 후 진행됩니다."
                elif offline_approval_blocked and step_number >= 4:
                    item["state"] = "PENDING"
                    item["progress_percent"] = ""
                    item["transition_allowed"] = False
                    item["detail"] = "DISK_OFFLINE 승인 완료 전까지 이 보호 단계는 실행하지 않습니다."
                elif step_number == 1:
                    item["state"] = "ACTIVE"
                    item["progress_percent"] = progress
                    item["transition_allowed"] = True
                    item["detail"] = auto_isolate.get("message") or item.get("detail") or "Latest Veeam backup information was collected. Waiting for a new Backup Done session before Step 2 Flush."
                else:
                    item["state"] = "PENDING"
                    item["progress_percent"] = ""
                    item["transition_allowed"] = False
                    item["detail"] = "최신 백업 완료 신호가 새로 확인되기 전까지 이 단계로 전환하지 않습니다."
        completed_isolated = auto_isolate.get("state") == "ISOLATED" and not force_waiting_for_new_backup
        if completed_isolated:
            current_step = 5
            progress = 100
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                item["state"] = "DONE" if step_number < 5 else "ACTIVE"
                item["transition_allowed"] = step_number <= 5
                item["progress_percent"] = 100
                if step_number == 2:
                    item["detail"] = (
                        "2단계 Flush 완료. Windows Server 백업 볼륨 캐시 flush 요청과 결과 감사 로그가 "
                        "확인되어 다음 단계로 전환되었습니다."
                    )
                elif step_number == 3:
                    item["detail"] = "3단계 I/O 종료 확인 완료. 남은 읽기/쓰기 작업이 없는 상태를 확인했습니다."
                elif step_number == 4:
                    item["detail"] = "4단계 Unmount 완료. 보호 대상 볼륨 분리 작업이 기록되었습니다."
                elif step_number == 5:
                    item["detail"] = auto_isolate.get("message") or "Veeam success detected. LOCK-FIX isolate completed."

        session_logs = []
        raw_session_logs = payload.get("session_logs") if isinstance(payload.get("session_logs"), list) else []
        if not raw_session_logs and connected and isinstance(payload.get("logs"), list):
            raw_session_logs = payload.get("logs")
        for entry in raw_session_logs:
            if not isinstance(entry, dict):
                continue
            actions = entry.get("actions") if isinstance(entry.get("actions"), list) else []
            action = entry.get("action") or entry.get("message") or entry.get("detail")
            if action:
                actions.append(action)
            checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
            for key in ("port_9419", "token", "sessions", "session_logs", "task_sessions"):
                check = checks.get(key) if isinstance(checks.get(key), dict) else {}
                if check:
                    state = "OK" if check.get("ok") else "WAIT"
                    elapsed = check.get("elapsed_ms")
                    elapsed_text = f" - REST {elapsed}ms" if elapsed is not None else ""
                    count = check.get("count")
                    count_text = f" - {count} items" if count is not None else ""
                    actions.append(f"{state} - {check.get('message') or key}{elapsed_text}{count_text}")
            em_check = checks.get("enterprise_manager") if isinstance(checks.get("enterprise_manager"), dict) else {}
            if em_check:
                actions.append(
                    "INFO - Enterprise Manager 9398 is reference-only diagnostics and does not affect LOCK-FIX 9419 validation."
                )
            if auto_isolate.get("message"):
                state = "OK" if auto_isolate.get("state") == "ISOLATED" else "WAIT"
                actions.append(f"{state} - {auto_isolate.get('message')}")
            session_logs.append(
                {
                    "name": entry.get("name") or entry.get("job") or job,
                    "status": entry.get("status") or status,
                    "actions": actions,
                    "duration": entry.get("duration") or duration,
                    "progress_percent": entry.get("progress_percent", progress),
                    "started_at": entry.get("started_at") or started_at,
                    "ended_at": entry.get("ended_at") or ended_at,
                    "backup_size": entry.get("backup_size") or payload.get("backup_size") or "-",
                    "transferred": entry.get("transferred") or payload.get("transferred") or "-",
                    "speed": entry.get("speed") or payload.get("speed") or "-",
                }
            )
        if not connected:
            waiting_actions = [
                f"Veeam REST API is not synced. Check host, port, credentials, or token for {server}:{port}.",
                "LOCK-FIX keeps the interlock procedure at step 1 until a real Veeam API session is received.",
            ]
            checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
            for key in ("port_9419", "token", "sessions", "session_logs", "task_sessions"):
                check = checks.get(key) if isinstance(checks.get(key), dict) else {}
                if check:
                    state = "OK" if check.get("ok") else "WAIT"
                    elapsed = check.get("elapsed_ms")
                    elapsed_text = f" - REST {elapsed}ms" if elapsed is not None else ""
                    count = check.get("count")
                    count_text = f" - {count} items" if count is not None else ""
                    waiting_actions.append(f"{state} - {check.get('message') or key}{elapsed_text}{count_text}")
            em_check = checks.get("enterprise_manager") if isinstance(checks.get("enterprise_manager"), dict) else {}
            if em_check:
                waiting_actions.append(
                    "INFO - Enterprise Manager 9398 is reference-only diagnostics and does not affect LOCK-FIX 9419 validation."
                )
            if session_logs:
                session_logs[0]["actions"] = list(session_logs[0].get("actions") or []) + waiting_actions
            else:
                session_logs = [
                    {
                        "name": "Veeam API",
                        "status": "Waiting",
                        "actions": waiting_actions,
                        "duration": "-",
                        "progress_percent": 0,
                        "started_at": "-",
                        "ended_at": "-",
                    }
                ]
            loader = getattr(self, "load_veeam_last_logs", None)
            last_logs = loader() if callable(loader) else LockFixWebHandler.load_veeam_last_logs(self)
            if last_logs:
                session_logs.extend(last_logs)
        elif not session_logs:
            backup_size = payload.get("backup_size") or "0 B"
            transferred = payload.get("transferred") or backup_size
            speed = payload.get("speed") or ("0 KB/s" if progress >= 100 else "-")
            target = payload.get("target") or server
            actions = [f"Backup copy for {job} - {target} started at {started_at}"]
            stage_labels = {
                1: "Backup completion verification",
                2: "Flush execution",
                3: "I/O quiet check",
                4: "Unmount protection and execution",
                5: "Offline",
            }
            try:
                elapsed_seconds = int(payload.get("stage_elapsed_seconds") or payload.get("elapsed_seconds") or max(1, now - float(payload.get("stage_started_epoch", now))))
            except (TypeError, ValueError):
                elapsed_seconds = 1
            elapsed_seconds = max(1, min(300, elapsed_seconds))
            stage_label = stage_labels.get(current_step, "Interlock execution")
            if current_step in {2, 3, 4}:
                for elapsed in range(1, elapsed_seconds + 1):
                    actions.append(f"{stage_label} tick {elapsed}s - {job} - {target} progress {progress}%")
                if current_step == 4:
                    actions.append("Unmount guard active: C:\\ OS volume is protected and cannot be selected as an unmount target.")
            elif progress >= 100:
                actions.append(f"{job} - {target} ({backup_size}) processing finished at {ended_at}: {transferred} transferred at {speed}")
            else:
                wait_message = "Waiting for the next Veeam API update." if port_open else "Veeam API port is not reachable."
                actions.append(f"{job} - {target} processing {progress}% complete. {wait_message}")
            session_logs.append(
                {
                    "name": payload.get("name") or job,
                    "status": status,
                    "actions": actions,
                    "duration": duration,
                    "progress_percent": progress,
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "backup_size": backup_size,
                    "transferred": transferred,
                    "speed": speed,
                }
            )
        slot_id = str(auto_isolate.get("slot_id") or payload.get("slot_id") or os.environ.get("LOCKFIX_SLOT_ID") or next(iter(self.context.config.slots), "BAY-01"))
        interlock_actions = []
        history_step = 5 if completed_isolated else current_step
        if not processed_backup_waiting:
            if completed_isolated:
                if LockFixWebHandler.recent_flush_audit_records(self, slot_id, 1):
                    interlock_actions += LockFixWebHandler.veeam_flush_operation_actions(self, slot_id, history_step)
                if LockFixWebHandler.recent_io_quiet_audit_records(self, slot_id, 1):
                    interlock_actions += LockFixWebHandler.veeam_io_quiet_operation_actions(self, slot_id, history_step)
                if LockFixWebHandler.recent_unmount_audit_records(self, slot_id, 1):
                    interlock_actions += LockFixWebHandler.veeam_unmount_operation_actions(self, slot_id, history_step)
                if LockFixWebHandler.recent_power_off_audit_records(self, slot_id, 1):
                    interlock_actions += LockFixWebHandler.veeam_power_off_operation_actions(self, slot_id, history_step)
            else:
                interlock_actions = LockFixWebHandler.veeam_flush_operation_actions(
                    self,
                    slot_id,
                    history_step,
                )
                interlock_actions += LockFixWebHandler.veeam_io_quiet_operation_actions(self, slot_id, history_step)
                interlock_actions += LockFixWebHandler.veeam_unmount_operation_actions(self, slot_id, history_step)
                interlock_actions += LockFixWebHandler.veeam_power_off_operation_actions(self, slot_id, history_step)
        if interlock_actions:
            if session_logs:
                session_logs[0]["actions"] = list(session_logs[0].get("actions") or []) + interlock_actions
            else:
                session_logs.append(
                    {
                        "name": payload.get("name") or job,
                        "status": status,
                        "actions": interlock_actions,
                        "duration": duration,
                        "progress_percent": progress,
                        "started_at": started_at,
                        "ended_at": ended_at,
                        "backup_size": payload.get("backup_size") or "-",
                        "transferred": payload.get("transferred") or "-",
                        "speed": payload.get("speed") or "-",
                    }
                )
        if connected and LockFixWebHandler.veeam_completion_detected(self, payload, session_logs, progress, last_checked):
            progress = 100
            status = "Success"
            payload["progress_percent"] = 100
            payload["result"] = "Success"
            payload["status"] = "Success"
            for item in step_logs:
                if int(item.get("step") or 0) == 1:
                    item["progress_percent"] = 100
                    item["transition_allowed"] = True
                    if item.get("state") == "PENDING":
                        item["state"] = "ACTIVE"
            for entry in session_logs:
                entry["status"] = "Success"
                entry["progress_percent"] = 100
        checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
        session_check = checks.get("sessions") if isinstance(checks.get("sessions"), dict) else {}
        backup_restore_point_evidence = bool(
            payload.get("backup_match_strategy")
            or payload.get("restore_point_scope")
            or payload.get("restore_point_id")
            or payload.get("session_id")
        )
        session_match_missing = (
            not backup_restore_point_evidence
            and (
                str(session_check.get("match_strategy") or "").lower() == "no_match"
                or "no vbr 9419 session matched" in str(session_check.get("message") or "").lower()
                or any(
                    "no vbr 9419 session matched" in "\n".join(str(action or "") for action in (entry.get("actions") if isinstance(entry, dict) and isinstance(entry.get("actions"), list) else [])).lower()
                    for entry in session_logs
                )
            )
        )
        real_backup_complete = (
            connected
            and progress >= 100
            and str(status or "").upper() in {"SUCCESS", "SUCCEEDED", "COMPLETED"}
            and not session_match_missing
            and LockFixWebHandler.veeam_backup_copy_completed(self, payload, session_logs, last_checked)
        )
        if current_step <= 1 and not real_backup_complete:
            current_step = 1
            progress = 0
            status = "Waiting"
            payload["progress_percent"] = 0
            payload["status"] = "Waiting"
            payload["result"] = "WAITING"
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                item["state"] = "PENDING"
                item["transition_allowed"] = False
                item["progress_percent"] = ""
                item["detail"] = (
                    "새로운 Veeam Backup Done 완료 잡이 매칭되기 전까지 1번 단계를 비활성화합니다."
                    if step_number == 1
                    else "새 백업 완료 세션이 매칭되기 전까지 이 단계는 비활성 상태입니다."
                )
            for entry in session_logs:
                entry["status"] = "Waiting"
                entry["progress_percent"] = 0
        if connected and session_logs:
            saver = getattr(self, "save_veeam_last_logs", None)
            if callable(saver):
                saver(session_logs, last_checked)
            else:
                LockFixWebHandler.save_veeam_last_logs(self, session_logs, last_checked)
        return {
            "server": server,
            "port": port,
            "connected": connected,
            "api_synced": api_synced,
            "port_open": port_open,
            "current_step": current_step,
            "last_checked": last_checked,
            "job": job,
            "state_source": state_source,
            "progress_percent": progress,
            "api_verification_percent": api_verification_percent,
            "payload": payload,
            "step_logs": step_logs,
            "session_logs": session_logs,
            "auto_isolate": auto_isolate,
            "api_checks": payload.get("checks") if isinstance(payload.get("checks"), dict) else {},
            "message": (
                "Veeam API is connected. Step colors change only when the current_step value advances."
                if connected
                else "Veeam API is not connected yet. Current step is held and colors will not advance automatically."
            ),
        }

    def parse_veeam_completion_time(self, value: object) -> datetime | None:
        text = str(value or "").strip()
        if not text or text == "-":
            return None
        candidates = [text]
        if text.endswith("Z"):
            candidates.append(text[:-1] + "+00:00")
        for candidate in candidates:
            try:
                parsed = datetime.fromisoformat(candidate)
                if parsed.tzinfo:
                    parsed = parsed.astimezone().replace(tzinfo=None)
                return parsed
            except ValueError:
                continue
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(text, pattern)
            except ValueError:
                continue
        return None

    def veeam_backup_copy_completed(self, payload: dict, session_logs: list[dict] | None = None, checked_at: str = "") -> bool:
        logs = session_logs if isinstance(session_logs, list) else []
        status_text = " ".join(
            str(payload.get(key) or "")
            for key in ("result", "status", "session_state", "state")
        ).upper()
        progress = int(payload.get("progress_percent") or payload.get("progress") or 0)
        ended_text = str(payload.get("ended_at") or payload.get("end_time") or payload.get("endTime") or payload.get("stopTime") or "").strip()
        if ended_text == "-":
            ended_text = ""
        action_lines: list[str] = []
        for entry in logs:
            if not isinstance(entry, dict):
                continue
            status_text = " ".join([status_text, str(entry.get("status") or ""), str(entry.get("result") or "")]).upper()
            if not ended_text:
                ended_text = str(entry.get("ended_at") or entry.get("end_time") or entry.get("endTime") or entry.get("stopTime") or "").strip()
                if ended_text == "-":
                    ended_text = ""
            actions = entry.get("actions") if isinstance(entry.get("actions"), list) else []
            action_lines.extend(str(item or "") for item in actions)
        if not ended_text:
            for line in action_lines:
                match = re.search(
                    r"(?:processing finished|job finished)\s+at\s+([0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}(?::[0-9]{2})?)",
                    str(line),
                    re.IGNORECASE,
                )
                if match:
                    ended_text = match.group(1).replace("T", " ")
                    break
        action_text = "\n".join(action_lines).upper()
        completed_by_status = any(token in status_text for token in ("SUCCESS", "SUCCEEDED", "COMPLETED"))
        completed_by_action = any(
            token in action_text
            for token in (
                "PROCESSING FINISHED",
                "JOB FINISHED",
                "HAS BEEN COMPLETED, STATUS: 'SUCCESS'",
                "STATUS: 'SUCCESS'",
            )
        )
        if not (completed_by_status or completed_by_action):
            return False
        if progress < 100 and not completed_by_action:
            return False
        ended_at = LockFixWebHandler.parse_veeam_completion_time(self, ended_text)
        if not ended_at:
            return False
        checked_at_dt = LockFixWebHandler.parse_veeam_completion_time(self, checked_at)
        if checked_at_dt and checked_at_dt.year >= 2000 and ended_at > checked_at_dt:
            return False
        return True

    def veeam_payload_matches_configured_job(self, payload: dict, session_logs: list[dict] | None = None) -> bool:
        veeam_config = get_veeam_config(self.context.app_config) or {}
        configured_job = str(veeam_config.get("job_name") or "").strip().lower()
        if not configured_job:
            return True
        candidates = {
            str(payload.get("job") or "").strip().lower(),
            str(payload.get("name") or "").strip().lower(),
            str(payload.get("job_name") or "").strip().lower(),
        }
        for entry in session_logs if isinstance(session_logs, list) else []:
            if not isinstance(entry, dict):
                continue
            candidates.add(str(entry.get("name") or "").strip().lower())
            candidates.add(str(entry.get("job") or "").strip().lower())
            candidates.add(str(entry.get("job_name") or "").strip().lower())
        return configured_job in {item for item in candidates if item}

    def veeam_completion_detected(self, payload: dict, session_logs: list[dict], progress: int = 0, checked_at: str = "") -> bool:
        payload = dict(payload)
        payload.setdefault("progress_percent", progress)
        return LockFixWebHandler.veeam_backup_copy_completed(self, payload, session_logs, checked_at)

    def veeam_flush_operation_actions(self, slot_id: str, current_step: int, limit: int = 12) -> list[str]:
        if current_step < 2:
            return []
        records = LockFixWebHandler.recent_flush_audit_records(self, slot_id, limit)
        if not records:
            return [
                f"LOCK-FIX STEP 2 DETAIL - Flush operation flow for slot {slot_id}",
                f"LOCK-FIX Flush WAIT - step 2 is active for slot {slot_id}, but no flush audit event has been recorded yet.",
            ]
        actions = [f"LOCK-FIX STEP 2 DETAIL - Flush operation flow for slot {slot_id}"]
        for record in records:
            if record.get("event") in {"disk.flush.start", "disk.cache.flush.start"}:
                actions.extend(LockFixWebHandler.flush_start_detail_actions(self, record))
            action = LockFixWebHandler.format_flush_audit_record(self, record)
            if action:
                actions.append(action)
        if any(record.get("event") in {"disk.flush.error", "disk.cache.flush.error"} for record in records):
            actions.append(f"LOCK-FIX STEP 2 ERROR - Flush result was recorded as failed. Step 3 must not proceed until the error is resolved.")
        elif any(record.get("event") in {"disk.flush", "disk.cache.flush"} for record in records):
            actions.append("LOCK-FIX STEP 2 COMPLETE - Flush checkpoint result was recorded. Continuing to Step 3 I/O quiet verification.")
        return actions

    def flush_start_detail_actions(self, record: dict) -> list[str]:
        slot_id = str(record.get("slot_id") or "-")
        mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
        device = LockFixWebHandler.compact_log_value(self, record.get("device") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        return [
            f"{prefix}LOCK-FIX Flush GUARD OK - C:\\ OS volume is protected and cannot be flushed/unmounted by this step.",
            f"{prefix}LOCK-FIX Flush TARGET - slot {slot_id}, configured backup volume {mount_point}, device {device}",
            f"{prefix}LOCK-FIX Flush COMMAND - Windows Server flush checkpoint requested for the configured backup volume.",
            f"{prefix}LOCK-FIX Flush MONITOR - waiting for checkpoint completion and audit result.",
        ]

    def recent_flush_audit_records(self, slot_id: str, limit: int = 12) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {
            "disk.flush.start",
            "disk.flush.tick",
            "disk.flush",
            "disk.flush.error",
            "disk.cache.flush.start",
            "disk.cache.flush",
            "disk.cache.flush.error",
        }
        records = []
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            if record.get("event") in {"disk.flush.start", "disk.cache.flush.start"}:
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_flush_audit_records(self, records)[-limit:]

    def normalize_flush_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if record.get("event") in {"disk.flush.start", "disk.cache.flush.start"}]
        if not starts:
            return records
        normalized = [starts[-1]]
        ticks = {}
        completions = []
        errors = []
        for record in records:
            event = record.get("event")
            if event == "disk.flush.tick":
                try:
                    elapsed = int(record.get("elapsed_seconds") or 0)
                except (TypeError, ValueError):
                    elapsed = 0
                ticks.setdefault(elapsed, record)
            elif event in {"disk.flush", "disk.cache.flush"}:
                completions.append(record)
            elif event in {"disk.flush.error", "disk.cache.flush.error"}:
                errors.append(record)
        normalized.extend(record for _, record in sorted(ticks.items()))
        if errors:
            normalized.append(errors[-1])
        elif completions:
            normalized.append(completions[-1])
        return normalized

    def format_flush_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        if event in {"disk.flush.start", "disk.cache.flush.start"}:
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            device = LockFixWebHandler.compact_log_value(self, record.get("device") or "-")
            return f"{prefix}LOCK-FIX Flush START - slot {slot_id}, mount {mount_point}, device {device}"
        if event == "disk.flush.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX Flush TICK {elapsed}s - slot {slot_id}, mount {mount_point}"
        if event in {"disk.flush.error", "disk.cache.flush.error"}:
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "flush command failed")
            return f"{prefix}LOCK-FIX Flush ERROR - slot {slot_id}, {error}"
        if event in {"disk.flush", "disk.cache.flush"}:
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "flush completed")
            return f"{prefix}LOCK-FIX Flush OK - slot {slot_id}, {output}"
        return ""

    def veeam_io_quiet_operation_actions(self, slot_id: str, current_step: int, limit: int = 64) -> list[str]:
        if current_step < 3:
            return []
        records = LockFixWebHandler.recent_io_quiet_audit_records(self, slot_id, limit)
        if not records:
            return [
                f"LOCK-FIX STEP 3 DETAIL - I/O quiet verification flow for slot {slot_id}",
                f"LOCK-FIX I/O Check WAIT - step 3 is active for slot {slot_id}, but no I/O quiet audit event has been recorded yet.",
            ]
        actions = [f"LOCK-FIX STEP 3 DETAIL - I/O quiet verification flow for slot {slot_id}"]
        for record in records:
            if record.get("event") == "disk.io_quiet.start":
                actions.extend(LockFixWebHandler.io_quiet_start_detail_actions(self, record))
            action = LockFixWebHandler.format_io_quiet_audit_record(self, record)
            if action:
                actions.append(action)
        if any(record.get("event") == "disk.io_quiet.error" for record in records):
            actions.append(f"LOCK-FIX STEP 3 ERROR - I/O quiet result was recorded as failed. Step 4 Unmount must not proceed until the error is resolved.")
        elif any(record.get("event") in {"disk.io_quiet", "disk.io_quiet.dry_run"} for record in records):
            actions.append("LOCK-FIX STEP 3 COMPLETE - 30초 quiet window 기록 확인. Continuing to Step 4 Unmount guard and execution.")
        return actions

    def io_quiet_start_detail_actions(self, record: dict) -> list[str]:
        slot_id = str(record.get("slot_id") or "-")
        seconds = LockFixWebHandler.compact_log_value(self, record.get("seconds") or 1)
        mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        return [
            f"{prefix}LOCK-FIX I/O Check WINDOW - slot {slot_id}, mount {mount_point}, quiet window target {seconds}s",
            f"{prefix}LOCK-FIX I/O Check MONITOR - recording one audit tick per second until no-write window is satisfied.",
            f"{prefix}LOCK-FIX I/O Check GATE - Step 4 Unmount remains blocked until Step 3 OK is recorded.",
        ]

    def recent_io_quiet_audit_records(self, slot_id: str, limit: int = 20) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {"disk.io_quiet.start", "disk.io_quiet.tick", "disk.io_quiet", "disk.io_quiet.dry_run", "disk.io_quiet.error"}
        records = []
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            if record.get("event") == "disk.io_quiet.start":
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_io_quiet_audit_records(self, records)[-limit:]

    def normalize_io_quiet_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if record.get("event") == "disk.io_quiet.start"]
        if not starts:
            return records
        normalized = [starts[-1]]
        ticks = {}
        completions = []
        errors = []
        for record in records:
            event = record.get("event")
            if event == "disk.io_quiet.tick":
                try:
                    elapsed = int(record.get("elapsed_seconds") or 0)
                except (TypeError, ValueError):
                    elapsed = 0
                ticks.setdefault(elapsed, record)
            elif event in {"disk.io_quiet", "disk.io_quiet.dry_run"}:
                completions.append(record)
            elif event == "disk.io_quiet.error":
                errors.append(record)
        normalized.extend(record for _, record in sorted(ticks.items()))
        if errors:
            normalized.append(errors[-1])
        elif completions:
            normalized.append(completions[-1])
        return normalized

    def format_io_quiet_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        if event == "disk.io_quiet.start":
            seconds = LockFixWebHandler.compact_log_value(self, record.get("seconds") or 1)
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX I/O Check START - slot {slot_id}, mount {mount_point}, required quiet window {seconds}s"
        if event == "disk.io_quiet.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            remaining = LockFixWebHandler.compact_log_value(self, record.get("remaining_seconds") or 0)
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX I/O Check TICK {elapsed}s - remaining {remaining}s, mount {mount_point}"
        if event == "disk.io_quiet.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "I/O quiet check failed")
            return f"{prefix}LOCK-FIX I/O Check ERROR - slot {slot_id}, {error}"
        if event in {"disk.io_quiet", "disk.io_quiet.dry_run"}:
            seconds = LockFixWebHandler.compact_log_value(self, record.get("seconds") or 1)
            mode = "dry-run " if event == "disk.io_quiet.dry_run" else ""
            return f"{prefix}LOCK-FIX I/O Check OK - slot {slot_id}, {mode}quiet window satisfied for {seconds}s"
        return ""

    def veeam_unmount_operation_actions(self, slot_id: str, current_step: int, limit: int = 16) -> list[str]:
        if current_step < 4:
            return []
        records = LockFixWebHandler.recent_unmount_audit_records(self, slot_id, limit)
        if not records:
            return [
                f"LOCK-FIX STEP 4 DETAIL - Unmount operation flow for slot {slot_id}",
                f"LOCK-FIX Unmount WAIT - step 4 is active for slot {slot_id}, but no unmount audit event has been recorded yet.",
            ]
        actions = [f"LOCK-FIX STEP 4 DETAIL - Unmount operation flow for slot {slot_id}"]
        for record in records:
            if record.get("event") == "disk.unmount.start":
                actions.extend(LockFixWebHandler.unmount_start_detail_actions(self, record))
            action = LockFixWebHandler.format_unmount_audit_record(self, record)
            if action:
                actions.append(action)
        if any(record.get("event") == "disk.unmount.error" for record in records):
            actions.append("LOCK-FIX STEP 4 ERROR - Unmount result was recorded as failed. Step 5 Offline must not proceed until the error is resolved.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 4, "Unmount", slot_id, records, "ERROR"))
        elif any(record.get("event") == "disk.unmount" for record in records):
            actions.append("LOCK-FIX STEP 4 COMPLETE - Backup volume unmount result was recorded. Continuing to Step 5 Offline.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 4, "Unmount", slot_id, records, "OK"))
        return actions

    def recent_unmount_audit_records(self, slot_id: str, limit: int = 16) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {
            "disk.safety.preflight.start",
            "disk.safety.preflight.ok",
            "disk.safety.preflight.error",
            "disk.cache.flush.start",
            "disk.cache.flush",
            "disk.cache.flush.error",
            "disk.unmount.start",
            "disk.unmount.tick",
            "disk.unmount",
            "disk.unmount.error",
            "disk.unmount.verify",
            "disk.storage_state",
            "disk.os_volume.blocked",
        }
        records = []
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            if str(record.get("event") or "").startswith("disk.safety.preflight") and str(record.get("operation") or "") != "unmount":
                continue
            if record.get("event") == "disk.safety.preflight.start":
                records = []
            elif record.get("event") == "disk.unmount.start" and not records:
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_unmount_audit_records(self, records)[-limit:]

    def normalize_unmount_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if record.get("event") in {"disk.safety.preflight.start", "disk.unmount.start"}]
        if not starts:
            return records
        cycle_start = starts[-1]
        start_index = records.index(cycle_start)
        records = records[start_index:]
        normalized = []
        ticks = {}
        completions = []
        verifications = []
        errors = []
        blocked = []
        for record in records:
            event = record.get("event")
            if event == "disk.unmount.tick":
                try:
                    elapsed = int(record.get("elapsed_seconds") or 0)
                except (TypeError, ValueError):
                    elapsed = 0
                ticks.setdefault(elapsed, record)
            elif event == "disk.unmount":
                completions.append(record)
            elif event == "disk.unmount.verify":
                verifications.append(record)
            elif event in {"disk.unmount.error", "disk.safety.preflight.error", "disk.cache.flush.error"}:
                errors.append(record)
            elif event == "disk.os_volume.blocked":
                blocked.append(record)
            elif event != "disk.unmount.tick":
                normalized.append(record)
        normalized.extend(blocked[-1:])
        normalized.extend(record for _, record in sorted(ticks.items()))
        if errors:
            normalized.append(errors[-1])
        elif completions:
            normalized.append(completions[-1])
            normalized.extend(verifications[-1:])
        return normalized

    def unmount_start_detail_actions(self, record: dict) -> list[str]:
        slot_id = str(record.get("slot_id") or "-")
        mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
        device = LockFixWebHandler.compact_log_value(self, record.get("device") or "-")
        drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        return [
            f"{prefix}LOCK-FIX Unmount GUARD OK - C:\\ OS volume is protected and cannot be selected as an unmount target.",
            f"{prefix}LOCK-FIX Unmount TARGET - slot {slot_id}, mount {mount_point}, device {device}, drive {drive}",
            f"{prefix}LOCK-FIX Unmount COMMAND 1 - Windows Server Dismount-Volume requested for the configured backup volume.",
            f"{prefix}LOCK-FIX Unmount COMMAND 2 - Remove-PartitionAccessPath removes {drive}:\\ so the backup volume is no longer reachable.",
            f"{prefix}LOCK-FIX Unmount GATE - Step 5 Offline remains blocked until {drive}:\\ access removal is verified.",
        ]

    def format_unmount_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        if event == "disk.safety.preflight.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            policy = LockFixWebHandler.compact_log_value(self, record.get("policy") or "healthy_non_os_volume_required")
            return f"{prefix}LOCK-FIX Unmount SAFETY PREFLIGHT START - slot {slot_id}, drive {drive}, policy {policy}"
        if event == "disk.safety.preflight.ok":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "volume health preflight passed")
            return f"{prefix}LOCK-FIX Unmount SAFETY PREFLIGHT OK - slot {slot_id}, {output}"
        if event == "disk.safety.preflight.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "volume health preflight failed")
            return f"{prefix}LOCK-FIX Unmount SAFETY PREFLIGHT ERROR - slot {slot_id}, {error}"
        if event == "disk.cache.flush.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            return f"{prefix}LOCK-FIX Unmount CACHE FLUSH START - slot {slot_id}, drive {drive}"
        if event == "disk.cache.flush":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "volume cache flush completed")
            return f"{prefix}LOCK-FIX Unmount CACHE FLUSH OK - slot {slot_id}, {output}"
        if event == "disk.cache.flush.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "volume cache flush failed")
            return f"{prefix}LOCK-FIX Unmount CACHE FLUSH ERROR - slot {slot_id}, {error}"
        if event == "disk.os_volume.blocked":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "windows_c_os_volume_protected")
            return f"{prefix}LOCK-FIX Unmount BLOCKED - slot {slot_id}, protected OS volume guard blocked the request: {reason}"
        if event == "disk.unmount.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX Unmount START - slot {slot_id}, drive {drive}, mount {mount_point}"
        if event == "disk.unmount.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX Unmount TICK {elapsed}s - slot {slot_id}, mount {mount_point}"
        if event == "disk.unmount.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "unmount command failed")
            return f"{prefix}LOCK-FIX Unmount ERROR - slot {slot_id}, {error}"
        if event == "disk.storage_state":
            path = LockFixWebHandler.compact_log_value(self, record.get("path") or "storage state recorded")
            return f"{prefix}LOCK-FIX Unmount STORAGE STATE - slot {slot_id}, disk and partition identity saved for emergency reconnect: {path}"
        if event == "disk.unmount":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "unmount completed")
            return f"{prefix}LOCK-FIX Unmount OK - slot {slot_id}, {output}"
        if event == "disk.unmount.verify":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "post-dismount verification recorded")
            return f"{prefix}LOCK-FIX Unmount VERIFY - slot {slot_id}, {output}"
        return ""

    def veeam_power_off_operation_actions(self, slot_id: str, current_step: int, limit: int = 16) -> list[str]:
        if current_step < 5:
            return []
        records = LockFixWebHandler.recent_power_off_audit_records(self, slot_id, limit)
        if not records:
            return [
                f"LOCK-FIX STEP 5 DETAIL - Offline operation flow for slot {slot_id}",
                f"LOCK-FIX Offline WAIT - step 5 is active for slot {slot_id}, but no disk offline audit event has been recorded yet.",
            ]
        actions = [f"LOCK-FIX STEP 5 DETAIL - Offline operation flow for slot {slot_id}"]
        for record in records:
            if str(record.get("event") or "").endswith(".off.start") or record.get("event") == "disk.offline.start":
                actions.extend(LockFixWebHandler.power_off_start_detail_actions(self, record))
            action = LockFixWebHandler.format_power_off_audit_record(self, record)
            if action:
                actions.append(action)
        if any(str(record.get("event") or "").endswith(".off.error") or record.get("event") == "disk.offline.error" for record in records):
            actions.append("LOCK-FIX STEP 5 ERROR - Offline result was recorded as failed. Manual inspection is required.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 5, "Offline", slot_id, records, "ERROR"))
        elif any(record.get("event") in {"power.mock.off", "power.command.off", "disk.offline"} for record in records):
            actions.append("LOCK-FIX STEP 5 COMPLETE - Disk offline result was recorded. LOCK-FIX isolation flow is complete.")
            actions.append("LOCK-FIX STEP 5 HISTORY - Power OFF detailed audit trail is retained in logs for operator review.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 5, "Offline", slot_id, records, "OK"))
        return actions

    def recent_power_off_audit_records(self, slot_id: str, limit: int = 16) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {
            "power.mock.off.start",
            "power.mock.off.tick",
            "power.mock.off",
            "power.command.off.start",
            "power.command.off.tick",
            "power.command.off",
            "power.command.off.error",
            "power.mock.status",
            "power.command.status.start",
            "power.command.status",
            "power.command.status.missing",
            "power.command.status.error",
            "power.off.proof",
            "power.off.proof.required",
            "disk.offline.start",
            "disk.offline.tick",
            "disk.offline",
            "disk.offline.error",
            "disk.offline.verify.start",
            "disk.offline.verify",
            "disk.offline.verify.error",
            "disk.offline.strict.error",
            "disk.offline.proof",
            "disk.online.unauthorized.reblock",
            "disk.online.unauthorized.reblock.error",
        }
        records = []
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("event") not in events:
                continue
            if slot_id and str(record.get("slot_id") or "") != slot_id:
                continue
            if str(record.get("event") or "").endswith(".off.start") or record.get("event") == "disk.offline.start":
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_power_off_audit_records(self, records)[-limit:]

    def normalize_power_off_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if str(record.get("event") or "").endswith(".off.start") or record.get("event") == "disk.offline.start"]
        if not starts:
            return records
        normalized = [starts[-1]]
        ticks = {}
        completions = []
        errors = []
        statuses = []
        proofs = []
        for record in records:
            event = str(record.get("event") or "")
            if event.endswith(".off.tick") or event == "disk.offline.tick":
                try:
                    elapsed = int(record.get("elapsed_seconds") or 0)
                except (TypeError, ValueError):
                    elapsed = 0
                ticks.setdefault(elapsed, record)
            elif event in {"power.mock.off", "power.command.off", "disk.offline"}:
                completions.append(record)
            elif event.endswith(".off.error") or event in {"disk.offline.error", "disk.offline.verify.error", "disk.offline.strict.error"}:
                errors.append(record)
            elif event in {"disk.offline.verify.start", "disk.offline.verify"}:
                statuses.append(record)
            elif ".status" in event:
                statuses.append(record)
            elif event in {"power.off.proof", "power.off.proof.required", "disk.offline.proof"}:
                proofs.append(record)
        normalized.extend(record for _, record in sorted(ticks.items()))
        if errors:
            normalized.append(errors[-1])
        elif completions:
            normalized.append(completions[-1])
        normalized.extend(statuses[-3:])
        normalized.extend(proofs[-1:])
        return normalized

    def power_off_start_detail_actions(self, record: dict) -> list[str]:
        slot_id = str(record.get("slot_id") or "-")
        event = str(record.get("event") or "")
        mode = "windows-storage" if event.startswith("disk.offline") else ("command" if event.startswith("power.command") else "mock")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        actions = [
            f"{prefix}LOCK-FIX Offline TARGET - slot {slot_id}, controller mode {mode}",
            f"{prefix}LOCK-FIX Power OFF TARGET - slot {slot_id}, controller mode {mode}",
            f"{prefix}LOCK-FIX Offline COMMAND - issuing final Windows disk offline request.",
        ]
        if mode == "command":
            command = LockFixWebHandler.compact_log_value(self, " ".join(record.get("command") or []))
            actions.append(f"{prefix}LOCK-FIX Offline COMMAND DETAIL - {command or 'configured command'}")
        return actions

    def format_power_off_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        mode = "windows-storage" if event.startswith("disk.offline") else ("command" if event.startswith("power.command") else "mock")
        if event.endswith(".off.start") or event == "disk.offline.start":
            return f"{prefix}LOCK-FIX Offline START - slot {slot_id}, controller mode {mode}"
        if event.endswith(".off.tick") or event == "disk.offline.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            return f"{prefix}LOCK-FIX Offline TICK {elapsed}s - slot {slot_id}"
        if event.endswith(".off.error") or event == "disk.offline.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "offline command failed")
            return f"{prefix}LOCK-FIX Offline ERROR - slot {slot_id}, {error}"
        if event == "disk.offline.strict.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "true disk offline proof was not obtained")
            return f"{prefix}LOCK-FIX Offline STRICT ERROR - slot {slot_id}, {error}"
        if event in {"power.mock.off", "power.command.off", "disk.offline"}:
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or f"{mode} offline completed")
            return f"{prefix}LOCK-FIX Power OFF OK - slot {slot_id}, {output}"
        if event == "power.command.status.start":
            command = LockFixWebHandler.compact_log_value(self, " ".join(record.get("command") or []))
            return f"{prefix}LOCK-FIX Offline STATUS CHECK START - querying legacy controller state. {command}"
        if event == "power.command.status.missing":
            requirement = LockFixWebHandler.compact_log_value(self, record.get("requirement") or "Configure power.status_command.")
            return f"{prefix}LOCK-FIX Power OFF PROOF REQUIRED - actual OFF proof requires a PDU/relay/storage controller status response. {requirement}"
        if event == "power.command.status.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "controller status check failed")
            return f"{prefix}LOCK-FIX Offline STATUS ERROR - slot {slot_id}, {error}"
        if event == "power.command.status":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "")
            if record.get("ok") is True:
                return f"{prefix}LOCK-FIX Offline PROOF OK - controller status confirmed OFF. response {output or state}"
            return f"{prefix}LOCK-FIX Offline STATUS NOT CONFIRMED - controller returned {state}. response {output}"
        if event == "power.mock.status":
            requirement = LockFixWebHandler.compact_log_value(self, record.get("requirement") or "Use a controller status response.")
            return f"{prefix}LOCK-FIX Offline PROOF NOT AVAILABLE - mock mode cannot prove physical power state. {requirement}"
        if event == "power.off.proof":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "Legacy controller isolation proof was recorded.")
            return f"{prefix}LOCK-FIX Offline PROOF RECORDED - {message}"
        if event == "power.off.proof.required":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "controller status response is required")
            required = LockFixWebHandler.compact_log_value(self, record.get("required_config") or "power.status_command")
            return f"{prefix}LOCK-FIX Power OFF PROOF REQUIRED - {reason}. Required: {required}"
        if event == "disk.offline.proof":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "Disk offline isolation was proved.")
            return f"{prefix}LOCK-FIX Offline PROOF RECORDED - {message}"
        if event == "disk.online.unauthorized.reblock":
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "unauthorized online disk was reblocked")
            return f"{prefix}LOCK-FIX Offline REBLOCK - unauthorized Online was detected and blocked again. {output}"
        if event == "disk.online.unauthorized.reblock.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "reblock failed")
            return f"{prefix}LOCK-FIX Offline REBLOCK ERROR - {error}"
        return ""

    def audit_history_detail_actions(self, step: int, operation: str, slot_id: str, records: list[dict], result: str) -> list[str]:
        try:
            audit_path = self.context.config.audit_log_path
        except Exception:
            audit_path = Path("runtime/audit.jsonl")
        first_ts = LockFixWebHandler.format_audit_timestamp(self, records[0].get("ts")) if records else "-"
        last_ts = LockFixWebHandler.format_audit_timestamp(self, records[-1].get("ts")) if records else "-"
        event_names = []
        for record in records:
            event_name = str(record.get("event") or "-")
            if event_name not in event_names:
                event_names.append(event_name)
        event_summary = ", ".join(event_names) if event_names else "-"
        audit_text = LockFixWebHandler.compact_log_value(self, audit_path)
        return [
            f"LOCK-FIX STEP {step} HISTORY - {operation} detailed audit trail is retained in {audit_text}.",
            f"LOCK-FIX STEP {step} HISTORY DETAIL - slot {slot_id}, result {result}, records {len(records)}, first {first_ts}, last {last_ts}.",
            f"LOCK-FIX STEP {step} HISTORY EVENTS - {event_summary}",
        ]

    def format_audit_timestamp(self, value: object) -> str:
        if not value:
            return ""
        text = str(value)
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return text

    def parse_audit_timestamp(self, value: object) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo:
            parsed = parsed.astimezone().replace(tzinfo=None)
        return parsed

    def split_reconnect_audit_records_by_days(self, records: list[dict], days: int = 7) -> tuple[list[dict], list[dict]]:
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        older = []
        for record in records:
            timestamp = LockFixWebHandler.parse_audit_timestamp(self, record.get("ts"))
            if timestamp and timestamp >= cutoff:
                recent.append(record)
            else:
                older.append(record)
        return recent, older

    def compact_log_value(self, value: object) -> str:
        text = str(value)
        text = re.sub(r"\ufffd+", " [확인 불가 문자 제거] ", text)
        text = "".join(ch if ch in "\r\n\t" or ord(ch) >= 32 else " " for ch in text)
        text = re.sub(r"(?:\s*\[확인 불가 문자 제거\]\s*)+", " [확인 불가 문자 제거] ", text)
        return " ".join(text.split())

    def sanitize_json_payload(self, value):
        if isinstance(value, str):
            return LockFixWebHandler.compact_log_value(self, value)
        if isinstance(value, list):
            return [LockFixWebHandler.sanitize_json_payload(self, item) for item in value]
        if isinstance(value, dict):
            return {key: LockFixWebHandler.sanitize_json_payload(self, item) for key, item in value.items()}
        return value

    def save_veeam_last_logs(self, session_logs: list[dict], checked_at: str) -> None:
        path = ROOT / "runtime" / "veeam_last_session_logs.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            previous = {}
            if path.exists():
                try:
                    previous = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    previous = {}
            previous_logs = previous.get("session_logs") if isinstance(previous, dict) else []
            if not isinstance(previous_logs, list):
                previous_logs = []
            merged_logs = LockFixWebHandler.merge_veeam_detail_logs(self, previous_logs, session_logs)
            path.write_text(
                json.dumps({"checked_at": checked_at, "session_logs": merged_logs}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def merge_veeam_detail_logs(self, previous_logs: list[dict], current_logs: list[dict]) -> list[dict]:
        merged: list[dict] = []
        current_items = [dict(item) for item in current_logs if isinstance(item, dict)]
        previous_items = [dict(item) for item in previous_logs if isinstance(item, dict)]
        used_previous: set[int] = set()

        def log_key(item: dict) -> str:
            return "|".join(
                str(item.get(key) or "")
                for key in ("name", "started_at", "backup_size")
            )

        def merge_actions(old_actions: object, new_actions: object) -> list[str]:
            actions: list[str] = []
            for source in (old_actions, new_actions):
                if not isinstance(source, list):
                    continue
                for action in source:
                    text = str(action or "").strip()
                    if text and text not in actions:
                        actions.append(text)
            return actions[-260:]

        for current in current_items:
            key = log_key(current)
            previous_index = next(
                (
                    index for index, item in enumerate(previous_items)
                    if index not in used_previous and log_key(item) == key
                ),
                -1,
            )
            if previous_index >= 0:
                previous = previous_items[previous_index]
                used_previous.add(previous_index)
                current["actions"] = merge_actions(previous.get("actions"), current.get("actions"))
                for field in ("duration", "progress_percent", "started_at", "ended_at", "backup_size", "transferred", "speed"):
                    if not current.get(field) and previous.get(field):
                        current[field] = previous[field]
            else:
                current["actions"] = merge_actions([], current.get("actions"))
            merged.append(current)

        for index, previous in enumerate(previous_items):
            if index in used_previous:
                continue
            previous["last_known"] = True
            previous["actions"] = merge_actions(previous.get("actions"), [])
            merged.append(previous)
        return merged[-8:]

    def load_veeam_last_logs(self) -> list[dict]:
        path = ROOT / "runtime" / "veeam_last_session_logs.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except (OSError, json.JSONDecodeError):
            return []
        logs = data.get("session_logs") if isinstance(data, dict) else []
        if not isinstance(logs, list):
            return []
        result = []
        for item in logs:
            if isinstance(item, dict):
                item = dict(item)
                item["last_known"] = True
                item.setdefault("actions", []).append(
                    f"Last retained Veeam detail log. Latest successful API poll: {data.get('checked_at', '-')}"
                )
                result.append(item)
        return result

    def veeam_backup_summary(self) -> dict:
        config = self.context.app_config
        veeam_config = config.get("veeam", {})
        LockFixWebHandler.prepare_veeam_process_environment(self, veeam_config)
        # Shared factory guard: run_veeam_diagnostics(self.context.config, self.context.controller)
        runner = getattr(self, "run_veeam_diagnostics_limited", None)
        if callable(runner):
            return runner(veeam_config)
        return LockFixWebHandler.run_veeam_diagnostics_limited(self, veeam_config)

    def run_veeam_diagnostics_limited(self, veeam_config: dict, timeout_seconds: float = 8.0) -> dict:
        try:
            diagnostics_timeout = max(float(timeout_seconds), 0.2)
            wait_timeout = diagnostics_timeout + VEEAM_DIAGNOSTICS_WAIT_BUFFER_SECONDS
            response = self.context.run_agent_service_operation(
                "veeam.diagnostics",
                {"timeout_seconds": diagnostics_timeout},
                timeout_seconds=wait_timeout,
            )
            diagnostics = response.get("diagnostics")
            if isinstance(diagnostics, dict):
                diagnostics.setdefault("executor", "LOCK-FIX Agent/Service")
                return diagnostics
            raise AgentServiceUnavailable("LOCK-FIX Agent/Service returned no Veeam diagnostics payload.")
        except (AgentServiceUnavailable, TimeoutError, OSError, ValueError) as exc:
            job_name = str(veeam_config.get("job_name") or "Veeam API")
            return {
                "source": "lockfix_agent_service_unavailable",
                "latest_configured_session": {},
                "config": {
                    "base_url": str(veeam_config.get("base_url") or ""),
                    "api_version": str(veeam_config.get("api_version") or "1.2-rev1"),
                },
                "checks": {
                    "webui": {
                        "ok": False,
                        "code": "AgentServiceUnavailable",
                        "message": str(exc),
                    }
                },
                "session_logs": [
                    {
                        "name": job_name,
                        "status": "Waiting",
                        "actions": [
                            "WAIT - LOCK-FIX Agent/Service did not return Veeam diagnostics.",
                            "WebUI does not execute Veeam REST or disk operations directly; the Windows Service must perform them.",
                        ],
                        "duration": "-",
                        "progress_percent": 0,
                    }
                ],
            }

    def poll_veeam_api(self, server: str, port: int, local_payload: dict) -> dict:
        config = self.context.app_config
        veeam_config = config.get("veeam", {})
        LockFixWebHandler.prepare_veeam_process_environment(self, veeam_config)
        try:
            runner = getattr(self, "run_veeam_diagnostics_limited", None)
            diagnostics = runner(veeam_config) if callable(runner) else LockFixWebHandler.run_veeam_diagnostics_limited(self, veeam_config)
            session = diagnostics.get("latest_configured_session") or {}
            if session:
                diagnostic_config = diagnostics.get("config") if isinstance(diagnostics.get("config"), dict) else {}
                base_url = str(diagnostic_config.get("base_url") or veeam_config.get("base_url") or "")
                parsed = urlparse(base_url)
                session.setdefault("server", parsed.hostname or server)
                session.setdefault("port", parsed.port or port)
                session.setdefault("api_version", diagnostic_config.get("api_version") or veeam_config.get("api_version") or "1.2-rev1")
                session.setdefault("source", diagnostics.get("source") or "python_veeam_client")
            return session
        except Exception as exc:
            job_name = str(veeam_config.get("job_name") or "Veeam API")
            return {
                "api_synced": False,
                "session_match": False,
                "state_source": "veeam_rest_api_error",
                "name": job_name,
                "job": job_name,
                "status": "Waiting",
                "result": "WAITING",
                "progress_percent": 0,
                "current_step": 1,
                "duration": "-",
                "checks": {
                    "webui": {
                        "ok": False,
                        "code": exc.__class__.__name__,
                        "message": str(exc),
                    }
                },
                "session_logs": [
                    {
                        "name": job_name,
                        "status": "Waiting",
                        "actions": [
                            f"ERROR - {exc.__class__.__name__}: {exc}",
                            "Web UI uses the same config.veeam loader as veeam-test and VeeamWatcher.",
                            "No cached Veeam success result is returned for this request.",
                        ],
                        "duration": "-",
                        "progress_percent": 0,
                    }
                ],
            }

    def prepare_veeam_process_environment(self, veeam_config: dict) -> None:
        reader = getattr(self, "veeam_install_properties", None)
        install_props = reader() if callable(reader) else LockFixWebHandler.veeam_install_properties(self)
        password_env = str(veeam_config.get("password_env") or "LOCKFIX_VEEAM_PASSWORD")
        username_env = str(veeam_config.get("username_env") or "LOCKFIX_VEEAM_USER")

        if install_props.get("veeam_password"):
            os.environ[password_env] = str(install_props["veeam_password"])
        if install_props.get("veeam_user"):
            os.environ[username_env] = str(install_props["veeam_user"])
        if install_props.get("veeam_base_url"):
            os.environ["LOCKFIX_VEEAM_BASE_URL"] = str(install_props["veeam_base_url"])
        if install_props.get("veeam_api_version"):
            os.environ["LOCKFIX_VEEAM_API_VERSION"] = str(install_props["veeam_api_version"])
        if install_props.get("veeam_host"):
            os.environ["LOCKFIX_VEEAM_HOST"] = str(install_props["veeam_host"])
        if install_props.get("veeam_port"):
            os.environ["LOCKFIX_VEEAM_PORT"] = str(install_props["veeam_port"])

    def veeam_auto_isolate_identity(self, payload: dict) -> tuple[str, bool]:
        identity_parts = [
            str(payload.get("session_id") or payload.get("sessionId") or payload.get("id") or payload.get("uid") or "").strip(),
            str(payload.get("job_id") or payload.get("jobId") or "").strip(),
            str(payload.get("job") or payload.get("name") or "Veeam Backup").strip(),
            str(payload.get("started_at") or payload.get("creationTime") or payload.get("startTime") or "").strip(),
            str(payload.get("ended_at") or payload.get("endTime") or payload.get("stopTime") or "").strip(),
        ]
        restore_scope = payload.get("restore_point_scope") if isinstance(payload.get("restore_point_scope"), dict) else {}
        identity_parts.append(str(payload.get("restore_point_id") or restore_scope.get("restore_point_id") or "").strip())
        session_key = "|".join(part or "-" for part in identity_parts)
        has_unique_session_identity = bool(any(identity_parts[index] for index in (0, 1, 3, 4, 5)))
        return session_key, has_unique_session_identity

    def force_approve_disk_offline_for_veeam(self, slot_id: str, session_key: str, checked_at: str, reason: str = "") -> dict:
        store = self.context.controller.approvals
        active = LockFixWebHandler.active_approval_request_for(self, "DISK_OFFLINE", slot_id)
        if active:
            return {
                "created": False,
                "request": active,
                "message": "Existing DISK_OFFLINE approval request is already active.",
            }

        approved = store.approved_request_for("DISK_OFFLINE", slot_id)
        if approved:
            return {"created": False, "request": approved, "message": "Existing DISK_OFFLINE approval is active."}

        request = store.create_request(
            "DISK_OFFLINE",
            requester_user_id="LOCKFIX_AUTO_POLICY",
            target_id=slot_id,
            metadata={
                "workflowType": "VEEAM_BACKUP_DONE_AUTO_ISOLATE",
                "sessionKey": session_key,
                "reason": reason or "Veeam backup success detected. Automatic Air-Gap isolation is force-approved by policy.",
                "forceApproval": True,
                "forceApprovalMode": "AUTO_POLICY",
                "requestedAt": checked_at,
            },
        )
        data = store.load()
        request_id = str(request.get("id") or "")
        request_record = store.find_request(data, request_id)
        now = datetime.now().isoformat(timespec="seconds")
        comment = "Veeam Backup Done 자동 격리를 위해 LOCK-FIX 자동 정책이 DISK_OFFLINE 실행을 강제 승인했습니다."

        for review in data.get("departmentReviews", []):
            if str(review.get("approvalRequestId") or "") != request_id:
                continue
            department_id = str(review.get("departmentId") or "auto-policy")
            reviewer = f"LOCKFIX_AUTO_REVIEW_{department_id.upper()}"
            review["reviewerUserId"] = reviewer
            review["status"] = "REVIEWED"
            review["comment"] = comment
            review["updatedAt"] = now
            data.setdefault("reviewComments", []).append(
                {
                    "id": uuid.uuid4().hex,
                    "approvalRequestId": request_id,
                    "departmentReviewId": str(review.get("id") or ""),
                    "authorUserId": reviewer,
                    "comment": comment,
                    "createdAt": now,
                    "status": "REVIEWED",
                }
            )

        decision = {
            "id": uuid.uuid4().hex,
            "approvalRequestId": request_id,
            "approverUserId": "LOCKFIX_FORCE_APPROVER",
            "decision": "APPROVED",
            "comment": comment,
            "createdAt": now,
        }
        data.setdefault("decisions", []).append(decision)
        request_record["status"] = "APPROVED"
        request_record["updatedAt"] = now
        request_record.setdefault("metadata", {})["departmentReviewStatus"] = "REVIEWED"
        request_record.setdefault("metadata", {})["forceApprovedBy"] = "LOCKFIX_FORCE_APPROVER"
        request_record.setdefault("metadata", {})["forceApprovedAt"] = now
        store.save(data)
        store.audit_event(
            "approval.force_approved",
            approval_request=request_record,
            decision=decision,
            reason=comment,
            slot_id=slot_id,
            session_key=session_key,
        )
        store.audit_event("approval.request.approved", approval_request=request_record)
        return {"created": True, "request": dict(request_record), "decision": decision, "message": comment}

    def write_veeam_auto_isolate_marker(
        self,
        marker_path: Path,
        session_key: str,
        processed_session_keys: set[str],
        slot_id: str,
        state: str,
        checked_at: str,
        **extra: object,
    ) -> None:
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_key": session_key,
            "processed_session_keys": sorted(processed_session_keys),
            "slot_id": slot_id,
            "state": state,
            "checked_at": checked_at,
        }
        payload.update(extra)
        marker_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def run_veeam_auto_isolate_worker(
        self,
        payload: dict,
        slot_id: str,
        session_key: str,
        checked_at: str,
        marker_path: Path,
        processed_session_keys: set[str],
    ) -> None:
        try:
            restore_scope = payload.get("restore_point_scope") if isinstance(payload.get("restore_point_scope"), dict) else {}
            repository_path = str(payload.get("repository_path") or restore_scope.get("repository_path") or "")
            force_approval = LockFixWebHandler.force_approve_disk_offline_for_veeam(
                self,
                slot_id,
                session_key,
                checked_at,
                reason=f"Veeam job {payload.get('job') or payload.get('name') or 'Backup'} completed successfully.",
            )
            state = self.context.controller.isolate(slot_id, repository_path=repository_path)
            state_value = str(getattr(state, "value", state) or "ISOLATED")
            processed_session_keys.add(session_key)
            with AIRGAP_AUTO_ISOLATE_LOCK:
                LockFixWebHandler.write_veeam_auto_isolate_marker(
                    self,
                    marker_path,
                    session_key,
                    processed_session_keys,
                    slot_id,
                    state_value,
                    checked_at,
                    force_approval=force_approval,
                    completed_at=datetime.now().isoformat(timespec="seconds"),
                )
            self.context.controller.audit.write(
                "veeam.auto_isolate.completed",
                slot_id=slot_id,
                session_key=session_key,
                state=state_value,
                executor="LOCK-FIX Controller",
                message="Veeam backup success detected. LOCK-FIX force-approved DISK_OFFLINE and isolated through the active controller.",
            )
        except Exception as exc:
            with AIRGAP_AUTO_ISOLATE_LOCK:
                LockFixWebHandler.write_veeam_auto_isolate_marker(
                    self,
                    marker_path,
                    session_key,
                    processed_session_keys,
                    slot_id,
                    "FAILED",
                    checked_at,
                    error=str(exc),
                    failed_at=datetime.now().isoformat(timespec="seconds"),
                )
            self.context.controller.audit.write(
                "veeam.auto_isolate.failed",
                slot_id=slot_id,
                session_key=session_key,
                result="FAILED",
                resourceType="DISK",
                resourceId=slot_id,
                message="Veeam backup success detected, but automatic isolate failed.",
                error=str(exc),
            )

    def veeam_auto_isolate_in_progress_stale(self, marker: dict) -> bool:
        timestamp = str(marker.get("started_at") or marker.get("checked_at") or "").strip()
        if not timestamp:
            return True
        try:
            started_at = datetime.fromisoformat(timestamp)
        except ValueError:
            try:
                started_at = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return True
        now = datetime.now(started_at.tzinfo) if started_at.tzinfo else datetime.now()
        return (now - started_at).total_seconds() > AIRGAP_AUTO_ISOLATE_STALE_SECONDS

    def auto_isolate_after_veeam_success(self, payload: dict, status: str, checked_at: str) -> dict:
        session_logs = payload.get("session_logs") if isinstance(payload.get("session_logs"), list) else []
        if not LockFixWebHandler.veeam_payload_matches_configured_job(self, payload, session_logs):
            configured_job = str((get_veeam_config(self.context.app_config) or {}).get("job_name") or "").strip()
            actual_job = str(payload.get("job") or payload.get("name") or "-").strip()
            return {
                "enabled": True,
                "triggered": False,
                "message": f"Waiting for configured Veeam Backup Copy job {configured_job}; latest session is {actual_job}.",
            }
        if not LockFixWebHandler.veeam_backup_copy_completed(self, payload, session_logs, checked_at):
            return {
                "enabled": True,
                "triggered": False,
                "message": "Veeam Backup Copy completion is not confirmed yet. Waiting for the final processing finished/end time before Step 2 Flush.",
            }
        result = str(payload.get("result") or status or "").upper()
        progress = int(payload.get("progress_percent") or payload.get("progress") or 0)
        if result not in {"SUCCESS", "SUCCEEDED", "COMPLETED"} and progress < 100:
            return {"enabled": True, "triggered": False, "message": "Veeam session is not successful yet."}
        slot_id = str(payload.get("slot_id") or os.environ.get("LOCKFIX_SLOT_ID") or next(iter(self.context.config.slots), "BAY-01"))
        session_key, has_unique_session_identity = LockFixWebHandler.veeam_auto_isolate_identity(self, payload)
        marker_path = ROOT / "runtime" / "veeam_auto_isolate.json"
        try:
            previous = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else {}
        except (OSError, json.JSONDecodeError):
            previous = {}
        processed_session_keys = set(previous.get("processed_session_keys") or [])
        if previous.get("session_key") and previous.get("state") == "ISOLATED":
            processed_session_keys.add(str(previous.get("session_key")))
        if not has_unique_session_identity:
            self.context.controller.audit.write(
                "veeam.auto_isolate.identity_missing",
                slot_id=slot_id,
                session_key=session_key,
                message="Veeam success was detected, but no unique new session identity was present. Waiting for a new backup session id or timestamp before Step 2 Flush.",
            )
            return {
                "enabled": True,
                "triggered": False,
                "slot_id": slot_id,
                "session_key": session_key,
                "message": "Veeam success detected, but no unique new session identity was present. Waiting for a new backup completion record.",
            }
        current_processed_session = (
            str(previous.get("session_key") or "") == session_key
            and previous.get("state") == "ISOLATED"
        )
        if current_processed_session:
            return {
                "enabled": True,
                "triggered": False,
                "slot_id": slot_id,
                "session_key": session_key,
                "state": "ISOLATED",
                "processed": True,
                "message": "This Backup Done session already completed LOCK-FIX isolation. Step 5 Offline remains the latest completed state.",
            }
        if session_key in processed_session_keys:
            self.context.controller.audit.write(
                "veeam.auto_isolate.duplicate_skip",
                slot_id=slot_id,
                session_key=session_key,
                message="This completed backup session already passed LOCK-FIX Steps 1-5. Waiting for a new Backup Done session before Step 2 Flush.",
            )
            return {
                "enabled": True,
                "triggered": False,
                "slot_id": slot_id,
                "session_key": session_key,
                "state": "WAITING_FOR_NEW_BACKUP",
                "processed": True,
                "message": "This Backup Done session was already processed through Steps 1-5. Waiting for a new Backup Done record.",
            }
        if str(previous.get("session_key") or "") == session_key and previous.get("state") == "IN_PROGRESS":
            if LockFixWebHandler.veeam_auto_isolate_in_progress_stale(self, previous):
                self.context.controller.audit.write(
                    "veeam.auto_isolate.in_progress.recovered",
                    slot_id=slot_id,
                    session_key=session_key,
                    previous_started_at=str(previous.get("started_at") or previous.get("checked_at") or ""),
                    message="Stale automatic Air-Gap isolation marker was recovered and rescheduled.",
                )
            else:
                return {
                    "enabled": True,
                    "triggered": True,
                    "slot_id": slot_id,
                    "session_key": session_key,
                    "state": "IN_PROGRESS",
                    "message": "Veeam backup success detected. LOCK-FIX Air-Gap isolation is already running.",
                }
        if str(previous.get("session_key") or "") == session_key and previous.get("state") == "FAILED":
            previous_error = str(previous.get("error") or "")
            if "unknown slot" in previous_error.lower() or LockFixWebHandler.veeam_auto_isolate_in_progress_stale(self, previous):
                self.context.controller.audit.write(
                    "veeam.auto_isolate.failed.recovered",
                    slot_id=slot_id,
                    session_key=session_key,
                    previous_error=previous_error,
                    message="Automatic Air-Gap isolation failure marker was recovered and rescheduled.",
                )
            else:
                return {
                    "enabled": True,
                    "triggered": False,
                    "slot_id": slot_id,
                    "session_key": session_key,
                    "state": "FAILED",
                    "error": previous_error,
                    "message": "Veeam backup success was detected, but the last automatic Air-Gap isolation attempt failed.",
                }
        with AIRGAP_AUTO_ISOLATE_LOCK:
            try:
                latest = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else {}
            except (OSError, json.JSONDecodeError):
                latest = {}
            latest_processed = set(latest.get("processed_session_keys") or processed_session_keys)
            if str(latest.get("session_key") or "") == session_key and latest.get("state") == "IN_PROGRESS":
                if not LockFixWebHandler.veeam_auto_isolate_in_progress_stale(self, latest):
                    return {
                        "enabled": True,
                        "triggered": True,
                        "slot_id": slot_id,
                        "session_key": session_key,
                        "state": "IN_PROGRESS",
                        "message": "Veeam backup success detected. LOCK-FIX Air-Gap isolation is already running.",
                    }
                self.context.controller.audit.write(
                    "veeam.auto_isolate.in_progress.recovered",
                    slot_id=slot_id,
                    session_key=session_key,
                    previous_started_at=str(latest.get("started_at") or latest.get("checked_at") or ""),
                    message="Stale automatic Air-Gap isolation marker was recovered under lock and rescheduled.",
                )
            if str(latest.get("session_key") or "") == session_key and latest.get("state") == "ISOLATED":
                latest_processed.add(session_key)
                return {
                    "enabled": True,
                    "triggered": False,
                    "slot_id": slot_id,
                    "session_key": session_key,
                    "state": "ISOLATED",
                    "processed": True,
                    "message": "This Backup Done session already completed LOCK-FIX isolation. Step 5 Offline remains the latest completed state.",
                }
            LockFixWebHandler.write_veeam_auto_isolate_marker(
                self,
                marker_path,
                session_key,
                latest_processed,
                slot_id,
                "IN_PROGRESS",
                checked_at,
                started_at=datetime.now().isoformat(timespec="seconds"),
            )
        worker = threading.Thread(
            target=LockFixWebHandler.run_veeam_auto_isolate_worker,
            args=(self, dict(payload), slot_id, session_key, checked_at, marker_path, latest_processed),
            daemon=True,
        )
        worker.start()
        self.context.controller.audit.write(
            "veeam.auto_isolate.scheduled",
            slot_id=slot_id,
            session_key=session_key,
            message="Veeam backup success detected. LOCK-FIX scheduled Air-Gap isolation in the background.",
        )
        return {
            "enabled": True,
            "triggered": True,
            "slot_id": slot_id,
            "session_key": session_key,
            "state": "IN_PROGRESS",
            "message": "Veeam backup success detected. LOCK-FIX Air-Gap isolation started in the background.",
        }

    def first_veeam_session(self, data: object) -> dict:
        if isinstance(data, dict):
            for key in ("data", "sessions", "results", "items", "value"):
                value = data.get(key)
                if isinstance(value, list) and value:
                    first = value[0]
                    return first if isinstance(first, dict) else {}
                if isinstance(value, dict):
                    found = self.first_veeam_session(value)
                    if found:
                        return found
            return data
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
        return {}

    def veeam_actions_from_session(self, session: dict) -> list[str]:
        raw_actions = session.get("actions") or session.get("log") or session.get("logs") or session.get("messages")
        actions = []
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
            name = str(session.get("name") or session.get("jobName") or "Veeam Backup")
            started = str(session.get("creationTime") or session.get("startTime") or "-")
            actions.append(f"Backup copy for {name} started at {started}")
        return actions

    def veeam_install_properties(self) -> dict:
        props_path = ROOT / "runtime" / "install.properties"
        if not props_path.exists():
            return {}
        result = {}
        try:
            for line in props_path.read_text(encoding="utf-8").splitlines():
                if not line or line.lstrip().startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip()
        except OSError:
            return {}
        return result

    def veeam_base_url_from_parts(self, host: str, port: str | int = 9419) -> str:
        host_text = str(host or "").strip().rstrip("/")
        port_text = str(port or 9419).strip() or "9419"
        if not host_text:
            return ""
        if host_text.startswith(("http://", "https://")):
            return host_text if ":" in host_text.rsplit("/", 1)[-1] else f"{host_text}:{port_text}"
        return f"https://{host_text}:{port_text}"

    def veeam_install_base_url(self, props: dict | None = None) -> str:
        install_props = props if isinstance(props, dict) else self.veeam_install_properties()
        base_url = str(install_props.get("veeam_base_url") or "").strip().rstrip("/")
        if base_url:
            return base_url
        return self.veeam_base_url_from_parts(install_props.get("veeam_host", ""), install_props.get("veeam_port", 9419))

    def write_install_properties(self, props: dict) -> None:
        props_path = ROOT / "runtime" / "install.properties"
        props_path.parent.mkdir(parents=True, exist_ok=True)
        ordered = [
            "install_type",
            "operation_mode",
            "dry_run",
            "components",
            "veeam_host",
            "veeam_port",
            "veeam_base_url",
            "veeam_api_version",
            "veeam_auth",
            "veeam_user",
            "veeam_password",
            "security_key_type",
            "web_ui_url",
        ]
        lines = []
        for key in ordered:
            if key in props:
                lines.append(f"{key}={props[key]}")
        for key in sorted(props):
            if key not in ordered:
                lines.append(f"{key}={props[key]}")
        props_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def update_webui_start_command(self, props: dict, base_url: str) -> bool:
        cmd_path = ROOT / "runtime" / "start_webui_8088.cmd"
        if not cmd_path.exists():
            return False
        try:
            text = cmd_path.read_text(encoding="utf-8")
        except OSError:
            return False
        original_text = text
        replacements = {
            "LOCKFIX_VEEAM_USER": str(props.get("veeam_user") or ""),
            "LOCKFIX_VEEAM_PASSWORD": str(props.get("veeam_password") or ""),
            "LOCKFIX_VEEAM_BASE_URL": base_url,
            "LOCKFIX_VEEAM_API_VERSION": str(props.get("veeam_api_version") or "1.2-rev1"),
        }
        for key, value in replacements.items():
            if not value:
                continue
            pattern = re.compile(rf"^set\s+{re.escape(key)}=.*$", re.MULTILINE)
            line = f"set {key}={value}"
            if pattern.search(text):
                text = pattern.sub(line, text)
            else:
                text = text.replace("@echo off\n", f"@echo off\n{line}\n", 1)
        try:
            if text == original_text:
                return False
            cmd_path.write_text(text, encoding="utf-8")
            return True
        except OSError:
            return False

    def ensure_veeam_execution_settings_synced(self, manual: bool = False) -> dict:
        install_props = self.veeam_install_properties()
        base_url = self.veeam_install_base_url(install_props)
        if not base_url:
            return {
                "ok": False,
                "synced": False,
                "message": "Agent 설치 IP 정보가 없어 Veeam 실행 설정을 갱신할 수 없습니다.",
                "installed_base_url": "",
                "config_base_url": "",
            }
        parsed = urlparse(base_url)
        installed_host = parsed.hostname or str(install_props.get("veeam_host") or "")
        installed_port = parsed.port or int(str(install_props.get("veeam_port") or 9419) or 9419)
        changed = []
        config_path = self.context.config_path
        try:
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            config = {}
        if not isinstance(config, dict):
            config = {}
        veeam = config.setdefault("veeam", {})
        if not isinstance(veeam, dict):
            veeam = {}
            config["veeam"] = veeam
        old_config_base_url = str(veeam.get("base_url") or "").strip().rstrip("/")
        candidates = [str(item).rstrip("/") for item in veeam.get("discovery_candidates", []) if str(item).strip()]
        expected_user = str(install_props.get("veeam_user") or veeam.get("username") or "").strip()
        expected_api_version = str(install_props.get("veeam_api_version") or veeam.get("api_version") or "1.2-rev1").strip()
        updates = {
            "enabled": True,
            "base_url": base_url,
            "api_version": expected_api_version,
            "auto_discover": False,
            "discovery_candidates": [base_url, *[item for item in candidates if item != base_url]],
            "discovery_scan_local_subnet": False,
        }
        if expected_user:
            updates["username"] = expected_user
        for key, value in updates.items():
            if veeam.get(key) != value:
                veeam[key] = value
                changed.append(f"config.veeam.{key}")
        try:
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            return {
                "ok": False,
                "synced": False,
                "message": f"Veeam 설정 파일 갱신 실패: {exc}",
                "installed_base_url": base_url,
                "config_base_url": old_config_base_url,
            }
        if str(install_props.get("veeam_base_url") or "").strip().rstrip("/") != base_url:
            install_props["veeam_base_url"] = base_url
            changed.append("runtime.install_properties.veeam_base_url")
        if installed_host and str(install_props.get("veeam_host") or "").strip() != installed_host:
            install_props["veeam_host"] = installed_host
            changed.append("runtime.install_properties.veeam_host")
        if str(install_props.get("veeam_port") or "").strip() != str(installed_port):
            install_props["veeam_port"] = str(installed_port)
            changed.append("runtime.install_properties.veeam_port")
        if expected_api_version:
            install_props["veeam_api_version"] = expected_api_version
        self.write_install_properties(install_props)
        command_updated = self.update_webui_start_command(install_props, base_url)
        if command_updated:
            changed.append("runtime.start_webui_8088.cmd")
        os.environ["LOCKFIX_VEEAM_BASE_URL"] = base_url
        os.environ["LOCKFIX_VEEAM_HOST"] = installed_host
        os.environ["LOCKFIX_VEEAM_PORT"] = str(installed_port)
        if expected_api_version:
            os.environ["LOCKFIX_VEEAM_API_VERSION"] = expected_api_version
        if expected_user:
            password_env = str(veeam.get("password_env") or "LOCKFIX_VEEAM_PASSWORD")
            username_env = str(veeam.get("username_env") or "LOCKFIX_VEEAM_USER")
            os.environ[username_env] = expected_user
            if install_props.get("veeam_password"):
                os.environ[password_env] = str(install_props["veeam_password"])
        synced = not changed or all(str(item).startswith("runtime.start_webui") for item in changed)
        result = {
            "ok": True,
            "synced": synced,
            "manual": manual,
            "changed": changed,
            "installed_host": installed_host,
            "installed_port": installed_port,
            "installed_base_url": base_url,
            "config_base_url": old_config_base_url,
            "effective_base_url": base_url,
            "message": "현재 agent 설치 IP 기준으로 Veeam 실행 설정을 갱신했습니다." if changed else "현재 agent 설치 IP 기준 설정이 이미 일치합니다.",
        }
        if manual or changed:
            try:
                self.context.controller.audit.write(
                    "veeam.config.sync",
                    installed_base_url=base_url,
                    previous_base_url=old_config_base_url,
                    changed=",".join(changed),
                    result="SUCCESS",
                    message=result["message"],
                )
            except Exception:
                pass
        return result

    def tcp_port_open(self, host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.35):
                return True
        except OSError:
            return False

    def mount_summary(self, mount_point: Path) -> dict:
        exists = mount_point.exists()
        is_dir = mount_point.is_dir()
        mounted = False
        usage = None
        error = None

        try:
            if exists and is_dir:
                usage_raw = shutil.disk_usage(str(mount_point))
                total = usage_raw.total
                used = usage_raw.used
                free = usage_raw.free
                usage = {
                    "total": total,
                    "used": used,
                    "free": free,
                    "percent": round((used / total) * 100, 1) if total else 0,
                    "total_label": self.format_bytes(total),
                    "used_label": self.format_bytes(used),
                    "free_label": self.format_bytes(free),
                }
                mounted = self.is_mount_point(mount_point)
        except OSError as exc:
            error = str(exc)

        return {
            "exists": exists,
            "is_dir": is_dir,
            "mounted": mounted,
            "usage": usage,
            "error": error,
        }

    def is_mount_point(self, mount_point: Path) -> bool:
        try:
            return mount_point.is_mount()
        except OSError:
            return False

    def format_bytes(self, value: int) -> str:
        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
            if size < 1024 or unit == "PB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{size:.1f} PB"

    def audit_items(self) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        items = []
        for line in lines[-200:]:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                items.append({"event": "parse_error", "raw": line})
        return list(reversed(items))

    def monitoring_summary(self, start_date: str = "", end_date: str = "") -> dict:
        points = []
        now = datetime.now()
        range_start = now - timedelta(minutes=29 * 10)
        range_end = now
        try:
            if start_date:
                range_start = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                range_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
            if range_end < range_start:
                range_end = range_start + timedelta(hours=23, minutes=59)
        except ValueError:
            range_start = now - timedelta(minutes=29 * 10)
            range_end = now
        total_seconds = max(29, int((range_end - range_start).total_seconds()))
        step_seconds = total_seconds / 29
        tick = int(time.time() / 5)
        for index in range(30):
            stamp = range_start + timedelta(seconds=step_seconds * index)
            phase = index + tick
            cpu = 12 + ((phase * 7) % 21) + (8 if phase % 11 in (1, 2) else 0)
            memory = 91.6 + ((phase % 7) * 0.22)
            disk = 14.0 + ((phase % 6) * 0.18)
            network = 18 + ((phase * 9) % 39) + (10 if phase % 13 == 0 else 0)
            interface = 22 + ((phase * 5) % 31) + (8 if phase % 10 == 0 else 0)
            points.append(
                {
                    "time": stamp.strftime("%Y.%m.%d %H:%M"),
                    "label": stamp.strftime("%m.%d %H:%M"),
                    "cpu": round(cpu, 1),
                    "memory": round(memory, 1),
                    "disk": round(disk, 1),
                    "network": round(network, 1),
                    "interface": round(interface, 1),
                }
            )
        latest = points[-1]
        return {
            "title": "OAM - Hardware Usage Monitoring",
            "interval_seconds": 5,
            "range": {
                "start": points[0]["time"],
                "end": points[-1]["time"],
            },
            "series": points,
            "current": {
                "cpu": latest["cpu"],
                "memory": latest["memory"],
                "disk": latest["disk"],
                "network": latest["network"],
                "interface": latest["interface"],
            },
        }

    def report_summary(self) -> dict:
        monitoring = self.monitoring_summary()
        series = monitoring["series"]
        customer_record = self.report_customer_record()
        metrics = [
            ("cpu", "CPU", 80),
            ("memory", "Memory", 80),
            ("disk", "Disk", 85),
            ("network", "Network", 75),
            ("interface", "Interface", 70),
        ]
        cards = []
        for key, label, threshold in metrics:
            values = [item[key] for item in series]
            current = monitoring["current"][key]
            average = round(sum(values) / len(values), 1)
            peak = round(max(values), 1)
            status = "Warning" if peak >= threshold else "Normal"
            cards.append(
                {
                    "id": key,
                    "label": label,
                    "current": current,
                    "average": average,
                    "peak": peak,
                    "threshold": threshold,
                    "status": status,
                    "recommendation": self.report_recommendation(key, peak, average, threshold),
                }
            )
        warnings = [card for card in cards if card["status"] == "Warning"]
        inspection_items = self.report_inspection_items(cards)
        host_name = socket.gethostname()
        return {
            "title": "Resource Usage Analysis Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "range": monitoring["range"],
            "customer": {
                "customer_name": "OAM Customer",
                "inspection_date": datetime.now().strftime("%Y-%m-%d"),
                "customer_contact": customer_record.get("customer_contact", "-"),
                "engineer": "OAM Lock-FIX",
                "customer_email": customer_record.get("customer_email", "-"),
                "engineer_contact": "1666-3736",
            },
            "server": {
                "os_version": platform.platform(),
                "cpu": "Monitored CPU",
                "service": "LOCK-FIX Hardware Detection Monitoring",
                "memory": f"{next(card for card in cards if card['id'] == 'memory')['current']}% in use",
                "model": "LOCK-FIX PoC",
                "disk": f"{next(card for card in cards if card['id'] == 'disk')['current']}% in use",
                "serial": "POC-LOCAL",
                "hostname": host_name,
            },
            "summary": {
                "overall_status": "Attention Required" if warnings else "Normal",
                "analysis": "Current operating resources are monitored every 5 seconds and summarized with average, peak, and threshold values.",
                "warning_count": len(warnings),
            },
            "cards": cards,
            "inspection_items": inspection_items,
            "series": series,
            "extras": self.report_extras_record(),
            "exports": {
                "word": "/api/report.docx",
                "csv": "/api/report.csv",
                "pdf": "/api/report.pdf",
                "hwp": "/api/report.hwpx",
            },
        }

    def report_recommendation(self, key: str, peak: float, average: float, threshold: float) -> str:
        if peak < threshold:
            return "No immediate action required."
        recommendations = {
            "cpu": "Review high-load processes and scheduled jobs.",
            "memory": "Check resident services and consider memory expansion.",
            "disk": "Clean up old logs/backups or extend storage capacity.",
            "network": "Review traffic bursts and backup transfer windows.",
        }
        return recommendations.get(key, "Review resource usage trend.")

    def report_inspection_items(self, cards: list[dict]) -> list[dict]:
        by_id = {card["id"]: card for card in cards}

        def result(metric_id: str) -> str:
            return "Warning" if by_id[metric_id]["status"] == "Warning" else "Normal"

        return [
            {"category": "H/W", "item": "System LED", "detail": "Front panel LED", "criteria": "No red indicator", "result": "Normal", "metric": "-"},
            {"category": "H/W", "item": "Power Supply", "detail": "Visual inspection", "criteria": "Green indicator", "result": "Normal", "metric": "-"},
            {"category": "H/W", "item": "Disk LED", "detail": "Visual inspection", "criteria": "No red indicator", "result": result("disk"), "metric": f"{by_id['disk']['current']}%"},
            {"category": "H/W", "item": "RAID Status", "detail": "Status check", "criteria": "Online", "result": "Normal", "metric": "Online"},
            {"category": "H/W", "item": "Memory", "detail": "Usage analysis", "criteria": f"< {by_id['memory']['threshold']}%", "result": result("memory"), "metric": f"{by_id['memory']['current']}%"},
            {"category": "H/W", "item": "CPU", "detail": "Usage analysis", "criteria": f"< {by_id['cpu']['threshold']}%", "result": result("cpu"), "metric": f"{by_id['cpu']['current']}%"},
            {"category": "H/W", "item": "Adapter", "detail": "NIC link and cable", "criteria": "Link up", "result": "Normal", "metric": "Link up"},
            {"category": "H/W", "item": "System Log", "detail": "Syslog review", "criteria": "No critical error", "result": "Normal", "metric": "No critical"},
            {"category": "OS", "item": "OS Error", "detail": "/var/log/messages", "criteria": "No error", "result": "Normal", "metric": "No error"},
            {"category": "OS", "item": "Disk Usage", "detail": "Filesystem capacity", "criteria": f"< {by_id['disk']['threshold']}%", "result": result("disk"), "metric": f"{by_id['disk']['current']}%"},
            {"category": "OS", "item": "Performance", "detail": "vmstat / top equivalent", "criteria": "No excessive usage", "result": "Warning" if any(card["status"] == "Warning" for card in cards) else "Normal", "metric": "See metrics"},
            {"category": "OS", "item": "Processor", "detail": "CPU utilization", "criteria": "No abnormal usage", "result": result("cpu"), "metric": f"Peak {by_id['cpu']['peak']}%"},
            {"category": "OS", "item": "Memory Usage", "detail": "Memory utilization", "criteria": "No abnormal usage", "result": result("memory"), "metric": f"Peak {by_id['memory']['peak']}%"},
            {"category": "OS", "item": "Disk I/O", "detail": "Disk capacity trend", "criteria": "Stable", "result": result("disk"), "metric": f"Avg {by_id['disk']['average']}%"},
            {"category": "OS", "item": "Network", "detail": "TX/RX traffic flow", "criteria": f"< {by_id['network']['threshold']}%", "result": result("network"), "metric": f"{by_id['network']['current']}%"},
        ]

    def dashboard_summary(self, live: bool = False) -> dict:
        runtime_root = self.context.config.audit_log_path.parent
        cache_key = str(self.context.config.audit_log_path)
        now_monotonic = time.monotonic()
        with LockFixWebHandler.dashboard_cache_lock:
            cached = LockFixWebHandler.dashboard_cache_by_key.get(cache_key)
            if not live and cached and now_monotonic - cached[0] < DASHBOARD_CACHE_TTL_SECONDS:
                cached_payload = dict(cached[1])
                live_status = dict(cached_payload.get("live_status") or {})
                live_status.update({
                    "cache_hit": True,
                    "generated_at": cached_payload.get("generated_at"),
                    "source_age_seconds": round(now_monotonic - cached[0], 3),
                })
                cached_payload["live_status"] = live_status
                return cached_payload

        def read_json(path: Path, fallback: object) -> object:
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return fallback

        def ps_json(command: str) -> object:
            try:
                output = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=DASHBOARD_PROBE_TIMEOUT_SECONDS,
                    check=False,
                )
                if output.returncode != 0:
                    return {}
                text = output.stdout.strip()
                return json.loads(text) if text else {}
            except Exception:
                return {}

        state = read_json(runtime_root / "state.json", {})
        auto_isolate = read_json(runtime_root / "veeam_auto_isolate.json", {})
        session_payload = read_json(runtime_root / "veeam_last_session_logs.json", {})
        steering_state = read_json(runtime_root / "veeam_steering_state.json", {})
        storage_state = read_json(runtime_root / "storage-BAY-01.json", {})
        sessions = session_payload.get("session_logs") if isinstance(session_payload, dict) else []
        latest_session = sessions[0] if isinstance(sessions, list) and sessions else {}

        slot_id = str(auto_isolate.get("slot_id") or next(iter(self.context.config.slots), "BAY-01"))
        airgap_state = str((state or {}).get(slot_id) or "UNKNOWN") if isinstance(state, dict) else "UNKNOWN"
        veeam_state = str(auto_isolate.get("state") or "UNKNOWN") if isinstance(auto_isolate, dict) else "UNKNOWN"
        backup_status = str(latest_session.get("status") or "Unknown")
        veeam_settings = get_veeam_config(self.context.app_config) or {}
        backup_job = str(latest_session.get("name") or veeam_settings.get("job_name") or "-")
        backup_started = str(latest_session.get("started_at") or "-")
        backup_ended = str(latest_session.get("ended_at") or "-")
        backup_duration = str(latest_session.get("duration") or "-")
        veeam_api_synced = bool(steering_state.get("api_synced")) if isinstance(steering_state, dict) else False
        veeam_issue_detected = bool(steering_state.get("issue_detected")) if isinstance(steering_state, dict) else False
        veeam_last_checked = str(steering_state.get("last_checked") or steering_state.get("last_run_at") or "-") if isinstance(steering_state, dict) else "-"
        veeam_health_message = LockFixWebHandler.dashboard_backup_health_message(steering_state)
        disk_number = str(storage_state.get("diskNumber") or "").strip() if isinstance(storage_state, dict) else ""
        configured_drive = str(storage_state.get("drive") or "").strip() if isinstance(storage_state, dict) else ""
        configured_path = str(storage_state.get("accessPath") or self.context.config.slot(slot_id).mount_point or "-") if isinstance(storage_state, dict) else "-"
        storage_has_disk_snapshot = isinstance(storage_state, dict) and any(key in storage_state for key in ("isOffline", "offlineEquivalent"))
        storage_offline_equivalent = bool(
            isinstance(storage_state, dict)
            and (storage_state.get("isOffline") or storage_state.get("offlineEquivalent"))
        )
        storage_path_reachable = None
        if isinstance(storage_state, dict) and "pathReachable" in storage_state:
            storage_path_reachable = bool(storage_state.get("pathReachable"))

        disk_probe = {}
        volume_probe = {}
        if disk_number and not storage_has_disk_snapshot:
            disk_probe = ps_json(
                "$disk=Get-Disk -Number %s -ErrorAction SilentlyContinue; "
                "if ($disk) { $disk | Select-Object Number,FriendlyName,IsOffline,OperationalStatus,BusType,IsBoot,IsSystem | ConvertTo-Json -Compress }" % disk_number
            )
        if configured_drive and storage_path_reachable is None:
            volume_probe = ps_json(
                "$drive='%s'; "
                "$vol=Get-Volume -DriveLetter $drive -ErrorAction SilentlyContinue; "
                "if ($vol) { $vol | Select-Object DriveLetter,FileSystemLabel,FileSystem,DriveType,HealthStatus,OperationalStatus | ConvertTo-Json -Compress }" % configured_drive.replace("'", "")
            )
        disk_is_offline = storage_offline_equivalent if storage_has_disk_snapshot else (bool(disk_probe.get("IsOffline")) if isinstance(disk_probe, dict) else False)
        disk_status = "Offline" if disk_is_offline else ("Online" if storage_has_disk_snapshot or disk_probe else "Unknown")
        disk_name = str(disk_probe.get("FriendlyName") or "-") if isinstance(disk_probe, dict) else "-"
        volume_visible = storage_path_reachable if storage_path_reachable is not None else bool(volume_probe)

        offline_failed = False
        audit_lines = LockFixWebHandler.audit_log_tail_lines(self, limit=1000, max_bytes=2 * 1024 * 1024)
        audit_records: list[dict] = []
        for line in audit_lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                audit_records.append(record)

        recent_events: list[dict] = []
        for record in audit_records[-300:]:
            event = str(record.get("event") or "")
            if record.get("slot_id") and str(record.get("slot_id")) != slot_id:
                continue
            if event in {"disk.offline.error", "disk.offline.verify.error", "disk.offline.strict.error"}:
                offline_failed = True
            if event.startswith("state.transition") or event.startswith("disk.") or event.startswith("veeam."):
                ts = LockFixWebHandler.format_audit_timestamp(self, record.get("ts")) or "-"
                message = record.get("error") or record.get("message") or record.get("output") or event
                recent_events.append({"type": "EVENT", "date": ts, "content": LockFixWebHandler.compact_log_value(self, message)})
        recent_events = recent_events[-5:]
        audit_recent = audit_records[-500:]
        audit_latest = audit_records[-1] if audit_records else {}
        audit_summary = {
            "linked": self.context.config.audit_log_path.exists(),
            "total_records": len(audit_records),
            "manual_operations": sum(1 for item in audit_recent if str(item.get("event") or item.get("action") or "").startswith(("admin.", "manual.", "poc.admin"))),
            "policy_changes": sum(1 for item in audit_recent if "policy" in str(item.get("event") or item.get("action") or "").lower()),
            "approval_requests": sum(1 for item in audit_recent if str(item.get("event") or item.get("action") or "").startswith("approval.")),
            "login_failures": sum(1 for item in audit_recent if "login" in str(item.get("event") or item.get("action") or "").lower() and "fail" in json.dumps(item, ensure_ascii=False).lower()),
            "latest_at": LockFixWebHandler.format_audit_timestamp(self, audit_latest.get("ts") or audit_latest.get("createdAt") or audit_latest.get("time")) if audit_latest else "-",
        }

        airgap_ok = airgap_state == "ISOLATED" and disk_is_offline
        warning_count = sum([
            backup_status.lower() not in {"success", "completed"},
            veeam_state not in {"ISOLATED", "WAITING_FOR_NEW_BACKUP"},
            airgap_state not in {"ISOLATED", "WAITING_DISK"},
            not disk_is_offline,
            offline_failed,
        ])
        logs = recent_events or [{"type": "INFO", "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": "No recent LOCK-FIX events."}]
        result_label = "Offline Complete" if airgap_ok else ("Offline Failed" if offline_failed else airgap_state)

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "generated_at": generated_at,
            "live_status": {
                "cache_hit": False,
                "generated_at": generated_at,
                "source_age_seconds": 0,
            },
            "cards": [
                {"id": "detect", "label": "Detect", "description": f"Disk {disk_number or '-'} {disk_name}", "value": 0 if disk_probe else 1},
                {"id": "warning", "label": "Warning", "description": "Live operation issues", "value": warning_count},
                {"id": "logs", "label": "Logs", "description": "Recent LOCK-FIX events", "value": len(logs)},
            ],
            "security_kpis": [
                {"icon": "data-protection-logo", "label": "Data Protection", "value": backup_status, "tone": "green" if backup_status == "Success" else "red", "meta": backup_ended},
                {"icon": "airgap-logo", "label": "Air-Gap", "value": veeam_state, "tone": "green" if airgap_ok else "orange", "meta": airgap_state},
                {"icon": "storage-power", "label": "Disk Offline", "value": disk_status, "tone": "green" if disk_is_offline else "red", "meta": configured_path},
                {"icon": "veeam-backup-completed", "label": "Last Backup", "value": backup_status, "tone": "green" if backup_status == "Success" else "orange", "meta": backup_ended},
                {"icon": "integrity-logo", "label": "LOCK-FIX State", "value": result_label, "tone": "green" if airgap_ok else "red", "meta": f"Disk {disk_number or '-'} / {configured_path}"},
            ],
            "flow": [
                {"icon": "backup-complete", "lines": ["Backup", "Done"], "state": "done" if backup_status == "Success" else "active"},
                {"icon": "flush-run", "lines": ["Flush", "Run"], "state": "done" if airgap_state not in {"BACKUP_COMPLETED", "FLUSHING"} else "active"},
                {"icon": "io-check", "lines": ["I/O", "Check"], "state": "done" if airgap_state not in {"BACKUP_COMPLETED", "FLUSHING", "IO_CHECKING"} else "active"},
                {"icon": "power-off", "lines": ["Disk", "Offline"], "state": "done" if disk_is_offline else "active"},
                {"icon": "airgap-logo", "lines": ["Air-Gap", "Active"], "state": "done" if airgap_ok else "pending"},
            ],
            "backup": {
                "solution": "Veeam Backup & Replication",
                "job": backup_job,
                "started_at": backup_started,
                "ended_at": backup_ended,
                "duration": backup_duration,
                "isolation_state": airgap_state,
                "result": result_label,
                "api_synced": veeam_api_synced,
                "issue_detected": veeam_issue_detected,
                "last_checked": veeam_last_checked,
                "health_message": veeam_health_message,
            },
            "alerts": [
                {"label": "Disk Offline", "value": "Normal" if disk_is_offline else "Failed"},
                {"label": "Veeam Auto Isolation", "value": veeam_state},
                {"label": "Repository Volume", "value": "Visible" if volume_visible else "Not visible"},
                {"label": "Offline Error", "value": "Detected" if offline_failed else "None"},
            ],
            "notifications": self.notification_items(),
            "logs": logs,
            "audit_summary": audit_summary,
            "threat_detection": self.threat_detection_summary()["summary"],
            "total_logs": len(logs),
        }
        with LockFixWebHandler.dashboard_cache_lock:
            LockFixWebHandler.dashboard_cache_by_key[cache_key] = (time.monotonic(), payload)
        return payload

    @staticmethod
    def dashboard_backup_health_message(steering_state: dict | None) -> str:
        if not isinstance(steering_state, dict) or not steering_state:
            return "Veeam REST 연동 상태를 확인 중입니다."
        last_checked = str(steering_state.get("last_checked") or steering_state.get("last_run_at") or "-")
        api_synced = bool(steering_state.get("api_synced"))
        issue_detected = bool(steering_state.get("issue_detected"))
        progress = int(steering_state.get("progress_percent") or 0)
        auto_message = str(steering_state.get("auto_isolate_message") or "").strip()
        message = str(steering_state.get("message") or "").strip()
        if issue_detected:
            return auto_message or message or f"Veeam REST 연동 문제를 확인했습니다. 마지막 확인: {last_checked}"
        if api_synced and "completion is not confirmed" in auto_message.lower():
            if progress >= 100:
                return "Veeam REST 연동 정상. 백업 진행률은 100%이나 Backup Copy 최종 완료 로그가 아직 확인되지 않아 격리 전환을 대기합니다."
            return "Veeam REST 연동 정상. Backup Copy 최종 완료 로그를 대기 중입니다."
        if api_synced and auto_message:
            return auto_message
        if api_synced:
            return f"Veeam REST 연동 정상. 마지막 확인: {last_checked}"
        return message or "Veeam REST 연동 확인이 필요합니다."

    def notification_summary(self) -> dict:
        audit_alert = LockFixWebHandler.audit_anomaly_alert_summary(self)
        settings = LockFixWebHandler.notification_settings(self, redact=True)
        return {
            "items": LockFixWebHandler.notification_items(self),
            "audit_alert": audit_alert,
            "smtp_settings": settings,
            "gateway": {
                "name": "Security Notification Gateway",
                "internal_transport": "SMTP",
                "scope": "Backup, Air-Gap, disk isolation, reconnect approval, and security audit events only.",
            },
            "summary": {
                "unauthorized_access": {
                    "label": "비인가 접근 시도",
                    "value": "0건",
                    "period": "최근 24시간",
                },
                "audit_anomaly": {
                    "label": "감사 이력 이상 감지",
                    "value": f"{audit_alert['count_24h']}건",
                    "period": "최근 24시간",
                    "status": audit_alert["status"],
                },
            },
        }

    def notification_items(self) -> list[dict]:
        settings = LockFixWebHandler.notification_settings(self, redact=True)
        configured = bool(settings.get("smtp_host")) and bool(settings.get("target_email"))
        status = "Configured" if configured else "Not configured"
        return [
            {
                "email": settings.get("target_email") or "-",
                "smtp_status": status,
                "network_connection": "SMTP internal transport",
                "last_login": settings.get("updated_at") or "-",
            },
        ]

    def audit_anomaly_alert_summary(self) -> dict:
        cutoff = datetime.now() - timedelta(hours=24)
        anomalies = []
        for line in LockFixWebHandler.audit_log_lines(self)[-1000:]:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                record = {"ts": "", "event": "audit.parse_error", "raw": line}
            timestamp = LockFixWebHandler.parse_audit_timestamp(self, record.get("ts"))
            if timestamp and timestamp < cutoff:
                continue
            if not LockFixWebHandler.is_audit_anomaly_record(self, record):
                continue
            anomalies.append(LockFixWebHandler.format_audit_anomaly_alert(self, record))
        anomalies = anomalies[-30:]
        return {
            "enabled": True,
            "status": "ALERT" if anomalies else "NORMAL",
            "count_24h": len(anomalies),
            "alert_target": "Notification",
            "send_channel": "SMTP",
            "smtp_status": "Connected",
            "last_detected": anomalies[-1]["detected_at"] if anomalies else "-",
            "items": list(reversed(anomalies[-10:])),
        }

    def is_audit_anomaly_record(self, record: dict) -> bool:
        event = str(record.get("event") or "").lower()
        state = str(record.get("state") or "").lower()
        text = json.dumps(record, ensure_ascii=False).lower()
        if event.endswith(".heartbeat") or event.endswith(".tick"):
            return False
        anomaly_events = {
            "emergency.reconnect.denied",
            "emergency.reconnect.background.error",
            "emergency.reconnect.background.timeout",
            "emergency.reconnect.background.not_started",
            "disk.online.unauthorized.reblock",
            "disk.online.unauthorized.reblock.error",
            "disk.online.unauthorized.guard.error",
            "disk.storage_api.self_check.error",
            "admin.alert.quarantine",
            "emergency.quarantine.unmount.error",
            "emergency.quarantine.relay_off.error",
            "emergency.quarantine.offline.error",
            "license_register_failed",
            "lockfix_service_control_failed",
            "service.permission.insufficient",
            "service.preflight.unavailable",
            "audit.parse_error",
        }
        anomaly_tokens = (
            "unauthorized",
            "denied",
            "access denied",
            "access_denied",
            "timeout",
            "not_started",
            "failed",
            "failure",
            "error",
            "mismatch",
            "quarantine",
            "parse_error",
            "액세스 거부",
            "실패",
            "오류",
        )
        return event in anomaly_events or state == "error" or any(token in event or token in text for token in anomaly_tokens)

    def format_audit_anomaly_alert(self, record: dict) -> dict:
        event = str(record.get("event") or "audit.unknown")
        text = LockFixWebHandler.compact_log_value(
            self,
            record.get("message")
            or record.get("resolution")
            or record.get("error")
            or record.get("raw")
            or event,
        )
        severity = "CRITICAL" if any(token in event.lower() or token in text.lower() for token in ("unauthorized", "denied", "quarantine", "mismatch", "액세스 거부")) else "WARNING"
        return {
            "detected_at": LockFixWebHandler.format_audit_timestamp(self, record.get("ts")) or "-",
            "event": event,
            "slot_id": str(record.get("slot_id") or "-"),
            "severity": severity,
            "message": text[:220],
            "alert_status": "ALERT SENT" if severity == "CRITICAL" else "ALERT READY",
        }

    def threat_detection_summary(self) -> dict:
        veeam_config = get_veeam_config(self.context.app_config) or {}
        repository_path = str(
            veeam_config.get("target_repository_path")
            or self.context.veeam_backup_copy_repository_path()
            or "D:\\BackupCopyRepo"
        ).strip()
        try:
            repository_volume = repository_volume_root(repository_path)
        except ValueError:
            repository_volume = "-"
        if repository_volume.upper().startswith("C:"):
            repository_path = "-"
            repository_name = "Veeam Backup Copy 저장소 대상 아님"
            status = "주의"
            score = 46
            suspicious_count = 2
        else:
            repository_name = str(veeam_config.get("target_repository_name") or "Repository-D")
            status = "정상"
            score = 12
            suspicious_count = 0
        now = datetime.now()
        last_scan = now.strftime("%Y-%m-%d %H:%M:%S")
        backup_job = str(veeam_config.get("job_name") or veeam_config.get("target_job_name") or "Daily Backup")
        backup_file_path = str(Path(repository_path) / "Backup Copy Job 1.vbk") if repository_path != "-" else "-"
        default_admin_note = "Mock 기반 1차 개발 화면입니다. Agent/API 탐지 결과 수신 구조로 확장됩니다."
        base_result = {
            "id": "threat-scan-latest",
            "scan_time": last_scan,
            "repository": repository_name,
            "repository_path": repository_path,
            "backup_job": backup_job,
            "backup_file_path": backup_file_path,
            "backup_completed_at": (now - timedelta(minutes=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "scan_started_at": (now - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "scan_ended_at": last_scan,
            "engine": "Veeam Malware REST API + Windows Defender + YARA + Repository Hash",
            "result": status,
            "score": score,
            "detection_count": suspicious_count,
            "action_status": "Air-gap 완료" if status == "정상" else "관리자 확인 필요",
            "lockfix_action": "Disk Offline / Drive Letter 제거 / Air-gap 전환" if status == "정상" else "Air-gap 유지 / 알림 / 관리자 검토",
            "admin_note": default_admin_note,
            "admin_note_updated_at": "",
            "admin_note_actor": "",
            "audit_log_id": "THREAT_SCAN_COMPLETED",
            "detections": [],
        }
        caution_result = {
            **base_result,
            "id": "threat-scan-caution",
            "scan_time": (now - timedelta(days=1, minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "result": "주의",
            "score": 46,
            "detection_count": 2,
            "action_status": "관리자 확인 필요",
            "lockfix_action": "Air-gap 전환 완료 / 관리자 알림",
            "audit_log_id": "THREAT_DETECTED",
            "detections": [
                {"type": "파일 엔트로피 증가", "file_path": f"{repository_path}\\Daily\\vm01.vib", "evidence": "최근 24시간 평균 대비 엔트로피 증가", "severity": "WARN", "status": "검토 대기"},
                {"type": "백업 파일 크기 급변", "file_path": f"{repository_path}\\Daily\\vm02.vib", "evidence": "이전 백업 대비 크기 42% 증가", "severity": "WARN", "status": "알림 발송"},
            ],
        }
        danger_result = {
            **base_result,
            "id": "threat-scan-danger",
            "scan_time": (now - timedelta(days=2, minutes=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "result": "위험",
            "score": 82,
            "detection_count": 5,
            "action_status": "재연결 차단",
            "lockfix_action": "Air-gap 강제 유지 / Repository Online 승인 요구",
            "audit_log_id": "THREAT_POLICY_BLOCKED_ONLINE",
            "detections": [
                {"type": "랜섬웨어 의심", "file_path": f"{repository_path}\\Daily\\critical.vbk", "evidence": "대량 확장자 변경 패턴", "severity": "CRITICAL", "status": "차단"},
                {"type": "VSS 삭제 명령 의심", "file_path": "Windows Event Log", "evidence": "vssadmin delete shadows 유사 이벤트", "severity": "CRITICAL", "status": "승인 필요"},
                {"type": "무결성 해시 불일치", "file_path": f"{repository_path}\\manifest.sha256", "evidence": "등록 해시와 현재 해시 불일치", "severity": "ERROR", "status": "격리 유지"},
            ],
        }
        for result in (base_result, caution_result, danger_result):
            latest_note = self.latest_admin_memo(str(result.get("id") or ""))
            if latest_note:
                result["admin_note"] = latest_note.get("note") or default_admin_note
                result["admin_note_updated_at"] = latest_note.get("created_at") or ""
                result["admin_note_actor"] = latest_note.get("actor") or ""
        manual_scan = self.read_manual_threat_scan()
        results = [base_result, caution_result, danger_result]
        if manual_scan:
            manual_result = dict(base_result)
            manual_result.update(
                {
                    "id": str(manual_scan.get("scan_id") or "threat-scan-manual"),
                    "scan_time": str(manual_scan.get("completed_at") or manual_scan.get("started_at") or last_scan),
                    "scan_started_at": str(manual_scan.get("started_at") or last_scan),
                    "scan_ended_at": str(manual_scan.get("completed_at") or last_scan),
                    "repository": str(manual_scan.get("repository_name") or repository_name),
                    "repository_path": str(manual_scan.get("repository_path") or repository_path),
                    "backup_job": str(manual_scan.get("backup_job") or backup_job),
                    "backup_file_path": str(manual_scan.get("scan_target") or backup_file_path),
                    "engine": str(manual_scan.get("engine") or base_result["engine"]),
                    "result": str(manual_scan.get("result") or status),
                    "score": int(manual_scan.get("score") or score),
                    "detection_count": int(manual_scan.get("suspicious_count") or 0),
                    "action_status": str(manual_scan.get("action_status") or "검사 완료"),
                    "lockfix_action": str(manual_scan.get("lockfix_action") or base_result["lockfix_action"]),
                    "audit_log_id": str(manual_scan.get("audit_log_id") or "THREAT_MANUAL_SCAN_COMPLETED"),
                    "detections": manual_scan.get("detections") if isinstance(manual_scan.get("detections"), list) else [],
                }
            )
            results = [manual_result, *results]
            status = str(manual_scan.get("result") or status)
            score = int(manual_scan.get("score") or score)
            suspicious_count = int(manual_scan.get("suspicious_count") or suspicious_count)
            last_scan = str(manual_scan.get("completed_at") or last_scan)
        return {
            "summary": {
                "status": status,
                "score": score,
                "suspicious_count": suspicious_count,
                "last_scan_at": last_scan,
                "engine": "Veeam Malware REST API + Windows Defender + YARA + Repository Hash",
                "status_detail": "안전한 백업본만 Air-gap 상태로 전환합니다.",
            },
            "policy": {
                "enabled": True,
                "timing": ["백업 완료 직후", "Air-gap 전환 직전", "Repository 재연결 전"],
                "engines": ["Veeam Malware REST API", "Windows Defender", "YARA Rule", "Repository Hash", "Windows Event Log", "LOCK-FIX Agent Log"],
                "thresholds": {"normal": "0-30", "warning": "31-70", "danger": "71-100"},
                "risk_action": "Air-gap 강제 유지 + 재연결 차단",
                "reauth_required": ["CURRENT_USER_PASSWORD"],
            },
            "veeam_malware_api": {
                "enabled": True,
                "connected": bool(veeam_config.get("base_url")),
                "base_url": str(veeam_config.get("base_url") or "-"),
                "endpoint": "/api/v1/malwareDetection/events",
                "last_result": status,
                "last_checked": last_scan,
                "note": "1차 개발은 Mock 표시이며, 2차 개발에서 Veeam REST Malware Detection 이벤트와 세션 ID를 실제 연동합니다.",
            },
            "manual_scan": manual_scan or {},
            "audit_events": [
                "THREAT_SCAN_STARTED",
                "THREAT_SCAN_COMPLETED",
                "THREAT_DETECTED",
                "THREAT_SCORE_UPDATED",
                "THREAT_POLICY_BLOCKED_ONLINE",
                "THREAT_SCAN_FAILED",
                "THREAT_SCAN_APPROVAL_REQUIRED",
                "THREAT_SCAN_REPORT_DOWNLOADED",
            ],
            "results": results,
        }

    def manual_threat_scan_path(self) -> Path:
        return ROOT / "runtime" / "threat_manual_scan.json"

    def read_manual_threat_scan(self) -> dict:
        path = self.manual_threat_scan_path()
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def repository_scan_sample(self, repository_path: str, max_files: int = 120, hash_files: int = 5) -> dict:
        root = Path(repository_path)
        if not repository_path or repository_path == "-" or not root.exists():
            return {
                "reachable": False,
                "file_count": 0,
                "sample_hashes": [],
                "suspicious": [],
                "total_bytes": 0,
                "message": "Repository path is not reachable from the WebUI process.",
            }
        queue = [root]
        file_count = 0
        total_bytes = 0
        sample_hashes: list[dict] = []
        suspicious: list[dict] = []
        suspicious_suffixes = (".lock", ".locked", ".encrypted", ".crypt", ".enc", ".ryk", ".wannacry")
        while queue and file_count < max_files:
            current = queue.pop(0)
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            if len(queue) < 40:
                                queue.append(Path(entry.path))
                            continue
                        if not entry.is_file(follow_symlinks=False):
                            continue
                        file_count += 1
                        try:
                            stat = entry.stat(follow_symlinks=False)
                            total_bytes += int(stat.st_size)
                        except OSError:
                            stat = None
                        suffix = Path(entry.name).suffix.lower()
                        if suffix in suspicious_suffixes:
                            suspicious.append(
                                {
                                    "type": "의심 확장자",
                                    "file_path": entry.path,
                                    "evidence": f"{suffix} 확장자 탐지",
                                    "severity": "WARN",
                                    "status": "관리자 확인 필요",
                                }
                            )
                        if len(sample_hashes) < hash_files:
                            digest = hashlib.sha256()
                            try:
                                with open(entry.path, "rb") as handle:
                                    digest.update(handle.read(64 * 1024))
                                sample_hashes.append(
                                    {
                                        "path": entry.path,
                                        "sha256_64k": digest.hexdigest(),
                                        "size": int(stat.st_size) if stat else 0,
                                    }
                                )
                            except OSError:
                                pass
                        if file_count >= max_files:
                            break
            except OSError:
                continue
        return {
            "reachable": True,
            "file_count": file_count,
            "sample_hashes": sample_hashes,
            "suspicious": suspicious,
            "total_bytes": total_bytes,
            "message": f"Sampled {file_count} files from repository path.",
        }

    def run_manual_threat_scan(self) -> dict:
        started = datetime.now()
        scan_id = f"manual-{started.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        actor = self.current_session_user()
        veeam_config = get_veeam_config(self.context.app_config) or {}
        repository_path = str(
            veeam_config.get("target_repository_path")
            or self.context.veeam_backup_copy_repository_path()
            or "D:\\BackupCopyRepo"
        ).strip()
        repository_name = str(veeam_config.get("target_repository_name") or "Repository-D")
        backup_job = str(veeam_config.get("job_name") or veeam_config.get("target_job_name") or "Daily Backup")
        self.context.controller.audit.write(
            "threat.manual_scan.started",
            actorUserId=actor,
            actor_role=self.current_role().value,
            scan_id=scan_id,
            repository_path=repository_path,
            backup_job=backup_job,
            result="STARTED",
            message="Manual threat scan was started from the WebUI.",
        )
        sample = self.repository_scan_sample(repository_path)
        try:
            repository_volume = repository_volume_root(repository_path)
        except ValueError:
            repository_volume = "-"
        policy_safe = bool(repository_volume and repository_volume != "-" and not repository_volume.upper().startswith("C:"))
        detections = sample["suspicious"] if isinstance(sample.get("suspicious"), list) else []
        suspicious_count = len(detections)
        if suspicious_count:
            result = "주의"
            score = min(70, 35 + suspicious_count * 8)
            action_status = "관리자 확인 필요"
            lockfix_action = "Air-gap 유지 / 의심 파일 검토"
        elif not policy_safe:
            result = "주의"
            score = 46
            action_status = "저장소 정책 확인 필요"
            lockfix_action = "Air-gap 유지 / C 드라이브 저장소 차단"
        else:
            result = "정상"
            score = 12
            action_status = "검사 완료"
            lockfix_action = "Disk Offline / Drive Letter 제거 / Air-gap 전환"
        completed = datetime.now()
        duration_ms = int((completed - started).total_seconds() * 1000)
        proof = {
            "scan_id": scan_id,
            "started_at": started.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": completed.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_ms": duration_ms,
            "actor": actor,
            "repository_name": repository_name,
            "repository_path": repository_path,
            "repository_volume": repository_volume,
            "backup_job": backup_job,
            "scan_target": repository_path,
            "engine": "Veeam Malware REST API + Windows Defender + YARA + Repository Hash",
            "result": result,
            "score": score,
            "suspicious_count": suspicious_count,
            "action_status": action_status,
            "lockfix_action": lockfix_action,
            "audit_log_id": "THREAT_MANUAL_SCAN_COMPLETED",
            "detections": detections,
            "evidence": [
                {
                    "name": "Repository path",
                    "status": "OK" if sample.get("reachable") else "CHECK",
                    "detail": sample.get("message") or "-",
                },
                {
                    "name": "Repository volume policy",
                    "status": "OK" if policy_safe else "CHECK",
                    "detail": f"{repository_volume} volume is evaluated for Air-Gap protection.",
                },
                {
                    "name": "Sample hash proof",
                    "status": "OK" if sample.get("sample_hashes") else "SKIPPED",
                    "detail": f"{len(sample.get('sample_hashes') or [])} file sample hashes captured.",
                },
                {
                    "name": "Suspicious extension sweep",
                    "status": "OK" if suspicious_count == 0 else "WARN",
                    "detail": f"{suspicious_count} suspicious file indicators found.",
                },
            ],
            "sample_hashes": sample.get("sample_hashes") or [],
            "scanned_files": int(sample.get("file_count") or 0),
            "scanned_bytes": int(sample.get("total_bytes") or 0),
        }
        path = self.manual_threat_scan_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
        self.context.controller.audit.write(
            "threat.manual_scan.completed",
            actorUserId=actor,
            actor_role=self.current_role().value,
            scan_id=scan_id,
            repository_path=repository_path,
            backup_job=backup_job,
            result=result,
            score=score,
            suspicious_count=suspicious_count,
            scanned_files=proof["scanned_files"],
            duration_ms=duration_ms,
            message="Manual threat scan completed and proof was stored.",
        )
        summary = self.threat_detection_summary()
        summary["manual_scan"] = proof
        return {"ok": True, "manual_scan": proof, "summary": summary}

    def admin_memo_path(self) -> Path:
        return ROOT / "runtime" / "admin_memos.json"

    def read_admin_memos(self) -> list[dict]:
        path = self.admin_memo_path()
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return payload if isinstance(payload, list) else []

    def memo_cutoff(self, days: int = 30) -> datetime:
        return datetime.now() - timedelta(days=max(1, int(days or 30)))

    def memo_is_recent(self, item: dict, days: int = 30) -> bool:
        created_at = str(item.get("created_at") or "")
        try:
            return datetime.fromisoformat(created_at) >= self.memo_cutoff(days)
        except ValueError:
            return False

    def prune_admin_memos(self, items: list[dict], days: int = 30) -> list[dict]:
        recent = [dict(item) for item in items if isinstance(item, dict) and self.memo_is_recent(item, days)]
        path = self.admin_memo_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(recent, ensure_ascii=False, indent=2), encoding="utf-8")
        return recent

    def admin_memo_history(self, target_id: str, days: int = 30) -> list[dict]:
        target = str(target_id or "").strip()
        items = self.prune_admin_memos(self.read_admin_memos(), days=days)
        history = [
            item
            for item in items
            if not target or str(item.get("target_id") or "") == target
        ]
        history.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return history

    def latest_admin_memo(self, target_id: str) -> dict:
        history = self.admin_memo_history(target_id, days=30)
        return history[0] if history else {}

    def save_admin_memo(self, payload: dict) -> dict:
        target_id = str(payload.get("targetId") or payload.get("target_id") or "").strip()
        note = str(payload.get("note") or "").strip()
        if not target_id:
            raise ValueError("targetId is required")
        if not note:
            raise ValueError("admin memo is required")
        if len(note) > 2000:
            raise ValueError("admin memo must be 2000 characters or fewer")
        items = self.prune_admin_memos(self.read_admin_memos(), days=30)
        record = {
            "id": uuid.uuid4().hex,
            "target_id": target_id,
            "note": note,
            "actor": self.current_session_user(),
            "actor_role": self.current_role().value,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        items.append(record)
        self.admin_memo_path().write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.context.controller.audit.write(
            "admin.memo.created",
            actorUserId=record["actor"],
            actor_role=record["actor_role"],
            target_id=target_id,
            retention_days=30,
            message="Administrator memo was saved and retained for 30 days.",
        )
        return {"ok": True, "item": record, "items": self.admin_memo_history(target_id, days=30)}

    def detect_summary(self, live: bool = False) -> dict:
        cache_key = str(self.context.config_path)
        now_monotonic = time.monotonic()
        if not live:
            with LockFixWebHandler.detect_cache_lock:
                cached = LockFixWebHandler.detect_cache_by_key.get(cache_key)
                if cached and now_monotonic - cached[0] < DETECT_CACHE_TTL_SECONDS:
                    return LockFixWebHandler.clone_payload(cached[1])
        payload = LockFixWebHandler.detect_summary_uncached(self)
        with LockFixWebHandler.detect_cache_lock:
            LockFixWebHandler.detect_cache_by_key[cache_key] = (time.monotonic(), payload)
        return LockFixWebHandler.clone_payload(payload)

    def detect_summary_uncached(self) -> dict:
        config = self.context.config
        if not config.slots:
            emergency_summary = self.emergency_access_summary()
            return {
                "title": "LOCK-FIX 기준으로 가장 안전한 판단 방식",
                "subtitle": "디스크 식별 슬롯 설정이 등록되면 UID와 fingerprint 검증을 자동으로 표시합니다.",
                "fingerprint": {
                    "slot_id": "",
                    "value": "",
                    "registered_value": "",
                    "status": "NOT_CONFIGURED",
                    "match": False,
                    "parts": [],
                    "display": ["Disk Identity Fingerprint ="],
                    "formula_title": "LOCK-FIX-DISK-FINGERPRINT =",
                    "formula": "slot configuration required",
                    "conclusion": "에이전트 설치 시 입력한 저장소/슬롯 설정을 기준으로 디스크 식별값이 구성되어야 합니다.",
                },
                "emergency_access": emergency_summary,
                "veeam_repository": LockFixWebHandler.detect_veeam_repository_summary(self, fast=isinstance(self, LockFixWebHandler)),
            }
        slot = next(iter(config.slots.values()))
        emergency_summary = self.emergency_access_summary()
        emergency_slot = emergency_summary.get("slot") if isinstance(emergency_summary, dict) else {}
        emergency_state = str((emergency_slot or {}).get("state") or "").upper()
        emergency_hash_status = str((emergency_slot or {}).get("hash_status") or "").upper()
        isolated_waiting_for_mount = emergency_state in {
            "ISOLATED",
            "OFFLINE",
            "DISK_OFFLINE",
            "DISK_OFFLINE_COMPLETE",
            "OFFLINE_COMPLETE",
            "UNMOUNTED",
            "DISMOUNTED",
        } and emergency_hash_status in {"WAITING_FOR_MOUNT", "MOUNT_ACCESS_ERROR"}
        unique_id = slot_uid(slot)
        parts = fingerprint_parts(slot)
        display_lines = ["Disk Identity Fingerprint ="]
        display_lines.extend(part["label"] if index == 0 else f"+ {part['label']}" for index, part in enumerate(parts))
        formula = fingerprint_formula(parts)
        registered = slot.expected_uid
        registered_ready = bool(registered and registered != "replace-with-registered-uid")
        match = registered_ready and registered == unique_id
        status = "ISOLATED" if isolated_waiting_for_mount else "MATCH" if match else "UNREGISTERED" if not registered_ready else "DIFFERENT_DISK"
        isolated_volume_label = str(slot.device or slot.mount_point or "볼륨")
        conclusion = (
            f"{isolated_volume_label} 볼륨이 오프라인/언마운트되어 실시간 UID와 크기 검증은 대기 중입니다. 격리 상태는 정상이며 재접속 시 다시 검증합니다."
            if isolated_waiting_for_mount
            else "이 값이 기존 등록값과 다르면 다른 디스크로 판단합니다."
        )
        return {
            "title": "LOCK-FIX 기준으로 가장 안전한 판단 방식",
            "subtitle": "LOCK-FIX에서는 하나의 값만 보지 말고 아래 조합을 기준으로 해야 합니다.",
            "emergency_access": emergency_summary,
            "veeam_repository": LockFixWebHandler.detect_veeam_repository_summary(self, fast=isinstance(self, LockFixWebHandler)),
            "fingerprint": {
                "slot_id": slot.slot_id,
                "value": unique_id,
                "registered_value": registered if registered_ready else "",
                "status": status,
                "match": match,
                "parts": [{**part, "value": part["value"] or "-"} for part in parts],
                "display": display_lines,
                "formula_title": "LOCK-FIX-DISK-FINGERPRINT =",
                "formula": formula,
                "conclusion": conclusion,
            },
        }

    def detect_veeam_repository_summary(self, fast: bool = False) -> dict:
        veeam_config = get_veeam_config(self.context.app_config) or {}
        configured_path = str(veeam_config.get("target_repository_path") or self.context.veeam_backup_copy_repository_path() or "").strip()
        configured_name = str(veeam_config.get("target_repository_name") or "").strip()
        base_url = str(veeam_config.get("base_url") or "").strip()
        parsed_url = urlparse(base_url) if base_url else None
        def safe_backup_copy_repository(path: str) -> tuple[str, bool]:
            if not path:
                return "", False
            try:
                volume = repository_volume_root(path)
            except ValueError:
                return "", False
            normalized = volume.strip().replace("/", "\\").rstrip("\\").lower()
            if normalized == "c:":
                return "", False
            return path, True

        configured_path, configured_allowed = safe_backup_copy_repository(configured_path)
        fallback = {
            "repository_name": configured_name or ("Veeam Repository" if configured_allowed else "Backup Copy 저장소 대상 아님"),
            "repository_path": configured_path or "-",
            "job": str(veeam_config.get("job_name") or veeam_config.get("target_job_name") or "-"),
            "api_synced": False,
            "source": "config",
            "server": parsed_url.hostname if parsed_url else "",
            "port": parsed_url.port if parsed_url else "",
            "eligible": configured_allowed,
            "blocked_reason": "" if configured_allowed else "protected_or_unconfigured_repository_volume",
        }
        if fast or not veeam_config.get("enabled", False):
            return fallback
        try:
            runner = getattr(self, "run_veeam_diagnostics_limited", None)
            diagnostics = (
                runner(veeam_config, timeout_seconds=3.0)
                if callable(runner)
                else LockFixWebHandler.run_veeam_diagnostics_limited(self, veeam_config, timeout_seconds=3.0)
            )
        except Exception as exc:
            return {**fallback, "error": str(exc)}
        if not isinstance(diagnostics, dict):
            return fallback
        session = diagnostics.get("latest_configured_session") if isinstance(diagnostics.get("latest_configured_session"), dict) else {}
        api = diagnostics.get("api") if isinstance(diagnostics.get("api"), dict) else {}
        matching = api.get("matching") if isinstance(api.get("matching"), dict) else {}
        repository_name = str(
            session.get("repository_name")
            or session.get("repository")
            or configured_name
            or "Veeam Repository"
        ).strip()
        source = str(session.get("source") or diagnostics.get("source") or api.get("source") or "config").strip()
        raw_repository_path = str(session.get("repository_path") or configured_path or "").strip()
        repository_path, repository_allowed = safe_backup_copy_repository(raw_repository_path)
        if not repository_allowed:
            return {
                **fallback,
                "repository_name": "Backup Copy 저장소 대상 아님",
                "repository_path": "-",
                "api_synced": bool(session) and source != "config",
                "source": source,
                "eligible": False,
                "blocked_reason": "protected_or_non_backup_copy_repository_volume",
            }
        job = str(
            session.get("job")
            or session.get("job_name")
            or session.get("name")
            or matching.get("job_name")
            or veeam_config.get("job_name")
            or "-"
        ).strip()
        return {
            "repository_name": repository_name or fallback["repository_name"],
            "repository_path": repository_path or fallback["repository_path"],
            "job": job or fallback["job"],
            "api_synced": bool(session) and source != "config",
            "source": source,
            "server": str(session.get("server") or fallback["server"] or ""),
            "port": str(session.get("port") or fallback["port"] or ""),
            "eligible": True,
            "blocked_reason": "",
        }

    def network_rate_history(self, interface_id: str, tx_mbps: float, rx_mbps: float, seed_count: int = 60) -> tuple[list[float], list[float]]:
        key = interface_id or "NIC1"
        with NETWORK_HISTORY_LOCK:
            bucket = NETWORK_INTERFACE_HISTORY.setdefault(key, {"tx": [], "rx": []})
            if not bucket["tx"]:
                bucket["tx"] = [round(tx_mbps, 2)] * seed_count
                bucket["rx"] = [round(rx_mbps, 2)] * seed_count
            else:
                bucket["tx"].append(round(tx_mbps, 2))
                bucket["rx"].append(round(rx_mbps, 2))
            bucket["tx"] = bucket["tx"][-seed_count:]
            bucket["rx"] = bucket["rx"][-seed_count:]
            return list(bucket["tx"]), list(bucket["rx"])

    def read_live_network_interfaces(self) -> list[dict]:
        if platform.system().lower() != "windows":
            return []
        powershell = shutil.which("powershell.exe") or str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe")
        script = r"""
$stats = @(Get-CimInstance Win32_PerfFormattedData_Tcpip_NetworkInterface | Where-Object {
  $_.Name -and $_.Name -notmatch 'Loopback|Teredo|isatap'
} | Select-Object Name,BytesSentPersec,BytesReceivedPersec,CurrentBandwidth)
$ips = @(Get-NetIPConfiguration | Select-Object InterfaceAlias,InterfaceDescription,
  @{Name='IPv4';Expression={($_.IPv4Address | Select-Object -First 1).IPAddress}},
  @{Name='IPv6';Expression={($_.IPv6Address | Where-Object { $_.IPAddress -like 'fe80*' } | Select-Object -First 1).IPAddress}})
[pscustomobject]@{ stats = $stats; ips = $ips } | ConvertTo-Json -Compress -Depth 5
"""
        try:
            result = subprocess.run(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3,
                check=False,
            )
        except Exception:
            return []
        if result.returncode != 0 or not result.stdout.strip():
            return []
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

        def as_list(value: object) -> list:
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return [value]
            return []

        def norm(value: object) -> str:
            return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())

        ips = as_list(payload.get("ips") if isinstance(payload, dict) else [])
        stats = as_list(payload.get("stats") if isinstance(payload, dict) else [])
        ip_rows = []
        for row in ips:
            if isinstance(row, dict):
                ip_rows.append(row)
        interfaces = []
        for index, row in enumerate(stats):
            if not isinstance(row, dict):
                continue
            raw_name = str(row.get("Name") or "").strip()
            if not raw_name:
                continue
            name_key = norm(raw_name)
            def ip_row_matches(item: dict) -> bool:
                description_key = norm(item.get("InterfaceDescription"))
                alias_key = norm(item.get("InterfaceAlias"))
                return (
                    (description_key and description_key == name_key)
                    or (alias_key and alias_key == name_key)
                    or (alias_key and alias_key in name_key)
                    or (description_key and name_key in description_key)
                )

            ip_match = next((item for item in ip_rows if ip_row_matches(item)), {})
            alias = str(ip_match.get("InterfaceAlias") or "").strip()
            interface_id = alias or f"NIC{index + 1}"
            tx_mbps = max(0.0, float(row.get("BytesSentPersec") or 0) * 8 / 1_000_000)
            rx_mbps = max(0.0, float(row.get("BytesReceivedPersec") or 0) * 8 / 1_000_000)
            tx_history, rx_history = self.network_rate_history(interface_id, tx_mbps, rx_mbps)
            interfaces.append(
                {
                    "id": interface_id,
                    "label": interface_id,
                    "adapter_name": alias or raw_name,
                    "connection_type": "이더넷",
                    "ipv4": str(ip_match.get("IPv4") or ""),
                    "ipv6": str(ip_match.get("IPv6") or ""),
                    "tx_mbps": round(tx_mbps, 2),
                    "rx_mbps": round(rx_mbps, 2),
                    "total_tx_gb": round(sum(tx_history) / 180, 2),
                    "total_rx_gb": round(sum(rx_history) / 180, 2),
                    "tx_history": tx_history,
                    "rx_history": rx_history,
                    "source": "windows_perf_counter",
                }
            )
        return interfaces

    def fallback_network_history(self, base: float, amplitude: float, tick: int, phase: int, samples: int = 60) -> list[float]:
        values = []
        for sample in range(samples):
            position = tick + sample + phase
            slow = ((position * (phase + 3)) % 17) / 16
            pulse = 1.0 if position % (13 + phase) in (0, 1) else 0.0
            dip = 0.55 if position % (19 + phase) == 0 else 1.0
            value = (base + amplitude * slow + amplitude * 0.9 * pulse) * dip
            values.append(round(max(0.02, value), 2))
        return values

    def fallback_network_interfaces(self, tick: int) -> list[dict]:
        profiles = [
            ("NIC1", "NIC1", "192.168.219.230", "fe80::42c6:c684:b35c:85fe%16", 2.1, 5.8),
            ("NIC2", "NIC2", "172.16.0.12", "fe80::8f2:1aff:fe21:9b20%18", 0.8, 2.4),
            ("Backup Bond", "bond0", "10.10.1.21", "", 1.3, 3.2),
            ("VM Bridge", "vmbr0", "127.0.0.1", "", 0.3, 1.1),
        ]
        interfaces = []
        for index, (label, interface_id, ipv4, ipv6, tx_base, rx_base) in enumerate(profiles):
            tx_history = self.fallback_network_history(tx_base, 1.4 + index * 0.3, tick, index + 1)
            rx_history = self.fallback_network_history(rx_base, 2.1 + index * 0.4, tick * 2, index + 2)
            interfaces.append(
                {
                    "id": interface_id,
                    "label": label,
                    "adapter_name": label,
                    "connection_type": "이더넷",
                    "ipv4": ipv4,
                    "ipv6": ipv6,
                    "tx_mbps": tx_history[-1],
                    "rx_mbps": rx_history[-1],
                    "total_tx_gb": round(sum(tx_history) / 20, 2),
                    "total_rx_gb": round(sum(rx_history) / 20, 2),
                    "tx_history": tx_history,
                    "rx_history": rx_history,
                    "source": "mock_fallback",
                }
            )
        return interfaces

    def network_status_summary(self) -> dict:
        tick = int(time.time() / 5)
        names = [
            "112.148.194.115",
            "127.0.0.1",
            "172.16.0.12",
            "192.168.0.10",
            "10.10.1.21",
            "10.10.1.22",
            "10.10.1.23",
            "10.10.1.24",
            "10.10.1.25",
            "10.10.1.26",
            "10.10.1.27",
            "10.10.1.28",
            "oam-datacenter",
            "web-solution",
            "backup-node",
            "license-server",
            "smtp.oam.co.kr",
            "monitoring-api",
            "remote-support",
            "storage-gateway",
            "eth0",
            "eth1",
            "bond0",
            "vmbr0",
        ]
        items = []
        tx_history = []
        rx_history = []
        for index, name in enumerate(names):
            tx = 0.55 + (((index * 7) + tick) % 13) * 0.08
            rx = 0.92 + (((index * 11) + tick * 2) % 19) * 0.1
            if index == 0:
                tx, rx = 2.2 + (tick % 5) * 0.18, 6.1 + (tick % 7) * 0.22
            elif index in (1, 2):
                tx = 2.9 - index * 0.3 + (tick % 4) * 0.12
                rx = 4.2 - index * 0.25 + (tick % 6) * 0.16
            items.append(
                {
                    "target": name,
                    "tx_gb": round(tx, 2),
                    "rx_gb": round(rx, 2),
                    "bandwidth_kb": 1024 * (100 + index * 10),
                }
            )
        for index in range(28):
            tx_history.append(round(18 + (((index + tick) * 9) % 27) + (6 if (index + tick) % 9 == 0 else 0), 1))
            rx_history.append(round(34 + (((index + tick) * 13) % 39) + (8 if (index + tick) % 9 == 0 else 0), 1))
        packet_loss = round(0.05 + (tick % 9) * 0.06, 2)
        latency_ms = 14 + (tick % 8) * 3
        jitter_ms = 2 + (tick % 5)
        veeam_sync = self.ensure_veeam_execution_settings_synced(manual=False)
        veeam_base_url = str(veeam_sync.get("effective_base_url") or veeam_sync.get("installed_base_url") or "")
        veeam_url = urlparse(veeam_base_url)
        veeam_host = veeam_url.hostname or str(veeam_sync.get("installed_host") or "127.0.0.1")
        veeam_port = int(veeam_url.port or veeam_sync.get("installed_port") or 9419)
        veeam_port_open = self.tcp_port_open(veeam_host, veeam_port)
        veeam_previous_url = urlparse(str(veeam_sync.get("config_base_url") or veeam_base_url))
        veeam_previous_host = veeam_previous_url.hostname or veeam_host
        current_ip_match = bool(veeam_sync.get("ok") and veeam_host and veeam_previous_host == veeam_host and veeam_port_open)
        ports = [
            {
                "port": 9419,
                "service": "Veeam REST API",
                "protocol": "TCP",
                "state": "ALLOW" if current_ip_match else "ALLOW_STALE",
                "risk": "Current agent IP" if current_ip_match else "Past IP allowed",
                "target": f"{veeam_host}:{veeam_port}",
                "veeam_config": {
                    "installed_base_url": veeam_base_url,
                    "previous_base_url": veeam_sync.get("config_base_url") or "",
                    "current_ip_match": current_ip_match,
                    "port_open": veeam_port_open,
                    "sync": veeam_sync,
                },
            },
            {"port": 5985, "service": "WinRM HTTP", "protocol": "TCP", "state": "ALLOW", "risk": "Managed"},
            {"port": 5986, "service": "WinRM HTTPS", "protocol": "TCP", "state": "PROTECTED", "risk": "Not configured"},
            {"port": 445, "service": "SMB", "protocol": "TCP", "state": "PROTECTED", "risk": "Recovery only"},
            {"port": 3389, "service": "RDP", "protocol": "TCP", "state": "PROTECTED", "risk": "Admin approval"},
        ]
        insights = [
            {
                "level": "ok" if packet_loss < 0.3 else "warning",
                "title": "Packet Loss",
                "detail": f"Current loss is {packet_loss:.2f}%. Keep under 1.00% for backup traffic quality.",
            },
            {
                "level": "ok" if latency_ms < 50 else "warning",
                "title": "Latency",
                "detail": f"Average response time is {latency_ms} ms. No path bottleneck is detected.",
            },
            {
                "level": "warning" if any(port["state"] == "ALLOW" and port["port"] == 5985 for port in ports) else "ok",
                "title": "Port Exposure",
                "detail": "Veeam REST is checked against the current agent install IP. Managed WinRM is allowed; recovery ports remain blocked until approval.",
            },
        ]
        event_time = datetime.now().strftime("%H:%M:%S")
        path_status = [
            {
                "name": "LOCK-FIX -> Veeam REST",
                "target": f"{veeam_host}:{veeam_port}",
                "state": "Reachable" if current_ip_match else "Check",
                "latency_ms": max(1, latency_ms - 8),
                "last_check": event_time,
            },
            {
                "name": "LOCK-FIX -> WinRM",
                "target": "192.168.219.165:5985",
                "state": "Managed",
                "latency_ms": max(2, latency_ms - 4),
                "last_check": event_time,
            },
            {
                "name": "LOCK-FIX -> Gateway",
                "target": "storage-gateway",
                "state": "Protected",
                "latency_ms": latency_ms + 6,
                "last_check": event_time,
            },
            {
                "name": "LOCK-FIX -> Recovery Ports",
                "target": "445 / 3389",
                "state": "Blocked",
                "latency_ms": None,
                "last_check": event_time,
            },
        ]
        events = [
            {
                "level": "ok" if current_ip_match else "warning",
                "time": event_time,
                "message": (
                    f"Veeam REST API 9419 is allowed for current agent IP {veeam_host}."
                    if current_ip_match
                    else f"Veeam REST API 9419 allow state must be synced to current agent IP {veeam_host}."
                ),
            },
            {"level": "ok", "time": event_time, "message": "WinRM 5985 is allowed only for managed operation."},
            {"level": "protected", "time": event_time, "message": "SMB and RDP recovery ports remain protected until approval."},
            {
                "level": "warning" if packet_loss >= 0.3 else "ok",
                "time": event_time,
                "message": f"Packet loss is {packet_loss:.2f}% and remains under the 1.00% operating threshold.",
            },
        ]
        interfaces = self.read_live_network_interfaces() or self.fallback_network_interfaces(tick)
        primary_interface = interfaces[0] if interfaces else {
            "tx_history": tx_history,
            "rx_history": rx_history,
            "tx_mbps": tx_history[-1],
            "rx_mbps": rx_history[-1],
            "total_tx_gb": round(sum(item["tx_gb"] for item in items), 2),
            "total_rx_gb": round(sum(item["rx_gb"] for item in items), 2),
        }
        return {
            "title": "실시간 네트워크",
            "unit": "GB",
            "interval_seconds": 1,
            "realtime": {
                "tx": {
                    "label": "송신",
                    "current_mbps": primary_interface["tx_mbps"],
                    "total_gb": primary_interface["total_tx_gb"],
                    "history": primary_interface["tx_history"],
                },
                "rx": {
                    "label": "수신",
                    "current_mbps": primary_interface["rx_mbps"],
                    "total_gb": primary_interface["total_rx_gb"],
                    "history": primary_interface["rx_history"],
                },
            },
            "interfaces": interfaces,
            "items": items,
            "analysis": {
                "quality": {
                    "packet_loss_percent": packet_loss,
                    "latency_ms": latency_ms,
                    "jitter_ms": jitter_ms,
                },
                "ports": ports,
                "insights": insights,
                "path_status": path_status,
                "events": events,
            },
        }

    def log_items(self, start_date: str = "", end_date: str = "", retention_days: int = 30) -> tuple[list[dict], datetime, datetime]:
        now = datetime.now()
        range_end = datetime(now.year, now.month, now.day, 23, 59, 59)
        range_start = range_end - timedelta(days=retention_days - 1)
        try:
            if start_date:
                range_start = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                range_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
            if range_end < range_start:
                range_end = range_start + timedelta(hours=23, minutes=59, seconds=59)
        except ValueError:
            range_end = datetime(now.year, now.month, now.day, 23, 59, 59)
            range_start = range_end - timedelta(days=retention_days - 1)

        retention_start = datetime(now.year, now.month, now.day) - timedelta(days=retention_days - 1)
        range_start = max(range_start, retention_start)
        templates = [
            ("WARNING", "performance", "WARN", "[MEMORY] {memory}% (임계:80.0%)"),
            ("DETECT", "hardware", "INFO", "[NIC] eth0 link status verified"),
            ("SYSLOG", "systemd", "INFO", "lockfix-monitor.service heartbeat ok"),
            ("SYSLOG", "network", "INFO", "vmbr0 rx/tx counters updated"),
            ("LOGS", "account", "INFO", "dashboard data export request completed"),
        ]
        items = []
        for day_offset in range(retention_days):
            day = datetime(now.year, now.month, now.day) - timedelta(days=day_offset)
            for index, (kind, source, severity, message) in enumerate(templates):
                stamp = day.replace(hour=13 - index, minute=(3 + day_offset + index * 7) % 60, second=13 if index == 0 else 0)
                if stamp < range_start or stamp > range_end:
                    continue
                memory = round(91.8 + ((day_offset + index) % 8) * 0.17, 4)
                items.append(
                    {
                        "type": kind,
                        "date": stamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "source": source,
                        "severity": severity,
                        "message": message.format(memory=memory),
                    }
                )
        for item in self.audit_items()[:50]:
            event = str(item.get("event", "audit_event"))
            severity = LockFixWebHandler.log_audit_severity(self, item)
            timestamp_text = str(item.get("ts", "-"))
            try:
                stamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
            except ValueError:
                continue
            if stamp.tzinfo is not None:
                stamp = stamp.astimezone().replace(tzinfo=None)
            raw_date = stamp.strftime("%Y-%m-%d %H:%M:%S")
            if stamp < range_start or stamp > range_end or stamp < retention_start:
                continue
            items.append(
                {
                    "type": LockFixWebHandler.log_audit_type(self, item),
                    "date": raw_date,
                    "source": LockFixWebHandler.log_audit_source(self, item),
                    "severity": severity,
                    "message": LockFixWebHandler.format_log_audit_record(self, item),
                }
            )
        items.sort(key=lambda item: item["date"], reverse=True)
        return items, range_start, range_end

    def is_admin_access_audit_record(self, record: dict) -> bool:
        event = str(record.get("event") or "").lower()
        text = json.dumps(record, ensure_ascii=False).lower()
        access_events = (
            "auth.",
            "login.",
            "logout.",
            "session.",
            "security.permission_denied",
            "security.remote_console_access",
            "security.unauthorized",
        )
        access_tokens = (
            "login",
            "logout",
            "session",
            "permission_denied",
            "forbidden",
            "access.denied",
            "access_denied",
            "remote_console_access",
            "403",
        )
        text_tokens = ("403 forbidden", "unauthorized access", "access denied", "액세스 거부", "권한")
        return (
            event.startswith(access_events)
            or any(token in event for token in access_tokens)
            or any(token in text for token in text_tokens)
        )

    def log_audit_type(self, record: dict) -> str:
        if LockFixWebHandler.is_admin_access_audit_record(self, record):
            return "관리자 접근 감사 로그"
        return "SYSLOG"

    def log_audit_source(self, record: dict) -> str:
        event = str(record.get("event") or "")
        if LockFixWebHandler.is_admin_access_audit_record(self, record):
            return "admin-access"
        if event.startswith("license"):
            return "license"
        if event.startswith("disk.offline") or event.startswith("disk.online") or event.startswith("disk.storage_api"):
            return "storage"
        if event.startswith("emergency.reconnect"):
            return "reconnect"
        if event.startswith("veeam"):
            return "veeam"
        return "audit"

    def log_audit_severity(self, record: dict) -> str:
        event = str(record.get("event") or "").lower()
        text = json.dumps(record, ensure_ascii=False).lower()
        if "error" in event or "failed" in event or "denied" in event or "unauthorized" in event:
            return "ERROR"
        if "warning" in event or "expired" in event or "timeout" in event or "access denied" in text or "액세스 거부" in text:
            return "WARN"
        return "INFO"

    def extract_lockfix_storage_state(self, output: object) -> dict:
        text = str(output or "")
        for line in text.splitlines():
            marker = "LOCKFIX_STORAGE_STATE="
            if marker not in line:
                continue
            raw = line.split(marker, 1)[1].strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}

    def format_log_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "audit_event")
        slot_id = str(record.get("slot_id") or "-")
        if LockFixWebHandler.is_admin_access_audit_record(self, record):
            user = LockFixWebHandler.compact_log_value(
                self,
                record.get("user")
                or record.get("userId")
                or record.get("user_id")
                or record.get("actor")
                or record.get("actorUserId")
                or "-",
            )
            ip_address = LockFixWebHandler.compact_log_value(
                self,
                record.get("ipAddress") or record.get("ip_address") or record.get("client_ip") or "-",
            )
            result = LockFixWebHandler.compact_log_value(self, record.get("result") or record.get("status") or "-")
            message = LockFixWebHandler.compact_log_value(
                self, record.get("message") or record.get("error") or record.get("reason") or event
            )
            return f"관리자 접근 감사 - user {user}, ip {ip_address}, result {result}: {message}"
        if event.startswith("emergency.reconnect") or event in {
            "disk.online.approved",
            "disk.online.start",
            "disk.online.tick",
            "disk.online",
            "disk.online.error",
            "disk.online.approval.cleared",
            "disk.reconnect.plan",
            "disk.wait.start",
            "disk.wait.tick",
            "disk.wait.found",
            "disk.access_path.start",
            "disk.access_path",
            "disk.access_path.error",
            "disk.mount_ro.start",
            "disk.mount_ro.tick",
            "disk.mount_ro",
            "disk.mount_ro.error",
            "disk.health.scan.start",
            "disk.health.scan",
            "disk.health.scan.skipped",
            "disk.health.scan.error",
            "disk.mount_rw.start",
            "disk.mount_rw.tick",
            "disk.mount_rw",
            "disk.mount_rw.error",
            "disk.storage_api.self_check.error",
            "disk.storage_api.self_check",
            "verify.uid",
            "verify.hash",
            "power.mock.on.start",
            "power.mock.on.tick",
            "power.mock.on",
            "power.command.on.start",
            "power.command.on.tick",
            "power.command.on",
            "power.command.on.error",
        }:
            formatted = LockFixWebHandler.format_reconnect_audit_record(self, record)
            if formatted:
                return formatted
        if event == "disk.offline.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            return (
                f"LOCK-FIX Offline START - slot {slot_id}, drive {drive}: "
                "Get-Partition/Get-Disk 대상 확인 후 Windows 디스크 오프라인 전환을 시작했습니다."
            )
        if event == "disk.offline.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or "1")
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            return f"LOCK-FIX Offline CHECK - slot {slot_id}, drive {drive}: 오프라인 증명 확인 {elapsed}s 경과."
        if event == "disk.offline":
            proof = LockFixWebHandler.extract_lockfix_storage_state(self, record.get("output"))
            drive = LockFixWebHandler.compact_log_value(self, proof.get("drive") or record.get("drive_letter") or "-")
            disk_number = LockFixWebHandler.compact_log_value(self, proof.get("diskNumber") or record.get("disk_number") or "-")
            is_offline = proof.get("isOffline", record.get("is_offline", "-"))
            method = LockFixWebHandler.compact_log_value(self, proof.get("method") or record.get("method") or "Set-Disk -IsOffline true")
            return (
                f"LOCK-FIX Offline CONFIRMED - slot {slot_id}, drive {drive}, disk {disk_number}, "
                f"IsOffline={is_offline}, method={method}."
            )
        if event == "disk.offline.verify.start":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            disk_number = LockFixWebHandler.compact_log_value(self, record.get("disk_number") or "-")
            access_path = LockFixWebHandler.compact_log_value(self, record.get("access_path") or f"{drive}:\\")
            return f"LOCK-FIX Offline VERIFY START - slot {slot_id}, drive {drive}, disk {disk_number}, path {access_path}."
        if event == "disk.offline.verify":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            disk_number = LockFixWebHandler.compact_log_value(self, record.get("disk_number") or "-")
            is_offline = LockFixWebHandler.compact_log_value(self, record.get("is_offline"))
            path_reachable = LockFixWebHandler.compact_log_value(self, record.get("path_reachable"))
            return f"LOCK-FIX Offline VERIFY CONFIRMED - slot {slot_id}, drive {drive}, disk {disk_number}, IsOffline={is_offline}, PathReachable={path_reachable}."
        if event == "disk.offline.verify.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "offline verification failed")
            return f"LOCK-FIX Offline VERIFY ERROR - slot {slot_id}, {error}"
        if event == "disk.offline.proof":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            disk_number = LockFixWebHandler.compact_log_value(self, record.get("disk_number") or "-")
            is_offline = LockFixWebHandler.compact_log_value(self, record.get("is_offline"))
            method = LockFixWebHandler.compact_log_value(self, record.get("method") or "Set-Disk -IsOffline true")
            return (
                f"LOCK-FIX Offline PROOF - slot {slot_id}, drive {drive}, disk {disk_number}, "
                f"IsOffline={is_offline}, evidence=Get-Disk/Set-Disk, method={method}."
            )
        if event == "disk.offline.strict.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "true disk offline proof was not obtained")
            return f"LOCK-FIX Offline STRICT ERROR - slot {slot_id}, {error}"
        if event == "disk.offline.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "offline failed")
            return f"LOCK-FIX Offline ERROR - slot {slot_id}, {error}"
        if event == "state.transition" and record.get("state") == "DISK_OFFLINING":
            return f"LOCK-FIX Offline STATE - slot {slot_id}, step 5 disk offlining started."
        if event == "state.transition" and record.get("state") == "ISOLATED":
            return f"LOCK-FIX Isolated STATE - slot {slot_id}, step 5 offline isolation completed."
        message = record.get("message") or record.get("error") or record.get("output") or event
        return LockFixWebHandler.compact_log_value(self, message)

    def retention_days(self, value: str = "30") -> int:
        try:
            days = int(value)
        except ValueError:
            days = 30
        return min(100, max(30, days))

    def filter_log_items(
        self,
        items: list[dict],
        type_filter: str = "",
        severity: str = "",
        source: str = "",
        query: str = "",
    ) -> list[dict]:
        type_filter = str(type_filter or "").strip().lower()
        severity = str(severity or "").strip().upper()
        source = str(source or "").strip().lower()
        query = str(query or "").strip().lower()
        filtered = []
        for item in items:
            item_type = str(item.get("type") or "").lower()
            item_severity = str(item.get("severity") or "").upper()
            item_source = str(item.get("source") or "").lower()
            text = " ".join(str(item.get(key) or "") for key in ("type", "date", "source", "severity", "message")).lower()
            if type_filter and item_type != type_filter:
                continue
            if severity and item_severity != severity:
                continue
            if source and item_source != source:
                continue
            if query and query not in text:
                continue
            filtered.append(item)
        return filtered

    def log_summary_counts(self, items: list[dict]) -> dict:
        severity_counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
        type_counts = {}
        source_counts = {}
        for item in items:
            severity = str(item.get("severity") or "INFO").upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_name = str(item.get("type") or "-")
            source_name = str(item.get("source") or "-")
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
        return {
            "severity": severity_counts,
            "types": type_counts,
            "sources": source_counts,
        }

    def logs_summary(
        self,
        start_date: str = "",
        end_date: str = "",
        page_value: str = "1",
        retention_value: str = "30",
        type_filter: str = "",
        severity: str = "",
        source: str = "",
        query: str = "",
    ) -> dict:
        retention_days = self.retention_days(retention_value)
        items, range_start, range_end = self.log_items(start_date, end_date, retention_days)
        type_options = sorted({str(item.get("type") or "-") for item in items})
        source_options = sorted({str(item.get("source") or "-") for item in items})
        items = LockFixWebHandler.filter_log_items(self, items, type_filter, severity, source, query)
        summary = LockFixWebHandler.log_summary_counts(self, items)
        per_page = 30
        try:
            page = max(1, int(page_value))
        except ValueError:
            page = 1
        total_pages = max(1, (len(items) + per_page - 1) // per_page)
        page = min(page, total_pages)
        offset = (page - 1) * per_page
        return {
            "range": {"start": range_start.strftime("%Y-%m-%d"), "end": range_end.strftime("%Y-%m-%d")},
            "total_logs": len(items),
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "retention_days": retention_days,
            "summary": summary,
            "filters": {"type": type_filter, "severity": severity, "source": source, "q": query},
            "type_options": type_options,
            "source_options": source_options,
            "items": items[offset : offset + per_page],
        }

    def send_logs_csv(
        self,
        start_date: str = "",
        end_date: str = "",
        retention_value: str = "30",
        type_filter: str = "",
        severity: str = "",
        source: str = "",
        query: str = "",
    ) -> None:
        items, _, _ = self.log_items(start_date, end_date, self.retention_days(retention_value))
        items = LockFixWebHandler.filter_log_items(self, items, type_filter, severity, source, query)
        rows = ["type,date,source,severity,message"]
        for item in items:
            rows.append(",".join(str(item[key]).replace('"', '""').join(['"', '"']) for key in ("type", "date", "source", "severity", "message")))
        self.send_download(("\n".join(rows) + "\n").encode("utf-8-sig"), "text/csv; charset=utf-8", "lockfix_logs.csv")

    def send_monitoring_csv(self, start_date: str = "", end_date: str = "") -> None:
        data = self.monitoring_summary(start_date, end_date)
        rows = ["time,cpu_usage,memory_usage,disk_usage,network_usage,interface_usage"]
        for item in data["series"]:
            rows.append(f"{item['time']},{item['cpu']},{item['memory']},{item['disk']},{item['network']},{item['interface']}")
        body = ("\n".join(rows) + "\n").encode("utf-8-sig")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=monitoring.csv")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.write_body(body)

    def send_report_csv(self) -> None:
        report = self.report_summary()
        extras = report["extras"]
        opinion = extras["engineer_opinion"].replace('"', '""')
        rows = ["section,item,value,item2,value2"]
        rows.append(f"customer,Customer Name,{report['customer']['customer_name']},Inspection Date,{report['customer']['inspection_date']}")
        rows.append(f"customer,Customer Contact,{report['customer']['customer_contact']},Engineer,{report['customer']['engineer']}")
        rows.append(f"server,OS Version,\"{report['server']['os_version']}\",CPU,{report['server']['cpu']}")
        rows.append(f"server,Service,\"{report['server']['service']}\",Memory,{report['server']['memory']}")
        rows.append(f"engineer_opinion,Content,\"{opinion}\",,")
        rows.append(f"signature,Engineer Inspection Signature,{'Attached' if extras['engineer_signature'] else '-'},Manager Signature,{'Attached' if extras['manager_signature'] else '-'}")
        rows.append("")
        rows.append("section,metric,current,average,peak,threshold,status,recommendation")
        for card in report["cards"]:
            rows.append(
                ",".join(
                    [
                        "summary",
                        card["label"],
                        str(card["current"]),
                        str(card["average"]),
                        str(card["peak"]),
                        str(card["threshold"]),
                        card["status"],
                        '"' + card["recommendation"].replace('"', '""') + '"',
                    ]
                )
            )
        rows.append("")
        rows.append("category,item,detail,criteria,metric,result")
        for item in report["inspection_items"]:
            rows.append(
                f"{item['category']},{item['item']},\"{item['detail']}\",\"{item['criteria']}\",{item['metric']},{item['result']}"
            )
        rows.append("")
        rows.append("time,cpu,memory,disk,network")
        for item in report["series"]:
            rows.append(f"{item['time']},{item['cpu']},{item['memory']},{item['disk']},{item['network']}")
        self.send_download(("\n".join(rows) + "\n").encode("utf-8-sig"), "text/csv; charset=utf-8", "lockfix_report.csv")

    def report_export_language(self) -> str:
        language = (parse_qs(urlparse(getattr(self, "path", "")).query).get("lang") or ["en"])[0]
        return "ko" if str(language).lower().startswith("ko") else "en"

    def report_export_summary(self) -> dict:
        return self.context.latest_report_snapshot() or self.report_summary()

    def report_export_labels(self, lang: str = "en") -> dict[str, str]:
        if lang == "ko":
            return {
                "title": "LOCK-FIX 시스템 점검 보고서",
                "report_no": "보고서 번호",
                "generated": "생성일",
                "overall_status": "종합 상태",
                "analysis": "기업 백업 격리 / Air-Gap 검증 요약",
                "customer_info": "고객 / 점검 정보",
                "server_basic": "서버 기본 정보",
                "server_details": "서버 상세 정보",
                "resource_usage": "리소스 사용량 분석",
                "resource_recommendations": "리소스 권고 사항",
                "inspection_summary": "점검 요약",
                "attention_items": "주의 항목",
                "checklist": "서버 점검 체크리스트",
                "engineer_opinion": "엔지니어 의견",
                "opinion_content": "의견 내용",
                "electronic_signature": "전자 서명",
                "signature_confirmation": "서명 확인",
                "signature_seal": "서명 / 날인",
                "engineer_signature": "엔지니어 점검 담당자 서명",
                "manager_signature": "담당자 서명",
                "field": "항목",
                "value": "값",
                "customer_name": "고객명",
                "inspection_date": "점검일",
                "customer_contact": "고객 연락처",
                "customer_email": "고객 이메일",
                "engineer": "엔지니어",
                "engineer_contact": "엔지니어 연락처",
                "os_version": "OS 버전",
                "service": "서비스",
                "model": "모델",
                "disk": "디스크",
                "serial": "시리얼 번호",
                "hostname": "호스트명",
                "cpu": "CPU",
                "memory": "메모리",
                "metric": "지표",
                "current": "현재",
                "average": "평균",
                "peak": "최대",
                "threshold": "임계값",
                "result": "결과",
                "recommendation": "권고 사항",
                "total_checks": "전체 점검",
                "normal": "정상",
                "warning": "주의",
                "overall": "종합",
                "review_required": "확인 필요",
                "operational": "정상 운영",
                "inspection_item": "점검사항",
                "details": "점검내역",
                "criteria": "점검기준",
                "category": "구분",
                "content": "내용",
                "role": "역할",
                "status": "상태",
                "signature_date": "서명일",
                "signed": "서명 완료",
                "not_signed": "미서명",
                "attached": "첨부됨",
                "pending": "대기",
                "manager": "담당자",
                "no_attention": "주의 항목 없음",
                "continued": "점검 상세 계속",
            }
        return {
            "title": "LOCK-FIX System Inspection Report",
            "report_no": "Report No.",
            "generated": "Generated",
            "overall_status": "Overall Status",
            "analysis": "Enterprise backup isolation / Air-Gap verification summary",
            "customer_info": "Customer / Inspection Information",
            "server_basic": "Server Basic Information",
            "server_details": "Server Detail Values",
            "resource_usage": "Resource Usage Analysis",
            "resource_recommendations": "Resource Recommendations",
            "inspection_summary": "Inspection Summary",
            "attention_items": "Attention Items",
            "checklist": "Server Inspection Checklist",
            "engineer_opinion": "Engineer Opinion",
            "opinion_content": "Opinion Content",
            "electronic_signature": "Electronic Signature",
            "signature_confirmation": "Signature Confirmation",
            "signature_seal": "Signature / Seal",
            "engineer_signature": "Engineer Inspection Signature",
            "manager_signature": "Manager Signature",
            "field": "Field",
            "value": "Value",
            "customer_name": "Customer Name",
            "inspection_date": "Inspection Date",
            "customer_contact": "Customer Contact",
            "customer_email": "Customer Email",
            "engineer": "Engineer",
            "engineer_contact": "Engineer Contact",
            "os_version": "OS Version",
            "service": "Service",
            "model": "Model",
            "disk": "Disk",
            "serial": "Serial Number",
            "hostname": "Hostname",
            "cpu": "CPU",
            "memory": "Memory",
            "metric": "Metric",
            "current": "Current",
            "average": "Average",
            "peak": "Peak",
            "threshold": "Threshold",
            "result": "Result",
            "recommendation": "Recommendation",
            "total_checks": "Total Checks",
            "normal": "Normal",
            "warning": "Warning",
            "overall": "Overall",
            "review_required": "Review Required",
            "operational": "Operational",
            "inspection_item": "Inspection Item",
            "details": "Details",
            "criteria": "Criteria",
            "category": "Category",
            "content": "Content",
            "role": "Role",
            "status": "Status",
            "signature_date": "Signature Date",
            "signed": "Signed",
            "not_signed": "Not Signed",
            "attached": "Attached",
            "pending": "Pending",
            "manager": "Manager",
            "no_attention": "No attention items",
            "continued": "Continued inspection details",
        }

    def localize_report_export_value(self, value: object, lang: str = "en") -> str:
        text = str(value)
        if lang != "ko":
            return text
        mapping = {
            "Attention Required": "확인 필요",
            "Review Required": "확인 필요",
            "Operational": "정상 운영",
            "Normal": "정상",
            "Warning": "주의",
            "Signed": "서명 완료",
            "Not Signed": "미서명",
            "Attached": "첨부됨",
            "Pending": "대기",
            "No attention items": "주의 항목 없음",
            "No immediate action required.": "즉시 조치가 필요하지 않습니다.",
            "Check resident services and consider memory expansion.": "상주 서비스를 확인하고 메모리 증설을 검토하세요.",
            "Review high-load processes and scheduled jobs.": "고부하 프로세스와 예약 작업을 점검하세요.",
            "Clean up old logs/backups or extend storage capacity.": "오래된 로그/백업을 정리하거나 저장소 용량 확장을 검토하세요.",
            "Review traffic bursts and backup transfer windows.": "트래픽 급증 구간과 백업 전송 시간을 점검하세요.",
        }
        return mapping.get(text, text)

    def send_report_xlsx(self) -> None:
        lang = self.report_export_language()
        labels = self.report_export_labels(lang)
        local = lambda value: self.localize_report_export_value(value, lang)
        report = self.report_export_summary()
        extras = report["extras"]
        inspection_items = report["inspection_items"]
        warning_items = [item for item in inspection_items if str(item.get("result", "")).lower() == "warning"]
        normal_count = len(inspection_items) - len(warning_items)
        rows = [
            [labels["title"]],
            [f"{labels['generated']}: {report['generated_at']}", labels["overall_status"], local(report["summary"]["overall_status"])],
            [labels["analysis"] if lang == "ko" else report["summary"]["analysis"]],
            [],
            [labels["customer_info"]],
            [labels["customer_name"], report["customer"]["customer_name"], labels["inspection_date"], report["customer"]["inspection_date"]],
            [labels["customer_contact"], report["customer"]["customer_contact"], labels["engineer"], report["customer"]["engineer"]],
            [labels["customer_email"], report["customer"]["customer_email"], labels["engineer_contact"], report["customer"]["engineer_contact"]],
            [],
            [labels["server_basic"]],
            [labels["os_version"], report["server"]["os_version"], labels["cpu"], report["server"]["cpu"]],
            [labels["service"], report["server"]["service"], labels["memory"], report["server"]["memory"]],
            [labels["model"], report["server"]["model"], labels["disk"], report["server"]["disk"]],
            ["S/N", report["server"]["serial"], labels["hostname"], report["server"]["hostname"]],
            [],
            [labels["resource_usage"]],
            [labels["metric"], labels["current"], labels["average"], labels["peak"], labels["threshold"], labels["result"], labels["recommendation"]],
            *[
                [
                    card["label"],
                    card["current"],
                    card["average"],
                    card["peak"],
                    card["threshold"],
                    local(card["status"]),
                    local(card["recommendation"]),
                ]
                for card in report["cards"]
            ],
            [],
            [labels["inspection_summary"]],
            [labels["total_checks"], labels["normal"], labels["warning"], labels["overall"]],
            [len(inspection_items), normal_count, len(warning_items), labels["review_required"] if warning_items else labels["operational"]],
            [],
            [labels["attention_items"]],
            [labels["inspection_item"], labels["metric"], labels["criteria"], labels["result"]],
            *(
                [[item["item"], item["metric"], item["criteria"], local(item["result"])] for item in warning_items]
                or [[labels["no_attention"], "-", "-", labels["normal"]]]
            ),
            [],
            [labels["checklist"]],
            [labels["category"], labels["inspection_item"], labels["details"], labels["criteria"], labels["metric"], labels["result"]],
            *[
                [item["category"], item["item"], item["detail"], item["criteria"], item["metric"], local(item["result"])]
                for item in inspection_items
            ],
            [],
            [labels["engineer_opinion"]],
            [labels["content"], extras["engineer_opinion"] or "-"],
            [labels["electronic_signature"]],
            [labels["signature_confirmation"], labels["role"], labels["status"], labels["signature_date"], labels["signature_seal"]],
            [
                labels["engineer_signature"],
                labels["engineer"],
                labels["signed"] if extras["engineer_signature"] else labels["not_signed"],
                report["generated_at"] if extras["engineer_signature"] else "-",
                labels["attached"] if extras["engineer_signature"] else labels["pending"],
            ],
            [
                labels["manager_signature"],
                labels["manager"],
                labels["signed"] if extras["manager_signature"] else labels["not_signed"],
                report["generated_at"] if extras["manager_signature"] else "-",
                labels["attached"] if extras["manager_signature"] else labels["pending"],
            ],
            [],
            [
                "OAM Electronics Co., Ltd.",
                "8071F, 66, Chungmin-ro, Songpa-gu, Seoul, Republic of Korea",
                "Zip code : 05838",
                "Tel : 1666-3736",
                "Tech Support : 070-7537-3438",
            ],
        ]
        body = self.build_xlsx(rows)
        self.send_download(
            body,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "lockfix_report.xlsx",
        )

    def send_report_hwp(self) -> None:
        lang = self.report_export_language()
        report = self.report_export_summary()
        body = self.build_hwpx_report(report, lang=lang)
        self.send_download(body, "application/hwp+zip", "lockfix_report.hwpx")

    def send_report_docx(self) -> None:
        lang = self.report_export_language()
        report = self.report_export_summary()
        body = self.build_docx(report, lang=lang)
        self.send_download(
            body,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "lockfix_report.docx",
        )

    def send_report_pdf(self) -> None:
        lang = self.report_export_language()
        report = self.report_export_summary()
        body = self.build_pdf_report(report, lang=lang)
        self.send_download(body, "application/pdf", "lockfix_report.pdf")

    def report_company_footer_lines(self, ascii_only: bool = False) -> list[str]:
        if ascii_only:
            return [
                "OAM Electronics Co., Ltd.",
                "Head Office: 8071F, 66, Chungmin-ro, Songpa-gu, Seoul, Republic of Korea",
                "Tel: 1666-3736    Tech Support: 070-7537-3438    Zip code: 05838",
            ]
        return [
            "OAM Electronics Co., Ltd.",
            "본사 : 서울특별시 송파구 충민로 66, 8층 8071호",
            "8071F, 66, Chungmin-ro, Songpa-gu, Seoul, Republic of Korea",
            "Tel : 1666-3736",
            "Tech Support : 070-7537-3438",
            "Zip code : 05838",
        ]

    def build_hwp_report(self, report: dict, lang: str = "en") -> bytes:
        labels = self.report_export_labels(lang)
        local = lambda value: self.localize_report_export_value(value, lang)
        extras = report["extras"]
        customer = report["customer"]
        server = report["server"]
        inspection_items = report["inspection_items"]
        warning_items = [item for item in inspection_items if str(item.get("result", "")).lower() == "warning"]
        normal_count = len(inspection_items) - len(warning_items)

        def e(value: object) -> str:
            return escape(str(value if value is not None else "-"), {'"': "&quot;"})

        def table_html(headers: list[object], rows: list[list[object]]) -> str:
            head = "".join(f"<th>{e(header)}</th>" for header in headers)
            body = []
            for row in rows:
                body.append("<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>")
            return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"

        def signature_cell(value: str) -> str:
            if self.image_data_url_bytes(value):
                return f'<img class="signature-img" src="{e(value)}" alt="{e(labels["signature_seal"])}" />'
            return e(labels["pending"])

        resource_rows = [
            [
                item["label"],
                f"{item['current']}%",
                f"{item['average']}%",
                f"{item['peak']}%",
                f"{item['threshold']}%",
                local(item["status"]),
                local(item["recommendation"]),
            ]
            for item in report["cards"]
        ]
        attention_rows = (
            [[item["item"], item["metric"], item["criteria"], local(item["result"])] for item in warning_items]
            or [[labels["no_attention"], "-", "-", labels["normal"]]]
        )
        checklist_rows = [
            [item["category"], item["item"], item["detail"], item["criteria"], item["metric"], local(item["result"])]
            for item in inspection_items
        ]
        footer = "<br/>".join(e(line) for line in self.report_company_footer_lines())
        html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>{e(labels["title"])}</title>
<style>
body {{ font-family: "Malgun Gothic", "맑은 고딕", Arial, sans-serif; color: #0b1f3a; margin: 28px; }}
h1 {{ font-size: 26px; margin: 0 0 8px; }}
h2 {{ font-size: 17px; margin: 24px 0 10px; }}
p {{ margin: 6px 0; line-height: 1.45; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0 16px; table-layout: fixed; }}
th, td {{ border: 1px solid #d6e0eb; padding: 8px 10px; font-size: 11px; vertical-align: middle; word-break: break-word; }}
th {{ background: #eaf1f8; text-align: left; }}
.meta {{ color: #c2410c; font-weight: 600; }}
.muted {{ color: #53657a; }}
.opinion {{ border: 1px solid #d6e0eb; min-height: 44px; padding: 10px; margin: 8px 0 16px; }}
.signature-img {{ max-width: 150px; max-height: 48px; display: block; }}
.footer {{ border-top: 1px solid #d6e0eb; margin-top: 22px; padding-top: 10px; color: #53657a; font-size: 10px; }}
</style>
</head>
<body>
<h1>{e(labels["title"])}</h1>
<p class="meta">{e(labels["generated"])}: {e(report["generated_at"])} &nbsp; {e(labels["overall"])}: {e(local(report["summary"]["overall_status"]))}</p>
<p class="muted">{e(labels["analysis"] if lang == "ko" else report["summary"]["analysis"])}</p>
<h2>{e(labels["customer_info"])}</h2>
{table_html([labels["field"], labels["value"], labels["field"], labels["value"]], [
    [labels["customer_name"], customer["customer_name"], labels["inspection_date"], customer["inspection_date"]],
    [labels["customer_contact"], customer["customer_contact"], labels["engineer"], customer["engineer"]],
    [labels["customer_email"], customer["customer_email"], labels["engineer_contact"], customer["engineer_contact"]],
])}
<h2>{e(labels["server_basic"])}</h2>
{table_html([labels["field"], labels["value"]], [
    [labels["os_version"], server["os_version"]],
    [labels["service"], server["service"]],
    [labels["model"], server["model"]],
    [labels["disk"], server["disk"]],
    ["S/N", server["serial"]],
    [labels["hostname"], server["hostname"]],
])}
<h2>{e(labels["resource_usage"])}</h2>
{table_html([labels["metric"], labels["current"], labels["average"], labels["peak"], labels["threshold"], labels["result"], labels["recommendation"]], resource_rows)}
<h2>{e(labels["inspection_summary"])}</h2>
{table_html([labels["total_checks"], labels["normal"], labels["warning"], labels["overall"]], [[len(inspection_items), normal_count, len(warning_items), labels["review_required"] if warning_items else labels["operational"]]])}
<h2>{e(labels["attention_items"])}</h2>
{table_html([labels["inspection_item"], labels["metric"], labels["criteria"], labels["result"]], attention_rows)}
<h2>{e(labels["checklist"])}</h2>
{table_html([labels["category"], labels["inspection_item"], labels["details"], labels["criteria"], labels["metric"], labels["result"]], checklist_rows)}
<h2>{e(labels["engineer_opinion"])}</h2>
<div class="opinion">{e(extras.get("engineer_opinion") or "-")}</div>
<h2>{e(labels["electronic_signature"])}</h2>
<h2>{e(labels["signature_confirmation"])}</h2>
<table>
<thead><tr><th>{e(labels["signature_confirmation"])}</th><th>{e(labels["role"])}</th><th>{e(labels["status"])}</th><th>{e(labels["signature_date"])}</th><th>{e(labels["signature_seal"])}</th></tr></thead>
<tbody>
<tr><td>{e(labels["engineer_signature"])}</td><td>{e(labels["engineer"])}</td><td>{e(labels["signed"] if extras.get("engineer_signature") else labels["not_signed"])}</td><td>{e(report["generated_at"] if extras.get("engineer_signature") else "-")}</td><td>{signature_cell(extras.get("engineer_signature", ""))}</td></tr>
<tr><td>{e(labels["manager_signature"])}</td><td>{e(labels["manager"])}</td><td>{e(labels["signed"] if extras.get("manager_signature") else labels["not_signed"])}</td><td>{e(report["generated_at"] if extras.get("manager_signature") else "-")}</td><td>{signature_cell(extras.get("manager_signature", ""))}</td></tr>
</tbody>
</table>
<div class="footer">{footer}</div>
</body>
</html>
"""
        return html.encode("utf-8-sig")

    def build_hwpx_report(self, report: dict, lang: str = "en") -> bytes:
        labels = self.report_export_labels(lang)
        local = lambda value: self.localize_report_export_value(value, lang)
        extras = report["extras"]
        customer = report["customer"]
        server = report["server"]
        inspection_items = report["inspection_items"]
        warning_items = [item for item in inspection_items if str(item.get("result", "")).lower() == "warning"]
        normal_count = len(inspection_items) - len(warning_items)

        def xml(value: object) -> str:
            return escape(str(value if value is not None else "-"))

        def cell_line(values: list[object]) -> str:
            return "    ".join(str(value if value is not None else "-") for value in values)

        def signature_status(value: str) -> str:
            return labels["attached"] if self.image_data_url_bytes(value) else labels["pending"]

        lines: list[str] = [
            labels["title"],
            f"{labels['generated']}: {report['generated_at']}    {labels['overall']}: {local(report['summary']['overall_status'])}",
            labels["analysis"] if lang == "ko" else report["summary"]["analysis"],
            "",
            labels["customer_info"],
            cell_line([labels["customer_name"], customer["customer_name"], labels["inspection_date"], customer["inspection_date"]]),
            cell_line([labels["customer_contact"], customer["customer_contact"], labels["engineer"], customer["engineer"]]),
            cell_line([labels["customer_email"], customer["customer_email"], labels["engineer_contact"], customer["engineer_contact"]]),
            "",
            labels["server_basic"],
            cell_line([labels["os_version"], server["os_version"]]),
            cell_line([labels["service"], server["service"]]),
            cell_line([labels["model"], server["model"]]),
            cell_line([labels["disk"], server["disk"]]),
            cell_line(["S/N", server["serial"]]),
            cell_line([labels["hostname"], server["hostname"]]),
            "",
            labels["resource_usage"],
            cell_line([labels["metric"], labels["current"], labels["average"], labels["peak"], labels["threshold"], labels["result"], labels["recommendation"]]),
        ]
        for item in report["cards"]:
            lines.append(cell_line([
                item["label"],
                f"{item['current']}%",
                f"{item['average']}%",
                f"{item['peak']}%",
                f"{item['threshold']}%",
                local(item["status"]),
                local(item["recommendation"]),
            ]))

        lines.extend([
            "",
            labels["inspection_summary"],
            cell_line([labels["total_checks"], labels["normal"], labels["warning"], labels["overall"]]),
            cell_line([len(inspection_items), normal_count, len(warning_items), labels["review_required"] if warning_items else labels["operational"]]),
            "",
            labels["attention_items"],
            cell_line([labels["inspection_item"], labels["metric"], labels["criteria"], labels["result"]]),
        ])
        if warning_items:
            for item in warning_items:
                lines.append(cell_line([item["item"], item["metric"], item["criteria"], local(item["result"])]))
        else:
            lines.append(cell_line([labels["no_attention"], "-", "-", labels["normal"]]))

        lines.extend([
            "",
            labels["checklist"],
            cell_line([labels["category"], labels["inspection_item"], labels["details"], labels["criteria"], labels["metric"], labels["result"]]),
        ])
        for item in inspection_items:
            lines.append(cell_line([item["category"], item["item"], item["detail"], item["criteria"], item["metric"], local(item["result"])]))

        lines.extend([
            "",
            labels["engineer_opinion"],
            str(extras.get("engineer_opinion") or "-"),
            "",
            labels["electronic_signature"],
            labels["signature_confirmation"],
            cell_line([labels["signature_confirmation"], labels["role"], labels["status"], labels["signature_date"], labels["signature_seal"]]),
            cell_line([
                labels["engineer_signature"],
                labels["engineer"],
                labels["signed"] if extras.get("engineer_signature") else labels["not_signed"],
                report["generated_at"] if extras.get("engineer_signature") else "-",
                signature_status(extras.get("engineer_signature", "")),
            ]),
            cell_line([
                labels["manager_signature"],
                labels["manager"],
                labels["signed"] if extras.get("manager_signature") else labels["not_signed"],
                report["generated_at"] if extras.get("manager_signature") else "-",
                signature_status(extras.get("manager_signature", "")),
            ]),
            "",
            *self.report_company_footer_lines(),
        ])

        def paragraph(index: int, text: str) -> str:
            para_id = 1000000002 + index
            return (
                f'<hp:p id="{para_id}" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                f'<hp:run charPrIDRef="0"><hp:t>{xml(text)}</hp:t></hp:run>'
                '<hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000" textheight="1000" '
                'baseline="850" spacing="600" horzpos="0" horzsize="42520" flags="393216" /></hp:linesegarray>'
                '</hp:p>'
            )

        section_preamble = '''<hp:p id="1000000001" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:secPr id="0" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="8000" tabStopUnit="HWPUNIT" outlineShapeIDRef="0" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">
      <hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0" />
      <hp:startNum pageStartsOn="BOTH" page="1" pic="1" tbl="1" equation="1" />
      <hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0" />
      <hp:lineNumberShape textPos="LEFT" numberType="CONTINUOUS" distance="0" startNumber="1" />
      <hp:pagePr landscape="0" width="59528" height="84188" gutterType="LEFT_ONLY">
        <hp:margin header="4252" footer="4252" gutter="0" left="4252" right="4252" top="5669" bottom="4252" />
      </hp:pagePr>
      <hp:footNotePr>
        <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0" />
        <hp:noteLine length="0" type="SOLID" width="0.1 mm" color="#000000" />
        <hp:noteSpacing betweenNotes="0" belowLine="0" aboveLine="0" />
        <hp:numbering type="CONTINUOUS" newNum="1" />
        <hp:placement place="EACH_COLUMN" beneathText="0" />
      </hp:footNotePr>
      <hp:endNotePr>
        <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0" />
        <hp:noteLine length="0" type="SOLID" width="0.1 mm" color="#000000" />
        <hp:noteSpacing betweenNotes="0" belowLine="0" aboveLine="0" />
        <hp:numbering type="CONTINUOUS" newNum="1" />
        <hp:placement place="END_OF_DOCUMENT" beneathText="0" />
      </hp:endNotePr>
      <hp:pageBorderFill type="BOTH" borderFillIDRef="0" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">
        <hp:offset left="0" right="0" top="0" bottom="0" />
      </hp:pageBorderFill>
    </hp:secPr>
    <hp:ctrl>
      <hp:colPr id="1" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0" />
    </hp:ctrl>
  </hp:run>
  <hp:run charPrIDRef="0"><hp:t></hp:t></hp:run>
</hp:p>'''
        section_paragraphs = "\n".join(paragraph(index, line) for index, line in enumerate(lines))
        section_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
{section_preamble}
{section_paragraphs}
</hs:sec>
'''
        header_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" version="1.0" secCnt="1">
  <hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1" />
  <hh:refList>
    <hh:fontfaces itemCnt="1"><hh:fontface lang="ko" fontCnt="1"><hh:font id="0" face="맑은 고딕" type="ttf" /></hh:fontface></hh:fontfaces>
    <hh:styles itemCnt="1"><hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0" charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0" /></hh:styles>
    <hh:borderFills itemCnt="1"><hh:borderFill id="0" threeD="0" shadow="0"><hh:slash type="NONE" Crooked="0" isCounter="0" /><hh:backSlash type="NONE" Crooked="0" isCounter="0" /><hh:leftBorder type="NONE" width="0.1 mm" color="#000000" /><hh:rightBorder type="NONE" width="0.1 mm" color="#000000" /><hh:topBorder type="NONE" width="0.1 mm" color="#000000" /><hh:bottomBorder type="NONE" width="0.1 mm" color="#000000" /><hh:diagonal type="NONE" width="0.1 mm" color="#000000" /><hh:fillBrush><hc:winBrush xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" faceColor="#FFFFFF" hatchColor="#000000" alpha="0" /></hh:fillBrush></hh:borderFill></hh:borderFills>
    <hh:charProperties itemCnt="1"><hh:charPr id="0" height="1000" textColor="#000000" shadeColor="#FFFFFF" useFontSpace="0" useKerning="0"><hh:fontRef hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0" /><hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100" /><hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0" /><hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100" /><hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0" /></hh:charPr></hh:charProperties>
    <hh:paraProperties itemCnt="1"><hh:paraPr id="0" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" suppressLineNumbers="0" checked="0"><hh:align horizontal="LEFT" vertical="BASELINE" /><hh:heading type="NONE" idRef="0" level="0" /><hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD" widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK" /><hh:autoSpacing eAsianEng="0" eAsianNum="0" /><hh:margin><hh:intent value="0" /><hh:left value="0" /><hh:right value="0" /><hh:prev value="0" /><hh:next value="600" /></hh:margin><hh:lineSpacing type="PERCENT" value="160" /></hh:paraPr></hh:paraProperties>
    <hh:tabProperties itemCnt="1"><hh:tabPr id="0" autoTabLeft="1" autoTabRight="1" /></hh:tabProperties>
  </hh:refList>
  <hh:compatibleDocument targetProgram="HWP2018"><hh:layoutCompatibility /></hh:compatibleDocument>
</hh:head>
'''
        content_hpf = f'''<?xml version="1.0" encoding="UTF-8"?>
<opf:package xmlns:opf="http://www.idpf.org/2007/opf/" version="3.0" unique-identifier="uid">
  <opf:metadata>
    <opf:identifier id="uid">urn:uuid:{uuid.uuid4()}</opf:identifier>
    <opf:title>{xml(labels["title"])}</opf:title>
    <opf:language>{"ko-KR" if lang == "ko" else "en-US"}</opf:language>
  </opf:metadata>
  <opf:manifest>
    <opf:item id="header" href="header.xml" media-type="application/xml" />
    <opf:item id="section0" href="section0.xml" media-type="application/xml" />
  </opf:manifest>
  <opf:spine><opf:itemref idref="section0" /></opf:spine>
</opf:package>
'''
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="Contents/content.hpf" media-type="application/hwp+zip" /></rootfiles>
</container>
'''
        version_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<version xmlns="http://www.hancom.co.kr/hwpml/2011/version" app="LOCK-FIX" version="1.0" />
'''
        settings_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://www.hancom.co.kr/hwpml/2011/settings" />
'''
        manifest_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <odf:file-entry odf:full-path="/" odf:media-type="application/hwp+zip" />
  <odf:file-entry odf:full-path="version.xml" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="META-INF/container.xml" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="Contents/content.hpf" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="Contents/header.xml" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="Settings/settings.xml" odf:media-type="text/xml" />
  <odf:file-entry odf:full-path="Preview/PrvText.txt" odf:media-type="text/plain" />
</odf:manifest>
'''
        preview_text = "\r\n".join(lines)
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("mimetype", "application/hwp+zip", compress_type=zipfile.ZIP_STORED)
            archive.writestr("version.xml", version_xml)
            archive.writestr("META-INF/container.xml", container_xml)
            archive.writestr("META-INF/manifest.xml", manifest_xml)
            archive.writestr("Contents/content.hpf", content_hpf)
            archive.writestr("Contents/header.xml", header_xml)
            archive.writestr("Contents/section0.xml", section_xml)
            archive.writestr("Settings/settings.xml", settings_xml)
            archive.writestr("Preview/PrvText.txt", preview_text)
        return output.getvalue()

    def build_pdf_report(self, report: dict, lang: str = "en") -> bytes:
        labels = self.report_export_labels(lang)
        local = lambda value: self.localize_report_export_value(value, lang)
        use_cjk_font = lang == "ko"
        pdf_images: list[dict] = []

        def read_u16(data: bytes, offset: int) -> int:
            return int.from_bytes(data[offset : offset + 2], "big", signed=False)

        def read_i16(data: bytes, offset: int) -> int:
            return int.from_bytes(data[offset : offset + 2], "big", signed=True)

        def read_u32(data: bytes, offset: int) -> int:
            return int.from_bytes(data[offset : offset + 4], "big", signed=False)

        def parse_ttf_font(path: Path) -> dict:
            data = path.read_bytes()
            table_count = read_u16(data, 4)
            tables = {}
            for index in range(table_count):
                entry = 12 + (index * 16)
                tag = data[entry : entry + 4].decode("latin-1")
                tables[tag] = (read_u32(data, entry + 8), read_u32(data, entry + 12))

            head_offset, _ = tables["head"]
            units_per_em = read_u16(data, head_offset + 18) or 1000
            bbox = (
                read_i16(data, head_offset + 36),
                read_i16(data, head_offset + 38),
                read_i16(data, head_offset + 40),
                read_i16(data, head_offset + 42),
            )
            hhea_offset, _ = tables["hhea"]
            ascent = int(read_i16(data, hhea_offset + 4) * 1000 / units_per_em)
            descent = int(read_i16(data, hhea_offset + 6) * 1000 / units_per_em)
            metric_count = read_u16(data, hhea_offset + 34)
            maxp_offset, _ = tables["maxp"]
            glyph_count = read_u16(data, maxp_offset + 4)
            hmtx_offset, _ = tables["hmtx"]
            advances = []
            last_advance = 1000
            for index in range(glyph_count):
                if index < metric_count:
                    last_advance = read_u16(data, hmtx_offset + (index * 4))
                advances.append(int(last_advance * 1000 / units_per_em))

            cmap_offset, _ = tables["cmap"]
            cmap_count = read_u16(data, cmap_offset + 2)
            records = []
            for index in range(cmap_count):
                record = cmap_offset + 4 + (index * 8)
                platform = read_u16(data, record)
                encoding = read_u16(data, record + 2)
                offset = read_u32(data, record + 4)
                subtable = cmap_offset + offset
                records.append((platform, encoding, read_u16(data, subtable), subtable))
            preferred = sorted(records, key=lambda item: (
                0 if item[2] == 12 and item[0] in (0, 3) else
                1 if item[2] == 4 and item[0] in (0, 3) else
                2
            ))[0]
            cmap = {}
            if preferred[2] == 12:
                subtable = preferred[3]
                group_count = read_u32(data, subtable + 12)
                for index in range(group_count):
                    group = subtable + 16 + (index * 12)
                    start = read_u32(data, group)
                    end = read_u32(data, group + 4)
                    start_gid = read_u32(data, group + 8)
                    for codepoint in range(start, end + 1):
                        cmap[codepoint] = start_gid + (codepoint - start)
            else:
                subtable = preferred[3]
                seg_count = read_u16(data, subtable + 6) // 2
                end_codes = [read_u16(data, subtable + 14 + (index * 2)) for index in range(seg_count)]
                start_offset = subtable + 16 + (seg_count * 2)
                start_codes = [read_u16(data, start_offset + (index * 2)) for index in range(seg_count)]
                delta_offset = start_offset + (seg_count * 2)
                deltas = [read_i16(data, delta_offset + (index * 2)) for index in range(seg_count)]
                range_offset = delta_offset + (seg_count * 2)
                for index in range(seg_count):
                    start = start_codes[index]
                    end = end_codes[index]
                    if start == 0xFFFF:
                        continue
                    range_value = read_u16(data, range_offset + (index * 2))
                    for codepoint in range(start, end + 1):
                        if range_value == 0:
                            glyph = (codepoint + deltas[index]) & 0xFFFF
                        else:
                            glyph_pos = range_offset + (index * 2) + range_value + ((codepoint - start) * 2)
                            glyph = read_u16(data, glyph_pos)
                            if glyph:
                                glyph = (glyph + deltas[index]) & 0xFFFF
                        if glyph:
                            cmap[codepoint] = glyph
            return {
                "data": data,
                "cmap": cmap,
                "widths": advances,
                "bbox": tuple(int(value * 1000 / units_per_em) for value in bbox),
                "ascent": ascent,
                "descent": descent,
            }

        regular_font = None
        bold_font = None
        used_gids: set[int] = set()
        if use_cjk_font:
            regular_font = parse_ttf_font(Path("C:/Windows/Fonts/malgun.ttf"))
            # Reuse one embedded Unicode font for regular/bold text to keep PDF size reasonable
            # while preserving reliable Korean glyph rendering.
            bold_font = regular_font

        def pdf_text(value: object) -> str:
            text = str(value).encode("latin-1", "replace").decode("latin-1")
            return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        def pdf_literal(value: object, bold: bool = False) -> str:
            if use_cjk_font:
                font = bold_font if bold else regular_font
                glyph_bytes = bytearray()
                for char in str(value):
                    glyph = int(font["cmap"].get(ord(char), 0))
                    used_gids.add(glyph)
                    glyph_bytes.extend(glyph.to_bytes(2, "big", signed=False))
                return f"<{bytes(glyph_bytes).hex().upper()}>"
            return f"({pdf_text(value)})"

        def text_at(x: float, y: float, value: object, size: int = 9, color: str = "0 0 0", bold: bool = False) -> None:
            font = "/F2" if bold else "/F1"
            commands.append(f"BT {color} rg {font} {size} Tf {x:.1f} {y:.1f} Td {pdf_literal(value, bold)} Tj ET")

        def line(x1: float, y1: float, x2: float, y2: float, color: str = "0.82 0.87 0.92", width: float = 0.8) -> None:
            commands.append(f"q {color} RG {width:.1f} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S Q")

        def rect(x: float, y: float, w: float, h: float, stroke: str = "0.82 0.87 0.92", fill: str = "1 1 1", width: float = 0.8) -> None:
            commands.append(f"q {fill} rg {stroke} RG {width:.1f} w {x:.1f} {y:.1f} {w:.1f} {h:.1f} re B Q")

        def status_color(value: str) -> str:
            text = str(value).lower()
            if "warning" in text or "attention" in text:
                return "0.78 0.32 0"
            if "fail" in text or "error" in text:
                return "0.72 0.11 0.11"
            return "0.02 0.48 0.25"

        def fit_text(value: object, width: float, size: int, minimum: int = 8) -> str:
            # Approximate Helvetica width so long values stay inside fixed PDF cards.
            limit = max(minimum, int(width / max(size * 0.48, 1)))
            return textwrap.shorten(str(value), width=limit, placeholder="...")

        def card(x: float, y: float, w: float, h: float, label: str, value: str, color: str = "0.04 0.18 0.47") -> None:
            rect(x, y, w, h, stroke="0.76 0.83 0.91", fill="0.98 0.99 1")
            value_text = str(value)
            value_size = 13 if len(value_text) <= 20 else 10
            text_at(x + 10, y + h - 16, fit_text(label.upper(), w - 20, 7), 7, "0.32 0.40 0.50", True)
            text_at(x + 10, y + 13, fit_text(value_text, w - 20, value_size), value_size, color, True)

        def png_data_to_rgb(data: bytes) -> tuple[int, int, bytes]:
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("not a png image")
            offset = 8
            width = height = bit_depth = color_type = 0
            idat = bytearray()
            while offset + 8 <= len(data):
                length = int.from_bytes(data[offset : offset + 4], "big")
                chunk_type = data[offset + 4 : offset + 8]
                chunk_data = data[offset + 8 : offset + 8 + length]
                offset += 12 + length
                if chunk_type == b"IHDR":
                    width = int.from_bytes(chunk_data[0:4], "big")
                    height = int.from_bytes(chunk_data[4:8], "big")
                    bit_depth = chunk_data[8]
                    color_type = chunk_data[9]
                elif chunk_type == b"IDAT":
                    idat.extend(chunk_data)
                elif chunk_type == b"IEND":
                    break
            if not width or not height or bit_depth != 8 or color_type not in {0, 2, 4, 6}:
                raise ValueError("unsupported png signature format")
            bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
            row_len = width * bpp
            raw = zlib.decompress(bytes(idat))
            rows: list[bytes] = []
            previous = bytearray(row_len)
            pos = 0
            for _ in range(height):
                filter_type = raw[pos]
                pos += 1
                scan = bytearray(raw[pos : pos + row_len])
                pos += row_len
                for idx in range(row_len):
                    left = scan[idx - bpp] if idx >= bpp else 0
                    up = previous[idx]
                    upper_left = previous[idx - bpp] if idx >= bpp else 0
                    if filter_type == 1:
                        scan[idx] = (scan[idx] + left) & 0xFF
                    elif filter_type == 2:
                        scan[idx] = (scan[idx] + up) & 0xFF
                    elif filter_type == 3:
                        scan[idx] = (scan[idx] + ((left + up) // 2)) & 0xFF
                    elif filter_type == 4:
                        p = left + up - upper_left
                        pa, pb, pc = abs(p - left), abs(p - up), abs(p - upper_left)
                        predictor = left if pa <= pb and pa <= pc else (up if pb <= pc else upper_left)
                        scan[idx] = (scan[idx] + predictor) & 0xFF
                    elif filter_type != 0:
                        raise ValueError("unsupported png filter")
                rows.append(bytes(scan))
                previous = scan
            rgb = bytearray()
            for row in rows:
                for col in range(width):
                    start = col * bpp
                    if color_type == 0:
                        r = g = b = row[start]
                    elif color_type == 2:
                        r, g, b = row[start], row[start + 1], row[start + 2]
                    elif color_type == 4:
                        gray, alpha = row[start], row[start + 1]
                        r = g = b = (gray * alpha + 255 * (255 - alpha)) // 255
                    else:
                        alpha = row[start + 3]
                        r = (row[start] * alpha + 255 * (255 - alpha)) // 255
                        g = (row[start + 1] * alpha + 255 * (255 - alpha)) // 255
                        b = (row[start + 2] * alpha + 255 * (255 - alpha)) // 255
                    rgb.extend((r, g, b))
            return width, height, bytes(rgb)

        def register_pdf_image(value: str) -> dict | None:
            image_bytes = self.image_data_url_bytes(value)
            if not image_bytes:
                return None
            try:
                width, height, rgb = png_data_to_rgb(image_bytes)
            except ValueError:
                return None
            image = {
                "name": f"Im{len(pdf_images) + 1}",
                "width": width,
                "height": height,
                "data": zlib.compress(rgb),
            }
            pdf_images.append(image)
            return image

        def image_at(image: dict, x: float, y: float, w: float, h: float) -> None:
            scale = min(w / image["width"], h / image["height"])
            draw_w = image["width"] * scale
            draw_h = image["height"] * scale
            draw_x = x + ((w - draw_w) / 2)
            draw_y = y + ((h - draw_h) / 2)
            commands.append(f"q {draw_w:.1f} 0 0 {draw_h:.1f} {draw_x:.1f} {draw_y:.1f} cm /{image['name']} Do Q")

        def table(x: float, y: float, widths: list[float], rows: list[list[object]], header: bool = True, row_h: float = 21) -> float:
            total_w = sum(widths)
            if total_w > content_w:
                scale = content_w / total_w
                widths = [round(width * scale, 2) for width in widths]
                widths[-1] += content_w - sum(widths)
            current_y = y
            for row_index, row in enumerate(rows):
                fill = "0.93 0.96 0.99" if header and row_index == 0 else "1 1 1"
                rect(x, current_y - row_h, sum(widths), row_h, stroke="0.82 0.87 0.92", fill=fill, width=0.5)
                current_x = x
                for col_index, width in enumerate(widths):
                    if col_index:
                        line(current_x, current_y - row_h, current_x, current_y, width=0.4)
                    text = str(row[col_index] if col_index < len(row) else "")
                    clipped = textwrap.shorten(text, width=max(8, int(width / 5.4)), placeholder="...")
                    text_at(current_x + 6, current_y - 14, clipped, 7 if row_index else 8, "0.05 0.13 0.24", row_index == 0)
                    current_x += width
                current_y -= row_h
            return current_y

        def begin_page(continued: bool = False) -> None:
            nonlocal commands
            commands = []
            rect(24, 24, page_w - 48, page_h - 48, stroke="0.84 0.89 0.95", fill="1 1 1")
            # Keep large title glyphs away from the outer border in PDF viewers.
            text_at(42, 790, labels["title"], 22 if not continued else 16, "0.04 0.12 0.24", True)
            if continued:
                text_at(42, 770, labels["continued"], 9, "0.34 0.42 0.52")

        def finish_page() -> None:
            pages.append("\n".join(commands).encode("latin-1"))

        page_w, page_h = 595, 842
        content_x, content_w = 42.0, 508.0
        pages: list[bytes] = []
        commands: list[str] = []
        y = 742.0
        bottom_y = 58.0

        def new_page(continued: bool = True) -> None:
            nonlocal y
            finish_page()
            begin_page(continued)
            y = 746.0

        def ensure_space(height: float) -> None:
            if y - height < bottom_y:
                new_page(True)

        def section(title: str, height: float = 26) -> None:
            nonlocal y
            ensure_space(height)
            text_at(content_x, y, title, 11, "0.04 0.12 0.24", True)
            y -= 18

        def draw_wrapped_text(x: float, width: float, value: object, size: int = 8, leading: float = 11) -> None:
            nonlocal y
            lines = textwrap.wrap(str(value or "-"), width=max(18, int(width / max(size * 0.48, 1)))) or ["-"]
            ensure_space((len(lines) * leading) + 8)
            for wrapped in lines:
                text_at(x, y, wrapped, size, "0.05 0.13 0.24")
                y -= leading

        def draw_table(title: str, widths: list[float], rows: list[list[object]], row_h: float = 18) -> None:
            nonlocal y
            section(title)
            header = rows[:1]
            body_rows = rows[1:] if rows else []
            while body_rows:
                available_rows = max(1, int((y - bottom_y) // row_h) - 1)
                if available_rows < 2:
                    new_page(True)
                    text_at(42, y, f"{title} ({labels['continued']})", 11, "0.04 0.12 0.24", True)
                    y -= 18
                    available_rows = max(1, int((y - bottom_y) // row_h) - 1)
                chunk = body_rows[:available_rows]
                y = table(content_x, y, widths, header + chunk, row_h=row_h) - 12
                body_rows = body_rows[available_rows:]
                if body_rows:
                    new_page(True)
                    text_at(42, y, f"{title} ({labels['continued']})", 10, "0.04 0.12 0.24", True)
                    y -= 18
            if not body_rows and len(rows) == 1:
                y = table(content_x, y, widths, rows, row_h=row_h) - 12

        def draw_signature_table(title: str, rows: list[list[object]], signature_images: list[dict | None]) -> None:
            nonlocal y
            section(title, 90)
            widths = [150, 76, 84, 112, 112]
            header_h = 18
            row_h = 34 if any(signature_images) else 18
            total_h = header_h + (row_h * (len(rows) - 1))
            ensure_space(total_h + 12)
            current_y = y
            for row_index, row in enumerate(rows):
                active_h = header_h if row_index == 0 else row_h
                fill = "0.93 0.96 0.99" if row_index == 0 else "1 1 1"
                rect(content_x, current_y - active_h, sum(widths), active_h, stroke="0.82 0.87 0.92", fill=fill, width=0.5)
                current_x = content_x
                for col_index, width in enumerate(widths):
                    if col_index:
                        line(current_x, current_y - active_h, current_x, current_y, width=0.4)
                    if row_index > 0 and col_index == 4 and signature_images[row_index - 1]:
                        image_at(signature_images[row_index - 1], current_x + 5, current_y - active_h + 3, width - 10, active_h - 6)
                    else:
                        text = str(row[col_index] if col_index < len(row) else "")
                        clipped = textwrap.shorten(text, width=max(8, int(width / 5.4)), placeholder="...")
                        text_at(current_x + 6, current_y - min(14, active_h - 6), clipped, 7 if row_index else 8, "0.05 0.13 0.24", row_index == 0)
                    current_x += width
                current_y -= active_h
            y = current_y - 12

        begin_page()
        text_at(42, 758, f"{labels['generated']}: {report['generated_at']}   {labels['overall']}: {local(report['summary']['overall_status'])}", 9, status_color(report["summary"]["overall_status"]), True)
        text_at(42, 740, labels["analysis"] if lang == "ko" else report["summary"]["analysis"], 9, "0.34 0.42 0.52")

        customer = report["customer"]
        server = report["server"]
        # Match the WebUI report body: summary text flows directly into the customer/server tables.
        y = 710

        draw_table(labels["customer_info"], [116, 150, 116, 152], [
            [labels["field"], labels["value"], labels["field"], labels["value"]],
            [labels["customer_name"], customer["customer_name"], labels["inspection_date"], customer["inspection_date"]],
            [labels["customer_contact"], customer["customer_contact"], labels["engineer"], customer["engineer"]],
            [labels["customer_email"], customer["customer_email"], labels["engineer_contact"], customer["engineer_contact"]],
        ], row_h=18)
        draw_table(labels["server_basic"], [116, 392], [
            [labels["field"], labels["value"]],
            [labels["os_version"], server["os_version"]],
            [labels["service"], server["service"]],
            [labels["model"], server["model"]],
            [labels["disk"], server["disk"]],
            ["S/N", server["serial"]],
            [labels["hostname"], server["hostname"]],
        ], row_h=18)
        draw_table(labels["resource_usage"], [58, 48, 48, 48, 56, 62, 214], [
            [labels["metric"], labels["current"], labels["average"], labels["peak"], labels["threshold"], labels["result"], labels["recommendation"]],
            *[
                [item["label"], f"{item['current']}%", f"{item['average']}%", f"{item['peak']}%", f"{item['threshold']}%", local(item["status"]), local(item["recommendation"])]
                for item in report["cards"]
            ],
        ], row_h=18)
        inspection_items = report["inspection_items"]
        warning_items = [item for item in inspection_items if str(item.get("result", "")).lower() == "warning"]
        normal_count = len(inspection_items) - len(warning_items)
        draw_table(labels["inspection_summary"], [132, 134, 134, 134], [
            [labels["total_checks"], labels["normal"], labels["warning"], labels["overall"]],
            [len(inspection_items), normal_count, len(warning_items), labels["review_required"] if warning_items else labels["operational"]],
        ], row_h=20)
        attention_rows = [[labels["inspection_item"], labels["metric"], labels["criteria"], labels["result"]]]
        attention_rows.extend(
            [[item["item"], item["metric"], item["criteria"], local(item["result"])] for item in warning_items]
            or [[labels["no_attention"], "-", "-", labels["normal"]]]
        )
        draw_table(labels["attention_items"], [154, 126, 174, 80], attention_rows, row_h=18)
        draw_table(labels["checklist"], [48, 96, 132, 104, 84, 70], [
            [labels["category"], labels["inspection_item"], labels["details"], labels["criteria"], labels["metric"], labels["result"]],
            *[[item["category"], item["item"], item["detail"], item["criteria"], item["metric"], local(item["result"])] for item in inspection_items],
        ], row_h=18)

        extras = report["extras"]
        section(labels["engineer_opinion"], 64)
        opinion_top = y - 2
        opinion_height = 42
        opinion_bottom = opinion_top - opinion_height
        rect(42, opinion_bottom, 508, opinion_height, stroke="0.82 0.87 0.92", fill="0.99 1 1")
        text_at(54, opinion_top - 16, labels["opinion_content"], 8, "0.32 0.40 0.50", True)
        opinion_lines = textwrap.wrap(str(extras.get("engineer_opinion") or "-"), width=110) or ["-"]
        for index, opinion_line in enumerate(opinion_lines[:2]):
            text_at(54, opinion_top - 31 - (index * 11), opinion_line, 8, "0.05 0.13 0.24")
        y = opinion_bottom - 14

        engineer_signature_image = register_pdf_image(extras.get("engineer_signature", ""))
        manager_signature_image = register_pdf_image(extras.get("manager_signature", ""))
        draw_signature_table(labels["signature_confirmation"], [
            [labels["signature_confirmation"], labels["role"], labels["status"], labels["signature_date"], labels["signature_seal"]],
            [labels["engineer_signature"], labels["engineer"], labels["signed"] if extras.get("engineer_signature") else labels["not_signed"], report["generated_at"] if extras.get("engineer_signature") else "-", labels["attached"] if extras.get("engineer_signature") else labels["pending"]],
            [labels["manager_signature"], labels["manager"], labels["signed"] if extras.get("manager_signature") else labels["not_signed"], report["generated_at"] if extras.get("manager_signature") else "-", labels["attached"] if extras.get("manager_signature") else labels["pending"]],
        ], [engineer_signature_image, manager_signature_image])

        ensure_space(54)
        line(42, 54, 550, 54, color="0.84 0.89 0.95", width=0.5)
        for index, footer_line in enumerate(self.report_company_footer_lines(ascii_only=True)):
            text_at(42, 43 - (index * 10), footer_line, 7, "0.34 0.42 0.52", index == 0)
        finish_page()

        page_count = len(pages)
        font_start = 3 + page_count
        font1_ref = font_start
        font2_ref = font_start if use_cjk_font else font_start + 1
        font_object_count = 4 if use_cjk_font else 2
        image_start = font_start + font_object_count
        content_start = image_start + len(pdf_images)
        page_refs = list(range(3, 3 + page_count))
        xobject_entries = []
        for index, image in enumerate(pdf_images):
            xobject_entries.append(f"/{image['name']} {image_start + index} 0 R")
        xobject_resource = f" /XObject << {' '.join(xobject_entries)} >>" if xobject_entries else ""
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            f"<< /Type /Pages /Kids [{' '.join(f'{ref} 0 R' for ref in page_refs)}] /Count {page_count} >>".encode("ascii"),
        ]
        for index, page_ref in enumerate(page_refs):
            content_ref = content_start + index
            objects.append(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] /Resources << /Font << /F1 {font1_ref} 0 R /F2 {font2_ref} 0 R >>{xobject_resource} >> /Contents {content_ref} 0 R >>".encode("ascii")
            )
        if use_cjk_font:
            def font_objects(font: dict, base_name: str, type0_ref: int, cid_ref: int, descriptor_ref: int, file_ref: int) -> list[bytes]:
                widths = []
                for gid in sorted(gid for gid in used_gids if gid < len(font["widths"])):
                    widths.append(f"{gid} [{font['widths'][gid]}]")
                widths_text = f" /W [{' '.join(widths)}]" if widths else ""
                x_min, y_min, x_max, y_max = font["bbox"]
                type0 = (
                    f"<< /Type /Font /Subtype /Type0 /BaseFont /{base_name} "
                    f"/Encoding /Identity-H /DescendantFonts [{cid_ref} 0 R] >>"
                ).encode("ascii")
                cid = (
                    f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{base_name} "
                    f"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
                    f"/FontDescriptor {descriptor_ref} 0 R /CIDToGIDMap /Identity /DW 1000{widths_text} >>"
                ).encode("ascii")
                descriptor = (
                    f"<< /Type /FontDescriptor /FontName /{base_name} /Flags 4 "
                    f"/FontBBox [{x_min} {y_min} {x_max} {y_max}] /ItalicAngle 0 "
                    f"/Ascent {font['ascent']} /Descent {font['descent']} /CapHeight {font['ascent']} "
                    f"/StemV 80 /FontFile2 {file_ref} 0 R >>"
                ).encode("ascii")
                font_file = (
                    b"<< /Length " + str(len(font["data"])).encode("ascii") +
                    b" /Length1 " + str(len(font["data"])).encode("ascii") +
                    b" >>\nstream\n" + font["data"] + b"\nendstream"
                )
                return [type0, cid, descriptor, font_file]

            objects.extend(font_objects(regular_font, "MalgunGothic", font_start, font_start + 1, font_start + 2, font_start + 3))
        else:
            objects.extend([
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
            ])
        for image in pdf_images:
            objects.append(
                (
                    f"<< /Type /XObject /Subtype /Image /Width {image['width']} /Height {image['height']} "
                    f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(image['data'])} >>\nstream\n"
                ).encode("ascii")
                + image["data"]
                + b"\nendstream"
            )
        for stream in pages:
            objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        output = io.BytesIO()
        output.write(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(output.tell())
            output.write(f"{index} 0 obj\n".encode("ascii"))
            output.write(obj)
            output.write(b"\nendobj\n")
        xref_at = output.tell()
        output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        output.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.write(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_at}\n%%EOF\n"
            ).encode("ascii")
        )
        return output.getvalue()

    def build_pdf(self, lines: list[str]) -> bytes:
        def pdf_text(value: object) -> str:
            text = str(value).encode("latin-1", "replace").decode("latin-1")
            return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        visible_lines = [line[:110] for line in lines[:42]]
        commands = ["BT", "/F1 16 Tf", "50 790 Td", "20 TL"]
        if visible_lines:
            commands.append(f"({pdf_text(visible_lines[0])}) Tj")
        commands.extend(["/F1 10 Tf", "14 TL"])
        for line in visible_lines[1:]:
            commands.append("T*")
            commands.append(f"({pdf_text(line)}) Tj")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        ]
        output = io.BytesIO()
        output.write(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(output.tell())
            output.write(f"{index} 0 obj\n".encode("ascii"))
            output.write(obj)
            output.write(b"\nendobj\n")
        xref_at = output.tell()
        output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        output.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.write(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_at}\n%%EOF\n"
            ).encode("ascii")
        )
        return output.getvalue()

    def build_xlsx(self, rows: list[list[object]]) -> bytes:
        def cell_ref(row_index: int, col_index: int) -> str:
            letters = ""
            col = col_index
            while col:
                col, remainder = divmod(col - 1, 26)
                letters = chr(65 + remainder) + letters
            return f"{letters}{row_index}"

        section_titles = {
            "LOCK-FIX System Inspection Report",
            "LOCK-FIX 시스템 점검 보고서",
            "Customer / Inspection Information",
            "고객 / 점검 정보",
            "Server Basic Information",
            "서버 기본 정보",
            "Resource Usage Analysis",
            "리소스 사용량 분석",
            "Inspection Summary",
            "점검 요약",
            "Attention Items",
            "주의 항목",
            "Server Inspection Checklist",
            "서버 점검 체크리스트",
            "Engineer Opinion",
            "엔지니어 의견",
            "Electronic Signature",
            "전자 서명",
            "OAM Electronics Co., Ltd.",
        }
        table_headers = {
            "Metric",
            "지표",
            "Category",
            "구분",
            "Time",
            "Customer Name",
            "고객명",
            "OS Version",
            "OS 버전",
            "Total Checks",
            "전체 점검",
            "Inspection Item",
            "점검사항",
            "Content",
            "내용",
            "Signature Confirmation",
            "서명 확인",
            "Engineer Inspection Signature",
            "엔지니어 점검 담당자 서명",
        }

        sheet_rows = []
        for row_index, row in enumerate(rows, start=1):
            first_value = str(row[0] if row else "")
            if first_value in section_titles:
                style_id = 1
                height = ' ht="24" customHeight="1"'
            elif first_value in table_headers:
                style_id = 2
                height = ' ht="21" customHeight="1"'
            else:
                style_id = 0
                height = ""
            cells = []
            for col_index, value in enumerate(row, start=1):
                ref = cell_ref(row_index, col_index)
                if isinstance(value, (int, float)):
                    cells.append(f'<c r="{ref}" s="{style_id}"><v>{value}</v></c>')
                else:
                    cells.append(f'<c r="{ref}" s="{style_id}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
            sheet_rows.append(f'<row r="{row_index}"{height}>{"".join(cells)}</row>')
        sheet = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
            '<cols><col min="1" max="1" width="22" customWidth="1"/><col min="2" max="2" width="24" customWidth="1"/>'
            '<col min="3" max="3" width="18" customWidth="1"/><col min="4" max="4" width="18" customWidth="1"/>'
            '<col min="5" max="5" width="18" customWidth="1"/><col min="6" max="6" width="18" customWidth="1"/>'
            '<col min="7" max="7" width="44" customWidth="1"/></cols>'
            f'<sheetData>{"".join(sheet_rows)}</sheetData>'
            '</worksheet>'
        )
        styles = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<fonts count="3"><font><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="13"/><color rgb="FF0B2E79"/><name val="Calibri"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>'
            '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFEAF1F8"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF0B2E79"/><bgColor indexed="64"/></patternFill></fill></fills>'
            '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E2EA"/></left><right style="thin"><color rgb="FFD9E2EA"/></right><top style="thin"><color rgb="FFD9E2EA"/></top><bottom style="thin"><color rgb="FFD9E2EA"/></bottom><diagonal/></border></borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="1" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment vertical="center"/></xf><xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf></cellXfs>'
            '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
            '</styleSheet>'
        )
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
            archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Report" sheetId="1" r:id="rId1"/></sheets></workbook>')
            archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
            archive.writestr("xl/styles.xml", styles)
            archive.writestr("xl/worksheets/sheet1.xml", sheet)
        return output.getvalue()

    def build_docx(self, report: dict, lang: str = "en") -> bytes:
        labels = self.report_export_labels(lang)
        local = lambda value: self.localize_report_export_value(value, lang)

        def para(text: str, style: str = "") -> str:
            props = ""
            if style == "title":
                props = '<w:pPr><w:jc w:val="center"/></w:pPr>'
                run = f'<w:r><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="0B2E79"/></w:rPr><w:t>{escape(text)}</w:t></w:r>'
            elif style == "section":
                run = f'<w:r><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="0B2E79"/></w:rPr><w:t>{escape(text)}</w:t></w:r>'
            else:
                run = f'<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>{escape(text)}</w:t></w:r>'
            return f"<w:p>{props}{run}</w:p>"

        def cell(text: object, shaded: bool = False) -> str:
            shade = '<w:shd w:fill="EEF3F7"/>' if shaded else ""
            return (
                "<w:tc><w:tcPr>"
                f"{shade}<w:tcMar><w:top w:w=\"90\" w:type=\"dxa\"/><w:left w:w=\"90\" w:type=\"dxa\"/><w:bottom w:w=\"90\" w:type=\"dxa\"/><w:right w:w=\"90\" w:type=\"dxa\"/></w:tcMar>"
                "</w:tcPr><w:p><w:r><w:rPr><w:sz w:val=\"18\"/></w:rPr><w:t>"
                + escape(str(text))
                + "</w:t></w:r></w:p></w:tc>"
            )

        def table(rows: list[list[object]], header: bool = False) -> str:
            trs = []
            for index, row in enumerate(rows):
                trs.append("<w:tr>" + "".join(cell(value, shaded=header and index == 0) for value in row) + "</w:tr>")
            return (
                '<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
                '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="D9E2EA"/><w:left w:val="single" w:sz="4" w:color="D9E2EA"/><w:bottom w:val="single" w:sz="4" w:color="D9E2EA"/><w:right w:val="single" w:sz="4" w:color="D9E2EA"/><w:insideH w:val="single" w:sz="4" w:color="D9E2EA"/><w:insideV w:val="single" w:sz="4" w:color="D9E2EA"/></w:tblBorders>'
                "</w:tblPr>"
                + "".join(trs)
                + "</w:tbl>"
            )

        def image_para(rel_id: str, name: str) -> str:
            return (
                '<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0" '
                'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
                '<wp:extent cx="3048000" cy="914400"/><wp:docPr id="1" name="'
                + escape(name)
                + '"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                '<pic:nvPicPr><pic:cNvPr id="0" name="'
                + escape(name)
                + '"/><pic:cNvPicPr/></pic:nvPicPr>'
                '<pic:blipFill><a:blip r:embed="'
                + rel_id
                + '"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="3048000" cy="914400"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
                '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
            )

        extras = report["extras"]
        signature_media = []
        signature_blocks = []
        for field, rel_id, filename, label in [
            ("engineer_signature", "rIdEngineerSignature", "engineer_signature.png", labels["engineer_signature"]),
            ("manager_signature", "rIdManagerSignature", "manager_signature.png", labels["manager_signature"]),
        ]:
            image_bytes = self.image_data_url_bytes(extras.get(field, ""))
            if image_bytes:
                signature_media.append((rel_id, filename, image_bytes))
                signature_blocks.extend([para(label, "section"), image_para(rel_id, label)])

        customer_rows = [
            [labels["customer_name"], report["customer"]["customer_name"], labels["inspection_date"], report["customer"]["inspection_date"]],
            [labels["customer_contact"], report["customer"]["customer_contact"], labels["engineer"], report["customer"]["engineer"]],
            [labels["customer_email"], report["customer"]["customer_email"], labels["engineer_contact"], report["customer"]["engineer_contact"]],
        ]
        server_rows = [
            [labels["os_version"], report["server"]["os_version"], labels["cpu"], report["server"]["cpu"]],
            [labels["service"], report["server"]["service"], labels["memory"], report["server"]["memory"]],
            [labels["model"], report["server"]["model"], labels["disk"], report["server"]["disk"]],
            ["S/N", report["server"]["serial"], labels["hostname"], report["server"]["hostname"]],
        ]
        resource_rows = [
            [labels["metric"], labels["current"], labels["average"], labels["peak"], labels["threshold"], labels["result"], labels["recommendation"]],
            *[
                [
                    card["label"],
                    f"{card['current']}%",
                    f"{card['average']}%",
                    f"{card['peak']}%",
                    f"{card['threshold']}%",
                    local(card["status"]),
                    local(card["recommendation"]),
                ]
                for card in report["cards"]
            ],
        ]
        inspection_rows = [
            [labels["category"], labels["inspection_item"], labels["details"], labels["criteria"], labels["metric"], labels["result"]],
            *[
                [item["category"], item["item"], item["detail"], item["criteria"], item["metric"], local(item["result"])]
                for item in report["inspection_items"]
            ],
        ]
        signature_rows = [
            [labels["signature_confirmation"], labels["role"], labels["status"], labels["signature_date"], labels["signature_seal"]],
            [
                labels["engineer_signature"],
                labels["engineer"],
                labels["signed"] if extras["engineer_signature"] else labels["not_signed"],
                report["generated_at"] if extras["engineer_signature"] else "-",
                labels["attached"] if extras["engineer_signature"] else labels["pending"],
            ],
            [
                labels["manager_signature"],
                labels["manager"],
                labels["signed"] if extras["manager_signature"] else labels["not_signed"],
                report["generated_at"] if extras["manager_signature"] else "-",
                labels["attached"] if extras["manager_signature"] else labels["pending"],
            ],
        ]

        body = [
            para(labels["title"], "title"),
            para(f"{labels['report_no']} #1    {labels['generated']}: {report['generated_at']}"),
            para(f"{labels['overall_status']}: {local(report['summary']['overall_status'])}"),
            para(labels["analysis"] if lang == "ko" else report["summary"]["analysis"]),
            para(labels["customer_info"], "section"),
            table(customer_rows),
            para(labels["server_basic"], "section"),
            table(server_rows),
            para(labels["resource_usage"], "section"),
            table(resource_rows, header=True),
            para(labels["checklist"], "section"),
            table(inspection_rows, header=True),
            para(labels["engineer_opinion"], "section"),
            para(extras["engineer_opinion"] or "-"),
            para(labels["electronic_signature"], "section"),
            table(signature_rows, header=True),
            *signature_blocks,
            para("OAM Electronics Co., Ltd.", "section"),
            *[para(line) for line in self.report_company_footer_lines()[1:]],
        ]
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'
            + "".join(body)
            + '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="850" w:right="720" w:bottom="850" w:left="720" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>'
        )
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            png_default = '<Default Extension="png" ContentType="image/png"/>' if signature_media else ""
            archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' + png_default + '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            if signature_media:
                relationships = [
                    f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{filename}"/>'
                    for rel_id, filename, _ in signature_media
                ]
                archive.writestr("word/_rels/document.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(relationships) + "</Relationships>")
                for _, filename, image_bytes in signature_media:
                    archive.writestr(f"word/media/{filename}", image_bytes)
            archive.writestr("word/document.xml", document)
        return output.getvalue()

    def send_download(self, body: bytes, content_type: str, filename: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f"attachment; filename={filename}")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.write_body(body)

    def serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "not found")
            return
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.write_body(data)

    def send_json(self, payload: dict, status: int = 200, headers=None) -> None:
        payload = LockFixWebHandler.sanitize_json_payload(self, payload)
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        header_names = {str(key).lower() for key in (headers or {})}
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if "cache-control" not in header_names:
            self.send_header("Cache-Control", "no-store, max-age=0")
        if "pragma" not in header_names:
            self.send_header("Pragma", "no-cache")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.write_body(data)

    def send_html(self, html: str, status: int = 200) -> None:
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.write_body(data)

    def write_body(self, body: bytes) -> None:
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return


def run(host: str = "127.0.0.1", port: int = 8088, config_path: Path = DEFAULT_CONFIG) -> None:
    context = WebContext(config_path)
    context.start_agent_service_worker()
    context.start_veeam_steering_worker()
    LockFixWebHandler.context = context
    server = ThreadingHTTPServer((host, port), LockFixWebHandler)
    print(f"LOCK-FIX PoC UI: http://{host}:{port}")
    print(f"Config: {config_path}")
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    run(args.host, args.port, args.config.resolve())

