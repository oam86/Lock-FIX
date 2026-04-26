from __future__ import annotations

import os
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build" / "lockfix-poc-linux"
PAYLOAD_DIR = BUILD_DIR / "payload"
DIST_DIR = ROOT / "dist"
ARCHIVE = DIST_DIR / "lockfix-poc-linux.tar.gz"

PAYLOAD_FILES = [
    "README.md",
    "lockfixctl.py",
    "webui.py",
    "requirements_from_ppt.md",
    "config/lockfix.example.json",
    "lockfix/__init__.py",
    "lockfix/audit.py",
    "lockfix/command.py",
    "lockfix/config.py",
    "lockfix/controller.py",
    "lockfix/disk.py",
    "lockfix/hashcheck.py",
    "lockfix/identity.py",
    "lockfix/integrated.py",
    "lockfix/power.py",
    "lockfix/source_inventory.py",
    "lockfix/state_store.py",
    "lockfix/states.py",
    "tests/test_lockfix.py",
    "web/static/app.js",
    "web/static/index.html",
    "web/static/oam-logo.png",
    "web/static/styles.css",
]

EXCLUDED_DIRS = {".git", ".idea", ".venv", "__MACOSX", "__pycache__", "node_modules", "target", ".cache", "logs"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".class", ".log", ".tmp"}


def copy_file(src_rel: str, target_root: Path) -> None:
    src = ROOT / src_rel
    dst = target_root / src_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    return path.name == ".DS_Store" or path.suffix.lower() in EXCLUDED_SUFFIXES


def copy_tree(src_rel: str, target_root: Path) -> None:
    src_root = ROOT / src_rel
    if not src_root.exists():
        return

    for src in src_root.rglob("*"):
        relative = src.relative_to(ROOT)
        if should_skip(relative):
            continue
        dst = target_root / relative
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def main() -> int:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for file in PAYLOAD_FILES:
        copy_file(file, PAYLOAD_DIR)

    copy_tree("integrated", PAYLOAD_DIR)

    for script in ["install.sh", "uninstall.sh"]:
        copy_file(f"packaging/linux/{script}", BUILD_DIR)
        os.chmod(BUILD_DIR / "packaging" / "linux" / script, 0o755)
        shutil.move(str(BUILD_DIR / "packaging" / "linux" / script), str(BUILD_DIR / script))

    shutil.rmtree(BUILD_DIR / "packaging")

    with tarfile.open(ARCHIVE, "w:gz") as tar:
        tar.add(BUILD_DIR, arcname="lockfix-poc-linux")

    print(ARCHIVE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
