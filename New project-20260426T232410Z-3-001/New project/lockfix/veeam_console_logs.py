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
        ended_dt = child.get("last_progress_dt") or parent.get("last_activity_dt") or started_dt
    if not (started_dt and ended_dt):
        return {}

    algorithm = child.get("algorithm") or "Incremental"
    transferred = child.get("transferred") or "0 B"
    backup_size = child.get("backup_size") or "-"
    status = child.get("status") or parent.get("status") or "Success"
    if normalize_status(status) != "Success" and started_dt and ended_dt and ended_dt < started_dt:
        ended_dt = parent.get("last_activity_dt") or child.get("last_progress_dt") or started_dt
    session_id = child.get("session_id") or parent.get("session_id") or ""
    duration = duration_text(started_dt, ended_dt)

    actions = [f"Backup copy for {full_name} started at {format_dt(started_dt)}"]
    normalized_status = normalize_status(status)
    if normalized_status == "Success":
        actions.append(
            f"{full_name} ({algorithm}) ({transferred}) processing finished at {format_dt(ended_dt)}: {transferred} transferred"
        )
    else:
        progress = child.get("progress_percent", 0)
        speed = child.get("speed") or "0 KB/s"
        actions.append(
            f"{full_name} ({algorithm}) ({backup_size}) is running: {transferred} transferred at {speed}, progress {progress}%"
        )
    for error in child.get("errors", [])[:3]:
        actions.append(f"WARN - Veeam console reported: {error}")
    if finished_dt and normalized_status == "Success":
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
        "status": normalized_status,
        "result": normalized_status,
        "session_state": "BACKUP_COMPLETED" if normalized_status == "Success" else "WAITING",
        "progress_percent": 100 if normalized_status == "Success" else int(child.get("progress_percent", 0) or 0),
        "current_step": 2 if normalized_status == "Success" else 1,
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
                "status": normalized_status,
                "actions": actions,
                "duration": duration,
                "progress_percent": 100 if normalized_status == "Success" else int(child.get("progress_percent", 0) or 0),
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
    working: list[tuple[datetime, str]] = []
    last_activity: datetime | None = None
    for line in text.splitlines():
        line_dt = parse_log_line_dt(line)
        if not line_dt:
            continue
        last_activity = line_dt
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
        working_match = re.search(r"\[Session\]\s+Id '([^']+)'.*State 'Working'", line)
        if working_match:
            working.append((line_dt, working_match.group(1)))
    if session_creation:
        started, session_id, _ = max(session_creation, key=lambda item: item[0])
        result["started_dt"] = started
        result["session_id"] = session_id
    if session_end:
        ended, session_id, _ = max(session_end, key=lambda item: item[0])
        result["ended_dt"] = ended
        result["session_id"] = result.get("session_id") or session_id
    latest_working = max(working, key=lambda item: item[0]) if working else None
    latest_completion = max(completions, key=lambda item: item[0]) if completions else None
    if latest_completion and not (latest_working and latest_working[0] > latest_completion[0]):
        _, session_id, status = latest_completion
        result["status"] = status
        result["session_id"] = result.get("session_id") or session_id
    elif latest_working or (result.get("started_dt") and not result.get("ended_dt")):
        result["status"] = "Working"
        if latest_working:
            _, session_id = latest_working
            result["session_id"] = result.get("session_id") or session_id
    if last_activity:
        result["last_activity_dt"] = last_activity
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
    progress_percent = 0
    last_progress_dt: datetime | None = None
    progress_events: list[tuple[datetime, int, str, str]] = []
    errors: list[str] = []
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
        starting_match = re.search(r"Starting job '([^']+)', id '([^']+)'", line)
        if starting_match:
            starts[starting_match.group(2)] = line_dt
            target_from_start = re.search(r" - ([^\\']+)$", starting_match.group(1))
            if target_from_start:
                target = target_from_start.group(1).strip()
        total_match = re.search(r"TotalSize '([^']+)'", line)
        if total_match:
            backup_size = format_log_size(total_match.group(1))
        progress_match = re.search(
            r"Job progress:\s+'(\d+)%',\s+'([^']+)'\s+of\s+'([^']+)'\s+bytes",
            line,
        )
        if progress_match:
            progress_percent = int(progress_match.group(1))
            transferred = format_log_size(progress_match.group(2))
            backup_size = format_log_size(progress_match.group(3))
            last_progress_dt = line_dt
            progress_events.append((line_dt, progress_percent, transferred, backup_size))
        error_match = re.search(r"(Cannot create folder\..+|CreateDirectory\(.+|Failed to create directory '.+')", line)
        if error_match:
            message = error_match.group(1).strip()
            if message not in errors:
                errors.append(message)
        complete_match = re.search(
            r"Job session '([^']+)'.*status:\s+'([^']+)'.*'([^']+)'\s+of\s+'([^']+)'\s+bytes",
            line,
        )
        if complete_match:
            session_id, status, raw_transferred, raw_total = complete_match.groups()
            completions.append((line_dt, session_id, status, raw_transferred, raw_total))
    latest_start = max(starts.items(), key=lambda item: item[1]) if starts else None
    latest_completion = max(completions, key=lambda item: item[0]) if completions else None
    running_is_newer = bool(
        latest_start
        and latest_completion
        and (latest_start[1] > latest_completion[0] or (last_progress_dt and last_progress_dt > latest_completion[0]))
    )
    if latest_completion and not running_is_newer:
        ended_dt, session_id, status, raw_transferred, raw_total = latest_completion
        result["session_id"] = session_id
        result["status"] = status
        result["ended_dt"] = ended_dt
        result["started_dt"] = starts.get(session_id) or min(starts.values()) if starts else ended_dt
        transferred = format_log_size(raw_transferred)
        backup_size = format_log_size(raw_total) if raw_total != "0 B" else backup_size
    elif latest_start:
        session_id, started_dt = latest_start
        current_progress = [item for item in progress_events if item[0] >= started_dt]
        if current_progress:
            last_progress_dt, progress_percent, transferred, backup_size = max(current_progress, key=lambda item: item[0])
        result["session_id"] = session_id
        result["status"] = "Working"
        result["started_dt"] = started_dt
        result["ended_dt"] = last_progress_dt or started_dt
    result["algorithm"] = algorithm or "Incremental"
    result["target"] = target
    result["backup_size"] = backup_size
    result["transferred"] = transferred
    result["speed"] = speed
    result["progress_percent"] = progress_percent
    if last_progress_dt:
        result["last_progress_dt"] = last_progress_dt
    if errors:
        result["errors"] = errors[-3:]
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
