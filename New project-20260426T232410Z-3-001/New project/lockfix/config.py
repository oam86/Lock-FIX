from __future__ import annotations

import json
import os
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PowerConfig:
    type: str
    off_command: list[str]
    on_command: list[str]
    status_command: list[str]
    off_status_values: list[str]


@dataclass(frozen=True)
class SlotConfig:
    slot_id: str
    device: str
    mount_point: Path
    expected_uid: str
    identity: dict[str, str]
    manifest_path: str
    power: PowerConfig


@dataclass(frozen=True)
class VeeamConfig:
    enabled: bool
    base_url: str
    enterprise_manager_url: str
    auto_discover: bool
    discovery_candidates: list[str]
    discovery_scan_local_subnet: bool
    discovery_timeout_seconds: float
    api_version: str
    username: str
    username_env: str
    password_env: str
    verify_ssl: bool
    job_name: str
    job_id: str
    require_backup_copy: bool
    target_repository_id: str
    target_repository_name: str
    target_repository_path: str
    exclude_os_repository: bool
    console_log_fallback_enabled: bool
    console_log_root: str
    poll_interval_seconds: int
    isolate_on_status: list[str]
    post_success_delay_seconds: int
    require_repository_resync_quiet: bool


@dataclass(frozen=True)
class LockFixConfig:
    dry_run: bool
    operation_mode: str
    state_path: Path
    audit_log_path: Path
    io_quiet_seconds: int
    disk_wait_seconds: int
    veeam: VeeamConfig
    slots: dict[str, SlotConfig]

    def slot(self, slot_id: str) -> SlotConfig:
        try:
            return self.slots[slot_id]
        except KeyError as exc:
            raise ValueError(f"unknown slot: {slot_id}") from exc


