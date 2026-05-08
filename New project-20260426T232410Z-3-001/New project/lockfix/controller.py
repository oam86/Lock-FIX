from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import secrets

from .audit import AuditLogger
from .command import CommandRunner
from .config import LockFixConfig, SlotConfig
from .disk import DiskOperator
from .hashcheck import verify_manifest
from .identity import slot_uid, verify_uid
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

    def isolate(self, slot_id: str, repository_path: str = "") -> LockFixState:
        slot = self.repository_slot(self.config.slot(slot_id), repository_path)
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
            power_status = power.status(slot_id)
            if power_status.get("ok") is True:
                self.audit.write(
                    "power.off.proof",
                    slot_id=slot_id,
                    proved=True,
                    source="controller_status_response",
                    message="Physical power OFF was proved by the PDU/relay/storage controller status response.",
                    power_status=power_status,
                )
            else:
                self.audit.write(
                    "power.off.proof.required",
                    slot_id=slot_id,
                    proved=False,
                    source="controller_status_response",
                    reason=power_status.get("reason") or power_status.get("error") or "controller status did not confirm OFF",
                    message="Power OFF can be proved only when the PDU/relay/storage controller status response confirms OFF.",
                    required_config="power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE",
                    power_status=power_status,
                )
            self.set_state(slot_id, LockFixState.ISOLATED)
            return LockFixState.ISOLATED
        except Exception as exc:
            self.set_state(slot_id, LockFixState.ERROR, error=str(exc))
            raise

    def reconnect(self, slot_id: str, repository_path: str = "") -> LockFixState:
        slot = self.repository_slot(self.config.slot(slot_id), repository_path)
        power = build_power_controller(self.runner, slot.power, self.audit)
        try:
            self.set_state(slot_id, LockFixState.RECONNECT_REQUESTED)
            self.set_state(slot_id, LockFixState.POWERING_ON)
            try:
                power.on(slot_id)
            except Exception as exc:
                self.audit.write(
                    "power.on.reconnect.warning",
                    slot_id=slot_id,
                    error=str(exc),
                    message="Power ON command failed. LOCK-FIX will check whether the stored backup disk is already visible before stopping emergency reconnect.",
                )
                if not self.disk.partition_visible(slot):
                    self.audit.write(
                        "power.on.reconnect.blocked",
                        slot_id=slot_id,
                        error=str(exc),
                        message="Power ON failed and the stored backup disk is not visible to Windows. Configure the real PDU/relay/storage controller ON command.",
                    )
                    raise
                self.audit.write(
                    "power.on.reconnect.continue_disk_visible",
                    slot_id=slot_id,
                    message="Power ON failed, but the stored backup disk is already visible. Continuing with access path recovery and verification.",
                )
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

    def emergency_access_hash(self, slot_id: str) -> str:
        slot = self.config.slot(slot_id)
        expected = str(slot.expected_uid or "").strip()
        if expected and expected != "replace-with-registered-uid":
            return expected
        return slot_uid(slot)

    def emergency_reconnect(self, slot_id: str, verification_hash: str) -> LockFixState:
        slot = self.config.slot(slot_id)
        expected = self.emergency_access_hash(slot_id).strip()
        provided = str(verification_hash or "").strip()
        provided_digest = hashlib.sha256(provided.encode("utf-8")).hexdigest()[:16] if provided else ""
        expected_digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()[:16] if expected else ""

        self.audit.write(
            "emergency.reconnect.request",
            slot_id=slot_id,
            mount_point=str(slot.mount_point),
            device=slot.device,
            provided_hash_digest=provided_digest,
        )
        if not expected or not provided or not secrets.compare_digest(provided.lower(), expected.lower()):
            self.audit.write(
                "emergency.reconnect.denied",
                slot_id=slot_id,
                reason="verification_hash_mismatch",
                provided_hash_digest=provided_digest,
                expected_hash_digest=expected_digest,
            )
            raise PermissionError("emergency verification hash mismatch")

        self.audit.write(
            "emergency.reconnect.approved",
            slot_id=slot_id,
            expected_hash_digest=expected_digest,
        )
        state = self.reconnect(slot_id)
        self.audit.write("emergency.reconnect.complete", slot_id=slot_id, state=state.value)
        return state

    def isolation_proof(self, slot_id: str, repository_path: str = "") -> dict[str, object]:
        slot = self.repository_slot(self.config.slot(slot_id), repository_path)
        power = build_power_controller(self.runner, slot.power, self.audit)
        volume_proof = self.disk.unmount_proof(slot)
        power_proof = power.status(slot_id)
        volume_ok = volume_proof.get("ok") is True
        power_ok = power_proof.get("ok") is True
        if volume_ok and power_ok:
            status = "PROVED"
        elif volume_ok and power_proof.get("provable") is False:
            status = "VOLUME_PROVED_POWER_NOT_PROVABLE"
        else:
            status = "NOT_PROVED"
        result = {
            "slot_id": slot_id,
            "status": status,
            "proved": status == "PROVED",
            "volume_unmounted": volume_proof,
            "power_off": power_proof,
        }
        self.audit.write("isolation.proof", **result)
        return result

    def repository_slot(self, slot: SlotConfig, repository_path: str = "") -> SlotConfig:
        selected_path = (repository_path or self.config.veeam.target_repository_path or "").strip()
        if not (self.config.veeam.enabled and self.config.veeam.require_backup_copy and selected_path):
            self.audit.write(
                "veeam.repository.volume.target",
                slot_id=slot.slot_id,
                source="slot_config",
                repository_path=selected_path,
                target_volume=str(slot.mount_point),
                message="Using configured slot volume because no Veeam Backup Copy repository path was supplied.",
            )
            return slot

        target_volume = repository_volume_root(selected_path)
        normalized = target_volume.strip().replace("/", "\\").rstrip("\\").lower()
        if normalized in {"", "\\", "c:"}:
            self.audit.write(
                "veeam.repository.volume.blocked",
                slot_id=slot.slot_id,
                repository_path=selected_path,
                target_volume=target_volume,
                reason="windows_c_os_volume_protected",
            )
            raise ValueError(f"Veeam Backup Copy repository cannot target protected Windows OS volume: {selected_path}")

        current = str(slot.mount_point).strip().replace("/", "\\").rstrip("\\").lower()
        source = "runtime_veeam_repository" if repository_path else "config.veeam.target_repository_path"
        self.audit.write(
            "veeam.repository.volume.target",
            slot_id=slot.slot_id,
            source=source,
            repository_path=selected_path,
            target_volume=target_volume,
            configured_slot_volume=str(slot.mount_point),
            message="LOCK-FIX will isolate only the Veeam Backup Copy repository volume.",
        )
        if current == normalized:
            return slot
        return replace(slot, device=target_volume, mount_point=Path(target_volume))

    def status(self) -> dict[str, str]:
        return self.state.read_all()


def repository_volume_root(repository_path: str) -> str:
    value = str(repository_path or "").strip().replace("/", "\\")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        return f"{value[0].upper()}:\\"
    raise ValueError(f"Veeam Backup Copy repository path must be a local Windows volume path, for example F:\\copy: {repository_path}")
