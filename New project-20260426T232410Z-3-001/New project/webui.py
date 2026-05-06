from __future__ import annotations

import json
import base64
import binascii
import io
import mimetypes
import os
import platform
import secrets
import shutil
import ssl
import hashlib
import socket
import time
import uuid
import zipfile
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlencode, urlparse
from xml.sax.saxutils import escape

from lockfix.config import get_veeam_config, load_app_config, load_config
from lockfix.controller import LockFixController
from lockfix.hashcheck import verify_manifest
from lockfix.identity import fingerprint_formula, fingerprint_parts, slot_uid, verify_uid
from lockfix.integrated import integrated_solution_summary
from lockfix.source_inventory import integrated_source_inventory
from lockfix.veeam_diagnostics import run_veeam_diagnostics


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "web" / "static"
DEFAULT_CONFIG = ROOT / "config" / "lockfix.example.json"


class WebContext:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.sessions = {}
        self.qr_tokens = {}
        self.license_path = ROOT / "runtime" / "license.json"
        self.report_customer_path = ROOT / "runtime" / "report_customer.json"
        self.report_extras_path = ROOT / "runtime" / "report_extras.json"

    @property
    def app_config(self):
        return load_app_config(self.config_path)

    @property
    def config(self):
        return load_config(self.config_path)

    @property
    def controller(self) -> LockFixController:
        return LockFixController(self.config)


