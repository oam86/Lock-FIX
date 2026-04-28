from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.hashcheck import manifest_digest
from lockfix.identity import compute_uid
from lockfix.states import LockFixState


def write_config(tmp_path: Path, expected_uid: str = "") -> Path:
    mount = tmp_path / "mount"
    mount.mkdir()
    (mount / "backup.dat").write_text("payload", encoding="utf-8")
    (mount / ".lockfix_manifest.sha256").write_text(manifest_digest(mount), encoding="utf-8")
    config = {
        "dry_run": True,
        "state_path": str(tmp_path / "state.json"),
        "audit_log_path": str(tmp_path / "audit.jsonl"),
        "io_quiet_seconds": 1,
        "disk_wait_seconds": 1,
        "slots": [
            {
                "slot_id": "BAY-01",
                "device": "/dev/test",
                "mount_point": str(mount),
                "expected_uid": expected_uid,
                "identity": {"serial": "S1", "model": "M1", "wwn": "W1"},
                "manifest_path": ".lockfix_manifest.sha256",
                "power": {"type": "mock", "off_command": [], "on_command": []},
            }
        ],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


class LockFixTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        root = Path.cwd() / "runtime" / f"test-{uuid.uuid4().hex}"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def test_compute_uid_is_stable(self) -> None:
        self.assertEqual(
            compute_uid("S1", "M1", "W1", "BAY-01"),
            compute_uid("S1", "M1", "W1", "BAY-01"),
        )

    def test_veeam_config_defaults_to_disabled(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))

        self.assertFalse(config.veeam.enabled)
        self.assertEqual(config.veeam.port, 9419)
        self.assertEqual(config.veeam.api_version, "1.3-rev1")

    def test_isolate_reaches_isolated(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        state = controller.isolate("BAY-01")

        self.assertEqual(state, LockFixState.ISOLATED)
        self.assertEqual(controller.status()["BAY-01"], "ISOLATED")

    def test_reconnect_uid_mismatch_quarantines(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path, expected_uid="wrong")))

        state = controller.reconnect("BAY-01")

        self.assertEqual(state, LockFixState.QUARANTINE)
        self.assertEqual(controller.status()["BAY-01"], "QUARANTINE")


if __name__ == "__main__":
    unittest.main()