def load_app_config(path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    raw["veeam"] = get_veeam_config(raw)
    return raw


def bool_value(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off", ""}:
        return False
    return default


def read_install_properties(root: Path) -> dict[str, str]:
    props_path = root / "runtime" / "install.properties"
    if not props_path.exists():
        return {}
    props: dict[str, str] = {}
    for line in props_path.read_text(encoding="utf-8-sig").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        props[key.strip()] = value.strip()
    return props


def install_veeam_base_url(props: dict[str, str]) -> str:
    base_url = str(props.get("veeam_base_url") or "").strip().rstrip("/")
    if base_url:
        return base_url
    host = str(props.get("veeam_host") or "").strip()
    if not host:
        return ""
    port = str(props.get("veeam_port") or "9419").strip() or "9419"
    if host.startswith(("http://", "https://")):
        host = host.rstrip("/")
        return host if ":" in host.rsplit("/", 1)[-1] else f"{host}:{port}"
    return f"https://{host}:{port}"


def dry_run_from_operation_mode(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower().replace("_", "-")
    if text in {"live", "production", "prod", "real", "active"}:
        return False
    if text in {"simulation", "simulate", "dry-run", "dryrun", "test", "safe"}:
        return True
    return None


def normalize_operation_mode(value: Any, dry_run: bool | None = None) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    if text in {"poc", "dev", "development", "simulation", "simulate", "dry-run", "dryrun", "test", "safe"}:
        return "poc"
    if text in {"delivery", "customer", "customer-delivery", "install", "deployment"}:
        return "delivery"
    if text in {"commercial", "live", "production", "prod", "real", "active", ""}:
        if dry_run is True and not text:
            return "poc"
        return "commercial"
    return "commercial"


def configured_operation_mode(raw: dict[str, Any], root: Path, dry_run: bool) -> str:
    props = read_install_properties(root)
    for value in (
        os.getenv("LOCKFIX_OPERATION_MODE"),
        props.get("operation_mode"),
        raw.get("operation_mode"),
    ):
        if value is not None:
            return normalize_operation_mode(value, dry_run)
    return normalize_operation_mode(None, dry_run)


def configured_dry_run(raw: dict[str, Any], root: Path) -> bool:
    props = read_install_properties(root)
    layers: list[tuple[Any, Any]] = [
        (os.getenv("LOCKFIX_DRY_RUN"), os.getenv("LOCKFIX_OPERATION_MODE")),
        (props.get("dry_run"), props.get("operation_mode")),
        (raw.get("dry_run"), raw.get("operation_mode")),
    ]
    for dry_run_value, mode_value in layers:
        if dry_run_value is not None:
            return bool_value(dry_run_value, True)
        mode_result = dry_run_from_operation_mode(mode_value)
        if mode_result is not None:
            return mode_result
    return True


def get_veeam_config(config: Any) -> dict[str, Any]:
    if isinstance(config, LockFixConfig):
        return asdict(config.veeam)
    if isinstance(config, VeeamConfig):
        return asdict(config)
    if isinstance(config, dict):
        raw = config.get("veeam", {})
        return dict(raw) if isinstance(raw, dict) else {}
    return {}


def load_config(path) -> LockFixConfig:
    base = Path(path).resolve().parent
    app_root = base.parent
    raw = load_app_config(path)
    install_props = read_install_properties(app_root)

    def resolve_path(value: str) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else app_root / candidate

    def resolve_command_args(values: list[Any]) -> list[str]:
        resolved: list[str] = []
        for value in values:
            text = str(value)
            text = text.replace("{app_root}", str(app_root))
            text = text.replace("{config_root}", str(base))
            candidate = Path(text)
            if candidate.is_absolute():
                resolved.append(str(candidate))
                continue
            normalized = text.replace("/", "\\").lstrip(".\\")
            if normalized.lower().startswith(("tools\\", "config\\", "web\\", "lockfix\\")):
                resolved.append(str(app_root / normalized))
            else:
                resolved.append(text)
        return resolved

    slots: dict[str, SlotConfig] = {}
    for item in raw.get("slots", []):
        power_raw: dict[str, Any] = item["power"]
        slot = SlotConfig(
            slot_id=item["slot_id"],
            device=item["device"],
            mount_point=Path(item["mount_point"]),
            expected_uid=item.get("expected_uid", ""),
            identity=dict(item.get("identity", {})),
            manifest_path=item.get("manifest_path", ".lockfix_manifest.sha256"),
            power=PowerConfig(
                type=power_raw.get("type", "mock"),
                off_command=resolve_command_args(list(power_raw.get("off_command", []))),
                on_command=resolve_command_args(list(power_raw.get("on_command", []))),
                status_command=resolve_command_args(list(power_raw.get("status_command", []))),
                off_status_values=[
                    str(value).strip().lower()
                    for value in power_raw.get("off_status_values", ["off", "power_off", "powered_off", "0", "false"])
                ],
            ),
        )
        slots[slot.slot_id] = slot

    veeam_raw = dict(raw.get("veeam", {}))
    installed_base_url = install_veeam_base_url(install_props)
    if installed_base_url:
        veeam_raw["base_url"] = installed_base_url
        existing_candidates = [
            str(item).rstrip("/")
            for item in veeam_raw.get("discovery_candidates", [])
            if str(item).strip()
        ]
        veeam_raw["discovery_candidates"] = [
            installed_base_url,
            *[item for item in existing_candidates if item != installed_base_url],
        ]
    if install_props.get("veeam_api_version"):
        veeam_raw["api_version"] = install_props["veeam_api_version"]
    if install_props.get("veeam_user"):
        veeam_raw["username"] = install_props["veeam_user"]
    veeam = VeeamConfig(
        enabled=bool_value(veeam_raw.get("enabled", False)),
        base_url=str(veeam_raw.get("base_url", "https://127.0.0.1:9419")).rstrip("/"),
        enterprise_manager_url=str(veeam_raw.get("enterprise_manager_url", "https://127.0.0.1:9398")).rstrip("/"),
        auto_discover=bool_value(veeam_raw.get("auto_discover", False), False),
        discovery_candidates=[str(item).rstrip("/") for item in veeam_raw.get("discovery_candidates", [])],
        discovery_scan_local_subnet=bool_value(veeam_raw.get("discovery_scan_local_subnet", False), False),
        discovery_timeout_seconds=float(veeam_raw.get("discovery_timeout_seconds", 0.35)),
        api_version=str(veeam_raw.get("api_version", "1.2-rev1")),
        username=str(veeam_raw.get("username", "")),
        username_env=str(veeam_raw.get("username_env", "LOCKFIX_VEEAM_USER")),
        password_env=str(veeam_raw.get("password_env", "LOCKFIX_VEEAM_PASSWORD")),
        verify_ssl=bool_value(veeam_raw.get("verify_ssl", False)),
        job_name=str(veeam_raw.get("job_name", "")),
        job_id=str(veeam_raw.get("job_id", "")),
        require_backup_copy=bool_value(veeam_raw.get("require_backup_copy", True), True),
        target_repository_id=str(veeam_raw.get("target_repository_id", "")),
        target_repository_name=str(veeam_raw.get("target_repository_name", "")),
        target_repository_path=str(veeam_raw.get("target_repository_path", "")),
        exclude_os_repository=bool_value(veeam_raw.get("exclude_os_repository", True), True),
        console_log_fallback_enabled=bool_value(veeam_raw.get("console_log_fallback_enabled", True), True),
        console_log_root=str(veeam_raw.get("console_log_root", "C:\\ProgramData\\Veeam\\Backup")),
        poll_interval_seconds=max(1, int(veeam_raw.get("poll_interval_seconds", 10))),
        isolate_on_status=[str(item) for item in veeam_raw.get("isolate_on_status", ["Success"])],
        post_success_delay_seconds=max(0, int(veeam_raw.get("post_success_delay_seconds", 10))),
        require_repository_resync_quiet=bool_value(veeam_raw.get("require_repository_resync_quiet", True), True),
    )

    dry_run = configured_dry_run(raw, base.parent)
    operation_mode = configured_operation_mode(raw, base.parent, dry_run)

    return LockFixConfig(
        dry_run=dry_run,
        operation_mode=operation_mode,
        state_path=resolve_path(raw.get("state_path", "runtime/state.json")),
        audit_log_path=resolve_path(raw.get("audit_log_path", "runtime/audit.jsonl")),
        io_quiet_seconds=int(raw.get("io_quiet_seconds", 30)),
        disk_wait_seconds=int(raw.get("disk_wait_seconds", 60)),
        veeam=veeam,
        slots=slots,
    )
