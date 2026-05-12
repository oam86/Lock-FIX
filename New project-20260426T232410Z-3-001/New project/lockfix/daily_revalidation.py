from __future__ import annotations

import argparse
import html
import json
import os
import platform
import smtplib
import ssl
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from .config import LockFixConfig, SlotConfig, load_config, read_install_properties
from .controller import LockFixController
from .veeam_diagnostics import run_veeam_diagnostics


ADMIN_ALERT_EMAIL = "rich.kim@oam.co.kr"
DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "lockfix.example.json"
BACKUP_SUCCESS_STATUSES = {"SUCCESS", "SUCCEEDED", "COMPLETED", "WARNING"}


@dataclass
class CheckResult:
    id: str
    name: str
    ok: bool
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_ok: bool | None = None
    recovery_message: str = ""


def run_daily_revalidation(
    config_path: Path = DEFAULT_CONFIG,
    report_dir: Path | None = None,
    json_log_dir: Path | None = None,
    recover: bool = True,
    email_to: str = ADMIN_ALERT_EMAIL,
    send_email_on_issue: bool = False,
) -> dict[str, Any]:
    prepare_runtime_environment(config_path)
    config = load_config(config_path)
    controller = LockFixController(config)
    now = datetime.now().astimezone()
    day = now.date()
    report_dir = report_dir or config_path.resolve().parent.parent / "reports"
    json_log_dir = json_log_dir or config.audit_log_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    json_log_dir.mkdir(parents=True, exist_ok=True)

    checks: list[CheckResult] = []
    diagnostics = safe_veeam_diagnostics(config, controller)
    checks.append(check_today_veeam_success(diagnostics, day))

    slot_results: dict[str, dict[str, Any]] = {}
    for slot_id, slot in config.slots.items():
        slot_report = validate_slot_state(config, controller, slot, recover=recover)
        slot_results[slot_id] = {
            **slot_report,
            "checks": [as_dict(item) for item in slot_report["checks"]],
        }
        checks.extend(slot_report["checks"])

    checks.append(check_log_anomalies(config.audit_log_path, day))

    overall_ok = all(item.ok for item in checks)
    summary = {
        "timestamp": now.isoformat(timespec="seconds"),
        "date": day.isoformat(),
        "overall_status": "OK" if overall_ok else "ISSUE_DETECTED",
        "recover_enabled": recover,
        "admin_alert_email": email_to,
        "veeam": summarize_veeam(diagnostics),
        "slots": slot_results,
        "checks": [as_dict(item) for item in checks],
    }

    json_path = json_log_dir / f"daily-revalidation-{day:%Y%m%d}.json"
    html_path = report_dir / f"daily-report-{day:%Y%m%d}.html"
    summary["json_log_path"] = str(json_path)
    summary["html_report_path"] = str(html_path)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(render_html_report(summary), encoding="utf-8")
    controller.audit.write(
        "daily.revalidation.completed",
        result=summary["overall_status"],
        report_path=str(html_path),
        json_log_path=str(json_path),
        issue_count=sum(1 for item in checks if not item.ok),
    )

    if send_email_on_issue and not overall_ok:
        summary["email"] = send_report_email(email_to, html_path, json_path, summary)
        json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    elif not overall_ok:
        summary["email"] = {
            "sent": False,
            "reason": "send_email_on_issue is disabled. Use scripts/send-lockfix-report.ps1 or set -SendOnIssue.",
            "to": email_to,
        }
    else:
        summary["email"] = {"sent": False, "reason": "no issue detected", "to": email_to}
    return summary


def prepare_runtime_environment(config_path: Path) -> None:
    root = config_path.resolve().parent.parent
    props = read_install_properties(root)
    mappings = {
        "LOCKFIX_VEEAM_BASE_URL": "veeam_base_url",
        "LOCKFIX_VEEAM_API_VERSION": "veeam_api_version",
        "LOCKFIX_VEEAM_USER": "veeam_user",
        "LOCKFIX_VEEAM_PASSWORD": "veeam_password",
        "LOCKFIX_VEEAM_HOST": "veeam_host",
        "LOCKFIX_VEEAM_PORT": "veeam_port",
    }
    for env_name, prop_name in mappings.items():
        if not os.environ.get(env_name) and props.get(prop_name):
            os.environ[env_name] = str(props[prop_name])


