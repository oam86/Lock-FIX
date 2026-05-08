from __future__ import annotations

import argparse
import json
from pathlib import Path

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.identity import slot_uid
from lockfix.veeam_client import (
    VeeamClient,
    VeeamSettings,
    is_success_status,
    match_sessions,
    normalized_job_id,
    session_id,
    session_job_id,
    session_name,
    session_status,
)
from lockfix.veeam_watcher import VeeamWatcher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lockfixctl")
    parser.add_argument("--config", default="config/lockfix.example.json")
    command_parent = argparse.ArgumentParser(add_help=False)
    command_parent.add_argument("--config", default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("isolate", "reconnect", "uid"):
        command = subparsers.add_parser(name, parents=[command_parent])
        command.add_argument("--slot", required=True)

    subparsers.add_parser("status", parents=[command_parent])
    subparsers.add_parser("veeam-test", parents=[command_parent])
    veeam_watch = subparsers.add_parser("veeam-watch", parents=[command_parent])
    veeam_watch.add_argument("--slot", default="")
    veeam_watch.add_argument("--once", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    controller = LockFixController(config)

    if args.command == "isolate":
        state = controller.isolate(args.slot)
        print(state.value)
        return 0
    if args.command == "reconnect":
        state = controller.reconnect(args.slot)
        print(state.value)
        return 0
    if args.command == "uid":
        print(slot_uid(config.slot(args.slot)))
        return 0
    if args.command == "status":
        print(json.dumps(controller.status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "veeam-test":
        settings = VeeamSettings.from_config(config.veeam)
        client = VeeamClient(settings)
        watcher = VeeamWatcher(config, controller)
        result = {
            "enabled": config.veeam.enabled,
            "vbr_rest_9419": {
                "required": True,
                "api_base": settings.api_base,
                "token_url": settings.token_url,
                "port": client.check_port(),
            },
            "tls": {
                "verify_ssl": config.veeam.verify_ssl,
                "poc_mode": "verify_ssl=false allows self-signed certificates for PoC validation.",
                "production_mode": "Use verify_ssl=true after registering the Veeam REST certificate in the Windows trusted root store.",
                "python_client": "LOCK-FIX validates Veeam with Python HTTPS client; PowerShell/curl Schannel failures are diagnostic only.",
            },
            "authentication": None,
            "jobs": None,
            "sessions": None,
            "matching": None,
            "isolate_condition": None,
            "reference_only_enterprise_manager_port": {
                **client.check_enterprise_manager_port(),
                "required": False,
                "affects_lockfix_integration": False,
                "message": "Enterprise Manager 9398 is reference-only. LOCK-FIX integration success is decided by VBR REST 9419 token and sessions.",
            },
            "latest_configured_session": None,
        }
        result["port"] = result["vbr_rest_9419"]["port"]
        try:
            token = client.login()
            result["authentication"] = {"ok": bool(token), "token_received": bool(token), "password_logged": False}
            jobs = client.get_jobs()
            result["jobs"] = {
                "ok": True,
                "count": len(jobs),
                "items": jobs,
            }
            sessions = client.get_sessions()
            result["sessions"] = {
                "ok": True,
                "count": len(sessions),
                "items": sessions,
            }
            wanted_job_id = normalized_job_id(settings.job_id)
            match = match_sessions(sessions, settings.job_name, wanted_job_id)
            result["matching"] = {
                "job_id": wanted_job_id,
                "job_name": settings.job_name,
                "strategy": match["strategy"],
                "matched": bool(match["matches"]),
                "similar_candidates": match["candidates"],
            }
            result["latest_configured_session"] = client.latest_session_summary(settings.job_name, settings.job_id)
            latest_session = sorted(match["matches"], key=lambda item: str(item.get("creationTime") or item.get("startTime") or ""), reverse=True)[0] if match["matches"] else None
            watcher_state = watcher.read_state()
            processed_session_ids = set(watcher_state.get("processed_session_ids") or [])
            current_session_id = session_id(latest_session) if latest_session else ""
            current_status = session_status(latest_session) if latest_session else ""
            status_allowed = is_success_status(current_status, config.veeam.isolate_on_status) if latest_session else False
            already_processed = bool(current_session_id and (current_session_id == watcher_state.get("last_isolated_session_id") or current_session_id in processed_session_ids))
            result["isolate_condition"] = {
                "watcher_enabled": config.veeam.enabled,
                "matched_session": bool(latest_session),
                "session_id": current_session_id,
                "job_name": session_name(latest_session) if latest_session else "",
                "job_id": session_job_id(latest_session) if latest_session else "",
                "status": current_status,
                "isolate_on_status": config.veeam.isolate_on_status,
                "status_allowed": status_allowed,
                "already_processed": already_processed,
                "would_call_isolate": bool(config.veeam.enabled and latest_session and status_allowed and not already_processed),
                "state_path": str(watcher.state_path),
            }
        except Exception as exc:
            result["error_type"] = getattr(exc, "code", exc.__class__.__name__)
            result["error"] = str(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if "error" not in result else 1
    if args.command == "veeam-watch":
        watcher = VeeamWatcher(config, controller)
        slot_id = args.slot or None
        if args.once:
            print(json.dumps(watcher.poll_once(slot_id=slot_id), ensure_ascii=False, indent=2))
            return 0
        watcher.run_forever(slot_id=slot_id)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
