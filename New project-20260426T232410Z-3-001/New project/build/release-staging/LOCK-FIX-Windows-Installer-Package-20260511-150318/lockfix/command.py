from __future__ import annotations

import subprocess


class CommandError(RuntimeError):
    pass


class CommandRunner:
    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run

    def run(self, args: list[str], timeout: int = 120) -> str:
        if not args:
            raise CommandError("empty command")
        if self.dry_run:
            return f"dry-run: {' '.join(args)}"
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        if result.returncode != 0:
            message = (result.stderr or "").strip() or (result.stdout or "").strip() or f"exit code {result.returncode}"
            raise CommandError(message)
        return (result.stdout or "").strip()