def safe_veeam_diagnostics(config: LockFixConfig, controller: LockFixController) -> dict[str, Any]:
    try:
        return run_veeam_diagnostics(config, controller)
    except Exception as exc:
        controller.audit.write("daily.revalidation.veeam.error", error=str(exc))
        return {"error": str(exc), "latest_configured_session": {}, "isolate_condition": {}}


def check_today_veeam_success(diagnostics: dict[str, Any], day: date) -> CheckResult:
    latest = diagnostics.get("latest_configured_session") if isinstance(diagnostics.get("latest_configured_session"), dict) else {}
    status = str(latest.get("status") or latest.get("result") or latest.get("session_state") or "").upper()
    started = parse_datetime(latest.get("started_at") or latest.get("start_time") or latest.get("creationTime"))
    ended = parse_datetime(latest.get("ended_at") or latest.get("end_time") or latest.get("endTime"))
    evidence_time = ended or started
    is_today = evidence_time is not None and evidence_time.astimezone().date() == day
    ok = status in BACKUP_SUCCESS_STATUSES and is_today and bool(latest.get("api_synced", diagnostics.get("api_synced", True)))
    return CheckResult(
        id="veeam.today.success",
        name="오늘 Veeam 백업 Job Success 확인",
        ok=ok,
        status="PASS" if ok else "FAIL",
        message=(
            f"Veeam job {latest.get('name') or '-'} is {status}; evidence time {format_dt(evidence_time)}."
            if ok
            else f"오늘 Success/Warning 완료 백업 증거가 없습니다. status={status or '-'}, evidence={format_dt(evidence_time)}"
        ),
        details={
            "job_name": latest.get("name") or "",
            "status": status,
            "progress_percent": latest.get("progress_percent"),
            "started_at": latest.get("started_at"),
            "ended_at": latest.get("ended_at"),
            "session_id": latest.get("session_id"),
            "repository_name": latest.get("repository_name"),
            "repository_path": latest.get("repository_path"),
            "match_strategy": latest.get("backup_match_strategy") or (diagnostics.get("matching") or {}).get("strategy"),
        },
    )


def validate_slot_state(config: LockFixConfig, controller: LockFixController, slot: SlotConfig, recover: bool) -> dict[str, Any]:
    proof = collect_slot_storage_proof(config, controller, slot)
    checks = [
        CheckResult(
            id=f"{slot.slot_id}.disk.offline",
            name=f"{slot.slot_id} Repository Disk Offline 상태 확인",
            ok=bool(proof.get("disk_found")) and bool(proof.get("is_offline")),
            status="PASS" if proof.get("is_offline") else "FAIL",
            message=proof.get("offline_message", ""),
            details=proof,
        ),
        CheckResult(
            id=f"{slot.slot_id}.drive_letter.removed",
            name=f"{slot.slot_id} Drive Letter 제거 확인",
            ok=not bool(proof.get("drive_letter_present")) and not bool(proof.get("path_reachable")),
            status="PASS" if not proof.get("drive_letter_present") and not proof.get("path_reachable") else "FAIL",
            message=proof.get("drive_letter_message", ""),
            details=proof,
        ),
        CheckResult(
            id=f"{slot.slot_id}.mount_point.removed",
            name=f"{slot.slot_id} Volume Mount Point 제거 확인",
            ok=not bool(proof.get("mount_point_present")),
            status="PASS" if not proof.get("mount_point_present") else "FAIL",
            message=proof.get("mount_point_message", ""),
            details=proof,
        ),
    ]
    approval_active = controller.online_approval_active(slot.slot_id)
    checks.append(
        CheckResult(
            id=f"{slot.slot_id}.online.block.policy",
            name=f"{slot.slot_id} 관리자 승인 전 Online 차단 정책 확인",
            ok=not approval_active and not is_protected_drive(slot),
            status="PASS" if not approval_active else "WARN",
            message=(
                "Online approval window is closed; unauthorized online state will be reblocked."
                if not approval_active
                else "An administrator-approved online window is currently active."
            ),
            details={"online_approval_active": approval_active, "online_approvals_path": str(controller.online_approval_path)},
        )
    )

    if recover and any(not item.ok for item in checks[:3]) and not approval_active:
        recovery = attempt_storage_recovery(controller, slot)
        for item in checks[:3]:
            if not item.ok:
                item.recovery_attempted = True
                item.recovery_ok = recovery.get("ok")
                item.recovery_message = recovery.get("message", "")
        if recovery.get("ok"):
            proof = collect_slot_storage_proof(config, controller, slot)
            for item in checks[:3]:
                item.details = proof
            checks[0].ok = bool(proof.get("disk_found")) and bool(proof.get("is_offline"))
            checks[1].ok = not bool(proof.get("drive_letter_present")) and not bool(proof.get("path_reachable"))
            checks[2].ok = not bool(proof.get("mount_point_present"))
            for item in checks[:3]:
                item.status = "PASS" if item.ok else "FAIL"
    return {"slot_id": slot.slot_id, "proof": proof, "checks": checks}


