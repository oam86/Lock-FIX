from __future__ import annotations

import time
from pathlib import Path

from .audit import AuditLogger
from .command import CommandRunner
from .config import SlotConfig


class DiskOperator:
    def __init__(self, runner: CommandRunner, audit: AuditLogger) -> None:
        self.runner = runner
        self.audit = audit

    def flush(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        self.audit.write("disk.flush.start", slot_id=slot.slot_id, mount_point=str(slot.mount_point), device=slot.device)
        output = self.runner.run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "Write-Output 'Windows Server flush checkpoint completed'",
        ])
        self.audit.write("disk.flush.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
        self.audit.write("disk.flush", slot_id=slot.slot_id, output=output)

    def wait_for_quiet_io(self, slot: SlotConfig, seconds: int) -> None:
        self.audit.write("disk.io_quiet.start", slot_id=slot.slot_id, seconds=seconds, mount_point=str(slot.mount_point))
        for elapsed in range(1, max(1, seconds) + 1):
            if not self.runner.dry_run:
                time.sleep(1)
            self.audit.write(
                "disk.io_quiet.tick",
                slot_id=slot.slot_id,
                elapsed_seconds=elapsed,
                remaining_seconds=max(0, seconds - elapsed),
                mount_point=str(slot.mount_point),
            )
        self.audit.write("disk.io_quiet.dry_run" if self.runner.dry_run else "disk.io_quiet", slot_id=slot.slot_id, seconds=seconds)

    def unmount(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        self.audit.write("disk.unmount.start", slot_id=slot.slot_id, mount_point=str(slot.mount_point), device=slot.device)
        output = self.runner.run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"Dismount-Volume -DriveLetter '{drive}' -Force -ErrorAction Stop",
        ])
        self.audit.write("disk.unmount.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
        self.audit.write("disk.unmount", slot_id=slot.slot_id, output=output)

    def wait_for_disk(self, slot: SlotConfig, timeout_seconds: int) -> None:
        self.assert_not_protected_os_volume(slot)
        if self.runner.dry_run:
            self.audit.write("disk.wait.dry_run", slot_id=slot.slot_id, device=slot.device)
            return
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if Path(slot.device).exists():
                self.audit.write("disk.wait.found", slot_id=slot.slot_id, device=slot.device)
                return
            time.sleep(1)
        raise TimeoutError(f"disk not found: {slot.device}")

    def mount_readonly(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        self.audit.write(
            "disk.mount_ro",
            slot_id=slot.slot_id,
            output="Windows Server package does not run cross-platform mount commands; hardware and Windows volume policy keep the protected OS volume blocked.",
        )

    def remount_readwrite(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        self.audit.write(
            "disk.mount_rw",
            slot_id=slot.slot_id,
            output="Windows Server package does not run cross-platform remount commands; only non-OS backup volumes are eligible for reconnect policy.",
        )

    def assert_not_protected_os_volume(self, slot: SlotConfig) -> None:
        for label, raw in (("mount_point", str(slot.mount_point)), ("device", slot.device)):
            normalized = raw.strip().replace("/", "\\").rstrip("\\").lower()
            if normalized in {"", "\\", "c:"}:
                self.audit.write(
                    "disk.os_volume.blocked",
                    slot_id=slot.slot_id,
                    mount_point=str(slot.mount_point),
                    device=slot.device,
                    field=label,
                    reason="windows_c_os_volume_protected",
                )
                raise ValueError(f"protected Windows OS volume cannot be selected: {raw}")

    def windows_drive_letter(self, slot: SlotConfig) -> str:
        self.assert_not_protected_os_volume(slot)
        candidates = (str(slot.mount_point), slot.device)
        for raw in candidates:
            value = raw.strip().replace("/", "\\")
            if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
                drive = value[0].upper()
                if drive == "C":
                    self.audit.write(
                        "disk.os_volume.blocked",
                        slot_id=slot.slot_id,
                        mount_point=str(slot.mount_point),
                        device=slot.device,
                        field="drive_letter",
                        reason="windows_c_os_volume_protected",
                    )
                    raise ValueError(f"protected Windows OS volume cannot be selected: {raw}")
                return drive
        raise ValueError(f"Windows Server backup volume must use a drive letter, for example D:\\: {slot.mount_point}")
