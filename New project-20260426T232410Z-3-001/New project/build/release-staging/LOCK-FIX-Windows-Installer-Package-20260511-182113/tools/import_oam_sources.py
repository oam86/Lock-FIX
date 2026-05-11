from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path(r"C:\Users\우암전자\OneDrive\Documents\우암전자+시스템")
TARGET_ROOT = ROOT / "integrated"

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__MACOSX",
    "node_modules",
    "target",
    "__pycache__",
    ".cache",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".class",
    ".log",
    ".DS_Store",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.name in EXCLUDED_DIRS:
        return True
    if path.name in EXCLUDED_SUFFIXES:
        return True
    return path.suffix in EXCLUDED_SUFFIXES


def copy_tree(name: str) -> tuple[int, int]:
    source = SOURCE_ROOT / name
    target = TARGET_ROOT / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    stack = [source]
    while stack:
        current = stack.pop()
        for path in current.iterdir():
            relative = path.relative_to(source)
            if path.is_dir():
                if should_skip(relative) or should_skip(path):
                    skipped += 1
                    continue
                (target / relative).mkdir(parents=True, exist_ok=True)
                stack.append(path)
                continue
            if should_skip(relative) or should_skip(path):
                skipped += 1
                continue
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            copied += 1
    return copied, skipped


def main() -> int:
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    results = {}
    for project in ("oam-hw-solution", "OamDataCenter"):
        copied, skipped = copy_tree(project)
        results[project] = {"copied": copied, "skipped": skipped}
    for name, result in results.items():
        print(f"{name}: copied={result['copied']} skipped={result['skipped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
