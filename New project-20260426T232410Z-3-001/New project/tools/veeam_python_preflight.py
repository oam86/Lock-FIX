from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lockfix.config import load_config
from lockfix.veeam_diagnostics import run_veeam_diagnostics


def emit(step: str, ok: bool, code: str, message: str, **payload: object) -> None:
    print(json.dumps({"step": step, "ok": ok, "code": code, "message": message, **payload}, ensure_ascii=False))


def main() -> int:
    config_path = ROOT / "config" / "lockfix.example.json"
    config = load_config(config_path)
    result = run_veeam_diagnostics(config)

    port = result.get("vbr_rest_9419", {}).get("port", {})
    emit("port", bool(port.get("ok")), str(port.get("code", "")), str(port.get("message", "")))
    if not port.get("ok"):
        return 1

    token = result.get("authentication") or {}
    emit("token", bool(token.get("ok")), "OK" if token.get("ok") else str(result.get("error_type", "")), "access_token issued." if token.get("ok") else str(result.get("error", "")))
    if not token.get("ok"):
        return 1

    sessions = result.get("sessions") or {}
    emit("sessions", bool(sessions.get("ok")), "OK" if sessions.get("ok") else str(result.get("error_type", "")), "/api/v1/sessions query succeeded." if sessions.get("ok") else str(result.get("error", "")), session_count=sessions.get("count", 0))
    if not sessions.get("ok"):
        return 1

    jobs = result.get("jobs") or {}
    emit("jobs", bool(jobs.get("ok")), "OK" if jobs.get("ok") else str(result.get("error_type", "")), "/api/v1/jobs query succeeded." if jobs.get("ok") else str(result.get("error", "")), job_count=jobs.get("count", 0))
    return 0 if jobs.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