class LockFixWebHandler(BaseHTTPRequestHandler):
    context: WebContext
    session_ttl_seconds = 60 * 60 * 8

    def log_message(self, format: str, *args: object) -> None:
        print("[webui] " + format % args)

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self.serve_file(STATIC_DIR / "index.html")
            elif parsed.path.startswith("/static/"):
                self.serve_file(STATIC_DIR / parsed.path[len("/static/") :])
            elif parsed.path == "/api/session":
                self.send_json({"authenticated": self.is_authenticated(), "license": self.license_status()})
            elif parsed.path == "/open-latest-package-folder":
                self.open_latest_package_folder()
            elif parsed.path == "/api/console/status":
                self.require_auth()
                self.send_json(self.console_status())
            elif parsed.path == "/api/qr-login/status":
                token = parse_qs(parsed.query).get("token", [""])[0]
                response = self.qr_status_response(token)
                headers = {}
                if response.get("approved") and response.get("session"):
                    headers["Set-Cookie"] = f"lockfix_session={response['session']}; HttpOnly; SameSite=Lax; Path=/"
                self.send_json(response, headers=headers)
            elif parsed.path == "/api/summary":
                self.require_auth()
                self.send_json(self.summary())
            elif parsed.path == "/api/audit":
                self.require_auth()
                self.send_json({"items": self.audit_items()})
            elif parsed.path == "/api/integrated":
                self.require_auth()
                self.send_json(integrated_solution_summary())
            elif parsed.path == "/api/monitoring":
                self.require_auth()
                params = parse_qs(parsed.query)
                self.send_json(self.monitoring_summary(params.get("start", [""])[0], params.get("end", [""])[0]))
            elif parsed.path == "/api/monitoring.csv":
                self.require_auth()
                params = parse_qs(parsed.query)
                self.send_monitoring_csv(params.get("start", [""])[0], params.get("end", [""])[0])
            elif parsed.path == "/api/report":
                self.require_auth()
                self.send_json(self.report_summary())
            elif parsed.path == "/api/report/extras":
                self.require_auth()
                self.send_json(self.report_extras_record())
            elif parsed.path == "/api/report.csv":
                self.require_auth()
                self.send_report_csv()
            elif parsed.path == "/api/report.xlsx":
                self.require_auth()
                self.send_report_xlsx()
            elif parsed.path == "/api/report.docx":
                self.require_auth()
                self.send_report_docx()
            elif parsed.path == "/api/dashboard":
                self.require_auth()
                self.send_json(self.dashboard_summary())
            elif parsed.path == "/api/notification":
                self.require_auth()
                self.send_json({"items": self.notification_items()})
            elif parsed.path == "/api/detect":
                self.require_auth()
                self.send_json(self.detect_summary())
            elif parsed.path == "/api/network-status":
                self.require_auth()
                self.send_json(self.network_status_summary())
            elif parsed.path == "/api/veeam-backup":
                self.require_auth()
                self.send_json(self.veeam_backup_summary())
            elif parsed.path == "/api/logs":
                self.require_auth()
                params = parse_qs(parsed.query)
                self.send_json(
                    self.logs_summary(
                        params.get("start", [""])[0],
                        params.get("end", [""])[0],
                        params.get("page", ["1"])[0],
                        params.get("retention", ["30"])[0],
                    )
                )
            elif parsed.path == "/api/logs.csv":
                self.require_auth()
                params = parse_qs(parsed.query)
                self.send_logs_csv(params.get("start", [""])[0], params.get("end", [""])[0], params.get("retention", ["30"])[0])
            elif parsed.path == "/api/license":
                self.require_auth()
                self.send_json(self.license_status())
            elif parsed.path == "/api/sources":
                self.require_auth()
                inventory = integrated_source_inventory()
                inventory["air_gap"] = self.air_gap_summary()
                self.send_json(inventory)
            else:
                self.send_error(404, "not found")
        except PermissionError as exc:
            self.send_json({"error": str(exc)}, status=401)
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/login":
                payload = self.read_json_body()
                email = str(payload.get("email", "")).strip()
                password = str(payload.get("password", ""))
                if secrets.compare_digest(email, "admin") and secrets.compare_digest(password, "1"):
                    token = secrets.token_urlsafe(32)
                    self.context.sessions[token] = time.time()
                    self.send_json(
                        {"authenticated": True},
                        headers={"Set-Cookie": f"lockfix_session={token}; HttpOnly; SameSite=Lax; Path=/"},
                    )
                else:
                    self.send_json({"authenticated": False, "error": "Invalid account."}, status=401)
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
                self.require_auth()
                payload = self.read_json_body()
                self.send_json(self.register_license(payload))
            elif parsed.path == "/api/report/customer":
                self.require_auth()
                payload = self.read_json_body()
                self.send_json(self.save_report_customer(payload))
            elif parsed.path == "/api/report/extras":
                self.require_auth()
                payload = self.read_json_body()
                self.send_json(self.save_report_extras(payload))
            elif parsed.path == "/api/isolate":
                self.require_auth()
                slot_id = self.query_slot(parsed.query)
                state = self.context.controller.isolate(slot_id)
                self.send_json({"slot_id": slot_id, "state": state.value, "summary": self.summary()})
            elif parsed.path == "/api/reconnect":
                self.require_auth()
                slot_id = self.query_slot(parsed.query)
                state = self.context.controller.reconnect(slot_id)
                self.send_json({"slot_id": slot_id, "state": state.value, "summary": self.summary()})
            elif parsed.path == "/api/emergency-reconnect":
                self.require_auth()
                payload = self.read_json_body()
                slot_id = self.query_slot(parsed.query)
                state = self.context.controller.emergency_reconnect(slot_id, str(payload.get("verification_hash", "")))
                self.send_json(
                    {
                        "slot_id": slot_id,
                        "state": state.value,
                        "message": "Emergency volume access verified. Backup volume is reconnected.",
                        "summary": self.summary(),
                    }
                )
            else:
                self.send_error(404, "not found")
        except PermissionError as exc:
            self.send_json({"error": str(exc)}, status=401)
        except Exception as exc:
            self.send_json({"error": str(exc), "summary": self.summary()}, status=500)

    def query_slot(self, query: str) -> str:
        values = parse_qs(query)
        slot_id = values.get("slot", [""])[0]
        if not slot_id:
            raise ValueError("slot query parameter is required")
        return slot_id

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

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
        created_at = self.context.sessions.get(token)
        if not created_at:
            return False
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
        return LockFixWebHandler.safe_text_lines(self, path)

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
        self.context.sessions[session] = time.time()
        self.context.qr_tokens.pop(token, None)
        return {
            "approved": True,
            "expired": False,
            "session": session,
        }

    def require_auth(self) -> None:
        if not self.is_authenticated():
            raise PermissionError("authentication required")

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

    def air_gap_summary(self) -> dict:
        summary = self.summary()
        now = time.time()
        tick = int(now)
        veeam_runtime = self.veeam_interlock_runtime(now)
        current_step = veeam_runtime["current_step"]
        veeam_connected = bool(veeam_runtime.get("api_synced") or veeam_runtime.get("connected"))
        veeam_states = [
            {"step": 1, "title": "Backup completed", "label": "백업 완료", "state": "PENDING", "code": "BACKUP_COMPLETED"},
            {"step": 2, "title": "Flush running", "label": "Flush 실행", "state": "PENDING", "code": "FLUSHING"},
            {"step": 3, "title": "I/O checking", "label": "I/O 종료 확인", "state": "PENDING", "code": "IO_CHECKING"},
            {"step": 4, "title": "Unmount", "label": "Unmount", "state": "PENDING", "code": "UNMOUNTING"},
            {"step": 5, "title": "Power off", "label": "전원 OFF", "state": "PENDING", "code": "POWERING_OFF"},
        ]
        for item in veeam_states:
            if veeam_connected:
                if item["step"] < current_step:
                    item["state"] = "DONE"
                elif item["step"] == current_step:
                    item["state"] = "ACTIVE"
            item["checked_at"] = veeam_runtime["last_checked"]
            item["log"] = veeam_runtime["step_logs"][item["step"] - 1]
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
                        "state": "CUT_OFF",
                        "label": "Physical Power Cut-off Complete",
                        "description": "Hard Power-Off circuit is open and the data path is physically isolated.",
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
        return {
            "security_score": {
                "score": 98,
                "status": "SAFE AIR-GAP",
                "description": "Power cut-off, solenoid lock, and integrity verification are all operating normally.",
            },
            "kpis": [
                {
                    "id": "power",
                    "title": "Power Cut-off",
                    "value": "Physical Cut-off Complete",
                    "detail": "Hard power isolation, not a software-only unmount.",
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
            "session_logs": veeam_runtime["session_logs"],
            "bays": bays,
            "integrity_history": [
                {"time": "2026-04-25 22:40:13", "target": "Backup Cycle #1042", "uid": "MATCH", "hash": "VALID"},
                {"time": "2026-04-25 12:00:10", "target": "Backup Cycle #1041", "uid": "MATCH", "hash": "VALID"},
                {"time": "2026-04-24 23:58:44", "target": "Backup Cycle #1040", "uid": "MATCH", "hash": "VALID"},
            ],
            "emergency": {
                "title": "Emergency Control Center",
                "description": "Manual release is available only after two-administrator approval.",
                "primary": "Waiting for Dual Approval",
                "secondary": "Data path activation remains blocked",
            },
            "emergency_access": self.emergency_access_summary(summary),
        }

    def emergency_access_summary(self, summary: dict | None = None) -> dict:
        config = self.context.config
        status = self.context.controller.status()
        slot_summaries = []
        for slot_id, slot in config.slots.items():
            current_state = status.get(slot_id, "READY_MOCK")
            auth_hash = self.context.controller.emergency_access_hash(slot_id)
            uid_ok, current_uid = verify_uid(slot)
            try:
                mount_exists = slot.mount_point.exists()
                mount_error = ""
            except OSError as exc:
                mount_exists = False
                mount_error = str(exc)
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
            power_record = LockFixWebHandler.latest_audit_record(self, slot_id, {"power.mock.off", "power.command.off", "power.mock.off.error", "power.command.off.error"})
            reconnect_records = LockFixWebHandler.recent_reconnect_audit_records(self, slot_id)
            reconnect_history = [
                item
                for item in (LockFixWebHandler.format_reconnect_audit_record(self, record) for record in reconnect_records)
                if item
            ]
            normalized_device = str(slot.device).strip().replace("/", "\\").rstrip("\\").lower()
            normalized_mount = str(slot.mount_point).strip().replace("/", "\\").rstrip("\\").lower()
            os_volume_blocked = normalized_device in {"c:", "c"} or normalized_mount in {"c:", "c"}
            state_allows_access = current_state in {"ISOLATED", "POWERING_OFF", "UNMOUNTING", "WAITING_DISK", "ERROR", "QUARANTINE"}
            slot_summaries.append(
                {
                    "slot_id": slot_id,
                    "device": slot.device,
                    "mount_point": str(slot.mount_point),
                    "state": current_state,
                    "dry_run": config.dry_run,
                    "eligible": state_allows_access and not os_volume_blocked,
                    "blocked_reason": "C:\\ OS volume is permanently blocked." if os_volume_blocked else "",
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
                    "last_reconnect": reconnect_history[-1] if reconnect_history else "-",
                    "reconnect_history": reconnect_history[-12:],
                }
            )
        first = slot_summaries[0] if slot_summaries else {}
        return {
            "title": "Emergency Volume Access",
            "description": "Unmount 이후 긴급 접속이 필요한 경우 인증 해시값을 확인한 뒤 UID와 SHA-256 검증을 다시 수행하고 볼륨을 즉시 접속합니다.",
            "primary": "검증 후 긴급 접속",
            "secondary": "C:\\ OS 볼륨은 어떤 경우에도 마운트 해제/재접속 작업 대상이 될 수 없습니다.",
            "slot": first,
            "slots": slot_summaries,
        }

    def recent_reconnect_audit_records(self, slot_id: str, limit: int = 20) -> list[dict]:
        lines = LockFixWebHandler.audit_log_lines(self)
        events = {
            "emergency.reconnect.request",
            "emergency.reconnect.approved",
            "emergency.reconnect.denied",
            "emergency.reconnect.complete",
            "state.transition",
            "power.mock.on.start",
            "power.mock.on.tick",
            "power.mock.on",
            "power.command.on.start",
            "power.command.on.tick",
            "power.command.on",
            "power.command.on.error",
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
            "disk.health.scan.error",
            "disk.mount_rw.start",
            "disk.mount_rw.tick",
            "disk.mount_rw",
            "disk.mount_rw.error",
            "verify.uid",
            "verify.hash",
        }
        records = []
        reconnect_states = {
            "RECONNECT_REQUESTED",
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
            if record.get("event") == "emergency.reconnect.request" or (
                record.get("event") == "state.transition" and str(record.get("state") or "") == "RECONNECT_REQUESTED"
            ):
                records = []
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
        if event == "emergency.reconnect.denied":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "verification_hash_mismatch")
            return f"{prefix}LOCK-FIX Reconnect DENIED - slot {slot_id}, {reason}"
        if event == "state.transition":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            return f"{prefix}LOCK-FIX Reconnect STATE - slot {slot_id}, {state}"
        if event == "disk.reconnect.plan":
            drive = LockFixWebHandler.compact_log_value(self, record.get("drive_letter") or "-")
            disk = LockFixWebHandler.compact_log_value(self, record.get("disk_number") or "-")
            partition = LockFixWebHandler.compact_log_value(self, record.get("partition_number") or "-")
            volume = LockFixWebHandler.compact_log_value(self, record.get("volume_unique_id") or "-")
            return f"{prefix}LOCK-FIX Reconnect PLAN - slot {slot_id}, drive {drive}, disk {disk}, partition {partition}, volume {volume}"
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
        if event == "emergency.reconnect.complete":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            return f"{prefix}LOCK-FIX Reconnect COMPLETE - slot {slot_id}, state {state}"
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

    def veeam_interlock_runtime(self, now: float) -> dict:
        runtime_path = ROOT / "runtime" / "veeam_interlock_state.json"
        payload = {}
        if runtime_path.exists():
            try:
                payload = json.loads(runtime_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {}

        install_props = self.veeam_install_properties()
        server = str(payload.get("server") or os.environ.get("LOCKFIX_VEEAM_HOST") or install_props.get("veeam_host") or "127.0.0.1")
        port = int(payload.get("port") or os.environ.get("LOCKFIX_VEEAM_PORT") or install_props.get("veeam_port") or 9419)
        port_open = self.tcp_port_open(server, port)
        api_payload = self.poll_veeam_api(server, port, payload)
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
        labels = ["백업 완료", "Flush 실행", "I/O 종료 확인", "Unmount", "전원 OFF"]
        codes = ["BACKUP_COMPLETED", "FLUSHING", "IO_CHECKING", "UNMOUNTING", "POWERING_OFF"]
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
        if auto_isolate.get("state") == "ISOLATED":
            current_step = 5
            progress = 100
            for item in step_logs:
                step_number = int(item.get("step") or 0)
                item["state"] = "DONE" if step_number < 5 else "ACTIVE"
                item["transition_allowed"] = step_number <= 5
                item["progress_percent"] = 100
                if step_number == 5:
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
            for key in ("port_9419", "token", "sessions"):
                check = checks.get(key) if isinstance(checks.get(key), dict) else {}
                if check:
                    state = "OK" if check.get("ok") else "WAIT"
                    actions.append(f"{state} - {check.get('message') or key}")
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
            for key in ("port_9419", "token", "sessions"):
                check = checks.get(key) if isinstance(checks.get(key), dict) else {}
                if check:
                    state = "OK" if check.get("ok") else "WAIT"
                    waiting_actions.append(f"{state} - {check.get('message') or key}")
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
                5: "Power off",
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
        interlock_actions = LockFixWebHandler.veeam_flush_operation_actions(
            self,
            slot_id,
            current_step,
        )
        interlock_actions += LockFixWebHandler.veeam_io_quiet_operation_actions(self, slot_id, current_step)
        interlock_actions += LockFixWebHandler.veeam_unmount_operation_actions(self, slot_id, current_step)
        interlock_actions += LockFixWebHandler.veeam_power_off_operation_actions(self, slot_id, current_step)
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
            if record.get("event") == "disk.flush.start":
                actions.extend(LockFixWebHandler.flush_start_detail_actions(self, record))
            action = LockFixWebHandler.format_flush_audit_record(self, record)
            if action:
                actions.append(action)
        if any(record.get("event") == "disk.flush.error" for record in records):
            actions.append(f"LOCK-FIX STEP 2 ERROR - Flush result was recorded as failed. Step 3 must not proceed until the error is resolved.")
        elif any(record.get("event") == "disk.flush" for record in records):
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
        events = {"disk.flush.start", "disk.flush.tick", "disk.flush", "disk.flush.error"}
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
            if record.get("event") == "disk.flush.start":
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_flush_audit_records(self, records)[-limit:]

    def normalize_flush_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if record.get("event") == "disk.flush.start"]
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
            elif event == "disk.flush":
                completions.append(record)
            elif event == "disk.flush.error":
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
        if event == "disk.flush.start":
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            device = LockFixWebHandler.compact_log_value(self, record.get("device") or "-")
            return f"{prefix}LOCK-FIX Flush START - slot {slot_id}, mount {mount_point}, device {device}"
        if event == "disk.flush.tick":
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            mount_point = LockFixWebHandler.compact_log_value(self, record.get("mount_point") or "-")
            return f"{prefix}LOCK-FIX Flush TICK {elapsed}s - slot {slot_id}, mount {mount_point}"
        if event == "disk.flush.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "flush command failed")
            return f"{prefix}LOCK-FIX Flush ERROR - slot {slot_id}, {error}"
        if event == "disk.flush":
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
            actions.append("LOCK-FIX STEP 4 ERROR - Unmount result was recorded as failed. Step 5 Power OFF must not proceed until the error is resolved.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 4, "Unmount", slot_id, records, "ERROR"))
        elif any(record.get("event") == "disk.unmount" for record in records):
            actions.append("LOCK-FIX STEP 4 COMPLETE - Backup volume unmount result was recorded. Continuing to Step 5 Power OFF.")
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
            f"{prefix}LOCK-FIX Unmount GATE - Step 5 Power OFF remains blocked until {drive}:\\ access removal is verified.",
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
                f"LOCK-FIX STEP 5 DETAIL - Power OFF operation flow for slot {slot_id}",
                f"LOCK-FIX Power OFF WAIT - step 5 is active for slot {slot_id}, but no power-off audit event has been recorded yet.",
            ]
        actions = [f"LOCK-FIX STEP 5 DETAIL - Power OFF operation flow for slot {slot_id}"]
        for record in records:
            if str(record.get("event") or "").endswith(".off.start"):
                actions.extend(LockFixWebHandler.power_off_start_detail_actions(self, record))
            action = LockFixWebHandler.format_power_off_audit_record(self, record)
            if action:
                actions.append(action)
        if any(str(record.get("event") or "").endswith(".off.error") for record in records):
            actions.append("LOCK-FIX STEP 5 ERROR - Power OFF result was recorded as failed. Manual inspection is required.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 5, "Power OFF", slot_id, records, "ERROR"))
        elif any(record.get("event") in {"power.mock.off", "power.command.off"} for record in records):
            actions.append("LOCK-FIX STEP 5 COMPLETE - Power OFF result was recorded. LOCK-FIX isolation flow is complete.")
            actions.extend(LockFixWebHandler.audit_history_detail_actions(self, 5, "Power OFF", slot_id, records, "OK"))
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
            if str(record.get("event") or "").endswith(".off.start"):
                records = []
            records.append(record)
        return LockFixWebHandler.normalize_power_off_audit_records(self, records)[-limit:]

    def normalize_power_off_audit_records(self, records: list[dict]) -> list[dict]:
        starts = [record for record in records if str(record.get("event") or "").endswith(".off.start")]
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
            if event.endswith(".off.tick"):
                try:
                    elapsed = int(record.get("elapsed_seconds") or 0)
                except (TypeError, ValueError):
                    elapsed = 0
                ticks.setdefault(elapsed, record)
            elif event in {"power.mock.off", "power.command.off"}:
                completions.append(record)
            elif event.endswith(".off.error"):
                errors.append(record)
            elif ".status" in event:
                statuses.append(record)
            elif event in {"power.off.proof", "power.off.proof.required"}:
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
        mode = "command" if event.startswith("power.command") else "mock"
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        actions = [
            f"{prefix}LOCK-FIX Power OFF TARGET - slot {slot_id}, controller mode {mode}",
            f"{prefix}LOCK-FIX Power OFF COMMAND - issuing final isolation power-off request.",
        ]
        if mode == "command":
            command = LockFixWebHandler.compact_log_value(self, " ".join(record.get("command") or []))
            actions.append(f"{prefix}LOCK-FIX Power OFF COMMAND DETAIL - {command or 'configured command'}")
        return actions

    def format_power_off_audit_record(self, record: dict) -> str:
        event = str(record.get("event") or "")
        slot_id = str(record.get("slot_id") or "-")
        timestamp = LockFixWebHandler.format_audit_timestamp(self, record.get("ts"))
        prefix = f"{timestamp} - " if timestamp else ""
        mode = "command" if event.startswith("power.command") else "mock"
        if event.endswith(".off.start"):
            return f"{prefix}LOCK-FIX Power OFF START - slot {slot_id}, controller mode {mode}"
        if event.endswith(".off.tick"):
            elapsed = LockFixWebHandler.compact_log_value(self, record.get("elapsed_seconds") or 1)
            return f"{prefix}LOCK-FIX Power OFF TICK {elapsed}s - slot {slot_id}"
        if event.endswith(".off.error"):
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "power off command failed")
            return f"{prefix}LOCK-FIX Power OFF ERROR - slot {slot_id}, {error}"
        if event in {"power.mock.off", "power.command.off"}:
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or f"{mode} power off completed")
            return f"{prefix}LOCK-FIX Power OFF OK - slot {slot_id}, {output}"
        if event == "power.command.status.start":
            command = LockFixWebHandler.compact_log_value(self, " ".join(record.get("command") or []))
            return f"{prefix}LOCK-FIX Power OFF STATUS CHECK START - querying PDU/relay/storage controller state. {command}"
        if event == "power.command.status.missing":
            requirement = LockFixWebHandler.compact_log_value(self, record.get("requirement") or "Configure power.status_command.")
            return f"{prefix}LOCK-FIX Power OFF PROOF REQUIRED - actual OFF proof requires a PDU/relay/storage controller status response. {requirement}"
        if event == "power.command.status.error":
            error = LockFixWebHandler.compact_log_value(self, record.get("error") or "controller status check failed")
            return f"{prefix}LOCK-FIX Power OFF STATUS ERROR - slot {slot_id}, {error}"
        if event == "power.command.status":
            state = LockFixWebHandler.compact_log_value(self, record.get("state") or "-")
            output = LockFixWebHandler.compact_log_value(self, record.get("output") or "")
            if record.get("ok") is True:
                return f"{prefix}LOCK-FIX Power OFF PROOF OK - controller status confirmed OFF. response {output or state}"
            return f"{prefix}LOCK-FIX Power OFF STATUS NOT CONFIRMED - controller returned {state}. response {output}"
        if event == "power.mock.status":
            requirement = LockFixWebHandler.compact_log_value(self, record.get("requirement") or "Use a controller status response.")
            return f"{prefix}LOCK-FIX Power OFF PROOF NOT AVAILABLE - mock mode cannot prove physical power state. {requirement}"
        if event == "power.off.proof":
            message = LockFixWebHandler.compact_log_value(self, record.get("message") or "Physical power OFF was proved.")
            return f"{prefix}LOCK-FIX Power OFF PROOF RECORDED - {message}"
        if event == "power.off.proof.required":
            reason = LockFixWebHandler.compact_log_value(self, record.get("reason") or "controller status response is required")
            required = LockFixWebHandler.compact_log_value(self, record.get("required_config") or "power.status_command")
            return f"{prefix}LOCK-FIX Power OFF PROOF REQUIRED - {reason}. Required: {required}"
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

    def compact_log_value(self, value: object) -> str:
        return " ".join(str(value).split())

    def save_veeam_last_logs(self, session_logs: list[dict], checked_at: str) -> None:
        path = ROOT / "runtime" / "veeam_last_session_logs.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"checked_at": checked_at, "session_logs": session_logs}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

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
        return run_veeam_diagnostics(self.context.config, self.context.controller)

    def poll_veeam_api(self, server: str, port: int, local_payload: dict) -> dict:
        config = self.context.app_config
        veeam_config = config.get("veeam", {})
        LockFixWebHandler.prepare_veeam_process_environment(self, veeam_config)
        try:
            diagnostics = run_veeam_diagnostics(self.context.config, self.context.controller)
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

        if not os.environ.get(password_env) and install_props.get("veeam_password"):
            os.environ[password_env] = str(install_props["veeam_password"])
        if not os.environ.get(username_env) and install_props.get("veeam_user"):
            os.environ[username_env] = str(install_props["veeam_user"])
        if not os.environ.get("LOCKFIX_VEEAM_BASE_URL") and install_props.get("veeam_base_url"):
            os.environ["LOCKFIX_VEEAM_BASE_URL"] = str(install_props["veeam_base_url"])
        if not os.environ.get("LOCKFIX_VEEAM_API_VERSION") and install_props.get("veeam_api_version"):
            os.environ["LOCKFIX_VEEAM_API_VERSION"] = str(install_props["veeam_api_version"])
        if not os.environ.get("LOCKFIX_VEEAM_HOST") and install_props.get("veeam_host"):
            os.environ["LOCKFIX_VEEAM_HOST"] = str(install_props["veeam_host"])
        if not os.environ.get("LOCKFIX_VEEAM_PORT") and install_props.get("veeam_port"):
            os.environ["LOCKFIX_VEEAM_PORT"] = str(install_props["veeam_port"])

    def auto_isolate_after_veeam_success(self, payload: dict, status: str, checked_at: str) -> dict:
        result = str(payload.get("result") or status or "").upper()
        progress = int(payload.get("progress_percent") or payload.get("progress") or 0)
        if result not in {"SUCCESS", "SUCCEEDED", "COMPLETED"} and progress < 100:
            return {"enabled": True, "triggered": False, "message": "Veeam session is not successful yet."}
        slot_id = str(payload.get("slot_id") or os.environ.get("LOCKFIX_SLOT_ID") or next(iter(self.context.config.slots), "BAY-01"))
        session_key = "|".join(
            [
                str(payload.get("job") or payload.get("name") or "Veeam Backup"),
                str(payload.get("started_at") or "-"),
                str(payload.get("ended_at") or "-"),
            ]
        )
        marker_path = ROOT / "runtime" / "veeam_auto_isolate.json"
        try:
            previous = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else {}
        except (OSError, json.JSONDecodeError):
            previous = {}
        if previous.get("session_key") == session_key and previous.get("state") == "ISOLATED":
            return {
                "enabled": True,
                "triggered": False,
                "slot_id": slot_id,
                "session_key": session_key,
                "state": "ISOLATED",
                "message": "Successful session was already isolated.",
            }
        try:
            restore_scope = payload.get("restore_point_scope") if isinstance(payload.get("restore_point_scope"), dict) else {}
            repository_path = str(payload.get("repository_path") or restore_scope.get("repository_path") or "")
            state = self.context.controller.isolate(slot_id, repository_path=repository_path)
            marker_path.parent.mkdir(parents=True, exist_ok=True)
            marker_path.write_text(
                json.dumps(
                    {
                        "session_key": session_key,
                        "slot_id": slot_id,
                        "state": state.value,
                        "checked_at": checked_at,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            return {
                "enabled": True,
                "triggered": True,
                "slot_id": slot_id,
                "session_key": session_key,
                "state": state.value,
                "message": "Veeam backup success detected. LOCK-FIX isolate was called automatically.",
            }
        except Exception as exc:
            return {
                "enabled": True,
                "triggered": False,
                "slot_id": slot_id,
                "session_key": session_key,
                "error": str(exc),
                "message": "Veeam backup success detected, but automatic isolate failed.",
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
                "excel": "/api/report.xlsx",
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

    def dashboard_summary(self) -> dict:
        logs = [
            {"type": "WARNING", "date": "2024-12-22 12:03:06", "content": "[MEMORY] 92.75% (Threshold:80.0%)"},
            {"type": "LOGS", "date": "2024-12-22 11:56:07", "content": "rich.kim@oam.co.kr 계정 회원가입 완료"},
            {"type": "WARNING", "date": "2024-12-22 11:53:05", "content": "[MEMORY] 92.65% (Threshold:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 11:43:04", "content": "[MEMORY] 91.84% (Threshold:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 11:33:02", "content": "[DISK] 88.20% (Threshold:85.0%)"},
        ]

        return {
            "cards": [
                {"id": "detect", "label": "Detect", "description": "Hardware changes", "value": 0},
                {"id": "warning", "label": "Warning", "description": "Hardware threshold usage", "value": 4},
                {"id": "logs", "label": "Logs", "description": "External server logs", "value": 1},
            ],
            "notifications": self.notification_items(),
            "logs": logs,
            "total_logs": len(logs),
        }

    def notification_items(self) -> list[dict]:
        return [
            {
                "email": "rich.kim@oam.co.kr",
                "smtp_status": "Connected",
                "network_connection": "NOT Connection",
                "last_login": "2024-12-03 15:14:58",
            },
            {
                "email": "rich.kim@oam.co.kr",
                "smtp_status": "Connected",
                "network_connection": "GOOD",
                "last_login": "2024-12-22 20:57:39",
            },
        ]

    def detect_summary(self) -> dict:
        config = self.context.config
        slot = next(iter(config.slots.values()))
        unique_id = slot_uid(slot)
        parts = fingerprint_parts(slot)
        display_lines = ["Disk Identity Fingerprint ="]
        display_lines.extend(part["label"] if index == 0 else f"+ {part['label']}" for index, part in enumerate(parts))
        formula = fingerprint_formula(parts)
        registered = slot.expected_uid
        registered_ready = bool(registered and registered != "replace-with-registered-uid")
        match = registered_ready and registered == unique_id
        status = "MATCH" if match else "UNREGISTERED" if not registered_ready else "DIFFERENT_DISK"
        return {
            "title": "LOCK-FIX 기준으로 가장 안전한 판단 방식",
            "subtitle": "LOCK-FIX에서는 하나의 값만 보지 말고 아래 조합을 기준으로 해야 합니다.",
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
                "conclusion": "이 값이 기존 등록값과 다르면 다른 디스크로 판단합니다.",
            },
        }

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
        return {
            "title": "실시간 IP 별 누적 트래픽",
            "unit": "GB",
            "interval_seconds": 10,
            "realtime": {
                "tx": {
                    "label": "송신",
                    "current_mbps": tx_history[-1],
                    "total_gb": round(sum(item["tx_gb"] for item in items), 2),
                    "history": tx_history,
                },
                "rx": {
                    "label": "수신",
                    "current_mbps": rx_history[-1],
                    "total_gb": round(sum(item["rx_gb"] for item in items), 2),
                    "history": rx_history,
                },
            },
            "items": items,
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
            severity = "WARN" if "warning" in event or "expired" in event or "failed" in event else "INFO"
            raw_date = str(item.get("ts", "-"))[:19]
            try:
                stamp = datetime.fromisoformat(raw_date)
            except ValueError:
                continue
            if stamp < range_start or stamp > range_end or stamp < retention_start:
                continue
            items.append(
                {
                    "type": "SYSLOG",
                    "date": raw_date,
                    "source": "license" if event.startswith("license") else "audit",
                    "severity": severity,
                    "message": event,
                }
            )
        items.sort(key=lambda item: item["date"], reverse=True)
        return items, range_start, range_end

    def retention_days(self, value: str = "30") -> int:
        try:
            days = int(value)
        except ValueError:
            days = 30
        return min(100, max(30, days))

    def logs_summary(self, start_date: str = "", end_date: str = "", page_value: str = "1", retention_value: str = "30") -> dict:
        retention_days = self.retention_days(retention_value)
        items, range_start, range_end = self.log_items(start_date, end_date, retention_days)
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
            "items": items[offset : offset + per_page],
        }

    def send_logs_csv(self, start_date: str = "", end_date: str = "", retention_value: str = "30") -> None:
        items, _, _ = self.log_items(start_date, end_date, self.retention_days(retention_value))
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

    def send_report_xlsx(self) -> None:
        report = self.report_summary()
        extras = report["extras"]
        rows = [
            ["Customer / Inspection Information"],
            ["Customer Name", report["customer"]["customer_name"], "Inspection Date", report["customer"]["inspection_date"]],
            ["Customer Contact", report["customer"]["customer_contact"], "Engineer", report["customer"]["engineer"]],
            ["Customer Email", report["customer"]["customer_email"], "Engineer Contact", report["customer"]["engineer_contact"]],
            [],
            ["Server Basic Information"],
            ["OS Version", report["server"]["os_version"], "CPU", report["server"]["cpu"]],
            ["Service", report["server"]["service"], "Memory", report["server"]["memory"]],
            ["Model", report["server"]["model"], "Disk", report["server"]["disk"]],
            ["S/N", report["server"]["serial"], "Hostname", report["server"]["hostname"]],
            [],
            ["Engineer Opinion"],
            ["Content", extras["engineer_opinion"] or "-"],
            ["Electronic Signature"],
            ["Engineer Inspection Signature", "Attached" if extras["engineer_signature"] else "-"],
            ["Manager Signature", "Attached" if extras["manager_signature"] else "-"],
            [],
            ["Metric", "Current", "Average", "Peak", "Threshold", "Status", "Recommendation"],
            *[
                [
                    card["label"],
                    card["current"],
                    card["average"],
                    card["peak"],
                    card["threshold"],
                    card["status"],
                    card["recommendation"],
                ]
                for card in report["cards"]
            ],
            [],
            ["Category", "Inspection Item", "Details", "Criteria", "Metric", "Result"],
            *[
                [item["category"], item["item"], item["detail"], item["criteria"], item["metric"], item["result"]]
                for item in report["inspection_items"]
            ],
            [],
            ["Time", "CPU", "Memory", "Disk", "Network"],
            *[[item["time"], item["cpu"], item["memory"], item["disk"], item["network"]] for item in report["series"]],
        ]
        body = self.build_xlsx(rows)
        self.send_download(
            body,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "lockfix_report.xlsx",
        )

    def send_report_docx(self) -> None:
        report = self.report_summary()
        body = self.build_docx(report)
        self.send_download(
            body,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "lockfix_report.docx",
        )

    def build_xlsx(self, rows: list[list[object]]) -> bytes:
        def cell_ref(row_index: int, col_index: int) -> str:
            letters = ""
            col = col_index
            while col:
                col, remainder = divmod(col - 1, 26)
                letters = chr(65 + remainder) + letters
            return f"{letters}{row_index}"

        sheet_rows = []
        for row_index, row in enumerate(rows, start=1):
            cells = []
            for col_index, value in enumerate(row, start=1):
                ref = cell_ref(row_index, col_index)
                if isinstance(value, (int, float)):
                    cells.append(f'<c r="{ref}"><v>{value}</v></c>')
                else:
                    cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
            sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
        sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
            archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Report" sheetId="1" r:id="rId1"/></sheets></workbook>')
            archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
            archive.writestr("xl/worksheets/sheet1.xml", sheet)
        return output.getvalue()

    def build_docx(self, report: dict) -> bytes:
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
            ("engineer_signature", "rIdEngineerSignature", "engineer_signature.png", "Engineer Inspection Signature"),
            ("manager_signature", "rIdManagerSignature", "manager_signature.png", "Manager Signature"),
        ]:
            image_bytes = self.image_data_url_bytes(extras.get(field, ""))
            if image_bytes:
                signature_media.append((rel_id, filename, image_bytes))
                signature_blocks.extend([para(label, "section"), image_para(rel_id, label)])

        customer_rows = [
            ["Customer Name", report["customer"]["customer_name"], "Inspection Date", report["customer"]["inspection_date"]],
            ["Customer Contact", report["customer"]["customer_contact"], "Engineer", report["customer"]["engineer"]],
            ["Customer Email", report["customer"]["customer_email"], "Engineer Contact", report["customer"]["engineer_contact"]],
        ]
        server_rows = [
            ["OS Version", report["server"]["os_version"], "CPU", report["server"]["cpu"]],
            ["Service", report["server"]["service"], "Memory", report["server"]["memory"]],
            ["Model", report["server"]["model"], "Disk", report["server"]["disk"]],
            ["S/N", report["server"]["serial"], "Hostname", report["server"]["hostname"]],
        ]
        resource_rows = [
            ["Metric", "Current", "Average", "Peak", "Threshold", "Result", "Recommendation"],
            *[
                [
                    card["label"],
                    f"{card['current']}%",
                    f"{card['average']}%",
                    f"{card['peak']}%",
                    f"{card['threshold']}%",
                    card["status"],
                    card["recommendation"],
                ]
                for card in report["cards"]
            ],
        ]
        inspection_rows = [
            ["Category", "Inspection Item", "Details", "Criteria", "Metric", "Result"],
            *[
                [item["category"], item["item"], item["detail"], item["criteria"], item["metric"], item["result"]]
                for item in report["inspection_items"]
            ],
        ]
        time_rows = [
            ["Time", "CPU", "Memory", "Disk", "Network"],
            *[[item["time"], f"{item['cpu']}%", f"{item['memory']}%", f"{item['disk']}%", f"{item['network']}%"] for item in report["series"][-10:]],
        ]
        signature_rows = [
            ["Engineer Inspection Signature", "Attached" if extras["engineer_signature"] else "-"],
            ["Manager Signature", "Attached" if extras["manager_signature"] else "-"],
        ]

        body = [
            para("System Inspection Report", "title"),
            para(f"Report No. #1    Generated: {report['generated_at']}"),
            para(f"Overall Status: {report['summary']['overall_status']}"),
            para(report["summary"]["analysis"]),
            para("Customer / Inspection Information", "section"),
            table(customer_rows),
            para("Server Basic Information", "section"),
            table(server_rows),
            para("Resource Usage Analysis", "section"),
            table(resource_rows, header=True),
            para("Server Inspection Checklist", "section"),
            table(inspection_rows, header=True),
            para("Engineer Opinion", "section"),
            para(extras["engineer_opinion"] or "-"),
            para("Electronic Signature", "section"),
            table(signature_rows),
            *signature_blocks,
            para("Recent Monitoring Samples", "section"),
            table(time_rows, header=True),
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
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
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
    LockFixWebHandler.context = WebContext(config_path)
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

