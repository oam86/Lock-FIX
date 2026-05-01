from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATED_ROOT = ROOT / "integrated"


def project_summary(name: str, relative_path: str, kind: str, run_hint: str) -> dict:
    root = INTEGRATED_ROOT / relative_path
    files = [path for path in root.rglob("*") if path.is_file()] if root.exists() else []
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
        "excluded": [".venv", "node_modules", "target", ".idea", "__MACOSX", "__pycache__", "logs"],
    }
