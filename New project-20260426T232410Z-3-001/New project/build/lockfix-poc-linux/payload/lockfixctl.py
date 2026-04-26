from __future__ import annotations

import argparse
import json
from pathlib import Path

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.identity import slot_uid


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
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
