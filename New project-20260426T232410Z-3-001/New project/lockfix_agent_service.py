from __future__ import annotations

import argparse
from pathlib import Path

from lockfix.agent_service import AgentServiceWorker


ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="LOCK-FIX privileged Agent/Service worker")
    parser.add_argument("--config", default=str(ROOT / "config" / "lockfix.example.json"))
    parser.add_argument("--queue-root", default=str(ROOT / "runtime" / "agent_service"))
    parser.add_argument("--once", action="store_true", help="Process pending requests once and exit")
    args = parser.parse_args()

    worker = AgentServiceWorker(Path(args.config), Path(args.queue_root))
    if args.once:
        worker.process_once()
        return
    worker.run_forever()


if __name__ == "__main__":
    main()