def collect_slot_storage_proof(config: LockFixConfig, controller: LockFixController, slot: SlotConfig) -> dict[str, Any]:
    drive = controller.disk.windows_drive_letter(slot) if not config.dry_run else "X"
    state = controller.disk.read_storage_state(slot)
    if platform.system().lower() != "windows":
        return linux_storage_proof(slot, drive)
    if config.dry_run:
        return {
            "slot_id": slot.slot_id,
            "drive": drive,
            "disk_found": False,
            "is_offline": None,
            "offline_message": "dry_run mode cannot prove Windows disk offline state.",
            "drive_letter_present": False,
            "path_reachable": False,
            "mount_point_present": False,
            "storage_state": state,
        }
    script = windows_storage_proof_script(slot, drive, state)
    try:
        output = run_powershell(script)
        proof = json.loads(output.splitlines()[-1])
        proof["ok"] = True
    except Exception as exc:
        proof = {"ok": False, "error": str(exc), "slot_id": slot.slot_id, "drive": drive}
    proof.setdefault("slot_id", slot.slot_id)
    proof.setdefault("drive", drive)
    proof.setdefault("storage_state", state)
    proof["offline_message"] = (
        "Repository disk is offline."
        if proof.get("is_offline")
        else "Repository disk is not offline or could not be identified."
    )
    proof["drive_letter_message"] = (
        "Drive letter and access path are removed."
        if not proof.get("drive_letter_present") and not proof.get("path_reachable")
        else "Drive letter or access path is still visible."
    )
    proof["mount_point_message"] = (
        "Volume mount point is removed."
        if not proof.get("mount_point_present")
        else "Volume mount point is still present."
    )
    return proof


