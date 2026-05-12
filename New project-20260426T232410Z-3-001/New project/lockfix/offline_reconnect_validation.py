from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import SlotConfig, load_config
from .controller import LockFixController
from .daily_revalidation import DEFAULT_CONFIG, as_dict, collect_slot_storage_proof, safe_veeam_diagnostics


def run_offline_reconnect_validation(
    config_path: Path = DEFAULT_CONFIG,
    report_dir: Path | None = None,
    json_log_dir: Path | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    controller = LockFixController(config)
    now = datetime.now().astimezone()
    report_dir = report_dir or config_path.resolve().parent.parent / "reports"
    json_log_dir = json_log_dir or config.audit_log_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    json_log_dir.mkdir(parents=True, exist_ok=True)

    diagnostics = safe_veeam_diagnostics(config, controller)
    slot_results = {}
    findings: list[dict[str, Any]] = []

    for slot_id, slot in config.slots.items():
        proof = collect_slot_storage_proof(config, controller, slot)
        emergency_checks = emergency_reconnect_checks(controller, slot, proof)
        reconnect_checks = reconnect_completion_checks(controller, slot)
        portability_checks = agent_portability_checks(slot)
        slot_findings = emergency_checks + reconnect_checks + portability_checks
        slot_results[slot_id] = {
            "slot_id": slot_id,
            "repository_path": str(slot.mount_point),
            "drive_letter": getattr(slot, "drive_letter", "") or "",
            "offline_proof": proof,
            "checks": slot_findings,
        }
        findings.extend(slot_findings)

    overall_ok = all(item["ok"] for item in findings)
    summary = {
        "timestamp": now.isoformat(timespec="seconds"),
        "overall_status": "OK" if overall_ok else "ISSUE_DETECTED",
        "purpose": "3-hour offline and emergency reconnect validation",
        "veeam": diagnostics.get("latest_configured_session", {}),
        "slots": slot_results,
        "findings": findings,
    }

    stamp = now.strftime("%Y%m%d-%H%M%S")
    json_path = json_log_dir / f"offline-reconnect-validation-{stamp}.json"
    html_path = report_dir / f"offline-reconnect-report-{stamp}.html"
    summary["json_log_path"] = str(json_path)
    summary["html_report_path"] = str(html_path)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(render_offline_reconnect_report(summary), encoding="utf-8")
    controller.audit.write(
        "offline.reconnect.validation.completed",
        result=summary["overall_status"],
        report_path=str(html_path),
        json_log_path=str(json_path),
        issue_count=sum(1 for item in findings if not item["ok"]),
    )
    return summary


def emergency_reconnect_checks(controller: LockFixController, slot: SlotConfig, proof: dict[str, Any]) -> list[dict[str, Any]]:
    approval_active = controller.online_approval_active(slot.slot_id)
    disk_offline_or_equivalent = bool(proof.get("is_offline")) or bool(proof.get("offline_equivalent"))
    path_blocked = not bool(proof.get("drive_letter_present")) and not bool(proof.get("path_reachable"))
    return [
        finding(
            "offline.proof",
            "Offline proof",
            disk_offline_or_equivalent,
            "Repository disk is offline or offline-equivalent proof is recorded."
            if disk_offline_or_equivalent
            else "Repository disk is not proven offline.",
            proof,
        ),
        finding(
            "drive.path.blocked",
            "Drive letter and path blocked",
            path_blocked,
            "Drive letter/access path is unavailable."
            if path_blocked
            else "Drive letter or repository path is still reachable.",
            proof,
        ),
        finding(
            "emergency.approval.gate",
            "Emergency reconnect approval gate",
            not approval_active,
            "No active online approval window; emergency reconnect remains blocked until approved."
            if not approval_active
            else "An approved online window is active. Confirm this is expected.",
            {"online_approval_active": approval_active},
            severity="WARN" if approval_active else "INFO",
        ),
    ]


def reconnect_completion_checks(controller: LockFixController, slot: SlotConfig) -> list[dict[str, Any]]:
    approval_active = controller.online_approval_active(slot.slot_id)
    drive = ""
    try:
        drive = controller.disk.windows_drive_letter(slot)
    except Exception:
        drive = str(slot.mount_point)[:1].replace(":", "").upper()

    if not approval_active:
        return [
            finding(
                "reconnect.blocked.until.approved",
                "Reconnect blocked until approval",
                True,
                "No approved online window is active. LOCK-FIX will not run reconnect verification or remount attempts.",
                {"online_approval_active": False, "drive_letter": drive},
            )
        ]

    try:
        controller.disk.verify_drive_accessible(slot, drive)
    except Exception as exc:
        controller.audit.write(
            "offline.reconnect.validation.reconnect.verify.error",
            slot_id=slot.slot_id,
            drive_letter=drive,
            error=str(exc),
        )
        return [
            finding(
                "reconnect.mount.restored",
                "Reconnect mount restored",
                False,
                "Approved online window is active, but the original volume mount/access path is not verified.",
                {"online_approval_active": True, "drive_letter": drive, "error": str(exc)},
            )
        ]

    controller.audit.write(
        "offline.reconnect.validation.reconnect.verify",
        slot_id=slot.slot_id,
        drive_letter=drive,
        result="SUCCESS",
        message="Approved reconnect window is active and repository volume access is verified.",
    )
    return [
        finding(
            "reconnect.mount.restored",
            "Reconnect mount restored",
            True,
            "Approved online window is active and the original mount/access path is reachable.",
            {"online_approval_active": True, "drive_letter": drive},
        )
    ]


def agent_portability_checks(slot: SlotConfig) -> list[dict[str, Any]]:
    repository_path = str(slot.mount_point)
    os_type = str(getattr(slot, "os_type", "") or ("windows" if ":\\" in repository_path else "linux")).lower()
    drive_letter = str(getattr(slot, "drive_letter", "") or repository_path[:1]).replace(":", "").upper()
    repository_path = str(slot.mount_point)
    checks = [
        finding(
            "agent.os.backend",
            "Agent OS backend selection",
            os_type in {"windows", "linux"},
            "WindowsDiskOps or LinuxDiskOps can be selected for this slot."
            if os_type in {"windows", "linux"}
            else "Slot os_type must be windows or linux for agent portability.",
            {"os_type": os_type},
        )
    ]
    if os_type == "windows":
        checks.extend([
            finding(
                "agent.windows.drive",
                "Windows drive target",
                bool(drive_letter) and drive_letter != "C",
                "Windows repository drive is configured and is not C:."
                if drive_letter and drive_letter != "C"
                else "Windows repository drive_letter is missing or points to protected C:.",
                {"drive_letter": drive_letter},
            ),
            finding(
                "agent.windows.repository",
                "Windows repository path",
                ":\\" in repository_path,
                "Repository path uses a Windows drive path.",
                {"repository_path": repository_path},
            ),
            finding(
                "agent.disk.identity",
                "Expected disk identity",
                bool(slot.identity.get("serial") or getattr(slot, "expected_disk_serial", "") or getattr(slot, "device", "")),
                "Disk identity is configured for cross-server validation.",
                {
                    "expected_disk_serial": getattr(slot, "expected_disk_serial", "") or slot.identity.get("serial", ""),
                    "device": getattr(slot, "device", ""),
                },
            ),
        ])
    return checks


def finding(
    check_id: str,
    name: str,
    ok: bool,
    message: str,
    details: dict[str, Any] | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "name": name,
        "ok": bool(ok),
        "status": "PASS" if ok else "FAIL",
        "severity": severity or ("INFO" if ok else "ERROR"),
        "message": message,
        "details": details or {},
    }


def render_offline_reconnect_report(summary: dict[str, Any]) -> str:
    rows = []
    for item in summary.get("findings", []):
        status = "PASS" if item.get("ok") else "FAIL"
        rows.append(
            "<tr>"
            f"<td>{html.escape(item.get('id', '-'))}</td>"
            f"<td>{html.escape(item.get('name', '-'))}</td>"
            f"<td class='{status.lower()}'>{status}</td>"
            f"<td>{html.escape(item.get('message', '-'))}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>LOCK-FIX Offline Reconnect Validation</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; color: #102235; margin: 32px; }}
    h1 {{ margin-bottom: 4px; }}
    .status {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: #eef6ff; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 22px; }}
    th, td {{ border: 1px solid #dbe6f1; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f5f8fb; }}
    .pass {{ color: #047857; font-weight: 800; }}
    .fail {{ color: #b42318; font-weight: 800; }}
  </style>
</head>
<body>
  <h1>LOCK-FIX Offline / Emergency Reconnect Validation</h1>
  <p>{html.escape(summary.get("timestamp", "-"))}</p>
  <p class="status">{html.escape(summary.get("overall_status", "-"))}</p>
  <table>
    <thead><tr><th>Check</th><th>Name</th><th>Status</th><th>Message</th></tr></thead>
    <tbody>{''.join(rows) or '<tr><td colspan="4">No checks.</td></tr>'}</tbody>
  </table>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LOCK-FIX offline/emergency reconnect validation.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--report-dir", type=Path, default=None)
    parser.add_argument("--json-log-dir", type=Path, default=None)
    args = parser.parse_args()
    summary = run_offline_reconnect_validation(args.config, args.report_dir, args.json_log_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["overall_status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
