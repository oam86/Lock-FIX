from __future__ import annotations

import argparse
import json
from pathlib import Path

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.identity import slot_uid
from lockfix.veeam_diagnostics import run_veeam_diagnostics
from lockfix.veeam_webui_check import DEFAULT_WEBUI_URL, compare_veeam_test_with_webui
from lockfix.veeam_watcher import VeeamWatcher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lockfixctl")
    parser.add_argument("--config", default="config/lockfix.example.json")
    command_parent = argparse.ArgumentParser(add_help=False)
    command_parent.add_argument("--config", default=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("isolate", "reconnect", "uid", "proof"):
        command = subparsers.add_parser(name, parents=[command_parent])
        command.add_argument("--slot", required=True)

    subparsers.add_parser("status", parents=[command_parent])
    subparsers.add_parser("veeam-test", parents=[command_parent])
    veeam_webui_test = subparsers.add_parser("veeam-webui-test", parents=[command_parent])
    veeam_webui_test.add_argument("--url", default=DEFAULT_WEBUI_URL)
    veeam_webui_test.add_argument("--email", default="admin")
    veeam_webui_test.add_argument("--password", default="1")
    veeam_watch = subparsers.add_parser("veeam-watch", parents=[command_parent])
    veeam_watch.add_argument("--slot", default="")
    veeam_watch.add_argument("--once", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config)
    config = load_config(config_path)
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
    if args.command == "proof":
        result = controller.isolation_proof(args.slot)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("proved") else 1
    if args.command == "status":
        print(json.dumps(controller.status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "veeam-test":
        result = run_veeam_diagnostics(config, controller)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if "error" not in result else 1
    if args.command == "veeam-webui-test":
        result = compare_veeam_test_with_webui(
            config,
            controller,
            webui_url=args.url,
            email=args.email,
            password=args.password,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get("webui", {}).get("running") is False:
            return 0
        return 0 if result.get("comparison", {}).get("ok") else 1
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