def windows_storage_proof_script(slot: SlotConfig, drive: str, state: dict[str, Any]) -> str:
    disk_number = ps_quote(str(state.get("diskNumber", "")))
    disk_unique_id = ps_quote(str(state.get("diskUniqueId", "")))
    partition_number = ps_quote(str(state.get("partitionNumber", "")))
    volume_path = ps_quote(str(state.get("volumePath") or state.get("volumeMountPath") or state.get("volumeName") or ""))
    access_path = ps_quote(str(state.get("accessPath") or f"{drive}:\\"))
    return f"""
$ErrorActionPreference = 'Stop'
$drive = '{ps_quote(drive)}'
if ($drive.ToUpper() -eq 'C') {{ throw 'C: drive is protected and cannot be validated as repository disk.' }}
$storedDiskNumber = '{disk_number}'
$storedDiskUniqueId = '{disk_unique_id}'
$storedPartitionNumber = '{partition_number}'
$storedVolumePath = '{volume_path}'
$accessPath = '{access_path}'
Update-HostStorageCache -ErrorAction SilentlyContinue
$disk = $null
if ($storedDiskNumber) {{ $disk = Get-Disk -Number ([UInt32]$storedDiskNumber) -ErrorAction SilentlyContinue }}
if (-not $disk -and $storedDiskUniqueId) {{
  $disk = Get-Disk -ErrorAction SilentlyContinue | Where-Object {{ [string]$_.UniqueId -eq $storedDiskUniqueId }} | Select-Object -First 1
}}
$partitionByDrive = Get-Partition -DriveLetter $drive -ErrorAction SilentlyContinue
if (-not $disk -and $partitionByDrive) {{ $disk = $partitionByDrive | Get-Disk -ErrorAction SilentlyContinue }}
$partitionByStored = $null
if ($disk -and $storedPartitionNumber) {{
  $partitionByStored = Get-Partition -DiskNumber $disk.Number -PartitionNumber ([UInt32]$storedPartitionNumber) -ErrorAction SilentlyContinue
}}
$volumeByDrive = Get-Volume -DriveLetter $drive -ErrorAction SilentlyContinue
$logicalDisk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$drive`:'" -ErrorAction SilentlyContinue
$win32Volume = Get-CimInstance Win32_Volume -Filter "DriveLetter='$drive`:'" -ErrorAction SilentlyContinue
$pathReachable = Test-Path $accessPath
$mountvolOutput = mountvol 2>&1 | Out-String
$mountPointPresent = $false
if ($accessPath) {{ $mountPointPresent = $mountvolOutput -match [regex]::Escape($accessPath) }}
if ($storedVolumePath) {{ $mountPointPresent = $mountPointPresent -or ($mountvolOutput -match [regex]::Escape($storedVolumePath)) }}
$proof = [ordered]@{{
  disk_found = [bool]($null -ne $disk)
  disk_number = if ($disk) {{ $disk.Number }} else {{ '' }}
  disk_serial = if ($disk) {{ $disk.SerialNumber }} else {{ '' }}
  disk_unique_id = if ($disk) {{ $disk.UniqueId }} else {{ $storedDiskUniqueId }}
  is_offline = if ($disk) {{ [bool]$disk.IsOffline }} else {{ $false }}
  is_boot = if ($disk) {{ [bool]$disk.IsBoot }} else {{ $false }}
  is_system = if ($disk) {{ [bool]$disk.IsSystem }} else {{ $false }}
  drive = $drive
  drive_letter_present = [bool]($null -ne $partitionByDrive -or $null -ne $volumeByDrive -or $null -ne $logicalDisk -or $null -ne $win32Volume -or $pathReachable)
  path_reachable = [bool]$pathReachable
  mount_point_present = [bool]$mountPointPresent
  logical_disk_present = [bool]($null -ne $logicalDisk)
  win32_volume_present = [bool]($null -ne $win32Volume)
  stored_disk_number = $storedDiskNumber
  stored_partition_number = $storedPartitionNumber
  stored_volume_path = $storedVolumePath
  access_path = $accessPath
}}
$proof | ConvertTo-Json -Compress
"""


def linux_storage_proof(slot: SlotConfig, drive: str) -> dict[str, Any]:
    mount_point = str(slot.mount_point)
    mounted = subprocess.run(["findmnt", "-n", mount_point], capture_output=True, text=True, check=False).returncode == 0
    return {
        "slot_id": slot.slot_id,
        "drive": drive,
        "disk_found": True,
        "is_offline": not mounted,
        "drive_letter_present": False,
        "path_reachable": Path(mount_point).exists(),
        "mount_point_present": mounted,
        "offline_message": "Linux mount point is not mounted." if not mounted else "Linux mount point is still mounted.",
        "drive_letter_message": "Drive letter is not applicable on Linux.",
        "mount_point_message": "Mount point removed." if not mounted else "Mount point still active.",
    }


def attempt_storage_recovery(controller: LockFixController, slot: SlotConfig) -> dict[str, Any]:
    try:
        controller.disk.unmount(slot)
        controller.disk.offline(slot)
        controller.audit.write("daily.revalidation.recovery.storage", slot_id=slot.slot_id, result="SUCCESS")
        return {"ok": True, "message": "Unmount and disk offline recovery completed."}
    except Exception as exc:
        controller.audit.write("daily.revalidation.recovery.storage.error", slot_id=slot.slot_id, error=str(exc))
        return {"ok": False, "message": str(exc)}


