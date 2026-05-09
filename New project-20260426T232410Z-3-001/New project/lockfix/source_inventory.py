from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATED_ROOT = ROOT / "integrated"
EXCLUDED_DIR_NAMES = {".venv", "node_modules", "target", ".idea", "__MACOSX", "__pycache__", "logs"}
MAX_FILES_PER_PROJECT = 2500


def project_files(root: Path, limit: int = MAX_FILES_PER_PROJECT) -> tuple[list[Path], bool]:
    if not root.exists():
        return [], False
    files: list[Path] = []
    stack = [root]
    limited = False
    while stack:
        current = stack.pop()
        try:
            children = list(current.iterdir())
        except OSError:
            continue
        for child in children:
            if child.is_dir():
                if child.name in EXCLUDED_DIR_NAMES:
                    continue
                stack.append(child)
                continue
            if not child.is_file():
                continue
            files.append(child)
            if len(files) >= limit:
                limited = True
                return files, limited
    return files, limited


def project_summary(name: str, relative_path: str, kind: str, run_hint: str) -> dict:
    root = INTEGRATED_ROOT / relative_path
    files, scan_limited = project_files(root)
    extensions: dict[str, int] = {}
    for path in files:
        suffix = path.suffix.lower() or "(none)"
        extensions[suffix] = extensions.get(suffix, 0) + 1

    return {
        "name": name,
        "path": str(root),
        "kind": kind,
        "exists": root.exists(),
        "file_count": len(files),
        "scan_limited": scan_limited,
        "top_extensions": sorted(
            [{"extension": key, "count": value} for key, value in extensions.items()],
            key=lambda item: item["count"],
            reverse=True,
        )[:8],
        "run_hint": run_hint,
    }


def integrated_source_inventory() -> dict:
    return {
        "root": str(INTEGRATED_ROOT),
        "projects": [
            project_summary(
                "oam-hw-solution",
                "oam-hw-solution",
                "Python Flask hardware monitoring server",
                'gunicorn -w 1 --threads 4 -b 127.0.0.1:5001 "app:create_app()"',
            ),
            project_summary(
                "OamDataCenter",
                "OamDataCenter",
                "Java Spring Boot data center server + React web-front",
                "./mvnw spring-boot:run",
            ),
        ],
        "excluded": sorted(EXCLUDED_DIR_NAMES),
    }
