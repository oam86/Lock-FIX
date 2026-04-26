from __future__ import annotations

import json
import io
import mimetypes
import platform
import secrets
import shutil
import hashlib
import socket
import time
import uuid
import zipfile
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from xml.sax.saxutils import escape

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.identity import slot_uid
from lockfix.integrated import integrated_solution_summary
from lockfix.source_inventory import integrated_source_inventory


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "web" / "static"
DEFAULT_CONFIG = ROOT / "config" / "lockfix.example.json"


class WebContext:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.sessions = {}
        self.qr_tokens = {}
        self.license_path = ROOT / "runtime" / "license.json"

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
                self.send_json(self.monitoring_summary())
            elif parsed.path == "/api/monitoring.csv":
                self.require_auth()
                self.send_monitoring_csv()
            elif parsed.path == "/api/report":
                self.require_auth()
                self.send_json(self.report_summary())
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
            elif parsed.path == "/api/logs":
                self.require_auth()
                self.send_json(self.logs_summary())
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
                if secrets.compare_digest(email, "admin") and secrets.compare_digest(password, "backup@1234"):
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

    def air_gap_summary(self) -> dict:
        summary = self.summary()
        tick = int(time.time() / 5)
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
            "timeline": [
                {"step": 1, "title": "Veeam backup completion signal received", "state": "DONE"},
                {"step": 2, "title": "Drive hard power-off executed", "state": "DONE"},
                {"step": 3, "title": "Solenoid lock engaged", "state": "DONE"},
                {"step": 4, "title": "Air-Gap isolation active", "state": "ACTIVE"},
            ],
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
        }

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
        path = self.context.config.audit_log_path
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        items = []
        for line in lines[-200:]:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                items.append({"event": "parse_error", "raw": line})
        return list(reversed(items))

    def monitoring_summary(self) -> dict:
        points = []
        now = datetime.now()
        tick = int(time.time() / 5)
        for index in range(30):
            stamp = now - timedelta(minutes=(29 - index) * 10)
            phase = index + tick
            cpu = 12 + ((phase * 7) % 21) + (8 if phase % 11 in (1, 2) else 0)
            memory = 91.6 + ((phase % 7) * 0.22)
            disk = 14.0 + ((phase % 6) * 0.18)
            network = 18 + ((phase * 9) % 39) + (10 if phase % 13 == 0 else 0)
            points.append(
                {
                    "time": stamp.strftime("%Y.%m.%d %H:%M"),
                    "label": stamp.strftime("%m.%d %H:%M"),
                    "cpu": round(cpu, 1),
                    "memory": round(memory, 1),
                    "disk": round(disk, 1),
                    "network": round(network, 1),
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
            },
        }

    def report_summary(self) -> dict:
        monitoring = self.monitoring_summary()
        series = monitoring["series"]
        metrics = [
            ("cpu", "CPU", 80),
            ("memory", "Memory", 80),
            ("disk", "Disk", 85),
            ("network", "Network", 75),
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
                "customer_contact": "-",
                "engineer": "OAM Lock-FIX",
                "customer_email": "-",
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
            {"type": "WARNING", "date": "2024-12-22 12:03:06", "content": "[MEMORY] 92.75% (?꾧퀎:80.0%)"},
            {"type": "LOGS", "date": "2024-12-22 11:56:07", "content": "rich.kim@oam.co.kr 계정 회원가입 완료"},
            {"type": "WARNING", "date": "2024-12-22 11:53:05", "content": "[MEMORY] 92.65% (?꾧퀎:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 11:43:04", "content": "[MEMORY] 91.84% (?꾧퀎:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 11:33:02", "content": "[DISK] 88.20% (?꾧퀎:85.0%)"},
        ]

        return {
            "cards": [
                {"id": "detect", "label": "Detect", "description": "?섎뱶?⑥뼱??蹂寃?異붽?,", "value": 0},
                {"id": "warning", "label": "Warning", "description": "?섎뱶?⑥뼱??珥덇낵 ?ъ슜", "value": 4},
                {"id": "logs", "label": "Logs", "description": "?댁쇅???쒕쾭 濡쒓렇", "value": 1},
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
        warning_items = [
            {"date": "2024-12-22 13:30", "event": "[MEMORY] 93.25% (임계:80%)"},
            {"date": "2024-12-22 13:20", "event": "[MEMORY] 92.65% (임계:80%)"},
            {"date": "2024-12-22 13:10", "event": "[MEMORY] 92.75% (임계:80%)"},
            {"date": "2024-12-22 13:05", "event": "[MEMORY] 92.90% (임계:80%)"},
            {"date": "2024-12-22 13:03", "event": "[MEMORY] 92.62% (임계:80%)"},
            {"date": "2024-12-22 13:03", "event": "[MEMORY] 92.62% (임계:80%)"},
            {"date": "2024-12-22 13:03", "event": "[MEMORY] 92.68% (임계:80%)"},
        ]
        log_items = [
            {"date": "2024-12-20 56:07", "event": "rich.kim@oam.co.kr 계정 회원가입 완료"},
        ]
        return {
            "range": {"start": "2024-12-22", "end": "2024-12-22"},
            "cards": [
                {"id": "detect", "label": "Detect", "description": "하드웨어의 변경(추가,", "value": 0},
                {"id": "warning", "label": "Warning", "description": "하드웨어의 초과 사용", "value": len(warning_items)},
                {"id": "logs", "label": "Logs", "description": "이외의 서버 로그", "value": len(log_items)},
            ],
            "detect": [],
            "warning": warning_items,
            "logs": log_items,
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

    def logs_summary(self) -> dict:
        items = [
            {"type": "WARNING", "date": "2024-12-22 13:03:13", "source": "performance", "severity": "WARN", "message": "[MEMORY] 92.5625% (임계:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 12:53:12", "source": "performance", "severity": "WARN", "message": "[MEMORY] 92.4375% (임계:80.0%)"},
            {"type": "DETECT", "date": "2024-12-22 12:43:11", "source": "hardware", "severity": "INFO", "message": "[NIC] eth0 link status verified"},
            {"type": "SYSLOG", "date": "2024-12-22 12:38:44", "source": "kernel", "severity": "INFO", "message": "usb-storage: device scan completed"},
            {"type": "SYSLOG", "date": "2024-12-22 12:34:22", "source": "systemd", "severity": "INFO", "message": "lockfix-monitor.service heartbeat ok"},
            {"type": "SYSLOG", "date": "2024-12-22 12:31:08", "source": "sshd", "severity": "NOTICE", "message": "accepted publickey for oam from management network"},
            {"type": "WARNING", "date": "2024-12-22 12:23:10", "source": "performance", "severity": "WARN", "message": "[MEMORY] 93.25% (임계:80.0%)"},
            {"type": "LOGS", "date": "2024-12-22 11:56:07", "source": "account", "severity": "INFO", "message": "rich.kim@oam.co.kr 계정 회원가입 완료"},
            {"type": "SYSLOG", "date": "2024-12-22 11:54:02", "source": "network", "severity": "INFO", "message": "vmbr0 rx/tx counters updated"},
            {"type": "WARNING", "date": "2024-12-22 11:53:05", "source": "performance", "severity": "WARN", "message": "[MEMORY] 92.625% (임계:80.0%)"},
            {"type": "SYSLOG", "date": "2024-12-22 11:47:33", "source": "audit", "severity": "INFO", "message": "dashboard data export request completed"},
            {"type": "WARNING", "date": "2024-12-22 11:43:04", "source": "performance", "severity": "WARN", "message": "[MEMORY] 92.625% (임계:80.0%)"},
            {"type": "WARNING", "date": "2024-12-22 11:33:03", "source": "performance", "severity": "WARN", "message": "[MEMORY] 92.6875% (임계:80.0%)"},
        ]
        for item in self.audit_items()[:50]:
            event = str(item.get("event", "audit_event"))
            severity = "WARN" if "warning" in event or "expired" in event or "failed" in event else "INFO"
            items.insert(
                0,
                {
                    "type": "SYSLOG",
                    "date": str(item.get("ts", "-"))[:19],
                    "source": "license" if event.startswith("license") else "audit",
                    "severity": severity,
                    "message": event,
                },
            )
        return {
            "range": {"start": "2024-12-22", "end": "2024-12-22"},
            "total_logs": len(items),
            "items": items,
        }

    def send_monitoring_csv(self) -> None:
        data = self.monitoring_summary()
        rows = ["time,cpu_usage,memory_usage,disk_usage,network_usage"]
        for item in data["series"]:
            rows.append(f"{item['time']},{item['cpu']},{item['memory']},{item['disk']},{item['network']}")
        body = ("\n".join(rows) + "\n").encode("utf-8-sig")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=monitoring.csv")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def send_report_csv(self) -> None:
        report = self.report_summary()
        rows = ["section,item,value,item2,value2"]
        rows.append(f"customer,Customer Name,{report['customer']['customer_name']},Inspection Date,{report['customer']['inspection_date']}")
        rows.append(f"customer,Customer Contact,{report['customer']['customer_contact']},Engineer,{report['customer']['engineer']}")
        rows.append(f"server,OS Version,\"{report['server']['os_version']}\",CPU,{report['server']['cpu']}")
        rows.append(f"server,Service,\"{report['server']['service']}\",Memory,{report['server']['memory']}")
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
            para("Recent Monitoring Samples", "section"),
            table(time_rows, header=True),
        ]
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            + "".join(body)
            + '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="850" w:right="720" w:bottom="850" w:left="720" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>'
        )
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            archive.writestr("word/document.xml", document)
        return output.getvalue()

    def send_download(self, body: bytes, content_type: str, filename: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f"attachment; filename={filename}")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.wfile.write(body)

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
        self.wfile.write(data)

    def send_json(self, payload: dict, status: int = 200, headers=None) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)


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

