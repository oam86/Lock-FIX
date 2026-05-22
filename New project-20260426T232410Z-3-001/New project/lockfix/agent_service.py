from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from .config import load_config
from .controller import LockFixController, repository_volume_root
from .veeam_diagnostics import run_veeam_diagnostics


REQUEST_MAX_AGE_SECONDS = 10 * 60
REQUEST_BATCH_SIZE = 1
STALE_QUEUE_PRUNE_THRESHOLD = 100
DIAGNOSTICS_PENDING_KEEP = 1


class AgentServiceUnavailable(RuntimeError):
    """Raised when the privileged LOCK-FIX Agent/Service did not answer."""


class AgentServiceClient:
    """File-queue client used by WebUI to delegate privileged work.

    The WebUI writes intent and already-validated policy context. A Windows
    Service running as LocalSystem or a dedicated lockfix-svc account processes
    the request and performs disk/Veeam operations outside the UI process.
    """

    def __init__(
        self,
        queue_root: Path,
        *,
        timeout_seconds: float = 30.0,
        allow_inline_fallback: bool = False,
        inline_executor: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.queue_root = Path(queue_root)
        self.requests_dir = self.queue_root / "requests"
        self.responses_dir = self.queue_root / "responses"
        self.timeout_seconds = timeout_seconds
        self.allow_inline_fallback = allow_inline_fallback
        self.inline_executor = inline_executor

    def ensure_dirs(self) -> None:
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    def submit_and_wait(self, operation: str, payload: dict[str, Any], *, timeout_seconds: float | None = None) -> dict[str, Any]:
        if self.allow_inline_fallback and self.inline_executor:
            return self.inline_executor(operation, payload)
        self.ensure_dirs()
        request_id = uuid.uuid4().hex
        request = {
            "request_id": request_id,
            "operation": operation,
            "payload": payload,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PENDING",
            "requested_by": "LOCK-FIX WebUI",
        }
        request_path = self.requests_dir / f"{request_id}.json"
        response_path = self.responses_dir / f"{request_id}.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
        deadline = time.time() + float(timeout_seconds or self.timeout_seconds)
        while time.time() < deadline:
            if response_path.exists():
                try:
                    response = json.loads(response_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    raise AgentServiceUnavailable(f"Invalid LOCK-FIX Agent/Service response: {exc}") from exc
                if not isinstance(response, dict):
                    raise AgentServiceUnavailable("Invalid LOCK-FIX Agent/Service response payload.")
                if response.get("ok") is False:
                    raise AgentServiceUnavailable(str(response.get("error") or "LOCK-FIX Agent/Service operation failed."))
                return response
            time.sleep(0.2)
        try:
            request_path.unlink(missing_ok=True)
        except OSError:
            pass
        if self.allow_inline_fallback and self.inline_executor:
            return self.inline_executor(operation, payload)
        raise AgentServiceUnavailable(
            "LOCK-FIX Agent/Service is not responding. Privileged disk and Veeam operations must run in the Windows Service."
        )


class AgentServiceWorker:
    """Privileged worker intended to run inside LOCK-FIX Windows Service."""

    def __init__(self, config_path: Path, queue_root: Path) -> None:
        self.config_path = Path(config_path)
        self.queue_root = Path(queue_root)
        self.requests_dir = self.queue_root / "requests"
        self.responses_dir = self.queue_root / "responses"
        self.processed_dir = self.queue_root / "processed"
        self.expired_dir = self.queue_root / "expired"

    def ensure_dirs(self) -> None:
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.expired_dir.mkdir(parents=True, exist_ok=True)

    def process_once(self, max_requests: int = REQUEST_BATCH_SIZE) -> int:
        self.ensure_dirs()
        self.prune_stale_backlog()
        processed = 0
        request_paths = sorted(
            self.requests_dir.glob("*.json"),
            key=lambda path: (self.request_sort_priority(path), path.stat().st_mtime),
            reverse=True,
        )
        for request_path in request_paths[: max(1, int(max_requests))]:
            try:
                request = json.loads(request_path.read_text(encoding="utf-8"))
                response = self.execute_request(request)
            except Exception as exc:
                request_id = request_path.stem
                response = {"ok": False, "request_id": request_id, "error": str(exc)}
            response_path = self.responses_dir / f"{request_path.stem}.json"
            response_path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
            try:
                request_path.replace(self.processed_dir / request_path.name)
            except FileNotFoundError:
                pass
            processed += 1
        return processed

    def request_sort_priority(self, request_path: Path) -> int:
        try:
            text = request_path.read_text(encoding="utf-8")
        except OSError:
            return 0
        if '"operation": "emergency.reconnect"' in text:
            return 3
        if '"operation": "disk.reconnect"' in text or '"operation": "disk.isolate"' in text:
            return 2
        return 1

    def run_forever(self, poll_seconds: float = 0.5) -> None:
        self.ensure_dirs()
        while True:
            try:
                self.process_once()
            except Exception as exc:
                self.record_worker_error(exc)
            time.sleep(poll_seconds)

    def prune_stale_backlog(self) -> int:
        request_paths = list(self.requests_dir.glob("*.json"))
        pruned = self.prune_superseded_diagnostics(request_paths)
        if len(request_paths) <= STALE_QUEUE_PRUNE_THRESHOLD:
            return pruned
        now = time.time()
        expired = 0
        for request_path in request_paths:
            if self.request_path_age_seconds(request_path, now=now) <= REQUEST_MAX_AGE_SECONDS:
                continue
            if self.expire_request_path(request_path):
                expired += 1
        if expired:
            self.record_queue_pruned(expired, len(request_paths))
        return pruned + expired

    def prune_superseded_diagnostics(self, request_paths: list[Path]) -> int:
        diagnostics = [
            path
            for path in request_paths
            if self.request_operation(path) == "veeam.diagnostics"
        ]
        if len(diagnostics) <= DIAGNOSTICS_PENDING_KEEP:
            return 0
        diagnostics.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        expired = 0
        for request_path in diagnostics[DIAGNOSTICS_PENDING_KEEP:]:
            if self.expire_request_path(request_path):
                expired += 1
        if expired:
            self.record_queue_pruned(expired, len(request_paths))
        return expired

    def request_operation(self, request_path: Path) -> str:
        try:
            request = json.loads(request_path.read_text(encoding="utf-8"))
            return str(request.get("operation") or "") if isinstance(request, dict) else ""
        except Exception:
            return ""

    def expire_request_path(self, request_path: Path) -> bool:
        target = self.expired_dir / request_path.name
        if target.exists():
            target = self.expired_dir / f"{request_path.stem}-{uuid.uuid4().hex}.json"
        try:
            request_path.replace(target)
            return True
        except FileNotFoundError:
            return False
        except OSError as exc:
            self.record_worker_error(exc)
            return False

    def execute_request(self, request: dict[str, Any]) -> dict[str, Any]:
        operation = str(request.get("operation") or "")
        payload = request.get("payload") if isinstance(request.get("payload"), dict) else {}
        config = load_config(self.config_path)
        controller = LockFixController(config)
        request_id = str(request.get("request_id") or "")
        if self.request_age_seconds(request) > REQUEST_MAX_AGE_SECONDS:
            controller.audit.write(
                "agent.service.request.expired",
                request_id=request_id,
                operation=operation,
                slot_id=str(payload.get("slot_id") or ""),
                job_id=str(payload.get("job_id") or ""),
                repository_path=str(payload.get("repository_path") or ""),
                message="Expired privileged request was not executed by LOCK-FIX Agent/Service.",
            )
            return {
                "ok": False,
                "request_id": request_id,
                "operation": operation,
                "error": "LOCK-FIX Agent/Service request expired before execution.",
            }
        controller.audit.write(
            "agent.service.request.received",
            request_id=request_id,
            operation=operation,
            slot_id=str(payload.get("slot_id") or ""),
            job_id=str(payload.get("job_id") or ""),
            repository_path=str(payload.get("repository_path") or ""),
            message="Privileged operation accepted by LOCK-FIX Agent/Service.",
        )
        if operation == "disk.isolate":
            state = controller.isolate(str(payload.get("slot_id") or ""), repository_path=str(payload.get("repository_path") or ""))
            return {"ok": True, "request_id": request_id, "operation": operation, "state": state.value}
        if operation == "disk.reconnect":
            state = controller.reconnect(str(payload.get("slot_id") or ""), repository_path=str(payload.get("repository_path") or ""))
            return {"ok": True, "request_id": request_id, "operation": operation, "state": state.value}
        if operation == "emergency.reconnect":
            state = controller.emergency_reconnect(
                str(payload.get("slot_id") or ""),
                repository_path=str(payload.get("repository_path") or ""),
                approval_bypass=bool(payload.get("approval_bypass")),
                approval_bypass_reason=str(payload.get("approval_bypass_reason") or ""),
            )
            return {"ok": True, "request_id": request_id, "operation": operation, "state": state.value}
        if operation == "veeam.diagnostics":
            diagnostics = run_veeam_diagnostics(config, controller)
            return {"ok": True, "request_id": request_id, "operation": operation, "diagnostics": diagnostics}
        if operation == "service.preflight":
            diagnostics = self.service_preflight(payload, controller)
            return {"ok": True, "request_id": request_id, "operation": operation, "diagnostics": diagnostics}
        raise ValueError(f"Unsupported LOCK-FIX Agent/Service operation: {operation}")

    def request_age_seconds(self, request: dict[str, Any], *, now: float | None = None) -> float:
        created_at = str(request.get("created_at") or "").strip()
        if not created_at:
            return 0.0
        try:
            return max(0.0, float(now or time.time()) - time.mktime(time.strptime(created_at, "%Y-%m-%d %H:%M:%S")))
        except ValueError:
            return 0.0

    def request_path_age_seconds(self, request_path: Path, *, now: float | None = None) -> float:
        current = float(now or time.time())
        try:
            request = json.loads(request_path.read_text(encoding="utf-8"))
            age = self.request_age_seconds(request, now=current) if isinstance(request, dict) else 0.0
            if age > 0:
                return age
        except Exception:
            pass
        try:
            return max(0.0, current - request_path.stat().st_mtime)
        except OSError:
            return 0.0

    def record_queue_pruned(self, expired_count: int, pending_count: int) -> None:
        try:
            controller = LockFixController(load_config(self.config_path))
            controller.audit.write(
                "agent.service.queue.pruned",
                expired_count=expired_count,
                pending_count=pending_count,
                message="Expired LOCK-FIX Agent/Service requests were moved out of the live queue.",
            )
        except Exception as exc:
            self.record_worker_error(exc)

    def record_worker_error(self, exc: Exception) -> None:
        try:
            self.queue_root.mkdir(parents=True, exist_ok=True)
            with (self.queue_root / "worker-error.log").open("a", encoding="utf-8") as handle:
                handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {type(exc).__name__}: {exc}\n")
        except OSError:
            pass

    def run_probe(self, command: list[str], timeout: float = 8.0) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        except Exception as exc:
            return {"ok": False, "command": " ".join(command), "error": str(exc), "output": ""}
        output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
        return {
            "ok": result.returncode == 0,
            "command": " ".join(command),
            "returncode": result.returncode,
            "output": output[-4000:],
        }

    def powershell_probe(self, script: str, timeout: float = 8.0) -> dict[str, Any]:
        powershell = shutil.which("powershell.exe") or shutil.which("pwsh")
        if not powershell:
            return {"ok": False, "command": script, "error": "PowerShell executable was not found.", "output": ""}
        return self.run_probe(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            timeout=timeout,
        )

    def current_identity(self) -> dict[str, Any]:
        whoami = self.run_probe(["whoami"], timeout=4)
        groups = self.run_probe(["whoami", "/groups"], timeout=4)
        account = (whoami.get("output") or os.getenv("USERNAME") or "").strip()
        group_text = str(groups.get("output") or "").lower()
        is_system = "s-1-5-18" in group_text or account.lower().endswith("\\system") or account.lower() == "nt authority\\system"
        is_admin = "s-1-5-32-544" in group_text or "administrators" in group_text or "관리자" in group_text
        return {
            "account": account or "unknown",
            "is_local_system": is_system,
            "is_local_admin": is_system or is_admin,
            "groups_probe_ok": bool(groups.get("ok")),
            "recommended_accounts": ["LocalSystem", "lockfix-svc"],
        }

    def diagnostic_contains_text(self, payload: Any, needle: str) -> bool:
        target = str(needle or "").strip().lower()
        if not target:
            return True
        if isinstance(payload, dict):
            return any(self.diagnostic_contains_text(value, target) for value in payload.values())
        if isinstance(payload, list):
            return any(self.diagnostic_contains_text(value, target) for value in payload)
        return target in str(payload or "").lower()

    def slot_for_repository_root(self, controller: LockFixController, volume_root: str) -> str:
        normalized = str(volume_root or "").strip().replace("/", "\\").rstrip("\\").lower()
        for slot_id, slot in controller.config.slots.items():
            candidates = [slot.mount_point, slot.device]
            for candidate in candidates:
                candidate_root = str(candidate or "").strip().replace("/", "\\").rstrip("\\").lower()
                if candidate_root == normalized:
                    return slot_id
        return ""

    def preflight_check(self, key: str, label: str, ok: bool, detail: str = "", resolution: str = "") -> dict[str, Any]:
        return {
            "key": key,
            "label": label,
            "ok": bool(ok),
            "detail": detail,
            "resolution": resolution,
        }

    def build_install_preflight_checks(
        self,
        controller: LockFixController,
        identity: dict[str, Any],
        disk_command_results: list[dict[str, Any]],
        veeam: dict[str, Any],
        veeam_ok: bool,
    ) -> list[dict[str, Any]]:
        config = controller.config
        veeam_config = config.veeam
        repo_path = str(veeam_config.target_repository_path or "").strip()
        job_name = str(veeam_config.job_name or "").strip()
        repository_name = str(veeam_config.target_repository_name or "").strip()
        repository_id = str(veeam_config.target_repository_id or "").strip()
        veeam_required = bool(veeam_config.enabled)

        checks: list[dict[str, Any]] = [
            self.preflight_check(
                "veeam_rest_connection",
                "Veeam REST 연결",
                (not veeam_required) or veeam_ok,
                str((veeam.get("config") or {}).get("base_url") or veeam_config.base_url or "Veeam disabled"),
                "Veeam REST 9419 주소, 계정, 토큰 권한을 확인하세요.",
            )
        ]

        latest_session = veeam.get("latest_configured_session") if isinstance(veeam.get("latest_configured_session"), dict) else {}
        matching = veeam.get("matching") if isinstance(veeam.get("matching"), dict) else {}
        job_detected = (not veeam_required) or (
            bool(job_name)
            and bool(veeam_ok)
            and (
                bool(matching.get("matched_session"))
                or self.diagnostic_contains_text(latest_session, job_name)
                or self.diagnostic_contains_text(veeam, job_name)
            )
        )
        checks.append(
            self.preflight_check(
                "veeam_job_detection",
                "Veeam Job 감지",
                job_detected,
                job_name or "미설정",
                "설치 설정의 Veeam Job 이름이 실제 Backup Copy Job과 일치해야 합니다.",
            )
        )

        protected_os_volume = False
        repository_volume = ""
        repository_path_ok = False
        repository_detected = False
        try:
            repository_volume = repository_volume_root(repo_path) if repo_path else ""
            protected_os_volume = repository_volume.strip().replace("/", "\\").rstrip("\\").lower() == "c:"
            repository_detected = any(
                self.diagnostic_contains_text(veeam, token)
                for token in (repo_path, repository_name, repository_id)
                if token
            )
            repository_path_ok = bool(repo_path) and not protected_os_volume
        except ValueError as exc:
            repository_volume = ""
            repo_path = repo_path or str(exc)
        checks.append(
            self.preflight_check(
                "repository_path",
                "Repository 경로",
                (not veeam_required) or repository_path_ok,
                f"{repo_path or '미설정'}" + (" · REST 감지" if repository_detected else ""),
                "Repository 경로는 D:\\Backup처럼 보호 대상 Windows OS 볼륨이 아닌 로컬 볼륨이어야 합니다.",
            )
        )

        slot_id = self.slot_for_repository_root(controller, repository_volume) if repository_volume else ""
        target_volume_ok = bool(repository_volume) and bool(slot_id)
        checks.append(
            self.preflight_check(
                "target_volume",
                "대상 볼륨 매핑",
                (not veeam_required) or target_volume_ok,
                f"{repository_volume or '-'} -> {slot_id or '등록 슬롯 없음'}",
                "Repository 경로의 루트 볼륨이 LOCK-FIX 슬롯(BAY-01 등)에 매핑되어야 합니다.",
            )
        )

        disk_result_by_name = {str(item.get("name") or ""): bool(item.get("ok")) for item in disk_command_results}
        disk_offline_permission_ok = bool(identity.get("is_local_admin")) and all(
            disk_result_by_name.get(name)
            for name in ("Get-Disk", "Get-Partition", "Get-Volume", "Set-Disk")
        )
        checks.append(
            self.preflight_check(
                "disk_offline_permission",
                "디스크 Offline 권한",
                disk_offline_permission_ok,
                str(identity.get("account") or "unknown"),
                "Agent/Service 계정은 로컬 관리자 또는 LocalSystem이어야 하며 Set-Disk 권한이 필요합니다.",
            )
        )
        return checks

    def service_preflight(self, payload: dict[str, Any], controller: LockFixController) -> dict[str, Any]:
        config = controller.config
        requested_mode = str(payload.get("operation_mode") or config.operation_mode or "commercial")
        identity = self.current_identity()
        ps_checks = [
            ("Get-Disk", "Get-Disk | Select-Object -First 1 | Out-Null"),
            ("Get-Partition", "Get-Partition | Select-Object -First 1 | Out-Null"),
            ("Get-Volume", "Get-Volume | Select-Object -First 1 | Out-Null"),
            ("Set-Disk", "Get-Command Set-Disk -ErrorAction Stop | Out-Null"),
            ("Write-VolumeCache", "Get-Command Write-VolumeCache -ErrorAction Stop | Out-Null"),
            ("mountvol", "mountvol | Out-Null"),
        ]
        disk_command_results = [
            {"name": name, **self.powershell_probe(script, timeout=8)}
            for name, script in ps_checks
        ]
        execution_policy = self.powershell_probe("Get-ExecutionPolicy -List | Out-String", timeout=6)
        firewall = self.powershell_probe(
            "Get-NetFirewallRule -Enabled True -ErrorAction Stop | Select-Object -First 1 | Out-Null",
            timeout=8,
        )
        winrm = self.powershell_probe("Get-Service WinRM -ErrorAction Stop | Select-Object Status,Name | Out-String", timeout=6)
        uac = self.powershell_probe(
            "Get-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System -Name EnableLUA | Select-Object -ExpandProperty EnableLUA",
            timeout=6,
        )
        try:
            veeam = run_veeam_diagnostics(config, controller)
            veeam_ok = bool(
                veeam.get("success")
                or (veeam.get("vbr_rest_9419") or {}).get("reachable")
                or (veeam.get("vbr_rest_9419") or {}).get("token_ok")
            )
        except Exception as exc:
            veeam = {"success": False, "error": str(exc)}
            veeam_ok = False

        restricted_features = []
        if not identity["is_local_admin"]:
            restricted_features.extend(["Disk Offline", "Drive Letter 제거", "Volume Dismount", "Flush 확인"])
        for item in disk_command_results:
            if not item.get("ok"):
                restricted_features.append(f"{item['name']} 실행 불가")
        if config.veeam.enabled and not veeam_ok:
            restricted_features.append("Veeam REST 조회 실패")
        if not firewall.get("ok"):
            restricted_features.append("Firewall 정책 확인 필요")
        if not winrm.get("ok"):
            restricted_features.append("WinRM 정책 확인 필요")

        install_preflight_checks = self.build_install_preflight_checks(
            controller,
            identity,
            disk_command_results,
            veeam,
            veeam_ok,
        )
        deployment_ready = all(item.get("ok") for item in install_preflight_checks)
        for item in install_preflight_checks:
            if not item.get("ok"):
                restricted_features.append(str(item.get("label") or item.get("key") or "설치 사전점검 실패"))

        service_ok = identity["is_local_admin"] and all(item.get("ok") for item in disk_command_results)
        if requested_mode in {"commercial", "delivery"} and not service_ok:
            controller.audit.write(
                "service.permission.insufficient",
                operation_mode=requested_mode,
                account=identity["account"],
                restricted_features=restricted_features,
                message="LOCK-FIX Agent/Service account does not satisfy privileged disk-control preflight.",
            )
        controller.audit.write(
            "service.preflight.completed",
            operation_mode=requested_mode,
            account=identity["account"],
            local_admin=identity["is_local_admin"],
            restricted_count=len(restricted_features),
        )
        controller.audit.write(
            "service.install_preflight.completed",
            operation_mode=requested_mode,
            account=identity["account"],
            deployment_ready=deployment_ready,
            failed_checks=[
                str(item.get("key") or item.get("label") or "")
                for item in install_preflight_checks
                if not item.get("ok")
            ],
        )
        status = "OK" if service_ok and deployment_ready else "권한 부족" if restricted_features else "고객사 정책 확인 필요"
        return {
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation_mode": requested_mode,
            "platform": platform.platform(),
            "status": status,
            "ok": status == "OK",
            "deployment_ready": deployment_ready,
            "preflight_checks": install_preflight_checks,
            "service": {
                "running": True,
                "account": identity["account"],
                "local_system": identity["is_local_system"],
                "local_admin": identity["is_local_admin"],
                "account_policy": "LocalSystem 또는 전용 lockfix-svc 최소 권한 계정을 권장합니다.",
            },
            "disk_commands": disk_command_results,
            "veeam_api": {"ok": veeam_ok, "diagnostics": veeam},
            "uac": {"ok": bool(uac.get("ok")), "detail": uac.get("output") or uac.get("error") or ""},
            "execution_policy": {"ok": bool(execution_policy.get("ok")), "detail": execution_policy.get("output") or execution_policy.get("error") or ""},
            "firewall": {"ok": bool(firewall.get("ok")), "detail": firewall.get("output") or firewall.get("error") or ""},
            "winrm": {"ok": bool(winrm.get("ok")), "detail": winrm.get("output") or winrm.get("error") or ""},
            "restricted_features": list(dict.fromkeys(restricted_features)),
            "resolution": [
                "LOCK-FIX Agent/Service를 LocalSystem 또는 lockfix-svc 서비스 계정으로 실행하세요.",
                "상용 모드에서는 WebUI가 직접 디스크 제어를 수행하지 않습니다.",
                "Disk Offline, Drive Letter 제거, Volume Dismount 권한을 서비스 계정에 부여하세요.",
                "Veeam REST 권한과 Windows 디스크 제어 권한은 별도로 확인하세요.",
            ],
        }