def check_log_anomalies(audit_path: Path, day: date) -> CheckResult:
    today_records = audit_records_for_day(audit_path, day)
    yesterday_records = audit_records_for_day(audit_path, day - timedelta(days=1))
    today_failed = failed_events(today_records)
    yesterday_failed = failed_events(yesterday_records)
    new_failed_actions = sorted({event_name(item) for item in today_failed} - {event_name(item) for item in yesterday_failed})
    anomaly = bool(new_failed_actions) or len(today_failed) > max(3, len(yesterday_failed) * 2)
    return CheckResult(
        id="audit.compare.today_yesterday",
        name="전날 로그와 오늘 로그 비교 이상 탐지",
        ok=not anomaly,
        status="PASS" if not anomaly else "WARN",
        message=(
            "No new abnormal audit pattern detected."
            if not anomaly
            else f"New or increased failed audit events detected: {', '.join(new_failed_actions[:8]) or len(today_failed)}"
        ),
        details={
            "today_count": len(today_records),
            "yesterday_count": len(yesterday_records),
            "today_failed_count": len(today_failed),
            "yesterday_failed_count": len(yesterday_failed),
            "new_failed_actions": new_failed_actions,
        },
    )


def audit_records_for_day(path: Path, day: date) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = parse_datetime(record.get("createdAt") or record.get("ts"))
        if ts and ts.astimezone().date() == day:
            records.append(record)
    return records


def failed_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    for record in records:
        text = " ".join(str(record.get(key) or "") for key in ("event", "action", "result", "error", "message")).lower()
        if any(token in text for token in ("failed", "fail", "error", "denied", "blocked", "unauthorized", "quarantine")):
            failed.append(record)
    return failed


def event_name(record: dict[str, Any]) -> str:
    return str(record.get("event") or record.get("action") or "unknown")


