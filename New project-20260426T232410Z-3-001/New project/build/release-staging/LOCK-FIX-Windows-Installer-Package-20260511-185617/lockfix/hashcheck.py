from __future__ import annotations

import hashlib
from pathlib import Path


def manifest_digest(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return hashlib.sha256(b"missing-root").hexdigest()

    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == ".lockfix_manifest.sha256":
            continue
        stat = path.stat()
        digest.update(rel.encode("utf-8"))
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
    return digest.hexdigest()


def read_expected_manifest(root: Path, manifest_path: str):
    path = root / manifest_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip().split()[0]


def verify_manifest(root: Path, manifest_path: str) -> tuple[bool, str, str | None]:
    actual = manifest_digest(root)
    expected = read_expected_manifest(root, manifest_path)
    if expected is None:
        return True, actual, None
    return actual == expected, actual, expected
