from __future__ import annotations

import json
import subprocess
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from .audit import AuditLogger
from .command import CommandError
from .command import CommandRunner
from .config import SlotConfig


class DiskOperator:
    def __init__(self, runner: CommandRunner, audit: AuditLogger) -> None:
        self.runner = runner
        self.audit = audit

    def storage_run(self, args: list[str], timeout: int = 120) -> str:
        try:
            return self.runner.run(args, timeout=timeout)
        except Exception as exc:
            command_text = self.powershell_command_text(args)
            if self.runner.dry_run or not command_text or not self.should_use_system_fallback(command_text, str(exc)):
                raise
            self.audit.write(
                "storage.command.primary_denied",
                reason="permission_denied",
                error=str(exc),
                fallback="system_scheduled_task",
            )
            try:
                return self.run_storage_command_as_system(command_text, timeout=timeout)
            except Exception as fallback_exc:
                self.audit.write(
                    "storage.command.system_fallback.error",
                    primary_error=str(exc),
                    fallback_error=str(fallback_exc),
                    guidance=(
                        "Run LOCK-FIX WebUI as LocalSystem or install the SYSTEM scheduled-task helper. "
                        "Confirm Task Scheduler, Windows Management Instrumentation, Virtual Disk, and Storage Service are running."
                    ),
                )
                raise CommandError(f"{exc}; SYSTEM fallback failed: {fallback_exc}") from fallback_exc

    def powershell_command_text(self, args: list[str]) -> str:
        lowered = [str(arg).lower() for arg in args]
        if not any("powershell" in arg or "pwsh" in arg for arg in lowered):
            return ""
        for flag in ("-Command", "-command"):
            if flag in args:
                index = args.index(flag)
                if index + 1 < len(args):
                    return str(args[index + 1])
        return ""

    def should_use_system_fallback(self, command_text: str, error_text: str) -> bool:
        storage_tokens = (
            "Get-Disk",
            "Get-Partition",
            "Get-Volume",
            "Mount-Volume",
            "Dismount-Volume",
            "Add-PartitionAccessPath",
            "Remove-PartitionAccessPath",
            "Set-Disk",
            "Repair-Volume",
            "Write-VolumeCache",
            "Update-HostStorageCache",
            "mountvol",
        )
        permission_tokens = (
            "access is denied",
            "access denied",
            "permission denied",
            "unauthorized",
            "액세스가 거부",
            "권한",
            "거부",
        )
        command_has_storage_api = any(token.lower() in command_text.lower() for token in storage_tokens)
        error_is_permission = any(token in error_text.lower() for token in permission_tokens)
        return command_has_storage_api and error_is_permission

    def run_storage_command_as_system(self, command_text: str, timeout: int = 120) -> str:
        work_dir = self.audit.path.parent / "system-fallback"
        work_dir.mkdir(parents=True, exist_ok=True)
        task_id = uuid.uuid4().hex
        task_name = f"LOCK-FIX-StorageFallback-{task_id}"
        script_path = work_dir / f"{task_id}.ps1"
        stdout_path = work_dir / f"{task_id}.out.txt"
        stderr_path = work_dir / f"{task_id}.err.txt"
        exit_path = work_dir / f"{task_id}.exit.txt"
        escaped_stdout = str(stdout_path).replace("'", "''")
        escaped_stderr = str(stderr_path).replace("'", "''")
        escaped_exit = str(exit_path).replace("'", "''")
        script_path.write_text(
            "\n".join(
                [
                    "$ErrorActionPreference = 'Stop'",
                    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
                    "try {",
                    "  & {",
                    f"    {command_text}",
                    f"  }} *>&1 | Out-File -FilePath '{escaped_stdout}' -Encoding UTF8",
                    f"  Set-Content -Path '{escaped_exit}' -Value '0' -Encoding ASCII",
                    "  exit 0",
                    "} catch {",
                    f"  ($_ | Out-String) | Out-File -FilePath '{escaped_stderr}' -Encoding UTF8",
                    f"  Set-Content -Path '{escaped_exit}' -Value '1' -Encoding ASCII",
                    "  exit 1",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        start_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        task_command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{script_path}"'
        self.audit.write(
            "storage.command.system_fallback.start",
            task_name=task_name,
            script=str(script_path),
            timeout_seconds=timeout,
        )
        self.run_schtasks([
            "/Create",
            "/TN",
            task_name,
            "/TR",
            task_command,
            "/SC",
            "ONCE",
            "/ST",
            start_time,
            "/RL",
            "HIGHEST",
            "/RU",
            "SYSTEM",
            "/F",
        ])
        try:
            self.run_schtasks(["/Run", "/TN", task_name])
            deadline = time.monotonic() + max(10, timeout)
            while time.monotonic() < deadline:
                if exit_path.exists():
                    code = exit_path.read_text(encoding="ascii", errors="ignore").strip()
                    stdout = stdout_path.read_text(encoding="utf-8-sig", errors="replace").strip() if stdout_path.exists() else ""
                    stderr = stderr_path.read_text(encoding="utf-8-sig", errors="replace").strip() if stderr_path.exists() else ""
                    if code == "0":
                        self.audit.write("storage.command.system_fallback.ok", task_name=task_name, output=stdout)
                        return stdout
                    raise CommandError(stderr or stdout or f"SYSTEM task exited with code {code}")
                time.sleep(1)
            raise TimeoutError("SYSTEM scheduled task did not finish before timeout")
        finally:
            try:
                self.run_schtasks(["/Delete", "/TN", task_name, "/F"])
            except Exception:
                pass

    def run_schtasks(self, args: list[str]) -> str:
        result = subprocess.run(
            ["schtasks", *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if result.returncode != 0:
            raise CommandError(error or output or f"schtasks exit code {result.returncode}")
        return output

    def flush(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        self.audit.write("disk.flush.start", slot_id=slot.slot_id, mount_point=str(slot.mount_point), device=slot.device)
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Write-Output 'Windows Server flush checkpoint completed'",
            ], timeout=45)
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

    def verify_storage_api_access(self, slot: SlotConfig, reason: str) -> dict[str, object]:
        checks = {
            "get_volume": "Get-Volume -ErrorAction Stop | Select-Object -First 1 | Out-Null; Write-Output 'Get-Volume OK'",
            "get_disk": "Get-Disk -ErrorAction Stop | Select-Object -First 1 | Out-Null; Write-Output 'Get-Disk OK'",
            "get_partition": "Get-Partition -ErrorAction Stop | Select-Object -First 1 | Out-Null; Write-Output 'Get-Partition OK'",
        }
        results: dict[str, dict[str, object]] = {}
        access_denied = False
        self.audit.write(
            "disk.storage_api.self_check.start",
            slot_id=slot.slot_id,
            reason=reason,
            message="Emergency reconnect failed; validating Windows disk/partition API access.",
        )
        for name, command in checks.items():
            try:
                output = self.storage_run([
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ], timeout=20)
            except Exception as exc:
                error = str(exc)
                denied = self.is_access_denied_error(error)
                access_denied = access_denied or denied
                results[name] = {"ok": False, "error": error, "access_denied": denied}
                self.audit.write(
                    "disk.storage_api.self_check.error",
                    slot_id=slot.slot_id,
                    reason=reason,
                    check=name,
                    error=error,
                    access_denied=denied,
                    resolution=(
                        "LOCKFIXWebUI 서비스를 LocalSystem 계정으로 재등록/재시작하고 "
                        "tools\\fix_lockfix_permissions_admin.ps1을 관리자 권한으로 실행하세요."
                    )
                    if denied
                    else "Windows Storage 서비스와 PowerShell 디스크 명령 상태를 확인하세요.",
                )
            else:
                results[name] = {"ok": True, "output": output, "access_denied": False}
                self.audit.write(
                    "disk.storage_api.self_check.ok",
                    slot_id=slot.slot_id,
                    reason=reason,
                    check=name,
                    output=output,
                )
        summary = {"ok": all(bool(item.get("ok")) for item in results.values()), "access_denied": access_denied, "checks": results}
        self.audit.write(
            "disk.storage_api.self_check",
            slot_id=slot.slot_id,
            reason=reason,
            ok=summary["ok"],
            access_denied=access_denied,
            message="Get-Volume access denied recurrence detected." if access_denied else "Windows disk/partition API self-check completed.",
        )
        return summary

    def unmount(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        try:
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
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; $volume = Get-Volume -DriveLetter $drive -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop; $disk = $partition | Get-Disk -ErrorAction Stop; if ($disk.IsBoot -or $disk.IsSystem) {{ throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }}; $accessPath = $drive + ':\\'; $record = [ordered]@{{ drive=$drive; accessPath=$accessPath; diskNumber=$partition.DiskNumber; partitionNumber=$partition.PartitionNumber; diskUniqueId=$disk.UniqueId; volumeUniqueId=$volume.UniqueId; volumePath=$volume.Path; volumeMountPath=$volume.Path; fileSystemLabel=$volume.FileSystemLabel }}; Write-Output ('LOCKFIX_STORAGE_STATE=' + ($record | ConvertTo-Json -Compress)); if (Get-Command Dismount-Volume -ErrorAction SilentlyContinue) {{ Dismount-Volume -DriveLetter $drive -ErrorAction Stop }} else {{ Write-Output 'Dismount-Volume unavailable; removing partition access path only.' }}; Remove-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop; $after = Get-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -ErrorAction Stop; if ($after.DriveLetter -eq $drive) {{ throw \"Volume $drive`: access path still present after dismount\" }}; Write-Output \"Volume $drive`: safe non-force dismount and access path removal completed\"",
            ], timeout=45)
        except Exception as exc:
            if self.is_drive_letter_absent_error(str(exc)):
                output = (
                    f"Volume {drive}: already unmounted; drive letter/access path is absent. "
                    "LOCK-FIX treats this as already released, not as an isolation failure."
                )
                self.audit.write(
                    "disk.unmount.already_absent",
                    slot_id=slot.slot_id,
                    mount_point=str(slot.mount_point),
                    device=slot.device,
                    drive_letter=drive,
                    reason="Drive letter is already absent; continuing isolation because the volume is already released.",
                    error=str(exc),
                )
                self.audit.write("disk.unmount.tick", slot_id=slot.slot_id, elapsed_seconds=1, mount_point=str(slot.mount_point))
                self.audit.write("disk.unmount", slot_id=slot.slot_id, output=output, already_absent=True)
                return
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
                output = self.storage_run([
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    f"Update-HostStorageCache -ErrorAction SilentlyContinue; Get-Disk -ErrorAction SilentlyContinue | Out-Null; Get-Volume -ErrorAction SilentlyContinue | Out-Null; {lookup} Write-Output \"Volume {drive}: backup partition detected by Windows Storage stack\"",
                ], timeout=10)
            except Exception:
                try:
                    self.reassign_access_path_with_mountvol(slot, drive, reason="wait_for_disk_storage_api_unavailable")
                except Exception:
                    time.sleep(1)
                    continue
                else:
                    self.audit.write(
                        "disk.wait.found",
                        slot_id=slot.slot_id,
                        device=slot.device,
                        output=f"Volume {drive}: backup volume recovered with mountvol fallback",
                    )
                    return
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
            output = self.storage_run([
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
            try:
                self.reassign_access_path_with_mountvol(slot, drive, reason="partition_visible_storage_api_unavailable")
            except Exception as fallback_exc:
                self.audit.write(
                    "disk.partition.visible.mountvol_fallback.error",
                    slot_id=slot.slot_id,
                    drive_letter=drive,
                    error=str(fallback_exc),
                )
                return False
            self.audit.write(
                "disk.partition.visible.mountvol_fallback",
                slot_id=slot.slot_id,
                drive_letter=drive,
                visible=True,
            )
            return True
        try:
            proof = json.loads(str(output).splitlines()[-1])
        except Exception:
            proof = {"raw": output}
        self.audit.write("disk.partition.visible", slot_id=slot.slot_id, drive_letter=drive, visible=True, proof=proof)
        return True

    def mount_readonly(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        self.ensure_access_path(slot, drive)
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
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} if ($partition.DriveLetter -ne $drive) {{ Set-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter $drive -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop }}; if (-not $disk.IsReadOnly) {{ Set-Disk -Number $disk.Number -IsReadOnly $true -ErrorAction Stop }}; Update-HostStorageCache -ErrorAction SilentlyContinue; if (Test-Path $accessPath) {{ Write-Output \"Volume $drive`: mounted for read-only verification\" }} else {{ throw \"Volume $drive`: read-only verification path is not reachable after drive-letter assignment\" }}",
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
        self.audit.write("disk.mount_ro", slot_id=slot.slot_id, output=f"{output}\nMount-Volume -DriveLetter $drive")

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
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"{lookup} if ($disk.IsReadOnly) {{ Set-Disk -Number $disk.Number -IsReadOnly $false -ErrorAction Stop }}; if ($partition.DriveLetter -ne $drive) {{ Set-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter $drive -ErrorAction Stop; $partition = Get-Partition -DriveLetter $drive -ErrorAction Stop }}; Update-HostStorageCache -ErrorAction SilentlyContinue; if (Test-Path $accessPath) {{ Write-Output \"Volume $drive`: online read-write access approved\" }} else {{ throw \"Volume $drive`: read-write path is not reachable after drive-letter assignment\" }}",
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

    def offline(self, slot: SlotConfig) -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        if self.runner.dry_run:
            self.audit.write("disk.offline.dry_run", slot_id=slot.slot_id, drive_letter=drive)
            return
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.offline.start",
            slot_id=slot.slot_id,
            drive_letter=drive,
            mount_point=str(slot.mount_point),
            device=slot.device,
            message="Windows cannot power off a disk directly; LOCK-FIX will place the backup disk offline.",
        )
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"{lookup} "
                    "$disk = $partition | Get-Disk -ErrorAction Stop; "
                    "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
                    "if (-not $disk.IsOffline) { Set-Disk -Number $disk.Number -IsOffline $true -ErrorAction Stop }; "
                    "$disk = Get-Disk -Number $disk.Number -ErrorAction Stop; "
                    "if (-not $disk.IsOffline) { throw \"Disk $($disk.Number) did not enter offline state\" }; "
                    "$proof = [ordered]@{ drive=$drive; diskNumber=$disk.Number; diskUniqueId=$disk.UniqueId; isOffline=[bool]$disk.IsOffline; method='Set-Disk -IsOffline true' }; "
                    "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
                    "Write-Output \"Disk $($disk.Number): offline isolation completed for $drive`:\""
                ),
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.offline.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.persist_storage_state(slot, output)
        self.audit.write("disk.offline.tick", slot_id=slot.slot_id, elapsed_seconds=1, drive_letter=drive)
        self.audit.write("disk.offline", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def online(self, slot: SlotConfig, approved_until: str = "") -> None:
        self.assert_not_protected_os_volume(slot)
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        if self.runner.dry_run:
            self.audit.write("disk.online.dry_run", slot_id=slot.slot_id, drive_letter=drive, approved_until=approved_until)
            return
        storage_state = self.read_storage_state(slot)
        disk_number = str(storage_state.get("diskNumber", ""))
        disk_unique_id = str(storage_state.get("diskUniqueId", ""))
        lookup = self.partition_lookup_script(slot, drive)
        self.audit.write(
            "disk.online.start",
            slot_id=slot.slot_id,
            drive_letter=drive,
            approved_until=approved_until,
            message="Administrator-approved limited-time online window is being opened.",
        )
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"$storedDiskNumber = '{self.ps_single_quote(disk_number)}'; "
                    f"$storedDiskUniqueId = '{self.ps_single_quote(disk_unique_id)}'; "
                    f"$approvedUntil = '{self.ps_single_quote(approved_until)}'; "
                    "$disk = $null; "
                    "if ($storedDiskNumber) { $disk = Get-Disk -Number ([UInt32]$storedDiskNumber) -ErrorAction SilentlyContinue }; "
                    "if (-not $disk -and $storedDiskUniqueId) { $disk = Get-Disk -ErrorAction SilentlyContinue | Where-Object { [string]$_.UniqueId -eq $storedDiskUniqueId } | Select-Object -First 1 }; "
                    "if ($disk -and $disk.IsOffline) { Set-Disk -Number $disk.Number -IsOffline $false -ErrorAction Stop; Start-Sleep -Milliseconds 250 }; "
                    f"{lookup} "
                    "$disk = $partition | Get-Disk -ErrorAction Stop; "
                    "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
                    "if ($disk.IsOffline) { Set-Disk -Number $disk.Number -IsOffline $false -ErrorAction Stop }; "
                    "$disk = Get-Disk -Number $disk.Number -ErrorAction Stop; "
                    "if ($disk.IsOffline) { throw \"Disk $($disk.Number) remained offline after online request\" }; "
                    "$proof = [ordered]@{ drive=$drive; diskNumber=$disk.Number; diskUniqueId=$disk.UniqueId; isOffline=[bool]$disk.IsOffline; approvedUntil=$approvedUntil; method='Set-Disk -IsOffline false' }; "
                    "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
                    "Write-Output \"Disk $($disk.Number): online access approved for $drive`:\""
                ),
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.online.error", slot_id=slot.slot_id, drive_letter=drive, error=str(exc))
            raise
        self.persist_storage_state(slot, output)
        self.audit.write("disk.online.tick", slot_id=slot.slot_id, elapsed_seconds=1, drive_letter=drive)
        self.audit.write("disk.online", slot_id=slot.slot_id, drive_letter=drive, approved_until=approved_until, output=output)

    def enforce_offline_unless_approved(self, slot: SlotConfig, approved: bool, reason: str) -> bool:
        self.assert_not_protected_os_volume(slot)
        if approved:
            self.audit.write("disk.online.approval.active", slot_id=slot.slot_id, reason=reason)
            return False
        drive = self.windows_drive_letter(slot) if not self.runner.dry_run else "X"
        if self.runner.dry_run:
            self.audit.write("disk.online.unauthorized.reblock.dry_run", slot_id=slot.slot_id, drive_letter=drive, reason=reason)
            return True
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"{self.partition_lookup_script(slot, drive)} "
                    "$disk = $partition | Get-Disk -ErrorAction Stop; "
                    "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
                    "if (-not $disk.IsOffline) { Set-Disk -Number $disk.Number -IsOffline $true -ErrorAction Stop; Write-Output \"Unauthorized online disk was reblocked with Set-Disk -IsOffline true\" } "
                    "else { Write-Output \"Disk is already offline\" }"
                ),
            ], timeout=30)
        except Exception as exc:
            self.audit.write("disk.online.unauthorized.reblock.error", slot_id=slot.slot_id, drive_letter=drive, reason=reason, error=str(exc))
            raise
        self.audit.write("disk.online.unauthorized.reblock", slot_id=slot.slot_id, drive_letter=drive, reason=reason, output=output)
        return True

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
            output = self.storage_run([
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
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; if (Get-Command Write-VolumeCache -ErrorAction SilentlyContinue) {{ Write-VolumeCache -DriveLetter $drive -ErrorAction Stop; Write-Output \"Write-VolumeCache OK for $drive`:\" }} else {{ Write-Output 'Write-VolumeCache unavailable; LOCK-FIX relied on flush checkpoint and quiet I/O gate before dismount.' }}",
            ], timeout=60)
        except Exception as exc:
            error = str(exc)
            if "Write-VolumeCache" in error and (
                "CmdletizationQuery_NotFound_DriveLetter" in error
                or "MSFT_Volume" in error
                or "개체가 없습니다" in error
            ):
                self.audit.write(
                    "disk.cache.flush.skipped",
                    slot_id=slot.slot_id,
                    drive_letter=drive,
                    reason="Volume drive letter is already absent; continuing because the backup volume appears to be unmounted.",
                    error=error,
                )
                return
            self.audit.write("disk.cache.flush.error", slot_id=slot.slot_id, drive_letter=drive, error=error)
            raise
        self.audit.write("disk.cache.flush", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def scan_volume_health(self, slot: SlotConfig, drive: str) -> None:
        self.audit.write("disk.health.scan.start", slot_id=slot.slot_id, drive_letter=drive, mount_point=str(slot.mount_point))
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"$drive = '{drive}'; if (Get-Command Repair-Volume -ErrorAction SilentlyContinue) {{ $result = Repair-Volume -DriveLetter $drive -Scan -ErrorAction Stop | Out-String; if ([string]::IsNullOrWhiteSpace($result)) {{ Write-Output \"Repair-Volume scan completed for $drive`:\" }} else {{ Write-Output $result.Trim() }} }} else {{ Write-Output 'Repair-Volume unavailable; storage health preflight result is used.' }}",
            ], timeout=45)
        except Exception as exc:
            error = str(exc)
            if "Repair-Volume" in error and ("not supported" in error.lower() or "43001" in error):
                self.audit.write(
                    "disk.health.scan.skipped",
                    slot_id=slot.slot_id,
                    drive_letter=drive,
                    reason="Repair-Volume is not supported for this filesystem. Continuing with storage health preflight.",
                    error=error,
                )
                return
            self.audit.write("disk.health.scan.error", slot_id=slot.slot_id, drive_letter=drive, error=error)
            raise
        self.audit.write("disk.health.scan", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def verify_unmounted(self, slot: SlotConfig, drive: str) -> None:
        try:
            output = self.storage_run([
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

    def verify_drive_accessible(self, slot: SlotConfig, drive: str) -> None:
        access_path = self.remembered_access_path(slot, drive)
        self.audit.write(
            "disk.reconnect.verify.start",
            slot_id=slot.slot_id,
            drive_letter=drive,
            access_path=access_path,
        )
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"$drive = '{drive}'; "
                    f"$accessPath = '{self.ps_single_quote(access_path)}'; "
                    "Update-HostStorageCache -ErrorAction SilentlyContinue; "
                    "$partition = Get-Partition -DriveLetter $drive -ErrorAction Stop; "
                    "$volume = Get-Volume -DriveLetter $drive -ErrorAction Stop; "
                    "$disk = $partition | Get-Disk -ErrorAction Stop; "
                    "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
                    "if (-not (Test-Path $accessPath)) { throw \"Volume $drive`: is not visible in Windows Explorer/access path after reconnect\" }; "
                    "$proof = [ordered]@{ "
                    "drive=$drive; "
                    "accessPath=$accessPath; "
                    "diskNumber=$partition.DiskNumber; "
                    "partitionNumber=$partition.PartitionNumber; "
                    "diskUniqueId=$disk.UniqueId; "
                    "volumeUniqueId=$volume.UniqueId; "
                    "volumePath=$volume.Path; "
                    "volumeMountPath=$volume.Path; "
                    "driveLetter=$partition.DriveLetter; "
                    "pathReachable=[bool](Test-Path $accessPath) "
                    "}; "
                    "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
                    "Write-Output \"Volume $drive`: verified visible and accessible after reconnect\""
                ),
            ], timeout=30)
        except Exception as exc:
            self.audit.write(
                "disk.reconnect.verify.error",
                slot_id=slot.slot_id,
                drive_letter=drive,
                access_path=access_path,
                error=str(exc),
                resolution="LOCK-FIX WebUI/Console must run as Administrator and Windows Storage cmdlets must allow Get-Disk/Get-Partition/Get-Volume.",
            )
            raise
        self.persist_storage_state(slot, output)
        self.audit.write("disk.reconnect.verify", slot_id=slot.slot_id, drive_letter=drive, output=output)

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
            output = self.storage_run([
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
        storage_state = self.read_storage_state(slot)
        if self.stored_volume_mount_path(storage_state):
            try:
                output = self.reassign_access_path_with_mountvol(slot, drive, reason="stored_volume_guid_first_priority")
            except Exception as exc:
                self.audit.write(
                    "disk.access_path.mountvol_first.error",
                    slot_id=slot.slot_id,
                    drive_letter=drive,
                    error=str(exc),
                    message="Stored Volume GUID mountvol recovery failed; LOCK-FIX will continue with Windows Storage API recovery.",
                )
            else:
                self.persist_storage_state(slot, output)
                self.audit.write("disk.access_path", slot_id=slot.slot_id, drive_letter=drive, output=output)
                return
        try:
            self.audit.write(
                "disk.access_path.start",
                slot_id=slot.slot_id,
                drive_letter=drive,
                disk_number=storage_state.get("diskNumber", ""),
                partition_number=storage_state.get("partitionNumber", ""),
                volume_unique_id=storage_state.get("volumeUniqueId", ""),
                access_path=storage_state.get("accessPath", f"{drive}:\\"),
            )
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"{lookup} "
                    "$wasReadOnly = [bool]$disk.IsReadOnly; "
                    "if ($wasReadOnly) { Set-Disk -Number $disk.Number -IsReadOnly $false -ErrorAction Stop }; "
                    "if ($partition.DriveLetter -ne $drive -or -not (Test-Path $accessPath)) { "
                    "try { "
                    "Set-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter $drive -ErrorAction Stop "
                    "} catch { "
                    "Add-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $accessPath -ErrorAction Stop "
                    "}; "
                    "$partition = Get-Partition -DriveLetter $drive -ErrorAction Stop "
                    "}; "
                    "Update-HostStorageCache -ErrorAction SilentlyContinue; "
                    "if (-not (Test-Path $accessPath)) { throw \"Volume $drive`: access path was assigned but the volume is not reachable\" }; "
                    "$volume = Get-Volume -DriveLetter $drive -ErrorAction SilentlyContinue; "
                    "$proof = [ordered]@{ "
                    "drive=$drive; "
                    "accessPath=$accessPath; "
                    "diskNumber=$partition.DiskNumber; "
                    "partitionNumber=$partition.PartitionNumber; "
                    "diskUniqueId=$disk.UniqueId; "
                    "volumeUniqueId=$volume.UniqueId; "
                    "driveLetter=$partition.DriveLetter; "
                    "wasReadOnly=$wasReadOnly; "
                    "pathReachable=[bool](Test-Path $accessPath) "
                    "}; "
                    "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
                    "Write-Output ('LOCKFIX_ACCESS_PATH=' + ($proof | ConvertTo-Json -Compress)); "
                    "Write-Output \"Volume $drive`: access path is available\""
                ),
            ], timeout=30)
        except Exception as exc:
            error = str(exc)
            self.audit.write("disk.access_path.error", slot_id=slot.slot_id, drive_letter=drive, error=error)
            try:
                output = self.reassign_access_path_with_mountvol(slot, drive, reason="ensure_access_path_storage_api_unavailable")
            except Exception:
                raise
        self.persist_storage_state(slot, output)
        self.audit.write("disk.access_path", slot_id=slot.slot_id, drive_letter=drive, output=output)

    def reassign_access_path_with_mountvol(self, slot: SlotConfig, drive: str, reason: str) -> str:
        self.assert_not_protected_os_volume(slot)
        access_path = self.remembered_access_path(slot, drive)
        storage_state = self.read_storage_state(slot)
        stored_volume_path = self.stored_volume_mount_path(storage_state)
        script = (
            f"$drive = '{drive}'; "
            f"$accessPath = '{self.ps_single_quote(access_path)}'; "
            f"$storedVolumePath = '{self.ps_single_quote(stored_volume_path)}'; "
            "$ErrorActionPreference = 'Stop'; "
            "if ($drive -eq 'C') { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
            "if (Test-Path $accessPath) { "
            "$proof = [ordered]@{ drive=$drive; accessPath=$accessPath; volumeMountPath=''; pathReachable=$true; method='existing_path' }; "
            "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
            "Write-Output \"Volume $drive`: already reachable\"; return "
            "}; "
            "$selected = $null; "
            "$mounted = mountvol 2>&1 | Out-String; "
            "$entries = @(); $current = $null; "
            "foreach ($line in ($mounted -split \"`r?`n\")) { "
            "$trim = $line.Trim(); "
            "if ($trim -match '^\\\\\\\\\\?\\\\Volume\\{[^}]+\\}\\\\$') { "
            "if ($current) { $entries += [pscustomobject]$current }; "
            "$current = [ordered]@{ Name=$trim; Mounts=@() }; "
            "} elseif ($current -and $trim -and $trim -ne '*** NO MOUNT POINTS ***') { "
            "$current.Mounts += $trim "
            "} "
            "}; "
            "if ($current) { $entries += [pscustomobject]$current }; "
            "if (-not $selected -and $storedVolumePath) { "
            "$selected = $entries | Where-Object { $_.Name -eq $storedVolumePath } | Select-Object -First 1 "
            "}; "
            "if ($storedVolumePath -and -not $selected) { "
            "Write-Output \"LOCKFIX_MOUNTVOL_NOTICE=stored Volume GUID is not visible in current mountvol output; selecting a current unmounted backup candidate\" "
            "}; "
            "if (-not $selected) { "
            "$mountedDriveSignatures = @($entries | Where-Object { $_.Mounts | Where-Object { $_ -match '^[A-Z]:\\\\$' } } | ForEach-Object { if ($_.Name -match '^\\\\\\\\\\?\\\\Volume\\{([^}-]+)-') { $Matches[1] } }); "
            "$candidates = @($entries | Where-Object { "
            "$_.Mounts.Count -eq 0 -and $_.Name -match '^\\\\\\\\\\?\\\\Volume\\{([^}-]+)-' -and $mountedDriveSignatures -notcontains $Matches[1] "
            "}); "
            "if ($candidates.Count -eq 1) { $selected = $candidates[0] } "
            "elseif ($candidates.Count -gt 1) { throw \"LOCK-FIX mountvol fallback found multiple unmounted non-system volume candidates for $drive`:; recorded volume GUID is required\" } "
            "}; "
            "if (-not $selected) { throw \"LOCK-FIX mountvol fallback could not identify the unmounted backup volume for $drive`:\" }; "
            "mountvol $accessPath $($selected.Name) | Out-Null; "
            "Start-Sleep -Milliseconds 250; "
            "if (-not (Test-Path $accessPath)) { throw \"Volume $drive`: mountvol assigned a volume GUID but the path is still not reachable\" }; "
            "$proof = [ordered]@{ drive=$drive; accessPath=$accessPath; volumeMountPath=$selected.Name; pathReachable=[bool](Test-Path $accessPath); method='mountvol' }; "
            "Write-Output ('LOCKFIX_STORAGE_STATE=' + ($proof | ConvertTo-Json -Compress)); "
            "Write-Output ('LOCKFIX_ACCESS_PATH=' + ($proof | ConvertTo-Json -Compress)); "
            "Write-Output \"Volume $drive`: access path recovered with mountvol fallback\""
        )
        self.audit.write(
            "disk.access_path.mountvol_fallback.start",
            slot_id=slot.slot_id,
            drive_letter=drive,
            access_path=access_path,
            stored_volume_path=stored_volume_path,
            reason=reason,
            message="Windows Storage cmdlets are unavailable; LOCK-FIX will try mountvol-based drive-letter recovery.",
        )
        try:
            output = self.storage_run([
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ], timeout=30)
        except Exception as exc:
            self.audit.write(
                "disk.access_path.mountvol_fallback.error",
                slot_id=slot.slot_id,
                drive_letter=drive,
                access_path=access_path,
                error=str(exc),
                resolution=(
                    "LOCKFIXWebUI 서비스 계정이 LocalSystem인지 확인하고 "
                    "tools\\fix_lockfix_permissions_admin.ps1을 관리자 권한으로 실행하세요. "
                    "기존 언마운트 시 저장된 volumeMountPath/volumePath 정보도 필요합니다."
                ),
            )
            raise
        self.persist_storage_state(slot, output)
        self.audit.write(
            "disk.access_path.mountvol_fallback",
            slot_id=slot.slot_id,
            drive_letter=drive,
            access_path=access_path,
            output=output,
        )
        return output

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

    def stored_volume_mount_path(self, storage_state: dict) -> str:
        value = str(
            storage_state.get("volumeMountPath")
            or storage_state.get("volumePath")
            or storage_state.get("volumeName")
            or ""
        ).strip()
        return value if value.startswith("\\\\?\\Volume{") and value.endswith("\\") else ""

    def persist_storage_state(self, slot: SlotConfig, output: str) -> None:
        prefix = "LOCKFIX_STORAGE_STATE="
        for line in str(output or "").splitlines():
            if line.startswith(prefix):
                try:
                    data = json.loads(line[len(prefix) :])
                except Exception as exc:
                    self.audit.write("disk.storage_state.error", slot_id=slot.slot_id, error=str(exc))
                    return
                previous = self.read_storage_state(slot)
                preserved = {
                    key: value
                    for key, value in previous.items()
                    if value not in ("", None)
                    and key
                    in {
                        "accessPath",
                        "diskNumber",
                        "partitionNumber",
                        "diskUniqueId",
                        "volumeUniqueId",
                        "volumePath",
                        "volumeMountPath",
                        "volumeName",
                    }
                }
                merged = {**preserved, **{key: value for key, value in data.items() if value not in ("", None)}}
                self.storage_state_path(slot).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
                self.audit.write("disk.storage_state", slot_id=slot.slot_id, path=str(self.storage_state_path(slot)))
                return

    def partition_lookup_script(self, slot: SlotConfig, drive: str) -> str:
        state = self.read_storage_state(slot)
        disk_number = str(state.get("diskNumber", ""))
        partition_number = str(state.get("partitionNumber", ""))
        disk_unique_id = str(state.get("diskUniqueId", ""))
        volume_unique_id = str(state.get("volumeUniqueId", ""))
        volume_path = str(state.get("volumePath") or state.get("volumeMountPath") or state.get("volumeName") or "")
        access_path = self.remembered_access_path(slot, drive)
        return (
            f"$drive = '{drive}'; "
            f"$accessPath = '{self.ps_single_quote(access_path)}'; "
            "Update-HostStorageCache -ErrorAction SilentlyContinue; "
            "Get-Disk -ErrorAction SilentlyContinue | Out-Null; "
            "Get-Volume -ErrorAction SilentlyContinue | Out-Null; "
            "$partition = Get-Partition -DriveLetter $drive -ErrorAction SilentlyContinue; "
            f"$storedDiskNumber = '{disk_number}'; "
            f"$storedPartitionNumber = '{partition_number}'; "
            f"$storedDiskUniqueId = '{self.ps_single_quote(disk_unique_id)}'; "
            f"$storedVolumeUniqueId = '{self.ps_single_quote(volume_unique_id)}'; "
            f"$storedVolumePath = '{self.ps_single_quote(volume_path)}'; "
            "if (-not $partition -and $storedDiskNumber -and $storedPartitionNumber) { "
            "$partition = Get-Partition -DiskNumber ([UInt32]$storedDiskNumber) -PartitionNumber ([UInt32]$storedPartitionNumber) -ErrorAction SilentlyContinue "
            "}; "
            "if (-not $partition -and $storedDiskUniqueId) { "
            "$diskByUnique = Get-Disk -ErrorAction SilentlyContinue | Where-Object { [string]$_.UniqueId -eq $storedDiskUniqueId } | Select-Object -First 1; "
            "if ($diskByUnique -and $storedPartitionNumber) { "
            "$partition = Get-Partition -DiskNumber $diskByUnique.Number -PartitionNumber ([UInt32]$storedPartitionNumber) -ErrorAction SilentlyContinue "
            "} elseif ($diskByUnique) { "
            "$partition = Get-Partition -DiskNumber $diskByUnique.Number -ErrorAction SilentlyContinue | Where-Object { $_.Type -notin @('Reserved','System') } | Select-Object -First 1 "
            "} "
            "}; "
            "if (-not $partition -and $storedVolumeUniqueId) { "
            "$volumeByUnique = Get-Volume -ErrorAction SilentlyContinue | Where-Object { [string]$_.UniqueId -eq $storedVolumeUniqueId } | Select-Object -First 1; "
            "if ($volumeByUnique) { $partition = Get-Partition -Volume $volumeByUnique -ErrorAction SilentlyContinue | Select-Object -First 1 } "
            "}; "
            "if (-not $partition) { "
            "$candidatePartitions = @(Get-Partition -ErrorAction Stop | Where-Object { "
            "-not $_.DriveLetter -and $_.Type -notin @('Reserved','System') "
            "} | ForEach-Object { "
            "$candidatePartition = $_; "
            "$candidateDisk = $candidatePartition | Get-Disk -ErrorAction SilentlyContinue; "
            "if ($candidateDisk -and -not $candidateDisk.IsBoot -and -not $candidateDisk.IsSystem) { "
            "$candidatePartition "
            "} "
            "}); "
            "if ($candidatePartitions.Count -eq 1) { "
            "$partition = $candidatePartitions[0] "
            "} elseif ($candidatePartitions.Count -gt 1) { "
            "throw \"LOCK-FIX found multiple unassigned non-OS partitions. Cannot safely choose drive $drive`: without recorded disk identity\" "
            "} "
            "}; "
            "if (-not $partition) { throw \"LOCK-FIX backup partition was not found for drive $drive`:\" }; "
            "$disk = $partition | Get-Disk -ErrorAction Stop; "
            "if ($disk.IsOffline) { Set-Disk -Number $disk.Number -IsOffline $false -ErrorAction Stop; $disk = Get-Disk -Number $disk.Number -ErrorAction Stop }; "
            "if ($disk.IsBoot -or $disk.IsSystem) { throw 'Protected Windows OS disk cannot be used by LOCK-FIX' }; "
        )

    def remembered_access_path(self, slot: SlotConfig, drive: str) -> str:
        state = self.read_storage_state(slot)
        access_path = str(state.get("accessPath") or "").strip()
        if access_path:
            return access_path
        return f"{drive}:\\"

    def ps_single_quote(self, value: str) -> str:
        return str(value).replace("'", "''")

    def is_access_denied_error(self, message: str) -> bool:
        normalized = str(message or "").lower()
        return any(token in normalized for token in ("access is denied", "access denied", "액세스가 거부", "0x80041003"))

    def is_drive_letter_absent_error(self, message: str) -> bool:
        normalized = str(message or "").lower()
        return any(
            token in normalized
            for token in (
                "cmdletizationquery_notfound_driveletter",
                "no msft_volume",
                "msft_volume",
                "개체가 없습니다",
                "cannot find",
                "not found",
                "does not exist",
                "driveletter",
            )
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

