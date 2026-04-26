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
        output = self.runner.run(["sync"])
        self.audit.write("disk.flush", slot_id=slot.slot_id, output=output)

    def wait_for_quiet_io(self, slot: SlotConfig, seconds: int) -> None:
        if self.runner.dry_run:
            self.audit.write("disk.io_quiet.dry_run", slot_id=slot.slot_id, seconds=seconds)
            return
        time.sleep(seconds)
        self.audit.write("disk.io_quiet", slot_id=slot.slot_id, seconds=seconds)

    def unmount(self, slot: SlotConfig) -> None:
        output = self.runner.run(["umount", str(slot.mount_point)])
        self.audit.write("disk.unmount", slot_id=slot.slot_id, output=output)

    def wait_for_disk(self, slot: SlotConfig, timeout_seconds: int) -> None:
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
        output = self.runner.run(["mount", "-o", "ro", slot.device, str(slot.mount_point)])
        self.audit.write("disk.mount_ro", slot_id=slot.slot_id, output=output)

    def remount_readwrite(self, slot: SlotConfig) -> None:
        output = self.runner.run(["mount", "-o", "remount,rw", str(slot.mount_point)])
        self.audit.write("disk.mount_rw", slot_id=slot.slot_id, output=output)
