from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import secrets

from .approvals import ApprovalStore
from .audit import AuditLogger
from .command import CommandRunner
from .config import LockFixConfig, SlotConfig
from .disk import DiskOperator
from .hashcheck import verify_manifest
from .identity import slot_uid, verify_uid
from .power import build_power_controller
from .secure_store import LockFixSecureStore
from .state_store import StateStore
from .states import LockFixState


class LockFixController:
    def __init__(self, config: LockFixConfig) -> None:
        self.config = config
        self.audit = AuditLogger(config.audit_log_path)
        self.state = StateStore(config.state_path)
        self.runner = CommandRunner(config.dry_run)
        self.disk = DiskOperator(self.runner, self.audit)
        self.secure_store = LockFixSecureStore.from_runtime(config.audit_log_path.parent)
        self.online_approval_path = config.audit_log_path.parent / "online-approvals.json"
        self.approvals = ApprovalStore(config.audit_log_path.parent / "approvals.json", self.audit)

    def set_state(self, slot_id: str, state: LockFixState, **payload: object) -> None:
        self.state.set(slot_id, state)
        self.audit.write("state.transition", slot_id=slot_id, state=state.value, **payload)

    def isolate(self, slot_id: str, repository_path: str = "") -> LockFixState:
        self.audit.write("disk.offline.request", slot_id=slot_id, resourceType="DISK", resourceId=slot_id)
        self.approvals.require_approved("DISK_OFFLINE", slot_id)
        slot = self.repository_slot(self.config.slot(slot_id), repository_path)
        try:
            self.set_state(slot_id, LockFixState.BACKUP_COMPLETED)
            self.set_state(slot_id, LockFixState.FLUSHING)
            self.disk.flush(slot)
            self.set_state(slot_id, LockFixState.IO_CHECKING)
            self.disk.wait_for_quiet_io(slot, self.config.io_quiet_seconds)
            self.set_state(slot_id, LockFixState.UNMOUNTING)
            self.disk.unmount(slot)
            self.clear_online_approval(slot_id, "isolation_started")
            self.set_state(slot_id, LockFixState.DISK_OFFLINING)
            self.disk.offline(slot)
            offline_proof = self.disk.read_storage_state(slot)
            if not self.config.dry_run and not bool(offline_proof.get("isOffline", False)):
                error = "True Disk Offline proof was not obtained after Veeam backup completion."
                self.audit.write(
                    "disk.offline.strict.error",
                    slot_id=slot_id,
                    disk_number=offline_proof.get("diskNumber", ""),
                    disk_unique_id=offline_proof.get("diskUniqueId", ""),
                    drive_letter=offline_proof.get("drive", ""),
                    is_offline=offline_proof.get("isOffline", False),
                    path_reachable=offline_proof.get("pathReachable", True),
                    error=error,
                )
                raise RuntimeError(error)
            self.audit.write(
                "power.mock.status",
                slot_id=slot_id,
                ok=None,
                requirement="Use Windows disk offline proof for current LOCK-FIX storage isolation.",
                compatibility_note="Legacy power proof compatibility event; actual isolation uses Windows disk offline proof or removable-media access-path removal proof.",
            )
            self.audit.write(
                "power.off.proof.required",
                slot_id=slot_id,
                reason="Power OFF can be proved only when the PDU/relay/storage controller status response confirms OFF.",
                required_config="power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE",
                compatibility_note="Windows disk offline proof is recorded separately as disk.offline.proof.",
            )
            self.audit.write(
                "disk.offline.proof",
                slot_id=slot_id,
                proved=True,
                source="windows_storage_stack",
                disk_number=offline_proof.get("diskNumber", ""),
                disk_unique_id=offline_proof.get("diskUniqueId", ""),
                drive_letter=offline_proof.get("drive", ""),
                is_offline=offline_proof.get("isOffline", True),
                offline_equivalent=offline_proof.get("offlineEquivalent", False),
                path_reachable=offline_proof.get("pathReachable", False),
                method=offline_proof.get("method", "Set-Disk -IsOffline true"),
                message="LOCK-FIX completed Windows storage isolation using the recorded disk offline proof or removable-media access-path removal proof.",
            )
            self.set_state(slot_id, LockFixState.ISOLATED)
            return LockFixState.ISOLATED
        except Exception as exc:
            self.set_state(slot_id, LockFixState.ERROR, error=str(exc))
            raise

    def reconnect(self, slot_id: str, repository_path: str = "") -> LockFixState:
        self.audit.write("disk.online.request", slot_id=slot_id, resourceType="DISK", resourceId=slot_id)
        self.approvals.require_approved("DISK_ONLINE", slot_id)
        base_slot = self.config.slot(slot_id)
        remembered_path = str(self.disk.read_storage_state(base_slot).get("accessPath") or "").strip()
        reconnect_repository_path = str(repository_path or self.veeam_backup_copy_repository_path() or remembered_path).strip()
        slot = self.repository_slot(base_slot, reconnect_repository_path)
        try:
            approved_until = self.grant_online_approval(slot_id, ttl_seconds=900, reason="admin_emergency_reconnect")
            self.audit.write(
                "power.on.reconnect.warning",
                slot_id=slot_id,
                warning="Legacy relay/PDU power-on is bypassed; using Windows disk online/access-path reconnect workflow.",
            )
            self.audit.write(
                "power.on.reconnect.continue_disk_visible",
                slot_id=slot_id,
                message="Continuing reconnect because the disk/partition will be verified by the Windows storage stack.",
            )
            self.set_state(slot_id, LockFixState.RECONNECT_REQUESTED)
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=1,
                message="관리자 승인 기반 제한 시간 Online 요청",
                repository_path=str(reconnect_repository_path or slot.mount_point or slot.device),
                approved_until=approved_until,
            )
            self.set_state(slot_id, LockFixState.DISK_ONLINING)
            self.disk.online(slot, approved_until=approved_until)
            self.set_state(slot_id, LockFixState.WAITING_DISK)
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=2,
                message="Windows 저장소 캐시 갱신",
            )
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=3,
                message="Get-Disk, Get-Volume 로 볼륨 재조회",
            )
            self.disk.wait_for_disk(slot, self.config.disk_wait_seconds)
            drive = self.disk.windows_drive_letter(slot) if not self.runner.dry_run else "X"
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=4,
                message="기존에 기억한 드라이브 문자/접근 경로 재할당",
                drive_letter=drive,
            )
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=5,
                message="Mount-Volume 시도",
                drive_letter=drive,
            )
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=6,
                message="실제 경로 접근 가능 여부 확인",
                drive_letter=drive,
            )
            self.disk.ensure_access_path(slot, drive)
            self.set_state(slot_id, LockFixState.VERIFYING_UID)
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=7,
                message="UID 검증",
                drive_letter=drive,
            )
            uid_ok, current_uid = verify_uid(slot)
            self.audit.write("verify.uid", slot_id=slot_id, ok=uid_ok, uid=current_uid)
            if not uid_ok:
                self.quarantine_after_verification_mismatch(
                    slot_id,
                    slot,
                    "uid_mismatch",
                    f"UID mismatch detected. expected={slot.expected_uid or '-'}, actual={current_uid or '-'}",
                )
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
                self.quarantine_after_verification_mismatch(
                    slot_id,
                    slot,
                    "hash_mismatch",
                    f"Hash mismatch detected. expected={expected or '-'}, actual={actual or '-'}",
                )
                return LockFixState.QUARANTINE

            self.disk.remount_readwrite(slot)
            self.disk.verify_drive_accessible(slot, drive)
            self.set_state(slot_id, LockFixState.ONLINE_VERIFIED_RW)
            self.audit.write(
                "emergency.reconnect.step",
                slot_id=slot_id,
                step=8,
                message="읽기/쓰기 볼륨 연결 완료",
                drive_letter=drive,
            )
            return LockFixState.ONLINE_VERIFIED_RW
        except Exception as exc:
            self.set_state(slot_id, LockFixState.ERROR, error=str(exc))
            raise

    def quarantine_after_verification_mismatch(self, slot_id: str, slot: SlotConfig, reason: str, detail: str) -> None:
        power = build_power_controller(self.runner, slot.power, self.audit)
        self.audit.write(
            "emergency.quarantine.start",
            slot_id=slot_id,
            reason=reason,
            detail=detail,
            sequence="unmount -> relay_off -> quarantine -> admin_alert",
        )
        try:
            self.set_state(slot_id, LockFixState.UNMOUNTING, reason=reason)
            self.disk.unmount(slot)
            self.audit.write("emergency.quarantine.unmount", slot_id=slot_id, reason=reason, ok=True)
        except Exception as exc:
            self.audit.write("emergency.quarantine.unmount.error", slot_id=slot_id, reason=reason, error=str(exc))
        try:
            power.off(slot_id)
            self.audit.write("emergency.quarantine.relay_off", slot_id=slot_id, reason=reason, ok=True)
        except Exception as exc:
            self.audit.write("emergency.quarantine.relay_off.error", slot_id=slot_id, reason=reason, error=str(exc))
        try:
            self.set_state(slot_id, LockFixState.DISK_OFFLINING, reason=reason)
            self.disk.offline(slot)
        except Exception as exc:
            self.audit.write("emergency.quarantine.offline.error", slot_id=slot_id, reason=reason, error=str(exc))
        self.clear_online_approval(slot_id, reason)
        self.set_state(slot_id, LockFixState.QUARANTINE, reason=reason)
        self.audit.write(
            "admin.alert.quarantine",
            slot_id=slot_id,
            reason=reason,
            severity="CRITICAL",
            message=f"{detail}. Immediate unmount, relay OFF, and QUARANTINE were executed.",
            notification="관리자 경보: UID/Hash 불일치로 볼륨을 즉시 격리했습니다.",
        )

    def grant_online_approval(self, slot_id: str, ttl_seconds: int, reason: str) -> str:
        expires = datetime.now(timezone.utc) + timedelta(seconds=max(1, ttl_seconds))
        record = self.read_online_approvals()
        record[slot_id] = {"approved_until": expires.isoformat(), "reason": reason}
        self.write_online_approvals(record)
        self.audit.write(
            "disk.online.approved",
            slot_id=slot_id,
            approved_until=record[slot_id]["approved_until"],
            ttl_seconds=max(1, ttl_seconds),
            reason=reason,
            message="Administrator approval opened a limited-time disk online window.",
        )
        return str(record[slot_id]["approved_until"])

    def clear_online_approval(self, slot_id: str, reason: str) -> None:
        record = self.read_online_approvals()
        if slot_id in record:
            record.pop(slot_id, None)
            self.write_online_approvals(record)
        self.audit.write("disk.online.approval.cleared", slot_id=slot_id, reason=reason)

    def online_approval_active(self, slot_id: str) -> bool:
        record = self.read_online_approvals().get(slot_id, {})
        raw = str(record.get("approved_until") or "")
        if not raw:
            return False
        try:
            expires = datetime.fromisoformat(raw)
        except ValueError:
            return False
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        active = datetime.now(timezone.utc) <= expires.astimezone(timezone.utc)
        if not active:
            self.clear_online_approval(slot_id, "approval_expired")
        return active

    def reblock_unauthorized_online(self, slot_id: str, reason: str = "unauthorized_online_detected") -> bool:
        slot = self.config.slot(slot_id)
        return self.disk.enforce_offline_unless_approved(slot, self.online_approval_active(slot_id), reason)

    def read_online_approvals(self) -> dict:
        if not self.online_approval_path.exists():
            return {}
        try:
            data = json.loads(self.online_approval_path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def write_online_approvals(self, data: dict) -> None:
        self.online_approval_path.parent.mkdir(parents=True, exist_ok=True)
        self.online_approval_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def emergency_access_hash(self, slot_id: str) -> str:
        slot = self.config.slot(slot_id)
        expected = str(slot.expected_uid or "").strip()
        if expected and expected != "replace-with-registered-uid":
            return expected
        return slot_uid(slot)

    def emergency_reconnect(self, slot_id: str, verification_hash: str = "", repository_path: str = "") -> LockFixState:
        self.audit.write("emergency.unlock.request", slot_id=slot_id, resourceType="EMERGENCY", resourceId=slot_id)
        emergency_approval = self.approvals.require_approved("EMERGENCY_UNLOCK", slot_id)
        emergency_reason = str((emergency_approval.get("metadata") or {}).get("reason") or "").strip()
        if not emergency_reason:
            self.audit.write(
                "emergency.unlock.denied",
                slot_id=slot_id,
                resourceType="EMERGENCY",
                resourceId=slot_id,
                result="FAILED",
                reason="emergency unlock reason is required",
            )
            raise PermissionError("emergency unlock reason is required")
        slot = self.config.slot(slot_id)
        storage_state = self.disk.read_storage_state(slot)
        remembered_path = str(storage_state.get("accessPath") or "").strip()
        reconnect_path = str(repository_path or self.veeam_backup_copy_repository_path() or remembered_path or slot.mount_point or slot.device or "").strip()
        expected = self.emergency_access_hash(slot_id).strip()
        provided = str(verification_hash or "").strip()
        current_hash_hmac = self.secure_store.hash_hmac(expected) if expected else ""
        stored_hash_hmac = self.secure_store.stored_hash_hmac(slot_id)
        if expected and not stored_hash_hmac:
            stored_hash_hmac = self.secure_store.remember_disk_hash(
                slot_id=slot_id,
                expected_hash=expected,
                identity=slot.identity,
                access_path=reconnect_path,
                storage_state=storage_state,
            )
        provided_hash_hmac = self.secure_store.hash_hmac(provided) if provided else ""
        provided_digest = hashlib.sha256(provided.encode("utf-8")).hexdigest()[:16] if provided else ""
        expected_digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()[:16] if expected else ""

        self.audit.write(
            "emergency.reconnect.request",
            slot_id=slot_id,
            mount_point=str(slot.mount_point),
            device=slot.device,
            repository_path=reconnect_path,
            emergency_reason=emergency_reason,
            verification_source="local_secure_store" if not provided else "manual_compatibility",
            stored_hash_hmac=current_hash_hmac[:16],
        )
        approved = bool(expected and stored_hash_hmac and secrets.compare_digest(stored_hash_hmac, current_hash_hmac))
        if provided:
            approved = approved and secrets.compare_digest(provided_hash_hmac, current_hash_hmac)
        if not approved:
            self.audit.write(
                "emergency.reconnect.denied",
                slot_id=slot_id,
                reason="stored_verification_hash_mismatch",
                provided_hash_digest=provided_digest,
                stored_hash_hmac=str(stored_hash_hmac or "")[:16],
                expected_hash_digest=expected_digest,
            )
            self.secure_store.record_emergency_event(
                slot_id=slot_id,
                event="emergency_reconnect",
                result="denied",
                hash_hmac=current_hash_hmac,
                access_path=reconnect_path,
                storage_state=storage_state,
                message="stored verification hash mismatch",
            )
            raise PermissionError("emergency verification hash mismatch")

        self.audit.write(
            "emergency.reconnect.approved",
            slot_id=slot_id,
            repository_path=reconnect_path,
            emergency_reason=emergency_reason,
            expected_hash_digest=expected_digest,
            hash_source="local_secure_store",
        )
        self.secure_store.record_emergency_event(
            slot_id=slot_id,
            event="emergency_reconnect",
            result="approved",
            hash_hmac=current_hash_hmac,
            access_path=reconnect_path,
            storage_state=storage_state,
            message="local secure store verification approved",
        )
        try:
            state = self.reconnect(slot_id, repository_path=reconnect_path)
        except Exception as exc:
            diagnostic = self.disk.verify_storage_api_access(slot, "emergency_reconnect_failure")
            self.audit.write(
                "emergency.reconnect.failure.diagnostic",
                slot_id=slot_id,
                repository_path=reconnect_path,
                error=str(exc),
                get_volume_access_denied=bool(diagnostic.get("checks", {}).get("get_volume", {}).get("access_denied")),
                storage_api_access_denied=bool(diagnostic.get("access_denied")),
                resolution="Get-Volume 액세스 거부가 확인되면 LOCK-FIX를 관리자 권한으로 재시작하고 Windows Storage WMI/CIM 권한을 확인하세요.",
            )
            raise
        self.audit.write("emergency.reconnect.complete", slot_id=slot_id, state=state.value, repository_path=reconnect_path)
        self.secure_store.record_emergency_event(
            slot_id=slot_id,
            event="emergency_reconnect",
            result=state.value,
            hash_hmac=current_hash_hmac,
            access_path=reconnect_path,
            storage_state=self.disk.read_storage_state(slot),
            message="emergency reconnect completed",
        )
        return state

    def hardware_power_off(self, slot_id: str) -> None:
        self.audit.write("hardware.power_off.requested", slot_id=slot_id, resourceType="HARDWARE_POWER", resourceId=slot_id)
        self.approvals.require_approved("HARDWARE_POWER_OFF", slot_id)
        slot = self.config.slot(slot_id)
        build_power_controller(self.runner, slot.power, self.audit).off(slot_id)

    def hardware_power_on(self, slot_id: str) -> None:
        self.audit.write("hardware.power_on.requested", slot_id=slot_id, resourceType="HARDWARE_POWER", resourceId=slot_id)
        self.approvals.require_approved("HARDWARE_POWER_ON", slot_id)
        slot = self.config.slot(slot_id)
        build_power_controller(self.runner, slot.power, self.audit).on(slot_id)

    def require_policy_change_approval(self, target_id: str = "policy") -> dict:
        self.audit.write("policy.change.requested", resourceType="POLICY", resourceId=target_id)
        return self.approvals.require_approved("POLICY_CHANGE", target_id)

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
        configured_repository_path = self.veeam_backup_copy_repository_path()
        selected_path = (repository_path or configured_repository_path or "").strip()
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
        if configured_repository_path and repository_path:
            configured_volume = repository_volume_root(configured_repository_path)
            if configured_volume.strip().replace("/", "\\").rstrip("\\").lower() != target_volume.strip().replace("/", "\\").rstrip("\\").lower():
                self.audit.write(
                    "veeam.repository.volume.mismatch",
                    slot_id=slot.slot_id,
                    supplied_repository_path=repository_path,
                    configured_repository_path=configured_repository_path,
                    supplied_volume=target_volume,
                    configured_volume=configured_volume,
                    reason="non_veeam_backup_copy_repository_volume_blocked",
                    message="LOCK-FIX blocks reconnect/isolation unless the target is the configured Veeam Backup Copy repository volume.",
                )
                raise ValueError(
                    "LOCK-FIX can reconnect/isolate only the Veeam Backup Copy repository volume "
                    f"({configured_volume}); supplied path was {repository_path}"
                )
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

    def veeam_backup_copy_repository_path(self) -> str:
        if self.config.veeam.enabled and self.config.veeam.require_backup_copy:
            return str(self.config.veeam.target_repository_path or "").strip()
        return ""

    def status(self) -> dict[str, str]:
        return self.state.read_all()


def repository_volume_root(repository_path: str) -> str:
    value = str(repository_path or "").strip().replace("/", "\\")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        return f"{value[0].upper()}:\\"
    raise ValueError(f"Veeam Backup Copy repository path must be a local Windows volume path, for example F:\\copy: {repository_path}")
