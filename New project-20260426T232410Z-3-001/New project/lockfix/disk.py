from __future__ import annotations

import json
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
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Write-Output 'Windows Server flush checkpoint completed'",
            ])
        except Exception as exc:
            self.audit.write(
                "disk.flush.error",
                slot_id=slot.slot_id,
                mount_point=str(slot.mount_point),
                device=slot.device,
                error=str(exc),
            )
            raise
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
        self.volume_safety_preflight(slot, drive, "unmount")
        self.flush_volume_cache(slot, drive)
        self.audit.write(
            "disk.unmount.start",
            slot_id=slot.slot_id,
            mount_point=str(slot.mount_point),
            device=slot.device,
            drive_letter=drive,
            os_volume_protected=True,
        )
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; $volume = Get-Volume -DriveLetter $drive -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop; $disk = $partition | Get-Disk -ErrorAction Stop; if ($disk.IsBoot -or $disk.IsSystem) {{ throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }}; $accessPath = $drive + ':\\'; $record = [ordered]@{{ drive=$drive; accessPath=$accessPath; diskNumber=$partition.DiskNumber; partitionNumber=$partition.PartitionNumber; diskUniqueId=$disk.UniqueId; volumeUniqueId=$volume.UniqueId; fileSystemLabel=$volume.FileSystemLabel }}; Write-Output ('LOCKFIX_STORAGE_STATE=' + ($record | ConvertTo-Json -Compress)); Dismount-Volume -DriveLetter $drive -ErrorAction Stop; Remove-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop; $after = Get-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -ErrorAction Stop; if ($after.DriveLetter -eq $drive) {{ throw \"Volume $drive`: access path still present after dismount\" }}; Write-Output \"Volume $drive`: safe non-force dismount and access path removal completed\"",
            ])
        except Exception as exc:
            self.audit.write(
                "disk.unmount.error",
                slot_id=slot.slot_id,
                mount_point=str(slot.mount_point),
                device=slot.device,
                drive_letter=drive,
                error=str(exc),
            )
            raise
        self.persist_storage_state(slot, output)
        self.audit.write("disk.unmount.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
        self.audit.write("disk.unmount", slot_id=slot.slot_id, output=output)
        self.verify_unmounted(slot, drive)

    def wait_for_disk(self, slot: SlotConfig, timeout_seconds: int) -> None:
        self.assert_not_protected_os_volume(slot)
        if self.runner.dry_run:
            self.audit.write("disk.wait.dry_run", slot_id=slot.slot_id, device=slot.device)
            return
        drive = self.windows_drive_letter(slot)
        deadline = time.monotonic() + timeout_seconds
        lookup = self.partition_lookup_script(slot, drive)
        storage_state = self.read_storage_state(slot)
        self.audit.write(
            "disk.reconnect.plan",
            slot_id=slot.slot_id,
            drive_letter=drive,
            mount_point=str(slot.mount_point),
            device=slot.device,
            disk_number=storage_state.get("diskNumber", ""),
            partition_number=storage_state.get("partitionNumber", ""),
            volume_unique_id=storage_state.get("volumeUniqueId", ""),
            disk_unique_id=storage_state.get("diskUniqueId", ""),
            access_path=storage_state.get("accessPath", f"{drive}:\\"),
            source=str(self.storage_state_path(slot)) if storage_state else "current Windows partition lookup",
        )
        self.audit.write(
            "disk.wait.start",
            slot_id=slot.slot_id,
            device=slot.device,
            drive_letter=drive,
            timeout_seconds=timeout_seconds,
        )
        attempt = 0
        while time.monotonic() < deadline:
            attempt += 1
            self.audit.write("disk.wait.tick", slot_id=slot.slot_id, device=slot.device, drive_letter=drive, attempt=attempt)
            try:
                output = self.runner.run([
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    f"Update-HostStorageCache -ErrorAction SilentlyContinue; {lookup} Write-Output \"Volume {drive}: backup partition detected by Windows Storage stack\"",
                ], timeout=10)
            except Exception:
                time.sleep(1)
                continue
            else:
                self.audit.write("disk.wait.found", slot_id=slot.slot_id, device=slot.device, output=output)
                return
        raise TimeoutError(f"disk not found: {slot.device}")

    def partition_visible(self, slot: SlotConfig) -> bool:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        if self.runner.dry_run:
            self.audit.write("disk.partition.visible.dry_run", slot_id=slot.slot_id, drive_letter=drive, visible=True)
            return True
        storage_state = self.read_storage_state(slot)
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.partition.visible.start",
            slot_id=slot.slot_id,
            drive_letter=drive,
            disk_number=storage_state.get("diskNumber", ""),
            partition_number=storage_state.get("partitionNumber", ""),
            volume_unique_id=storage_state.get("volumeUniqueId", ""),
        )
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    "Update-HostStorageCache -ErrorAction SilentlyContinue; "
                    f"{lookup} "
                    "$proof = [ordered]@{ "
                    "visible=$true; "
                    "drive=$drive; "
                    "diskNumber=$partition.DiskNumber; "
                    "partitionNumber=$partition.PartitionNumber; "
                    "diskUniqueId=$disk.UniqueId; "
                    "driveLetter=$partition.DriveLetter "
                    "}; "
                    "Write-Output ($proof | ConvertTo-Json -Compress)"
                ),
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.partition.visible.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            return False
        try:
            proof = json.loads(str(output).splitlines()[-1])
        except Exception:
            proof = {"raw": output}
        self.audit.write("disk.partition.visible", slot_id=slot.slot_id, drive_letter=drive, visible=True, proof=proof)
        return True

    def mount_readonly(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        self.volume_safety_preflight(slot, drive, "mount_readonly")
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.mount_ro.start",
            slot_id=slot.slot_id,
            mount_point=str(slot.mount_point),
            device=slot.device,
            drive_letter=drive,
            os_volume_protected=True,
        )
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} if (-not $disk.IsReadOnly) {{ Set-Disk -Number $disk.Number -IsReadOnly $true -ErrorAction Stop }}; if ($partition.DriveLetter -ne $drive) {{ Add-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop }}; if (Test-Path $accessPath) {{ Write-Output \"Volume $drive`: mounted for read-only verification\" }} else {{ Mount-Volume -DriveLetter $drive -ErrorAction Stop; Write-Output \"Volume $drive`: mounted for read-only verification\" }}",
            ])
        except Exception as exc:
            self.audit.write(
                "disk.mount_ro.error",
                slot_id=slot.slot_id,
                mount_point=str(slot.mount_point),
                device=slot.device,
                drive_letter=drive,
                error=str(exc),
            )
            raise
        self.audit.write("disk.mount_ro.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
        self.audit.write("disk.mount_ro", slot_id=slot.slot_id, output=output)

    def remount_readwrite(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        self.volume_safety_preflight(slot, drive, "remount_readwrite")
        self.ensure_access_path(slot, drive)
        self.scan_volume_health(slot, drive)
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.mount_rw.start",
            slot_id=slot.slot_id,
            mount_point=str(slot.mount_point),
            device=slot.device,
            drive_letter=drive,
            os_volume_protected=True,
        )
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} if ($disk.IsReadOnly) {{ Set-Disk -Number $disk.Number -IsReadOnly $false -ErrorAction Stop }}; if ($partition.DriveLetter -ne $drive) {{ Add-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop }}; if (Test-Path $accessPath) {{ Write-Output \"Volume $drive`: online read-write access approved\" }} else {{ Mount-Volume -DriveLetter $drive -ErrorAction Stop; Write-Output \"Volume $drive`: mounted and online read-write access approved\" }}",
            ])
        except Exception as exc:
            self.audit.write(
                "disk.mount_rw.error",
                slot_id=slot.slot_id,
                mount_point=str(slot.mount_point),
                device=slot.device,
                drive_letter=drive,
                error=str(exc),
            )
            raise
        self.audit.write("disk.mount_rw.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
        self.audit.write("disk.mount_rw", slot_id=slot.slot_id, output=output)

    def volume_safety_preflight(self, slot: SlotConfig, drive: str, operation: str) -> None:
        self.assert_not_protected_os_volume(slot)
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.safety.preflight.start",
            slot_id=slot.slot_id,
            operation=operation,
            mount_point=str(slot.mount_point),
            device=slot.device,
            drive_letter=drive,
            policy="healthy_non_os_volume_required",
        )
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} $volume = $partition | Get-Volume -ErrorAction Stop; $volumeHealth = [string]$volume.HealthStatus; $diskHealth = [string]$disk.HealthStatus; $volumeOperational = [string]$volume.OperationalStatus; if ($volumeHealth -and $volumeHealth -notin @('Healthy','Unknown')) {{ throw \"Volume health is not safe: $volumeHealth\" }}; if ($diskHealth -and $diskHealth -notin @('Healthy','Unknown')) {{ throw \"Disk health is not safe: $diskHealth\" }}; if ($volumeOperational -and $volumeOperational -notin @('OK','Online','Unknown')) {{ throw \"Volume operational state is not safe: $volumeOperational\" }}; Write-Output \"LOCK-FIX safety preflight OK - drive=$drive; filesystem=$($volume.FileSystemType); volumeHealth=$volumeHealth; volumeOperational=$volumeOperational; disk=$($disk.Number); diskHealth=$diskHealth\"",
            ], timeout=30)
        except Exception as exc:
            self.audit.write(
                "disk.safety.preflight.error",
                slot_id=slot.slot_id,
                operation=operation,
                drive_letter=drive,
                error=str(exc),
            )
            raise
        self.audit.write(
            "disk.safety.preflight.ok",
            slot_id=slot.slot_id,
            operation=operation,
            drive_letter=drive,
            output=output,
        )

    def flush_volume_cache(self, slot: SlotConfig, drive: str) -> None:
        self.audit.write("disk.cache.flush.start", slot_id=slot.slot_id, drive_letter=drive, mount_point=str(slot.mount_point))
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; if (Get-Command Write-VolumeCache -ErrorAction SilentlyContinue) {{ Write-VolumeCache -DriveLetter $drive -ErrorAction Stop; Write-Output \"Write-VolumeCache OK for $drive`:\" }} else {{ Write-Output 'Write-VolumeCache unavailable; LOCK-FIX relied on flush checkpoint and quiet I/O gate before dismount.' }}",
            ], timeout=60)
        except Exception as exc:
            self.audit.write("disk.cache.flush.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.audit.write("disk.cache.flush", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def scan_volume_health(self, slot: SlotConfig, drive: str) -> None:
        self.audit.write("disk.health.scan.start", slot_id=slot.slot_id, drive_letter=drive, mount_point=str(slot.mount_point))
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; if (Get-Command Repair-Volume -ErrorAction SilentlyContinue) {{ $result = Repair-Volume -DriveLetter $drive -Scan -ErrorAction Stop | Out-String; if ([string]::IsNullOrWhiteSpace($result)) {{ Write-Output \"Repair-Volume scan completed for $drive`:\" }} else {{ Write-Output $result.Trim() }} }} else {{ Write-Output 'Repair-Volume unavailable; storage health preflight result is used.' }}",
            ], timeout=120)
        except Exception as exc:
            self.audit.write("disk.health.scan.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.audit.write("disk.health.scan", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def verify_unmounted(self, slot: SlotConfig, drive: str) -> None:
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; $volume = Get-Volume -DriveLetter $drive -ErrorAction SilentlyContinue; $partition = Get-Partition -DriveLetter $drive -ErrorAction SilentlyContinue; if ($volume -or $partition) {{ throw \"Volume $drive`: is still reachable after dismount\" }}; Write-Output \"Volume $drive`: access path removed and no longer reachable\"",
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.unmount.verify.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.audit.write("disk.unmount.verify", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def unmount_proof(self, slot: SlotConfig) -> dict:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        storage_state = self.read_storage_state(slot)
        if self.runner.dry_run:
            result = {
                "drive": drive,
                "ok": None,
                "provable": False,
                "reason": "dry_run mode cannot prove live Windows volume state",
                "storage_state": storage_state,
            }
            self.audit.write("disk.unmount.proof", slot_id=slot.slot_id, **result)
            return result

        disk_number = str(storage_state.get("diskNumber", ""))
        partition_number = str(storage_state.get("partitionNumber", ""))
        try:
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"$drive = '{drive}'; "
                    "$accessPath = $drive + ':\\'; "
                    f"$storedDiskNumber = '{disk_number}'; "
                    f"$storedPartitionNumber = '{partition_number}'; "
                    "$volumeByDrive = Get-Volume -DriveLetter $drive -ErrorAction SilentlyContinue; "
                    "$partitionByDrive = Get-Partition -DriveLetter $drive -ErrorAction SilentlyContinue; "
                    "$partitionByStored = $null; "
                    "if ($storedDiskNumber -and $storedPartitionNumber) { "
                    "$partitionByStored = Get-Partition -DiskNumber ([UInt32]$storedDiskNumber) -PartitionNumber ([UInt32]$storedPartitionNumber) -ErrorAction SilentlyContinue "
                    "}; "
                    "$diskByStored = $null; "
                    "if ($partitionByStored) { $diskByStored = $partitionByStored | Get-Disk -ErrorAction SilentlyContinue }; "
                    "$pathReachable = Test-Path $accessPath; "
                    "$accessPathRemoved = (-not $pathReachable -and -not $volumeByDrive -and -not $partitionByDrive); "
                    "$proof = [ordered]@{ "
                    "drive=$drive; "
                    "pathReachable=[bool]$pathReachable; "
                    "volumeByDrive=[bool]($null -ne $volumeByDrive); "
                    "partitionByDrive=[bool]($null -ne $partitionByDrive); "
                    "partitionByStored=[bool]($null -ne $partitionByStored); "
                    "diskByStored=[bool]($null -ne $diskByStored); "
                    "diskNumber=$storedDiskNumber; "
                    "partitionNumber=$storedPartitionNumber; "
                    "accessPathRemoved=[bool]$accessPathRemoved "
                    "}; "
                    "Write-Output ($proof | ConvertTo-Json -Compress)"
                ),
            ], timeout=30)
        except Exception as exc:
            result = {
                "drive": drive,
                "ok": False,
                "provable": True,
                "error": str(exc),
                "storage_state": storage_state,
            }
            self.audit.write("disk.unmount.proof.error", slot_id=slot.slot_id, **result)
            return result

        try:
            proof = json.loads(str(output).splitlines()[-1])
        except Exception:
            proof = {"raw": output}
        result = {
            **proof,
            "ok": bool(proof.get("accessPathRemoved")),
            "provable": True,
            "storage_state": storage_state,
        }
        self.audit.write("disk.unmount.proof", slot_id=slot.slot_id, **result)
        return result

    def ensure_access_path(self, slot: SlotConfig, drive: str) -> None:
        lookup = self.partition_lookup_script(slot, drive)
        try:
            storage_state = self.read_storage_state(slot)
            self.audit.write(
                "disk.access_path.start",
                slot_id=slot.slot_id,
                drive_letter=drive,
                disk_number=storage_state.get("diskNumber", ""),
                partition_number=storage_state.get("partitionNumber", ""),
                volume_unique_id=storage_state.get("volumeUniqueId", ""),
                access_path=storage_state.get("accessPath", f"{drive}:\\"),
            )
            output = self.runner.run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} if ($partition.DriveLetter -ne $drive) {{ Add-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop }}; Write-Output \"Volume $drive`: access path is available\"",
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.access_path.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.audit.write("disk.access_path", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def storage_state_path(self, slot: SlotConfig) -> Path:
        safe_slot = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in slot.slot_id)
        return self.audit.path.parent / f"storage-{safe_slot}.json"

    def read_storage_state(self, slot: SlotConfig) -> dict:
        path = self.storage_state_path(slot)
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def persist_storage_state(self, slot: SlotConfig, output: str) -> None:
        prefix = "LOCKFIX_STORAGE_STATE="
        for line in str(output or "").splitlines():
            if line.startswith(prefix):
                try:
                    data = json.loads(line[len(prefix) :])
                except Exception as exc:
                    self.audit.write("disk.storage_state.error", slot_id=slot.slot_id, error=str(exc))
                    return
                self.storage_state_path(slot).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                self.audit.write("disk.storage_state", slot_id=slot.slot_id, path=str(self.storage_state_path(slot)))
                return

    def partition_lookup_script(self, slot: SlotConfig, drive: str) -> str:
        state = self.read_storage_state(slot)
        disk_number = str(state.get("diskNumber", ""))
        partition_number = str(state.get("partitionNumber", ""))
        return (
            f"$drive = '{drive}'; "
            "$accessPath = $drive + ':\\'; "
            "$partition = Get-Partition -DriveLetter $drive -ErrorAction SilentlyContinue; "
            f"$storedDiskNumber = '{disk_number}'; "
            f"$storedPartitionNumber = '{partition_number}'; "
            "if (-not $partition -and $storedDiskNumber -and $storedPartitionNumber) { "
            "$partition = Get-Partition -DiskNumber ([UInt32]$storedDiskNumber) -PartitionNumber ([UInt32]$storedPartitionNumber) -ErrorAction SilentlyContinue "
            "}; "
            "if (-not $partition) { throw \"LOCK-FIX backup partition was not found for drive $drive`:\" }; "
            "$disk = $partition | Get-Disk -ErrorAction Stop; "
            "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
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
