from __future__ import annotations

import json
import os

import paramiko


TARGETS = [
    ("DataCenter", "112.148.194.115", 3223),
    ("WebSolution", "112.148.194.115", 3222),
]

COMMANDS = {
    "identity": "printf 'USER=%s\\nHOME=%s\\nPWD=%s\\n' \"$USER\" \"$HOME\" \"$PWD\"; hostname",
    "home_listing": "find \"$HOME\" -maxdepth 2 -mindepth 1 -printf '%y %p\\n' 2>/dev/null | sort | head -200",
    "git_repos": "find \"$HOME\" -maxdepth 5 -type d -name .git -printf '%h\\n' 2>/dev/null | sort | head -100",
    "lockfix_files": "find \"$HOME\" -maxdepth 6 \\( -iname '*lockfix*' -o -iname '*lock-fix*' -o -iname 'webui.py' -o -iname 'lockfixctl.py' \\) -printf '%y %p\\n' 2>/dev/null | sort | head -200",
    "dev_markers": "find \"$HOME\" -maxdepth 5 -type f \\( -name package.json -o -name requirements.txt -o -name pyproject.toml -o -name docker-compose.yml -o -name Dockerfile -o -name '*.sln' -o -name '*.csproj' \\) -printf '%p\\n' 2>/dev/null | sort | head -200",
    "processes": "ps -u \"$USER\" -o pid,etime,cmd --sort=cmd | grep -Ei 'python|node|npm|uvicorn|gunicorn|lockfix|webui' | grep -v grep || true",
}


def run_command(client: paramiko.SSHClient, command: str) -> str:
    _, stdout, stderr = client.exec_command(command, timeout=30)
    output = stdout.read().decode(errors="replace").strip()
    error = stderr.read().decode(errors="replace").strip()
    return output or error


def main() -> int:
    password = os.environ["LOCKFIX_SSH_PW"]
    results = []
    for name, host, port in TARGETS:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result = {"name": name, "host": host, "port": port, "sections": {}}
        try:
            client.connect(
                hostname=host,
                port=port,
                username="oam",
                password=password,
                timeout=10,
                banner_timeout=10,
                auth_timeout=10,
                look_for_keys=False,
                allow_agent=False,
            )
            for key, command in COMMANDS.items():
                result["sections"][key] = run_command(client, command)
        except Exception as exc:
            result["error"] = str(exc)
        finally:
            client.close()
        results.append(result)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
