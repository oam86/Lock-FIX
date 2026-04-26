from __future__ import annotations

import os
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[1]
REMOTE_ROOT = "/home/oam/lockfix-poc"
FILES = [
    ".gitignore",
    "README.md",
    "build_windows.ps1",
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


def mkdir_p(sftp: paramiko.SFTPClient, path: str) -> None:
    parts = [part for part in path.split("/") if part]
    current = ""
    for part in parts:
        current += "/" + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def upload_file(sftp: paramiko.SFTPClient, local_rel: str) -> None:
    local_path = ROOT / local_rel
    remote_path = REMOTE_ROOT + "/" + local_rel.replace("\\", "/")
    mkdir_p(sftp, str(Path(remote_path).parent).replace("\\", "/"))
    sftp.put(str(local_path), remote_path)


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    return path.name == ".DS_Store" or path.suffix.lower() in EXCLUDED_SUFFIXES


def upload_tree(sftp: paramiko.SFTPClient, local_rel: str) -> None:
    local_root = ROOT / local_rel
    if not local_root.exists():
        return

    for local_path in local_root.rglob("*"):
        relative = local_path.relative_to(ROOT)
        if should_skip(relative):
            continue
        remote_path = REMOTE_ROOT + "/" + str(relative).replace("\\", "/")
        if local_path.is_dir():
            mkdir_p(sftp, remote_path)
        elif local_path.is_file():
            mkdir_p(sftp, str(Path(remote_path).parent).replace("\\", "/"))
            sftp.put(str(local_path), remote_path)


def run(client: paramiko.SSHClient, command: str) -> str:
    _, stdout, stderr = client.exec_command(command, timeout=30)
    output = stdout.read().decode(errors="replace").strip()
    error = stderr.read().decode(errors="replace").strip()
    if error and not output:
        return error
    return output


def main() -> int:
    password = os.environ["LOCKFIX_SSH_PW"]
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        "112.148.194.115",
        port=3223,
        username="oam",
        password=password,
        timeout=10,
        look_for_keys=False,
        allow_agent=False,
    )
    try:
        sftp = client.open_sftp()
        mkdir_p(sftp, REMOTE_ROOT)
        for file in FILES:
            upload_file(sftp, file)
            print(f"uploaded {file}")
        upload_tree(sftp, "integrated")
        print("uploaded integrated sources")
        sftp.close()
        print(run(client, f"cd {REMOTE_ROOT} && python3 -m compileall -q lockfix webui.py lockfixctl.py && python3 -m unittest discover -s tests -v"))
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
