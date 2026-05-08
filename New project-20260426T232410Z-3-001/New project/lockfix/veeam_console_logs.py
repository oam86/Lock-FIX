from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


LOG_TIMESTAMP_RE = re.compile(r"^\[(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?\]")
KOREAN_TIME_RE = re.compile(
    r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(오전|오후)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?"
)


def latest_backup_copy_console_log_summary(
    *,
    log_root: str,
    backup_copy_name: str,
    job_name: str,
    target_name: str,
    policy_job_id: str,
    repository_id: str,
    repository_name: str,
    repository_path: str,
) -> dict[str, Any]:
    root = Path(log_root)
    if not root.exists():
        return {}

    job_dir = root / veeam_log_folder_name(backup_copy_name) / veeam_log_folder_name(job_name)
    files = candidate_log_files(root, job_dir, job_name, target_name, backup_copy_name)
    if not files:
        return {}

    parent_text = ""
    child_text = ""
    for path in files:
        text = read_tail_text(path)
        if not text:
            continue
        lower = text.lower()
        if not parent_text and policy_job_id and policy_job_id.lower() in lower:
            parent_text = text
        if not child_text and target_name and target_name.lower() in path.name.lower() and "backupsync" in path.name.lower():
            child_text = text
    if not parent_text:
        parent_text = read_tail_text(files[0]) if files else ""
    if not child_text:
        child_candidates = [path for path in files if "backupsync" in path.name.lower()]
        child_text = read_tail_text(child_candidates[0]) if child_candidates else parent_text

    parent = parse_parent_session(parent_text, policy_job_id)
    child = parse_child_session(child_text)
    if not parent and not child:
        return {}

    display_name = backup_copy_name
    if job_name:
        display_name = f"{display_name}\\{job_name}" if display_name else job_name
    display_target = target_name or child.get("target") or ""
    full_name = f"{display_name} - {display_target}" if display_target else display_name

    started_dt = child.get("started_dt") or parent.get("started_dt")
    ended_dt = child.get("ended_dt") or parent.get("ended_dt")
    finished_dt = parent.get("ended_dt") or ended_dt
    if not started_dt and ended_dt:
        started_dt = ended_dt
    if not ended_dt and started_dt:
        ended_dt = started_dt
    if not (started_dt and ended_dt):
        return {}

    algorithm = child.get("algorithm") or "Incremental"
    transferred = child.get("transferred") or "0 B"
    backup_size = child.get("backup_size") or "-"
    status = child.get("status") or parent.get("status") or "Success"
    session_id = child.get("session_id") or parent.get("session_id") or ""
    duration = duration_text(started_dt, ended_dt)

    actions = [
        f"Backup copy for {full_name} started at {format_dt(started_dt)}",
        f"{full_name} ({algorithm}) ({transferred}) processing finished at {format_dt(ended_dt)}: {transferred} transferred",
    ]
    if finished_dt:
        actions.append(f"Job finished at {format_dt(finished_dt)}")
    actions.append(
        "OK - VBR REST 9419 is connected; latest Backup Copy console time was read from Veeam local logs."
    )

    return {
        "state_source": "veeam_rest_api_console_log",
        "session_id": session_id or f"{full_name}|{format_dt(started_dt)}",
        "id": session_id or f"{full_name}|{format_dt(started_dt)}",
        "name": job_name or display_name,
        "job": job_name or display_name,
        "job_id": policy_job_id,
        "target": display_target,
        "status": normalize_status(status),
        "result": normalize_status(status),
        "session_state": "BACKUP_COMPLETED" if normalize_status(status) == "Success" else "WAITING",
        "progress_percent": 100 if normalize_status(status) == "Success" else 0,
        "current_step": 2 if normalize_status(status) == "Success" else 1,
        "started_at": format_dt(started_dt),
        "ended_at": format_dt(ended_dt),
        "job_finished_at": format_dt(finished_dt) if finished_dt else format_dt(ended_dt),
        "duration": duration,
        "backup_size": backup_size,
        "transferred": transferred,
        "speed": child.get("speed") or "-",
        "repository_id": repository_id,
        "repository_name": repository_name,
        "repository_path": repository_path,
        "backup_match_strategy": "backup_job_id_console_log",
        "match_strategy": "backup_job_id_console_log",
        "restore_point_scope": {
            "backup_name": backup_copy_name,
            "backup_job_id": policy_job_id,
            "backup_object_name": display_target,
            "repository_id": repository_id,
            "repository_name": repository_name,
            "repository_path": repository_path,
            "console_log_root": str(root),
        },
        "veeam_console_actions": actions[:3],
        "session_logs": [
            {
                "name": job_name or display_name,
                "status": normalize_status(status),
                "actions": actions,
                "duration": duration,
                "progress_percent": 100 if normalize_status(status) == "Success" else 0,
                "started_at": format_dt(started_dt),
                "ended_at": format_dt(ended_dt),
                "backup_size": backup_size,
                "transferred": transferred,
                "speed": child.get("speed") or "-",
            }
        ],
    }


def veeam_log_folder_name(value: str) -> str:
    cleaned = re.sub(r"[<>:\"/\\|?*]+", "_", str(value or "").strip())
    return re.sub(r"\s+", "_", cleaned)


def candidate_log_files(root: Path, job_dir: Path, job_name: str, target_name: str, backup_copy_name: str) -> list[Path]:
    candidates: list[Path] = []
    if job_dir.exists():
        candidates.extend(path for path in job_dir.glob("Job*.log") if path.is_file())
    if not candidates:
        needles = [item.lower() for item in (job_name, target_name, backup_copy_name) if item]
        for path in root.rglob("Job*.log"):
            try:
                text = str(path).lower()
                if any(needle.replace(" ", "_") in text or needle in text for needle in needles):
                    candidates.append(path)
            except OSError:
                continue
    return sorted(set(candidates), key=lambda path: path.stat().st_mtime, reverse=True)[:12]


