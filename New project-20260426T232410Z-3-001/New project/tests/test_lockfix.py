from __future__ import annotations

import json
import os
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import webui
from lockfix.config import load_config
from lockfix.controller import LockFixController, repository_volume_root
from lockfix.disk import DiskOperator
from lockfix.command import CommandError, CommandRunner
from lockfix.audit import AuditLogger
from lockfix.hashcheck import manifest_digest
from lockfix.identity import compute_uid, fingerprint_parts, slot_uid
from lockfix.state_store import StateStore
from lockfix.states import LockFixState
from lockfix.veeam_client import VeeamAuthenticationError, VeeamClient, VeeamSettings, enrich_summary_with_logs, filter_target_repositories, match_backups, restore_point_summary, session_summary
from lockfix.veeam_console_logs import latest_backup_copy_console_log_summary
from lockfix.veeam_factory import create_veeam_client
from lockfix.veeam_diagnostics import run_veeam_diagnostics
from lockfix.veeam_webui_check import WebUiServerNotRunning, compare_veeam_test_with_webui, summarize_webui_backup
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

    def test_config_loader_accepts_utf8_bom(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = config_path.read_text(encoding="utf-8")
        config_path.write_text("\ufeff" + raw, encoding="utf-8")

        config = load_config(config_path)

        self.assertEqual(config.slot("BAY-01").device, "D:\\")

    def test_install_properties_can_enable_live_operation_mode(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_path = config_dir / "lockfix.example.json"
        config_path.write_text(source_config.read_text(encoding="utf-8"), encoding="utf-8")
        runtime_dir = tmp_path / "runtime"
        runtime_dir.mkdir()
        (runtime_dir / "install.properties").write_text(
            "operation_mode=live\n"
            "dry_run=false\n",
            encoding="utf-8",
        )

        config = load_config(config_path)

        self.assertFalse(config.dry_run)

    def test_power_command_paths_are_resolved_from_install_root(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        install_root = tmp_path / "install"
        config_dir = install_root / "config"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "lockfix.example.json"
        raw = json.loads(source_config.read_text(encoding="utf-8"))
        raw["slots"][0]["power"] = {
            "type": "command",
            "off_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "{app_root}\\tools\\lockfix_power_control.ps1",
                "-Action",
                "Off",
                "-SlotId",
                "BAY-01",
            ],
            "on_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "tools\\lockfix_power_control.ps1",
                "-Action",
                "On",
                "-SlotId",
                "BAY-01",
            ],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        power = config.slot("BAY-01").power

        self.assertEqual(power.type, "command")
        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.off_command)
        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.on_command)

    def test_power_status_command_paths_are_resolved_from_install_root(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        install_root = tmp_path / "install"
        config_dir = install_root / "config"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "lockfix.example.json"
        raw = json.loads(source_config.read_text(encoding="utf-8"))
        raw["slots"][0]["power"] = {
            "type": "command",
            "off_command": [],
            "on_command": [],
            "status_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "tools\\lockfix_power_control.ps1",
                "-Action",
                "Status",
                "-SlotId",
                "BAY-01",
            ],
            "off_status_values": ["off", "powered_off"],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        power = config.slot("BAY-01").power

        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.status_command)
        self.assertEqual(power.off_status_values, ["off", "powered_off"])

    def test_isolation_proof_reports_volume_and_power_evidence(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        result = controller.isolation_proof("BAY-01")

        self.assertEqual(result["slot_id"], "BAY-01")
        self.assertEqual(result["status"], "NOT_PROVED")
        self.assertFalse(result["proved"])
        self.assertEqual(result["volume_unmounted"]["reason"], "dry_run mode cannot prove live Windows volume state")
        self.assertEqual(result["power_off"]["reason"], "mock power controller cannot prove physical power state")
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "disk.unmount.proof"', audit_text)
        self.assertIn('"event": "power.mock.status"', audit_text)
        self.assertIn('"event": "isolation.proof"', audit_text)

    def test_isolate_records_power_off_proof_requirement_when_status_is_unavailable(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        controller.isolate("BAY-01")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "power.mock.status"', audit_text)
        self.assertIn('"event": "power.off.proof.required"', audit_text)
        self.assertIn("Power OFF can be proved only when the PDU/relay/storage controller status response confirms OFF.", audit_text)

    def test_controller_uses_veeam_backup_copy_repository_volume(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "require_backup_copy": True,
            "target_repository_path": "F:\\Repository\\Copy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))

        controller.isolate("BAY-01")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "veeam.repository.volume.target"', audit_text)
        self.assertIn('"repository_path": "F:\\\\Repository\\\\Copy"', audit_text)
        self.assertIn('"target_volume": "F:\\\\"', audit_text)
        self.assertIn('"configured_slot_volume":', audit_text)

    def test_repository_volume_root_blocks_c_volume(self) -> None:
        self.assertEqual(repository_volume_root("F:\\Repository\\Copy"), "F:\\")
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "require_backup_copy": True,
            "target_repository_path": "C:\\BackupCopy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))

        with self.assertRaisesRegex(ValueError, "protected Windows OS volume"):
            controller.isolate("BAY-01")

    def test_lockfix_dry_run_environment_override_takes_precedence(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        with patch.dict("os.environ", {"LOCKFIX_DRY_RUN": "false"}, clear=False):
            config = load_config(config_path)

        self.assertFalse(config.dry_run)

    def test_command_runner_handles_windows_output_decode_failures_safely(self) -> None:
        class Result:
            returncode = 1
            stdout = None
            stderr = None

        with patch("subprocess.run", return_value=Result()) as run:
            with self.assertRaisesRegex(CommandError, "exit code 1"):
                CommandRunner(dry_run=False).run(["powershell", "-Command", "Write-Error 실패"])

        kwargs = run.call_args.kwargs
        self.assertEqual(kwargs["encoding"], "utf-8")
        self.assertEqual(kwargs["errors"], "replace")

    def test_detect_fingerprint_uses_configured_identity_fields(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["slots"][0]["identity"].update(
            {
                "unique_id": "DISK-UNIQUE-01",
                "disk_size": "4 TB",
                "firmware": "FW-9001",
                "controller_location": "PCIROOT(0)#SLOT(2)",
            }
        )
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)
        slot = config.slot("BAY-01")

        parts = {part["key"]: part["value"] for part in fingerprint_parts(slot)}

        self.assertEqual(parts["unique_id"], "DISK-UNIQUE-01")
        self.assertEqual(parts["size"], "4 TB")
        self.assertEqual(parts["firmware"], "FW-9001")
        self.assertEqual(parts["controller_location"], "PCIROOT(0)#SLOT(2)")

        raw["slots"][0]["identity"]["firmware"] = "FW-9002"
        changed_path = tmp_path / "changed.json"
        changed_path.write_text(json.dumps(raw), encoding="utf-8")
        changed_slot = load_config(changed_path).slot("BAY-01")

        self.assertNotEqual(slot_uid(slot), slot_uid(changed_slot))

    def test_detect_disk_size_fallback_uses_volume_capacity_not_path(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        slot = config.slot("BAY-01")

        parts = {part["key"]: part["value"] for part in fingerprint_parts(slot)}

        self.assertNotEqual(parts["size"], str(slot.mount_point))
        self.assertNotEqual(parts["size"], slot.device)
        self.assertRegex(parts["size"], r"^[\d,]+ GB$")

    def test_webui_detect_summary_is_backed_by_fingerprint_parts(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["slots"][0]["identity"].update({"disk_size": "8 TB", "firmware": "FW-WEB"})
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        summary = webui.LockFixWebHandler.detect_summary(Probe())
        parts = {part["key"]: part["value"] for part in summary["fingerprint"]["parts"]}

        self.assertEqual(parts["size"], "8 TB")
        self.assertEqual(parts["firmware"], "FW-WEB")
        self.assertIn("Disk Size", summary["fingerprint"]["formula"])

    def test_detect_webui_uses_judgement_module_layout(self) -> None:
        root = Path.cwd()
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("Judgement Module UI", app_source)
        self.assertIn('statusClass = isNormal ? "normal" : "abnormal"', app_source)
        self.assertIn(".detect-judgement-normal", css_source)
        self.assertIn(".detect-judgement-abnormal", css_source)
        self.assertIn("background: #ffffff;", css_source)
        self.assertIn("color: #16a34a", css_source)
        self.assertIn("color: #ef4444", css_source)

    def test_logs_navigation_uses_lockfix_logs_icon_asset(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertTrue((root / "web" / "static" / "lockfix-logs-icon.png").exists())
        self.assertIn('class="nav-icon logs-nav-icon"', index_source)
        self.assertIn('src="/static/lockfix-logs-icon.png?v=20260505-logs"', index_source)
        self.assertIn(".logs-nav-icon img", css_source)
        self.assertIn("transform: none;", css_source)
        self.assertNotIn("transform: scale(2.25);", css_source)

    def test_webui_sidebar_is_compact_to_prioritize_content(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("width: min(1280px, calc(100% - 20px));", css_source)
        self.assertIn("grid-template-columns: 124px minmax(0, 1fr);", css_source)
        self.assertIn("grid-template-columns: 46px minmax(0, 1fr);", css_source)
        self.assertIn("padding: 28px 12px 22px;", css_source)
        self.assertIn("padding: 32px 34px 42px;", css_source)
        self.assertIn('id="sidebarToggle"', index_source)
        self.assertTrue((root / "web" / "static" / "oam-brand-mark.svg").exists())
        self.assertIn('class="sidebar-logo-mark"', index_source)
        self.assertIn('src="/static/oam-brand-mark.svg"', index_source)
        self.assertIn("lockfix.sidebarCollapsed", app_source)
        self.assertIn("applySidebarState", app_source)
        self.assertIn(".sidebar-collapsed .sidebar-logo-full", css_source)
        self.assertIn(".sidebar-collapsed .sidebar-logo-mark", css_source)
        self.assertIn("width: 24px;", css_source)
        self.assertIn(".sidebar-collapsed .side-item > span:not(.nav-icon)", css_source)
        self.assertIn("grid-template-columns: 1fr;", css_source)
        self.assertIn("grid-template-columns: repeat(6, 28px);", css_source)
        self.assertIn("pointer-events: auto;", css_source)
        self.assertIn("box-shadow: none;", css_source)

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

    def test_reconnect_recovers_access_path_when_power_on_fails_but_disk_is_visible(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        class FailingPower:
            def on(self, slot_id: str) -> None:
                raise RuntimeError("invalid PDU URL")

            def off(self, slot_id: str) -> None:
                return None

            def status(self, slot_id: str) -> dict[str, object]:
                return {"ok": None}

        with patch("lockfix.controller.build_power_controller", return_value=FailingPower()), patch.object(
            controller.disk, "partition_visible", return_value=True
        ):
            state = controller.reconnect("BAY-01")

        self.assertEqual(state, LockFixState.ONLINE_VERIFIED_RW)
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("power.on.reconnect.warning", audit_text)
        self.assertIn("power.on.reconnect.continue_disk_visible", audit_text)
        self.assertIn("disk.access_path", audit_text)

    def test_emergency_reconnect_requires_matching_disk_hash(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        with self.assertRaises(PermissionError):
            controller.emergency_reconnect("BAY-01", "wrong-hash")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("emergency.reconnect.denied", audit_text)
        self.assertNotIn("wrong-hash", audit_text)
        self.assertIn("provided_hash_digest", audit_text)
        self.assertIn("expected_hash_digest", audit_text)
        self.assertNotIn("expected_hash_prefix", audit_text)

    def test_emergency_reconnect_verifies_then_reconnects_volume(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        state = controller.emergency_reconnect("BAY-01", controller.emergency_access_hash("BAY-01"))

        self.assertEqual(state, LockFixState.ONLINE_VERIFIED_RW)
        self.assertEqual(controller.status()["BAY-01"], "ONLINE_VERIFIED_RW")
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("emergency.reconnect.approved", audit_text)
        self.assertIn("disk.safety.preflight.start", audit_text)
        self.assertIn("disk.mount_ro.start", audit_text)
        self.assertIn("Set-Disk -Number $disk.Number -IsReadOnly $true", audit_text)
        self.assertIn("Mount-Volume -DriveLetter $drive", audit_text)
        self.assertIn("Repair-Volume -DriveLetter $drive -Scan", audit_text)
        self.assertIn("Set-Disk -Number $disk.Number -IsReadOnly $false", audit_text)
        self.assertIn("disk.access_path.start", audit_text)
        self.assertIn("disk.access_path", audit_text)
        self.assertIn("disk.mount_rw", audit_text)
        self.assertIn("emergency.reconnect.complete", audit_text)

    def test_airgap_summary_exposes_emergency_volume_access_state(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        summary = webui.LockFixWebHandler.emergency_access_summary(Probe(), {})
        emergency = summary["slot"]

        self.assertEqual(emergency["slot_id"], "BAY-01")
        self.assertNotIn("authorization_hash", emergency)
        self.assertNotIn("current_uid", emergency)
        self.assertNotIn("manifest_hash", emergency)
        self.assertEqual(emergency["authorization_hash_short"], f"{slot_uid(Probe.context.config.slot('BAY-01'))[:16]}...{slot_uid(Probe.context.config.slot('BAY-01'))[-8:]}")
        self.assertTrue(emergency["authorization_hash_protected"])
        self.assertIn("current_uid_short", emergency)
        self.assertIn("hash_status", emergency)

    def test_webui_audit_readers_tolerate_windows_non_utf8_output(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        config.audit_log_path.write_bytes(
            b'{"ts":"2026-05-05T13:14:09+00:00","event":"disk.unmount","slot_id":"BAY-01","output":"ok"}\n'
            b'{"ts":"2026-05-05T13:14:16+00:00","event":"disk.unmount.error","slot_id":"BAY-01","error":"\xbd"}\n'
        )

        class Probe:
            context = webui.WebContext(config_path)

        latest = webui.LockFixWebHandler.latest_audit_record(Probe(), "BAY-01", {"disk.unmount", "disk.unmount.error"})
        items = webui.LockFixWebHandler.audit_items(Probe())

        self.assertEqual(latest["event"], "disk.unmount.error")
        self.assertEqual(items[0]["event"], "disk.unmount.error")
        self.assertIn("�", items[0]["error"])

    def test_state_store_repairs_trailing_json_garbage(self) -> None:
        tmp_path = self.make_workspace()
        state_path = tmp_path / "state.json"
        state_path.write_text('{\n  "BAY-01": "UNMOUNTING"\n}\n}\n', encoding="utf-8")
        store = StateStore(state_path)

        self.assertEqual(store.read_all(), {"BAY-01": "UNMOUNTING"})
        self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"BAY-01": "UNMOUNTING"})
        self.assertTrue(state_path.with_suffix(".json.corrupt").exists())

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

    def test_unmount_uses_preflight_cache_flush_and_non_force_dismount(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        audit_path = tmp_path / "safe-unmount-audit.jsonl"
        disk = DiskOperator(CommandRunner(dry_run=True), AuditLogger(audit_path))

        disk.unmount(config.slot("BAY-01"))

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.safety.preflight.start", audit_text)
        self.assertIn("disk.safety.preflight.ok", audit_text)
        self.assertIn("disk.cache.flush.start", audit_text)
        self.assertIn("disk.cache.flush", audit_text)
        self.assertIn("Dismount-Volume -DriveLetter $drive -ErrorAction Stop", audit_text)
        self.assertIn("Remove-PartitionAccessPath", audit_text)
        self.assertIn("access path removed and no longer reachable", audit_text)
        self.assertIn("disk.unmount.verify", audit_text)
        self.assertNotIn("-Force", audit_text)

    def test_storage_permission_denied_uses_system_fallback(self) -> None:
        tmp_path = self.make_workspace()
        audit_path = tmp_path / "system-fallback-audit.jsonl"

        class DeniedRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                raise CommandError("Get-Volume : 액세스가 거부되었습니다.")

        class FallbackDisk(DiskOperator):
            def run_storage_command_as_system(self, command_text: str, timeout: int = 120) -> str:
                self.audit.write("test.system_fallback.invoked", command=command_text)
                return "SYSTEM fallback OK"

        disk = FallbackDisk(DeniedRunner(), AuditLogger(audit_path))

        output = disk.storage_run([
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Volume -DriveLetter D",
        ])

        self.assertEqual(output, "SYSTEM fallback OK")
        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn('"event": "storage.command.primary_denied"', audit_text)
        self.assertIn('"event": "test.system_fallback.invoked"', audit_text)

    def test_non_storage_permission_denied_does_not_use_system_fallback(self) -> None:
        tmp_path = self.make_workspace()

        class DeniedRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                raise CommandError("access is denied")

        class FallbackDisk(DiskOperator):
            def run_storage_command_as_system(self, command_text: str, timeout: int = 120) -> str:
                raise AssertionError("fallback should not run for non-storage commands")

        disk = FallbackDisk(DeniedRunner(), AuditLogger(tmp_path / "non-storage-audit.jsonl"))

        with self.assertRaisesRegex(CommandError, "access is denied"):
            disk.storage_run([
                "powershell",
                "-NoProfile",
                "-Command",
                "Write-Output 'hello'",
            ])

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

    def test_veeam_auto_discovery_settings_are_loaded(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "auto_discover": True,
            "discovery_candidates": ["https://192.168.219.230:9419"],
            "discovery_scan_local_subnet": False,
            "discovery_timeout_seconds": 0.2,
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        settings = VeeamSettings.from_config(config.veeam)

        self.assertTrue(config.veeam.auto_discover)
        self.assertEqual(config.veeam.discovery_candidates, ["https://192.168.219.230:9419"])
        self.assertFalse(settings.discovery_scan_local_subnet)
        self.assertEqual(settings.discovery_timeout_seconds, 0.2)

    def test_veeam_auto_discovery_selects_working_backup_server(self) -> None:
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = create_veeam_client(
                {
                    "username": "administrator",
                    "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
                    "base_url": "https://127.0.0.1:9419",
                    "auto_discover": True,
                    "discovery_candidates": ["https://192.168.219.230:9419"],
                    "discovery_scan_local_subnet": False,
                }
            )
        with patch(
            "lockfix.veeam_client.discover_veeam_base_url",
            return_value=("https://192.168.219.230:9419", [{"base_url": "https://192.168.219.230:9419", "ok": True}]),
        ):
            client.ensure_discovered_base_url()

        self.assertEqual(client.settings.base_url, "https://192.168.219.230:9419")
        self.assertEqual(client.discovery_result["selected"], "https://192.168.219.230:9419")

    def test_only_config_veeam_section_is_used_for_veeam_settings(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"job_name": "OriginalJob", "api_version": "1.2-rev1"}
        raw["veeam_backup"] = {
            "job_name": "Agent_backup",
            "api_version": "1.3-rev0",
            "target_repository_name": "DREPO",
            "target_repository_path": "D:\\copy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)

        self.assertEqual(config.veeam.job_name, "OriginalJob")
        self.assertEqual(config.veeam.api_version, "1.2-rev1")
        self.assertEqual(config.veeam.target_repository_name, "")
        self.assertEqual(config.veeam.target_repository_path, "")

    def test_veeam_verify_ssl_string_false_becomes_boolean_false(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "verify_ssl": "false",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = create_veeam_client({"username": "administrator", "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD", "verify_ssl": "false"})

        self.assertIs(config.veeam.verify_ssl, False)
        self.assertIs(client.settings.verify_ssl, False)

    def test_veeam_entrypoints_use_shared_client_factory(self) -> None:
        root = Path.cwd()
        entrypoints = [
            root / "lockfixctl.py",
            root / "webui.py",
            root / "lockfix" / "veeam_diagnostics.py",
            root / "lockfix" / "veeam_watcher.py",
        ]

        for path in entrypoints:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("VeeamClient(", source, f"{path} must not construct VeeamClient directly")

        self.assertIn("run_veeam_diagnostics(self.context.config, self.context.controller)", (root / "webui.py").read_text(encoding="utf-8"))
        self.assertIn("create_veeam_client(veeam_config)", (root / "lockfix" / "veeam_diagnostics.py").read_text(encoding="utf-8"))
        self.assertIn("run_veeam_diagnostics(self.config, self.controller)", (root / "lockfix" / "veeam_watcher.py").read_text(encoding="utf-8"))
        self.assertIn("VeeamClient(settings)", (root / "lockfix" / "veeam_factory.py").read_text(encoding="utf-8"))
        self.assertIn('veeam_config = config.get("veeam", {})', (root / "webui.py").read_text(encoding="utf-8"))

    def test_webui_treats_console_log_veeam_state_as_synced(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function isVeeamSynced", source)
        self.assertIn('stateSource.startsWith("veeam_rest_api")', source)

    def test_airgap_ui_exposes_emergency_volume_access_button(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("emergency_access", source)
        self.assertIn("/api/emergency-reconnect", source)
        self.assertIn("긴급 볼륨 접속", source)
        self.assertIn("Reconnect History", source)
        self.assertIn("Reconnect State Flow", source)
        self.assertIn("ONLINE_VERIFIED_RW", source)
        self.assertIn("RECONNECT_REQUESTED", source)
        self.assertIn("emergency-reconnect-flow", source)
        self.assertIn("인증 해시값 전체를 입력하세요", source)
        self.assertNotIn("data-hash=", source)
        self.assertIn("last_reconnect", source)
        self.assertIn("reconnect_history", source)
        self.assertIn("data-lock-disabled", source)
        self.assertIn(".emergency-access-panel", css)
        self.assertIn(".emergency-access-button", css)
        self.assertIn(".emergency-reconnect-flow", css)
        self.assertIn(".emergency-reconnect-arrow", css)
        self.assertIn(".emergency-access-grid .emergency-history", css)

    def test_webui_has_local_package_folder_open_endpoint(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("/open-latest-package-folder", source)
        self.assertIn("os.startfile", source)
        self.assertIn("local access only", source)

    def test_login_success_shows_two_second_loading_splash(self) -> None:
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css_source = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("const LOGIN_SPLASH_DURATION_MS = 2000;", app_source)
        self.assertIn("showLoginSplashThenEnter", app_source)
        self.assertIn("setTimeout(resolve, LOGIN_SPLASH_DURATION_MS)", app_source)
        self.assertIn('class="splash-stage"', html_source)
        self.assertIn('class="splash-loader"', html_source)
        self.assertIn("@keyframes splashProgress", css_source)
        self.assertIn("animation: splashProgress 2000ms", css_source)
        self.assertIn("@keyframes splashBreath", css_source)

    def test_admin_update_script_can_apply_live_operation_mode(self) -> None:
        source = (Path.cwd() / "tools" / "apply_latest_webui_update_admin.ps1").read_text(encoding="utf-8")

        self.assertIn('[ValidateSet("simulation", "live")]', source)
        self.assertIn('[string]$OperationMode = "live"', source)
        self.assertIn('$props["operation_mode"] = $OperationMode', source)
        self.assertIn('$props["dry_run"] = if ($OperationMode -eq "live") { "false" } else { "true" }', source)
        self.assertIn("Set-ObjectProperty -Object $config -Name dry_run -Value $effectiveDryRun", source)
        self.assertIn('"lockfix\\command.py"', source)

    def test_installer_and_default_config_use_live_operation_mode(self) -> None:
        root = Path.cwd()
        config = load_config(root / "config" / "lockfix.example.json")
        setup_source = (root / "src" / "LockFixSetupWizard.cs").read_text(encoding="utf-8")

        self.assertFalse(config.dry_run)
        self.assertEqual(json.loads((root / "config" / "lockfix.example.json").read_text(encoding="utf-8"))["operation_mode"], "live")
        self.assertIn('"operation_mode=live"', setup_source)
        self.assertIn('"dry_run=false"', setup_source)
        self.assertIn('root["operation_mode"] = "live";', setup_source)
        self.assertIn('root["dry_run"] = false;', setup_source)

    def test_latest_package_zip_selects_newest_release_package(self) -> None:
        tmp_path = self.make_workspace()
        old_package = tmp_path / "LOCK-FIX-Windows-Installer-Package-20260505-010000.zip"
        new_package = tmp_path / "LOCK-FIX-Windows-Installer-Package-20260505-020000.zip"
        old_package.write_text("old", encoding="utf-8")
        new_package.write_text("new", encoding="utf-8")
        os.utime(old_package, (1, 1))
        os.utime(new_package, (2, 2))

        selected = webui.LockFixWebHandler.latest_package_zip(object(), tmp_path)

        self.assertEqual(selected, new_package)

    def test_webui_renders_interlock_action_sections_without_status_icon(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('text.startsWith("LOCK-FIX STEP ")', source)
        self.assertIn("veeam-action-section", source)
        self.assertIn(".veeam-session-actions .veeam-action-section", css)

    def test_airgap_steps_stay_grey_until_real_api_transition(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('state: "PENDING", code: "BACKUP_COMPLETED"', source)
        self.assertIn("apiSynced &&", source)
        self.assertIn("isStepLive(item)", source)
        self.assertIn(".veeam-step-pending,", css)
        self.assertIn("background: #f6f8fb;", css)
        self.assertIn("background: #94a3b8;", css)
        self.assertIn(".veeam-step-active,", css)
        self.assertIn("background: linear-gradient(90deg, #22c55e 0%, #16a34a 52%, #0f8f3d 100%);", css)
        self.assertIn("filter: drop-shadow(0 6px 9px rgba(15, 143, 61, 0.28));", css)
        self.assertIn("grid-template-columns: repeat(5, minmax(158px, 1fr));", css)
        self.assertIn("grid-template-columns: 30px minmax(0, 1fr);", css)
        self.assertIn("gap: 10px;", css)
        self.assertIn("padding: 14px 22px;", css)
        self.assertIn("min-height: 104px;", css)
        self.assertIn("width: 100%;", css)
        self.assertIn("text-overflow: ellipsis;", css)
        self.assertIn("width: 42px;", css)
        self.assertIn("height: 26px;", css)

    def test_airgap_detail_log_area_scrolls_inside_blue_left_border(self) -> None:
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".veeam-log-wrap", css)
        self.assertIn("box-sizing: border-box;", css)
        self.assertIn("height: clamp(280px, 42vh, 340px);", css)
        self.assertIn("max-height: 340px;", css)
        self.assertIn("border: 1px solid #c8d8ea;", css)
        self.assertIn("direction: ltr;", css)
        self.assertIn("overflow-x: auto;", css)
        self.assertIn("overflow-y: scroll;", css)
        self.assertIn("overscroll-behavior: contain;", css)
        self.assertIn("scrollbar-width: thin;", css)
        self.assertIn("scrollbar-gutter: stable;", css)
        self.assertIn("scrollbar-color: #dcdcdf #ffffff;", css)
        self.assertIn(".veeam-log-wrap:hover", css)
        self.assertIn("scrollbar-color: #8a8a8f #ffffff;", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-button:vertical:decrement", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-button:vertical:increment", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-track-piece", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-corner", css)
        self.assertIn("border-left: 1px solid #eef2f7;", css)
        self.assertIn("min-height: 112px;", css)
        self.assertIn("border: 4px solid #ffffff;", css)
        self.assertIn("background-clip: padding-box;", css)
        self.assertIn("background: #dcdcdf;", css)
        self.assertIn("background: #8a8a8f;", css)
        self.assertIn("background: #747478;", css)
        self.assertIn(".veeam-log-wrap:hover::-webkit-scrollbar-thumb", css)
        self.assertIn("position: sticky;", css)

    def test_airgap_monitoring_heading_has_no_underline(self) -> None:
        source = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".veeam-monitoring-panel h2", source)
        self.assertIn("border-bottom: 0;", source)
        self.assertIn(".veeam-log-meta span", source)
        self.assertIn("overflow-wrap: anywhere;", source)
        self.assertNotIn("margin: -31px 12px 18px 0;", source)

    def test_veeam_client_from_config_and_get_backup_status(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "job_name": "Agent_backup",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)

        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = VeeamClient.from_config(config.veeam)

        with patch.object(client, "latest_session_summary", return_value={"api_synced": True}) as summary:
            result = client.get_backup_status()

        summary.assert_called_once_with("Agent_backup", "")
        self.assertTrue(result["api_synced"])
        self.assertEqual(client.settings.username, "administrator")
        self.assertEqual(client.settings.password, "secret")

    def test_veeam_username_env_and_password_env_are_supported(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username_env": "LOCKFIX_TEST_VEEAM_USER",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        with patch.dict(
            "os.environ",
            {"LOCKFIX_TEST_VEEAM_USER": "env-user", "LOCKFIX_TEST_VEEAM_PASSWORD": "secret"},
            clear=False,
        ):
            config = load_config(config_path)
            client = VeeamClient.from_config(config.veeam)
            helper_client = create_veeam_client(
                {
                    "username_env": "LOCKFIX_TEST_VEEAM_USER",
                    "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
                    "base_url": "https://127.0.0.1:9419",
                }
            )

        self.assertEqual(config.veeam.username_env, "LOCKFIX_TEST_VEEAM_USER")
        self.assertEqual(client.settings.username, "env-user")
        self.assertEqual(client.settings.password, "secret")
        self.assertEqual(helper_client.settings.username, "env-user")
        self.assertEqual(helper_client.settings.password, "secret")

    def test_veeam_login_reports_missing_username_or_password_env(self) -> None:
        missing_user = VeeamClient(VeeamSettings(username="", password="secret"))
        with self.assertRaisesRegex(VeeamAuthenticationError, "username is not configured"):
            missing_user.login()

        missing_password = VeeamClient(
            VeeamSettings(username="administrator", password="", password_env="LOCKFIX_MISSING_PASSWORD")
        )
        with self.assertRaisesRegex(VeeamAuthenticationError, "LOCKFIX_MISSING_PASSWORD"):
            missing_password.login()

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Veeam username is not configured"):
                create_veeam_client({"password_env": "LOCKFIX_MISSING_PASSWORD"})
            with self.assertRaisesRegex(ValueError, "LOCKFIX_MISSING_PASSWORD"):
                create_veeam_client({"username": "administrator", "password_env": "LOCKFIX_MISSING_PASSWORD"})

    def test_backup_copy_match_uses_non_c_target_repository(self) -> None:
        repositories = [
            {"id": "repo-c", "name": "CREPO", "repository": {"path": "C:\\backup"}},
            {"id": "repo-d", "name": "DREPO", "repository": {"path": "D:\\copy"}},
        ]
        backups = [
            {"id": "source-backup", "name": "Agent_backup - 192.168.219.102", "repositoryId": "repo-c"},
            {"id": "copy-backup", "name": "Backup Copy Job 2", "repositoryId": "repo-d"},
        ]

        eligible = filter_target_repositories(repositories, target_name="DREPO", target_path="D:\\copy")
        match = match_backups(backups, job_name="Agent_backup", eligible_repositories=eligible)
        restore_point = {
            "id": "restore-point-1",
            "sessionId": "session-1",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "_backup": match["matches"][0],
            "_repository": eligible[0],
        }
        summary = restore_point_summary(restore_point)

        self.assertEqual(match["strategy"], "target_repository_backup_copy")
        self.assertEqual(match["matches"][0]["id"], "copy-backup")
        self.assertEqual(summary["repository_path"], "D:\\copy")
        self.assertEqual(summary["current_step"], 2)

    def test_backup_copy_job_id_priority_records_restore_point_scope(self) -> None:
        repositories = [
            {"id": "repo-d", "name": "DREPO", "repository": {"path": "D:\\copy"}},
        ]
        backups = [
            {
                "id": "copy-backup",
                "name": "Backup Copy Job 2",
                "jobId": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
                "policyUniqueId": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
                "repositoryId": "repo-d",
            }
        ]

        eligible = filter_target_repositories(repositories, target_id="repo-d")
        match = match_backups(
            backups,
            job_name="Agent_backup",
            job_id="a61d20b5-2555-4635-ab65-86b6fc2bf449",
            eligible_repositories=eligible,
        )
        restore_point = {
            "id": "restore-point-1",
            "sessionId": "session-1",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "_backup": match["matches"][0],
            "_backup_object": {"id": "object-1", "name": "192.168.219.102"},
            "_repository": eligible[0],
            "_configured_job_name": "Agent_backup",
            "_configured_job_id": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
            "_backup_match_strategy": match["strategy"],
        }
        summary = restore_point_summary(restore_point)

        self.assertEqual(match["strategy"], "backup_job_id")
        self.assertEqual(summary["job_id"], "a61d20b5-2555-4635-ab65-86b6fc2bf449")
        self.assertEqual(summary["backup_match_strategy"], "backup_job_id")
        self.assertEqual(summary["restore_point_scope"]["backup_id"], "copy-backup")
        self.assertEqual(summary["restore_point_scope"]["repository_id"], "repo-d")

    def test_veeam_console_log_fallback_reads_latest_backup_copy_time(self) -> None:
        root = self.make_workspace() / "logs"
        job_dir = root / "Backup_Copy_Job_2" / "Agent_backup"
        job_dir.mkdir(parents=True)
        (job_dir / "Job.Agent_backup.log").write_text(
            "\n".join(
                [
                    "[04.05.2026 12:48:53.381]    Info    [JobSession] Update session [parent-1] CreationTime: 2026-05-04 오후 12:48:53",
                    "[04.05.2026 12:48:53.893]    Info    JobId=a61d20b5-2555-4635-ab65-86b6fc2bf449, JobName=Backup Copy Job 2",
                    "[04.05.2026 12:49:16.269]    Info    Job session 'parent-worker' has been completed, status: 'Success', '0 B' of '0 B' bytes",
                    "[04.05.2026 12:49:16.298]    Info    [JobSession] Update session [parent-1] EndTime: 2026-05-04 오후 12:49:16",
                ]
            ),
            encoding="utf-8",
        )
        (job_dir / "Job.192.168.219.102.BackupSync.log").write_text(
            "\n".join(
                [
                    "[04.05.2026 12:48:57.726]    Info    [Session] Id 'child-1', State 'Working'.",
                    "[04.05.2026 12:48:59.767]    Info    [JobSession] Set new totals: TotalObjects '1', TotalSize '479 GB'",
                    "[04.05.2026 12:49:00.543]    Info    [CSimpleCopyPointAlg] Creating incremental point",
                    "[04.05.2026 12:49:05.826]    Info    Job session 'child-1' has been completed, status: 'Success', '0 B' of '0 B' bytes",
                ]
            ),
            encoding="utf-8",
        )

        summary = latest_backup_copy_console_log_summary(
            log_root=str(root),
            backup_copy_name="Backup Copy Job 2",
            job_name="Agent_backup",
            target_name="192.168.219.102",
            policy_job_id="a61d20b5-2555-4635-ab65-86b6fc2bf449",
            repository_id="repo-d",
            repository_name="DREPO",
            repository_path="D:\\copy",
        )

        self.assertEqual(summary["started_at"], "2026-05-04 12:48:57")
        self.assertEqual(summary["ended_at"], "2026-05-04 12:49:05")
        self.assertEqual(summary["job_finished_at"], "2026-05-04 12:49:16")
        self.assertEqual(summary["duration"], "00:08")
        self.assertEqual(summary["backup_size"], "479 GB")
        self.assertEqual(summary["transferred"], "0 B")
        self.assertEqual(summary["session_id"], "child-1")

    def test_veeam_session_summary_keeps_realtime_progress_size_and_time(self) -> None:
        session = {
            "id": "session-1",
            "name": "Agent_backup",
            "state": "Working",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "progressPercent": 23,
        }
        logs = [
            {
                "title": "Agent_backup - 192.168.219.102 processing",
                "status": "Running",
                "startTime": "2026-05-01T07:00:00+09:00",
                "updateTime": "2026-05-01T07:00:05+09:00",
            }
        ]
        tasks = [
            {
                "name": "Agent_backup - 192.168.219.102",
                "status": "Running",
                "progressPercent": 42,
                "totalBytes": 1024 * 1024 * 1024,
                "transferredBytes": 512 * 1024 * 1024,
                "transferSpeed": 1024 * 1024,
            }
        ]

        summary = enrich_summary_with_logs(session_summary(session), logs, tasks)

        self.assertEqual(summary["progress_percent"], 42)
        self.assertEqual(summary["backup_size"], "1.0 GB")
        self.assertEqual(summary["transferred"], "512.0 MB")
        self.assertEqual(summary["speed"], "1.0 MB/s")
        self.assertIn("512.0 MB / 1.0 GB", "\n".join(summary["session_logs"][0]["actions"]))

    def test_veeam_session_summary_reads_nested_realtime_metrics(self) -> None:
        session = {
            "id": "session-1",
            "name": "Agent_backup",
            "state": "Working",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "endTime": "2026-05-01T07:00:08+09:00",
            "statistics": {
                "progress": "0%",
                "totalBytes": 479 * 1024 * 1024 * 1024,
                "transferredBytes": 0,
                "transferSpeed": "0 KB/s",
            },
        }

        summary = session_summary(session)

        self.assertEqual(summary["progress_percent"], 0)
        self.assertEqual(summary["backup_size"], "479.0 GB")
        self.assertEqual(summary["transferred"], "0 B")
        self.assertEqual(summary["speed"], "0 KB/s")
        self.assertEqual(summary["duration"], "00:08")

    def test_veeam_restore_point_logs_supply_size_and_duration(self) -> None:
        summary = restore_point_summary(
            {
                "id": "restore-point-1",
                "sessionId": "session-1",
                "creationTime": "2026-05-01T07:00:00+09:00",
                "_backup": {"name": "Backup Copy Job 2"},
                "_repository": {"name": "DREPO", "repository": {"path": "D:\\copy"}},
            }
        )
        logs = [
            {
                "status": "Succeeded",
                "title": "Total size: 11.3 GB",
                "startTime": "2026-05-01T07:00:00+09:00",
                "updateTime": "2026-05-01T07:00:00+09:00",
            },
            {
                "status": "Succeeded",
                "title": "Job finished at 2026-05-01 07:00:08",
                "startTime": "2026-05-01T07:00:08+09:00",
                "updateTime": "2026-05-01T07:00:08+09:00",
            },
        ]

        enriched = enrich_summary_with_logs(summary, logs, [])

        self.assertEqual(enriched["backup_size"], "11.3 GB")
        self.assertEqual(enriched["duration"], "00:08")
        self.assertIn("Total size: 11.3 GB", "\n".join(enriched["session_logs"][0]["actions"]))

    def test_veeam_restore_point_console_lines_use_session_log_time(self) -> None:
        summary = restore_point_summary(
            {
                "id": "restore-point-1",
                "sessionId": "session-1",
                "creationTime": "2026-05-01T06:59:58+09:00",
                "_backup": {"name": "Backup Copy Job 2"},
                "_backup_object": {"name": "192.168.219.102"},
                "_repository": {"name": "DREPO", "repository": {"path": "D:\\copy"}},
                "_configured_job_name": "Agent_backup",
            }
        )
        logs = [
            {
                "status": "Succeeded",
                "title": "Job started at 2026-05-01 오전 7:00:01",
                "startTime": "2026-05-01T07:00:01+09:00",
                "updateTime": "2026-05-01T07:00:01+09:00",
            },
            {
                "status": "Succeeded",
                "title": "Job finished at 2026-05-01 오전 7:01:10",
                "startTime": "2026-05-01T07:01:10+09:00",
                "updateTime": "2026-05-01T07:01:10+09:00",
            },
        ]

        enriched = enrich_summary_with_logs(summary, logs, [])
        actions = "\n".join(enriched["session_logs"][0]["actions"])

        self.assertIn("Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-01 07:00:01", actions)
        self.assertIn("Agent_backup - 192.168.219.102 (0 B) processing finished at 2026-05-01 07:01:10", actions)
        self.assertIn("Succeeded - Job started at 2026-05-01 07:00:01", actions)
        self.assertNotIn("06:59:58", actions)
        self.assertNotIn(" 오전 ", actions)

    def test_webui_veeam_backup_uses_context_config(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "base_url": "https://192.168.219.230:9419",
            "enterprise_manager_url": "https://127.0.0.1:9398",
            "api_version": "1.2-rev1",
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "verify_ssl": False,
            "job_name": "Agent_backup",
            "require_backup_copy": True,
            "target_repository_name": "DREPO",
            "target_repository_path": "D:\\copy",
            "exclude_os_repository": True,
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return False

        def fake_diagnostics(config, controller):
            veeam_config = config.veeam
            return {
                "latest_configured_session": {
                    "api_synced": True,
                    "job": veeam_config.job_name,
                    "job_id": veeam_config.job_id,
                    "status": "Success",
                    "progress_percent": 100,
                    "current_step": 2,
                    "repository_name": veeam_config.target_repository_name,
                    "repository_path": veeam_config.target_repository_path,
                }
            }

        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            with patch.object(webui, "run_veeam_diagnostics", fake_diagnostics):
                result = webui.LockFixWebHandler.poll_veeam_api(Probe(), "127.0.0.1", 9419, {})

        self.assertTrue(result["api_synced"])
        self.assertEqual(result["job"], "Agent_backup")
        self.assertEqual(result["current_step"], 2)
        self.assertEqual(result["server"], "192.168.219.230")
        self.assertEqual(result["port"], 9419)
        self.assertEqual(result["repository_name"], "DREPO")
        self.assertEqual(result["repository_path"], "D:\\copy")

    def test_webui_loads_veeam_password_from_install_properties_into_process_env(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username_env": "LOCKFIX_TEST_VEEAM_USER",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "base_url": "https://127.0.0.1:9419",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {
                    "veeam_user": "administrator",
                    "veeam_password": "secret",
                    "veeam_base_url": "https://192.168.219.230:9419",
                    "veeam_api_version": "1.2-rev1",
                }

        with patch.dict("os.environ", {}, clear=True):
            webui.LockFixWebHandler.prepare_veeam_process_environment(
                Probe(),
                Probe.context.app_config.get("veeam", {}),
            )
            self.assertEqual(os.environ["LOCKFIX_TEST_VEEAM_USER"], "administrator")
            self.assertEqual(os.environ["LOCKFIX_TEST_VEEAM_PASSWORD"], "secret")
            self.assertEqual(os.environ["LOCKFIX_VEEAM_BASE_URL"], "https://192.168.219.230:9419")

    def test_webui_veeam_backup_returns_error_without_stale_success(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"job_name": "Agent_backup"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return False

            def poll_veeam_api(self, server, port, local_payload):
                return webui.LockFixWebHandler.poll_veeam_api(self, server, port, local_payload)

        stale_path = webui.ROOT / "runtime" / "veeam_interlock_state.json"
        stale_path.parent.mkdir(parents=True, exist_ok=True)
        old_value = stale_path.read_text(encoding="utf-8") if stale_path.exists() else None
        stale_path.write_text(
            json.dumps({"api_synced": True, "status": "Success", "progress_percent": 100, "current_step": 5}),
            encoding="utf-8",
        )
        try:
            with patch.object(webui, "run_veeam_diagnostics", side_effect=RuntimeError("configured Veeam check failed")):
                result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        finally:
            if old_value is None:
                stale_path.unlink(missing_ok=True)
            else:
                stale_path.write_text(old_value, encoding="utf-8")

        self.assertFalse(result["api_synced"])
        self.assertEqual(result["progress_percent"], 0)
        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["state_source"], "veeam_rest_api_error")
        self.assertEqual(result["step_logs"][0]["state"], "PENDING")
        self.assertFalse(result["step_logs"][0]["transition_allowed"])
        self.assertEqual(result["step_logs"][0]["progress_percent"], "")
        self.assertIn("configured Veeam check failed", result["session_logs"][0]["actions"][0])

    def test_webui_keeps_last_veeam_detail_logs_when_api_waits(self) -> None:
        class Probe:
            pass

        path = webui.ROOT / "runtime" / "veeam_last_session_logs.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        old_value = path.read_text(encoding="utf-8") if path.exists() else None
        log = {
            "name": "Agent_backup",
            "status": "Success",
            "actions": ["Agent_backup processing finished at 2026-05-01T07:00:08+09:00"],
            "duration": "00:08",
            "progress_percent": 100,
            "backup_size": "479.0 GB",
            "transferred": "0 B",
            "speed": "0 KB/s",
        }
        try:
            webui.LockFixWebHandler.save_veeam_last_logs(Probe(), [log], "2026-05-01 07:00:09")
            logs = webui.LockFixWebHandler.load_veeam_last_logs(Probe())
        finally:
            if old_value is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(old_value, encoding="utf-8")

        self.assertEqual(logs[0]["name"], "Agent_backup")
        self.assertTrue(logs[0]["last_known"])
        self.assertEqual(logs[0]["backup_size"], "479.0 GB")
        self.assertIn("Last retained Veeam detail log", logs[0]["actions"][-1])

    def test_webui_auto_isolate_uses_context_controller(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        marker_path = webui.ROOT / "runtime" / "veeam_auto_isolate.json"
        old_value = marker_path.read_text(encoding="utf-8") if marker_path.exists() else None
        payload = {
            "slot_id": "BAY-01",
            "job": "Agent_backup",
            "result": "Success",
            "progress_percent": 100,
            "started_at": f"test-{uuid.uuid4().hex}",
            "ended_at": f"test-{uuid.uuid4().hex}",
        }
        try:
            result = webui.LockFixWebHandler.auto_isolate_after_veeam_success(Probe(), payload, "Success", "2026-05-01 10:00:00")
        finally:
            if old_value is None:
                marker_path.unlink(missing_ok=True)
            else:
                marker_path.write_text(old_value, encoding="utf-8")

        self.assertTrue(result["triggered"])
        self.assertEqual(result["state"], "ISOLATED")

    def test_webui_airgap_step2_appends_flush_audit_logs_after_veeam_logs(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {
                "ts": "2026-05-04T12:00:01+00:00",
                "event": "disk.flush.start",
                "slot_id": "BAY-01",
                "mount_point": "D:\\copy",
                "device": "D:\\",
            },
            {
                "ts": "2026-05-04T12:00:02+00:00",
                "event": "disk.flush.tick",
                "slot_id": "BAY-01",
                "elapsed_seconds": 1,
                "mount_point": "D:\\copy",
            },
            {
                "ts": "2026-05-04T12:00:03+00:00",
                "event": "disk.flush",
                "slot_id": "BAY-01",
                "output": "Windows Server flush checkpoint completed",
            },
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 25,
                    "current_step": 2,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "-",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "actions": ["Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37"],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]

        self.assertEqual(actions[0], "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37")
        self.assertTrue(any("LOCK-FIX STEP 2 DETAIL" in item for item in actions))
        self.assertGreater(actions.index(next(item for item in actions if "LOCK-FIX Flush GUARD OK" in item)), 0)
        self.assertTrue(any("LOCK-FIX Flush TARGET" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush COMMAND" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush MONITOR" in item for item in actions))
        self.assertGreater(actions.index(next(item for item in actions if "LOCK-FIX Flush START" in item)), 0)
        self.assertTrue(any("LOCK-FIX Flush TICK 1s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 2 COMPLETE" in item for item in actions))

    def test_webui_airgap_step3_appends_io_quiet_logs_after_flush_logs(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "Windows Server flush checkpoint completed"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.io_quiet", "slot_id": "BAY-01", "seconds": 3},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 50,
                    "current_step": 3,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "-",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "actions": ["Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37"],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]
        flush_ok_index = actions.index(next(item for item in actions if "LOCK-FIX Flush OK" in item))
        io_start_index = actions.index(next(item for item in actions if "LOCK-FIX I/O Check START" in item))

        self.assertGreater(io_start_index, flush_ok_index)
        self.assertTrue(any("LOCK-FIX STEP 3 DETAIL" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check WINDOW" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check MONITOR" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check GATE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check TICK 1s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check TICK 2s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 3 COMPLETE" in item for item in actions))

    def test_webui_airgap_step3_deduplicates_overlapping_io_ticks(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 3, "remaining_seconds": 0, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet.dry_run", "slot_id": "BAY-01", "seconds": 3},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.io_quiet.dry_run", "slot_id": "BAY-01", "seconds": 3},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_io_quiet_operation_actions(Probe(), "BAY-01", 3)

        self.assertEqual(len([item for item in actions if "I/O Check TICK 2s" in item]), 1)
        self.assertLess(
            actions.index(next(item for item in actions if "I/O Check TICK 1s" in item)),
            actions.index(next(item for item in actions if "I/O Check TICK 3s" in item)),
        )
        self.assertEqual(len([item for item in actions if "I/O Check OK" in item]), 1)

    def test_webui_airgap_step4_and_step5_logs_follow_previous_flow(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "Windows Server flush checkpoint completed"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet", "slot_id": "BAY-01", "seconds": 3},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.unmount.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\", "drive_letter": "D", "os_volume_protected": True},
            {"ts": "2026-05-04T12:00:08+00:00", "event": "disk.unmount.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:09+00:00", "event": "disk.unmount", "slot_id": "BAY-01", "output": "Dismount-Volume completed"},
            {"ts": "2026-05-04T12:00:10+00:00", "event": "power.mock.off.start", "slot_id": "BAY-01"},
            {"ts": "2026-05-04T12:00:11+00:00", "event": "power.mock.off.tick", "slot_id": "BAY-01", "elapsed_seconds": 1},
            {"ts": "2026-05-04T12:00:12+00:00", "event": "power.mock.off", "slot_id": "BAY-01"},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 75,
                    "current_step": 5,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "-",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "actions": ["Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37"],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]
        step2_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 2 COMPLETE" in item))
        step3_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 3 COMPLETE" in item))
        step4_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 4 DETAIL" in item))
        step5_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 5 DETAIL" in item))

        self.assertLess(step2_index, step3_index)
        self.assertLess(step3_index, step4_index)
        self.assertLess(step4_index, step5_index)
        self.assertTrue(any("LOCK-FIX Unmount GUARD OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Unmount COMMAND" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Unmount OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 COMPLETE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY - Unmount detailed audit trail is retained" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY DETAIL - slot BAY-01, result OK, records 3" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY EVENTS - disk.unmount.start, disk.unmount.tick, disk.unmount" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF TARGET" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 COMPLETE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY - Power OFF detailed audit trail is retained" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY DETAIL - slot BAY-01, result OK, records 3" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY EVENTS - power.mock.off.start, power.mock.off.tick, power.mock.off" in item for item in actions))

    def test_webui_airgap_step5_logs_power_status_proof_requirement(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:10+00:00", "event": "power.command.off.start", "slot_id": "BAY-01", "command": ["powershell", "-File", "lockfix_power_control.ps1"]},
            {"ts": "2026-05-04T12:00:11+00:00", "event": "power.command.off.tick", "slot_id": "BAY-01", "elapsed_seconds": 1},
            {"ts": "2026-05-04T12:00:12+00:00", "event": "power.command.off", "slot_id": "BAY-01", "output": "OFF command completed"},
            {
                "ts": "2026-05-04T12:00:13+00:00",
                "event": "power.command.status.missing",
                "slot_id": "BAY-01",
                "requirement": "Configure power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE.",
            },
            {
                "ts": "2026-05-04T12:00:14+00:00",
                "event": "power.off.proof.required",
                "slot_id": "BAY-01",
                "reason": "power.status_command is not configured",
                "required_config": "power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE",
            },
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_power_off_operation_actions(Probe(), "BAY-01", 5)

        self.assertTrue(any("LOCK-FIX Power OFF PROOF REQUIRED - actual OFF proof requires a PDU/relay/storage controller status response" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF PROOF REQUIRED - power.status_command is not configured" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY EVENTS - power.command.off.start, power.command.off.tick, power.command.off, power.command.status.missing, power.off.proof.required" in item for item in actions))

    def test_webui_airgap_flush_logs_keep_only_latest_flush_cycle(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T11:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\old", "device": "D:\\"},
            {"ts": "2026-05-04T11:00:02+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "old flush"},
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\new", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\new"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "new flush"},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_flush_operation_actions(Probe(), "BAY-01", 2)

        self.assertEqual(len(actions), 9)
        self.assertNotIn("old flush", "\n".join(actions))
        self.assertIn("new flush", "\n".join(actions))

    def test_webui_veeam_backup_exposes_same_diagnostics_as_veeam_test(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"enabled": True, "job_name": "Agent_backup"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        expected = {
            "source": "python_veeam_client",
            "diagnostics": {
                "vbr_rest_9419": {"port": {"ok": True, "code": "OK"}},
                "authentication": {"ok": True, "token_received": True, "password_logged": False},
                "jobs": {"ok": True, "count": 0, "items": []},
                "sessions": {"ok": True, "count": 16, "items": []},
                "matching": {"job_id": "", "job_name": "Agent_backup", "strategy": "backup_restore_point", "matched": True},
            },
            "api": {
                "source": "python_veeam_client",
                "jobs": {"ok": True, "count": 0},
                "sessions": {"ok": True, "count": 16},
                "matching": {"job_id": "", "job_name": "Agent_backup", "strategy": "backup_restore_point", "matched": True},
            },
        }

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_interlock_runtime(self, now):
                return {
                    "server": "127.0.0.1",
                    "port": 9419,
                    "connected": True,
                    "api_synced": True,
                    "port_open": True,
                    "api_checks": {},
                    "last_checked": "2026-05-01 10:00:00",
                    "state_source": "veeam_rest_api",
                    "message": "ok",
                    "current_step": 2,
                    "job": "Agent_backup",
                    "progress_percent": 100,
                    "payload": {"status": "Success", "progress_percent": 100},
                    "step_logs": [
                        {"time": "2026-05-01 10:00:00", "transition_allowed": True, "step": 1, "code": "BACKUP_COMPLETED", "detail": "ok", "source": "test"},
                        {"time": "2026-05-01 10:00:00", "transition_allowed": True, "step": 2, "code": "FLUSHING", "detail": "ok", "source": "test"},
                    ],
                    "session_logs": [],
                    "auto_isolate": {},
                }

        with patch.object(webui, "run_veeam_diagnostics", return_value=expected):
            result = webui.LockFixWebHandler.veeam_backup_summary(Probe())

        self.assertEqual(result["diagnostics"]["vbr_rest_9419"], expected["diagnostics"]["vbr_rest_9419"])
        self.assertEqual(result["diagnostics"]["authentication"], expected["diagnostics"]["authentication"])
        self.assertEqual(result["diagnostics"]["jobs"]["count"], expected["diagnostics"]["jobs"]["count"])
        self.assertEqual(result["diagnostics"]["sessions"]["count"], expected["diagnostics"]["sessions"]["count"])
        self.assertEqual(result["diagnostics"]["matching"], expected["diagnostics"]["matching"])
        self.assertEqual(result["api"]["jobs"]["count"], expected["api"]["jobs"]["count"])
        self.assertEqual(result["api"]["sessions"]["count"], expected["api"]["sessions"]["count"])
        self.assertEqual(result["api"]["matching"], expected["api"]["matching"])
        self.assertEqual(result["api"]["source"], "python_veeam_client")
        self.assertEqual(result["source"], "python_veeam_client")

    def test_veeam_watcher_runs_jobs_sessions_match_status_then_isolate(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "job_id": "job-123",
            "job_name": "Agent_backup",
            "isolate_on_status": ["Success"],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)
        controller = LockFixController(config)

        diagnostics = {
            "success": True,
            "source": "python_veeam_client",
            "matching": {"strategy": "job_id", "matched": True},
            "latest_configured_session": {"repository_path": "F:\\BackupCopyRepo"},
            "isolate_condition": {
                "watcher_enabled": True,
                "matched_session": True,
                "session_id": "session-123",
                "job_name": "Agent_backup",
                "job_id": "job-123",
                "status": "Success",
                "status_allowed": True,
                "already_processed": False,
                "would_call_isolate": True,
            },
            "pre_isolate_checks": {"ready": True},
        }
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            watcher = VeeamWatcher(config, controller, state_path=tmp_path / "veeam_watcher_state.json")
            with patch("lockfix.veeam_watcher.run_veeam_diagnostics", return_value=diagnostics):
                result = watcher.poll_once(slot_id="BAY-01")

        self.assertEqual(result["action"], "isolated")
        self.assertEqual(result["session_id"], "session-123")
        self.assertEqual(result["repository_path"], "F:\\BackupCopyRepo")
        self.assertEqual(controller.status()["BAY-01"], "ISOLATED")

    def test_veeam_webui_test_does_not_launch_process_when_8088_is_closed(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)

        with patch(
            "lockfix.veeam_webui_check.run_veeam_diagnostics",
            return_value={"config": {"base_url": "https://127.0.0.1:9419"}, "latest_configured_session": {}},
        ):
            with patch(
                "lockfix.veeam_webui_check.fetch_webui_veeam_backup",
                side_effect=WebUiServerNotRunning("connection refused"),
            ) as fetch:
                result = compare_veeam_test_with_webui(config, controller)

        fetch.assert_called_once()
        self.assertFalse(result["process_launch_attempted"])
        self.assertFalse(result["webui"]["running"])
        self.assertEqual(result["webui"]["message"], "Web UI server is not running")
        self.assertIn("not treated as a Veeam REST integration failure", result["comparison"]["message"])

    def test_veeam_webui_test_keeps_http_error_separate_from_not_running(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)

        with patch(
            "lockfix.veeam_webui_check.run_veeam_diagnostics",
            return_value={"config": {"base_url": "https://127.0.0.1:9419"}, "latest_configured_session": {}},
        ):
            with patch(
                "lockfix.veeam_webui_check.fetch_webui_veeam_backup",
                side_effect=HTTPError("http://127.0.0.1:8088/api/veeam-backup", 500, "Internal Server Error", {}, None),
            ):
                result = compare_veeam_test_with_webui(config, controller)

        self.assertFalse(result["process_launch_attempted"])
        self.assertTrue(result["webui"]["running"])
        self.assertEqual(result["webui"]["message"], "Web UI HTTP check failed")
        self.assertIn("separate from Veeam REST 9419 validation", result["comparison"]["message"])

    def test_veeam_webui_test_compares_http_response_with_veeam_test(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)
        veeam_test_payload = {
            "config": {
                "base_url": "https://127.0.0.1:9419",
                "api_version": "1.2-rev1",
                "verify_ssl": False,
                "job_name": "Agent_backup",
                "job_id": "",
            },
            "authentication": {"ok": True},
            "jobs": {"ok": True, "count": 0},
            "sessions": {"ok": True, "count": 16},
            "matching": {"matched": True, "strategy": "backup_restore_point"},
            "latest_configured_session": {
                "source": "python_veeam_client",
                "name": "Agent_backup",
                "status": "Success",
                "result": "Success",
                "duration": "00:09",
            },
            "vbr_rest_9419": {"port": {"ok": True}},
        }
        webui_payload = {
            "source": "python_veeam_client",
            "api": {
                "source": "python_veeam_client",
                "base_url": "https://127.0.0.1:9419",
                "api_version": "1.2-rev1",
                "verify_ssl": False,
                "token": {"ok": True},
                "jobs": {"ok": True, "count": 0},
                "sessions": {"ok": True, "count": 16},
                "matching": {"matched": True, "strategy": "backup_restore_point"},
                "job_name": "Agent_backup",
                "job_id": "",
            },
            "job": {"name": "Agent_backup", "result": "Success", "duration": "00:09"},
        }

        with patch("lockfix.veeam_webui_check.run_veeam_diagnostics", return_value=veeam_test_payload):
            with patch("lockfix.veeam_webui_check.fetch_webui_veeam_backup", return_value=webui_payload):
                result = compare_veeam_test_with_webui(config, controller)

        self.assertTrue(result["webui"]["running"])
        self.assertTrue(result["webui"]["ok"])
        self.assertTrue(result["comparison"]["ok"])
        self.assertTrue(all(result["comparison"]["matches"].values()))
        self.assertEqual(summarize_webui_backup(webui_payload)["source"], "python_veeam_client")


if __name__ == "__main__":
    unittest.main()

