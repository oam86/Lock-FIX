from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from lockfix.config import load_config
from lockfix.controller import LockFixController
from lockfix.disk import DiskOperator
from lockfix.command import CommandRunner
from lockfix.audit import AuditLogger
from lockfix.hashcheck import manifest_digest
from lockfix.identity import compute_uid
from lockfix.states import LockFixState
from lockfix.veeam_client import VeeamSettings
from lockfix.veeam_watcher import VeeamWatcher


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
                "device": "D:\\",
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

    def test_windows_c_volume_is_never_unmount_target(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        slot = config.slot("BAY-01")
        protected_slot = type(slot)(
            slot_id=slot.slot_id,
            device="C:\\",
            mount_point=Path("C:\\"),
            expected_uid=slot.expected_uid,
            identity=slot.identity,
            manifest_path=slot.manifest_path,
            power=slot.power,
        )
        disk = DiskOperator(CommandRunner(dry_run=True), AuditLogger(tmp_path / "audit-c-block.jsonl"))

        with self.assertRaises(ValueError):
            disk.unmount(protected_slot)

    def test_veeam_api_version_defaults_to_vbr_reference_version(self) -> None:
        tmp_path = self.make_workspace()

        config = load_config(write_config(tmp_path))
        settings = VeeamSettings.from_config(config.veeam)

        self.assertEqual(config.veeam.api_version, "1.2-rev1")
        self.assertEqual(settings.api_version, "1.2-rev1")

    def test_veeam_api_version_can_be_overridden_by_config(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"api_version": "1.3-rev0"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        settings = VeeamSettings.from_config(config.veeam)

        self.assertEqual(config.veeam.api_version, "1.3-rev0")
        self.assertEqual(settings.api_version, "1.3-rev0")

    def test_veeam_watcher_runs_jobs_sessions_match_status_then_isolate(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "job_id": "job-123",
            "job_name": "Agent_backup",
            "isolate_on_status": ["Success"],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)
        controller = LockFixController(config)

        class FakeVeeamClient:
            def __init__(self) -> None:
                self.calls = []

            def check_port(self):
                self.calls.append("port")
                return {"ok": True, "code": "OK", "message": "9419 reachable"}

            def login(self):
                self.calls.append("token")
                return "token"

            def get_jobs(self):
                self.calls.append("jobs")
                return [{"id": "job-123", "name": "Agent_backup"}]

            def get_sessions(self):
                self.calls.append("sessions")
                return [
                    {
                        "id": "session-123",
                        "name": "Agent_backup",
                        "jobId": "job-123",
                        "creationTime": "2026-05-01T07:00:00+09:00",
                        "result": {"result": "Success"},
                    }
                ]

        watcher = VeeamWatcher(config, controller, state_path=tmp_path / "veeam_watcher_state.json")
        fake_client = FakeVeeamClient()
        watcher.client = fake_client

        result = watcher.poll_once(slot_id="BAY-01")

        self.assertEqual(fake_client.calls, ["port", "token", "jobs", "sessions"])
        self.assertEqual(result["action"], "isolated")
        self.assertEqual(result["session_id"], "session-123")
        self.assertEqual(controller.status()["BAY-01"], "ISOLATED")


if __name__ == "__main__":
    unittest.main()
