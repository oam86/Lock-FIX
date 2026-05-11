from __future__ import annotations

import argparse
from pathlib import Path

from webui import DEFAULT_CONFIG, run


def run_server(host: str = "127.0.0.1", port: int = 8088, config_path: Path = DEFAULT_CONFIG) -> None:
    run(host=host, port=port, config_path=config_path.resolve())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    run_server(args.host, args.port, args.config)


if __name__ == "__main__":
    main()
