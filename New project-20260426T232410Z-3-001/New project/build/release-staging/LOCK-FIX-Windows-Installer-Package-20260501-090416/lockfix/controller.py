from __future__ import annotations

from .audit import AuditLogger
from .command import CommandRunner
from .config import LockFixConfig
from .disk import DiskOperator
from .hashcheck import verify_manifest
from .identity import verify_uid
from .power import build_power_controller
from .state_store import StateStore
from .states import LockFixState


class LockFixController:
    def __init__(self, config: LockFixConfig) -> None:
        self.config = config
        self.audit = AuditLogger(config.audit_log_path)
        self.state = StateStore(config.state_path)
        self.runner = CommandRunner(config.dry_run)
        self.disk = DiskOperator(self.runner, self.audit)

    def set_state(self, slot_id: str, state: LockFixState, **payload: object) -> None:
        self.state.set(slot_id, state)
        self.audit.write("state.transition", slot_id=slot_id, state=state.value, **payload)

    def isolate(self, slot_id: str) -> LockFixState:
        slot = self.config.slot(slot_id)
        power = build_power_controller(self.runner, slot.power, self.audit)
        try:
            self.set_state(slot_id, LockFixState.BACKUP_COMPLETED)
            self.set_state(slot_id, LockFixState.FLUSHING)
            self.disk.flush(slot)
            self.set_state(slot_id, LockFixState.IO_CHECKING)
            self.disk.wait_for_quiet_io(slot, self.config.io_quiet_seconds)
            self.set_state(slot_id, LockFixState.UNMOUNTING)
            self.disk.unmount(slot)
            self.set_state(slot_id, LockFixState.POWERING_OFF)
            power.off(slot_id)
            self.set_state(slot_id, LockFixState.ISOLATED)
            return LockFixState.ISOLATED
        except Exception as exc:
            self.set_state(slot_id, LockFixState.ERROR, error=str(exc))
            raise

    def reconnect(self, slot_id: str) -> LockFixState:
        slot = self.config.slot(slot_id)
        power = build_power_controller(self.runner, slot.power, self.audit)
        try:
            self.set_state(slot_id, LockFixState.RECONNECT_REQUESTED)
            self.set_state(slot_id, LockFixState.POWERING_ON)
            power.on(slot_id)
            self.set_state(slot_id, LockFixState.WAITING_DISK)
            self.disk.wait_for_disk(slot, self.config.disk_wait_seconds)
            self.set_state(slot_id, LockFixState.VERIFYING_UID)
            uid_ok, current_uid = verify_uid(slot)
            self.audit.write("verify.uid", slot_id=slot_id, ok=uid_ok, uid=current_uid)
            if not uid_ok:
                power.off(slot_id)
                self.set_state(slot_id, LockFixState.QUARANTINE, reason="uid_mismatch")
                return LockFixState.QUARANTINE

            self.disk.mount_readonly(slot)
            self.set_state(slot_id, LockFixState.MOUNTED_READONLY)
            self.set_state(slot_id, LockFixState.VERIFYING_HASH)
            hash_ok, actual, expected = verify_manifest(slot.mount_point, slot.manifest_path)
            self.audit.write(
                "verify.hash",
                slot_id=slot_id,
                ok=hash_ok,
                actual=actual,
                expected=expected,
            )
            if not hash_ok:
                self.disk.unmount(slot)
                power.off(slot_id)
                self.set_state(slot_id, LockFixState.QUARANTINE, reason="hash_mismatch")
                return LockFixState.QUARANTINE

            self.disk.remount_readwrite(slot)
            self.set_state(slot_id, LockFixState.ONLINE_VERIFIED_RW)
            return LockFixState.ONLINE_VERIFIED_RW
        except Exception as exc:
            self.set_state(slot_id, LockFixState.ERROR, error=str(exc))
            raise

    def status(self) -> dict[str, str]:
        return self.state.read_all()