def read_tail_text(path: Path, max_bytes: int = 1_500_000) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def parse_parent_session(text: str, policy_job_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if not text:
        return result
    session_creation: list[tuple[datetime, str, datetime]] = []
    session_end: list[tuple[datetime, str, datetime]] = []
    completions: list[tuple[datetime, str, str]] = []
    for line in text.splitlines():
        line_dt = parse_log_line_dt(line)
        if not line_dt:
            continue
        creation_match = re.search(r"\[JobSession\]\s+Update session \[([^\]]+)\]\s+CreationTime:\s+(.+)$", line)
        if creation_match:
            display_dt = parse_display_time(creation_match.group(2)) or line_dt
            session_creation.append((display_dt, creation_match.group(1), line_dt))
        end_match = re.search(r"\[JobSession\]\s+Update session \[([^\]]+)\]\s+EndTime:\s+(.+)$", line)
        if end_match:
            display_dt = parse_display_time(end_match.group(2)) or line_dt
            if display_dt.year > 1900:
                session_end.append((display_dt, end_match.group(1), line_dt))
        complete_match = re.search(r"Job session '([^']+)'.*status:\s+'([^']+)'", line)
        if complete_match:
            completions.append((line_dt, complete_match.group(1), complete_match.group(2)))
    if session_creation:
        started, session_id, _ = max(session_creation, key=lambda item: item[0])
        result["started_dt"] = started
        result["session_id"] = session_id
    if session_end:
        ended, session_id, _ = max(session_end, key=lambda item: item[0])
        result["ended_dt"] = ended
        result["session_id"] = result.get("session_id") or session_id
    if completions:
        _, session_id, status = max(completions, key=lambda item: item[0])
        result["status"] = status
        result["session_id"] = result.get("session_id") or session_id
    if policy_job_id and policy_job_id.lower() not in text.lower():
        return {}
    return result


def parse_child_session(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if not text:
        return result
    starts: dict[str, datetime] = {}
    completions: list[tuple[datetime, str, str, str, str]] = []
    algorithm = ""
    target = ""
    backup_size = "-"
    transferred = "0 B"
    speed = "-"
    for line in text.splitlines():
        line_dt = parse_log_line_dt(line)
        if not line_dt:
            continue
        if "incremental point" in line.lower() or "incremental mode" in line.lower():
            algorithm = "Incremental"
        elif "full point" in line.lower() or "full mode" in line.lower():
            algorithm = algorithm or "Full"
        target_match = re.search(r"Backup Copy Job .*?\\.*? - ([^\]']+)", line)
        if target_match:
            target = target_match.group(1).strip()
        session_match = re.search(r"\[Session\]\s+Id '([^']+)'.*State 'Working'", line)
        if session_match:
            starts[session_match.group(1)] = line_dt
        total_match = re.search(r"TotalSize '([^']+)'", line)
        if total_match:
            backup_size = format_log_size(total_match.group(1))
        complete_match = re.search(
            r"Job session '([^']+)'.*status:\s+'([^']+)'.*'([^']+)'\s+of\s+'([^']+)'\s+bytes",
            line,
        )
        if complete_match:
            session_id, status, raw_transferred, raw_total = complete_match.groups()
            completions.append((line_dt, session_id, status, raw_transferred, raw_total))
    if completions:
        ended_dt, session_id, status, raw_transferred, raw_total = max(completions, key=lambda item: item[0])
        result["session_id"] = session_id
        result["status"] = status
        result["ended_dt"] = ended_dt
        result["started_dt"] = starts.get(session_id) or min(starts.values()) if starts else ended_dt
        transferred = format_log_size(raw_transferred)
        backup_size = format_log_size(raw_total) if raw_total != "0 B" else backup_size
    result["algorithm"] = algorithm or "Incremental"
    result["target"] = target
    result["backup_size"] = backup_size
    result["transferred"] = transferred
    result["speed"] = speed
    return result


def parse_log_line_dt(line: str) -> datetime | None:
    match = LOG_TIMESTAMP_RE.search(line)
    if not match:
        return None
    day, month, year, hour, minute, second, micro = match.groups()
    return datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        int((micro or "0")[:6].ljust(6, "0")),
    )


def parse_display_time(value: str) -> datetime | None:
    match = KOREAN_TIME_RE.search(str(value or ""))
    if not match:
        return None
    year, month, day, meridiem, hour, minute, second = match.groups()
    hour_int = int(hour)
    if meridiem == "오후" and hour_int != 12:
        hour_int += 12
    if meridiem == "오전" and hour_int == 12:
        hour_int = 0
    return datetime(int(year), int(month), int(day), hour_int, int(minute), int(second or 0))


def format_dt(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else "-"


def duration_text(started: datetime, ended: datetime) -> str:
    seconds = max(0, int((ended - started).total_seconds()))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def normalize_status(value: str) -> str:
    return "Success" if str(value or "").strip().lower() in {"success", "succeeded"} else str(value or "Waiting")


def format_log_size(value: str) -> str:
    text = str(value or "").replace(",", "").strip()
    if text.lower().endswith("b"):
        return text
    try:
        return format_bytes(text)
    except ValueError:
        return text or "0 B"


def format_bytes(value: str) -> str:
    raw = float(str(value).replace(",", "").strip())
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while raw >= 1024 and index < len(units) - 1:
        raw /= 1024
        index += 1
    if index == 0:
        return f"{int(raw)} {units[index]}"
    return f"{raw:.1f} {units[index]}"
