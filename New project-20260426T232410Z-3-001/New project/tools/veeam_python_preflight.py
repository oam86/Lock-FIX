from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lockfix.config import load_config
from lockfix.veeam_client import VeeamClient, VeeamSettings


def emit(step: str, ok: bool, code: str, message: str, **payload: object) -> None:
    print(json.dumps({"step": step, "ok": ok, "code": code, "message": message, **payload}, ensure_ascii=False))


def main() -> int:
    config_path = ROOT / "config" / "lockfix.example.json"
    config = load_config(config_path)
    client = VeeamClient(VeeamSettings.from_config(config.veeam))

    port = client.check_port()
    emit("port", bool(port.get("ok")), str(port.get("code", "")), str(port.get("message", "")))
    if not port.get("ok"):
        return 1

    try:
        token = client.login()
        emit("token", True, "OK", "access_token issued.", token_length=len(token))
    except Exception as exc:
        emit("token", False, getattr(exc, "code", exc.__class__.__name__), str(exc))
        return 1

    try:
        sessions = client.get_sessions()
        emit("sessions", True, "OK", "/api/v1/sessions query succeeded.", session_count=len(sessions))
    except Exception as exc:
        emit("sessions", False, getattr(exc, "code", exc.__class__.__name__), str(exc))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