def render_html_report(summary: dict[str, Any]) -> str:
    rows = []
    for check in summary["checks"]:
        css = "ok" if check["ok"] else "bad"
        rows.append(
            f"<tr class='{css}'><td>{esc(check['name'])}</td><td>{esc(check['status'])}</td>"
            f"<td>{esc(check['message'])}</td><td>{esc(check.get('recovery_message') or '-')}</td></tr>"
        )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>LOCK-FIX Daily Revalidation Report {esc(summary['date'])}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #102033; }}
    h1 {{ font-size: 22px; margin-bottom: 4px; }}
    .meta {{ color: #53657a; margin-bottom: 18px; }}
    .status {{ display: inline-block; padding: 6px 10px; border-radius: 4px; font-weight: 700; }}
    .OK {{ background: #e7f7ef; color: #087545; }}
    .ISSUE_DETECTED {{ background: #fff0e6; color: #b35300; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 14px; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f4f8fb; }}
    tr.ok td:first-child {{ border-left: 4px solid #18a058; }}
    tr.bad td:first-child {{ border-left: 4px solid #d93025; }}
    pre {{ background: #f7fafc; border: 1px solid #d9e2ec; padding: 10px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>LOCK-FIX Daily Revalidation Report</h1>
  <div class="meta">Generated: {esc(summary['timestamp'])} / Date: {esc(summary['date'])}</div>
  <div class="status {esc(summary['overall_status'])}">{esc(summary['overall_status'])}</div>
  <h2>Validation Checks</h2>
  <table>
    <thead><tr><th>Check</th><th>Status</th><th>Message</th><th>Recovery</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <h2>Veeam Evidence</h2>
  <pre>{esc(json.dumps(summary.get('veeam', {}), ensure_ascii=False, indent=2))}</pre>
  <h2>Slot Evidence</h2>
  <pre>{esc(json.dumps(summary.get('slots', {}), ensure_ascii=False, indent=2, default=str))}</pre>
</body>
</html>
"""


def send_report_email(to_addr: str, html_path: Path, json_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    smtp_host = os.environ.get("LOCKFIX_SMTP_HOST") or os.environ.get("SMTP_HOST") or ""
    smtp_port = int(os.environ.get("LOCKFIX_SMTP_PORT") or os.environ.get("SMTP_PORT") or "25")
    smtp_user = os.environ.get("LOCKFIX_SMTP_USER") or os.environ.get("SMTP_USER") or ""
    smtp_password = os.environ.get("LOCKFIX_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or ""
    sender = os.environ.get("LOCKFIX_SMTP_FROM") or smtp_user or "lockfix@localhost"
    use_ssl = str(os.environ.get("LOCKFIX_SMTP_SSL") or "").lower() in {"1", "true", "yes", "on"}
    use_tls = str(os.environ.get("LOCKFIX_SMTP_TLS") or "true").lower() in {"1", "true", "yes", "on"}
    if not smtp_host:
        return {"sent": False, "to": to_addr, "reason": "LOCKFIX_SMTP_HOST is not configured."}
    message = EmailMessage()
    message["Subject"] = f"[LOCK-FIX] Daily Revalidation {summary['overall_status']} {summary['date']}"
    message["From"] = sender
    message["To"] = to_addr
    message.set_content(f"LOCK-FIX daily revalidation result: {summary['overall_status']}\nReport: {html_path}\nJSON: {json_path}\n")
    message.add_alternative(html_path.read_text(encoding="utf-8"), subtype="html")
    message.add_attachment(json_path.read_bytes(), maintype="application", subtype="json", filename=json_path.name)
    context = ssl.create_default_context()
    try:
        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20, context=context) as server:
                if smtp_user or smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if use_tls:
                    server.starttls(context=context)
                if smtp_user or smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(message)
    except Exception as exc:
        return {"sent": False, "to": to_addr, "reason": str(exc)}
    return {"sent": True, "to": to_addr, "smtp_host": smtp_host}


def summarize_veeam(diagnostics: dict[str, Any]) -> dict[str, Any]:
    latest = diagnostics.get("latest_configured_session") if isinstance(diagnostics.get("latest_configured_session"), dict) else {}
    return {
        "api_synced": latest.get("api_synced"),
        "name": latest.get("name"),
        "status": latest.get("status"),
        "session_state": latest.get("session_state"),
        "progress_percent": latest.get("progress_percent"),
        "started_at": latest.get("started_at"),
        "ended_at": latest.get("ended_at"),
        "session_id": latest.get("session_id"),
        "repository_name": latest.get("repository_name"),
        "repository_path": latest.get("repository_path"),
        "matching": diagnostics.get("matching"),
        "isolate_condition": diagnostics.get("isolate_condition"),
    }


def as_dict(item: CheckResult) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "ok": item.ok,
        "status": item.status,
        "message": item.message,
        "details": item.details,
        "recovery_attempted": item.recovery_attempted,
        "recovery_ok": item.recovery_ok,
        "recovery_message": item.recovery_message,
    }


def run_powershell(script: str) -> str:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "").strip())
    return (result.stdout or "").strip()


def parse_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text or text == "-":
        return None
    candidates = [text, text.replace("Z", "+00:00")]
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            return parsed if parsed.tzinfo else parsed.astimezone()
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y.%m.%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            parsed = datetime.strptime(text[:19], fmt)
            return parsed.astimezone()
        except ValueError:
            pass
    return None


def format_dt(value: datetime | None) -> str:
    return value.astimezone().isoformat(timespec="seconds") if value else "-"


def is_protected_drive(slot: SlotConfig) -> bool:
    for raw in (str(slot.mount_point), slot.device):
        normalized = raw.strip().replace("/", "\\").rstrip("\\").lower()
        if normalized in {"c:", "c"}:
            return True
    return False


def ps_quote(value: str) -> str:
    return str(value).replace("'", "''")


def esc(value: Any) -> str:
    return html.escape(str(value or ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LOCK-FIX daily revalidation checks.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--report-dir", type=Path, default=None)
    parser.add_argument("--json-log-dir", type=Path, default=None)
    parser.add_argument("--no-recover", action="store_true")
    parser.add_argument("--send-on-issue", action="store_true")
    parser.add_argument("--email-to", default=ADMIN_ALERT_EMAIL)
    args = parser.parse_args()
    summary = run_daily_revalidation(
        config_path=args.config,
        report_dir=args.report_dir,
        json_log_dir=args.json_log_dir,
        recover=not args.no_recover,
        email_to=args.email_to,
        send_email_on_issue=args.send_on_issue,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["overall_status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
