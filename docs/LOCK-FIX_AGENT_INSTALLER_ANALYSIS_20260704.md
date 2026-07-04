# LOCK-FIX Agent Installer ZIP Analysis - 2026-07-04

## Scope

Analyzed local package:

```text
C:\tmp\LOCK-FIX-Agent-Installer-Current-20260704.zip
```

SHA-256:

```text
5D54C9ABA883ABAC0A659AE6094C294B9870DFA847A4AF004F406E0BD3F46FA2
```

The package was extracted for inspection only. Installer executables were not run during this analysis.

## Package Summary

Top-level extracted folder:

```text
LOCK-FIX-Windows-Installer-Package-20260515-135149
```

Key included components:

- `LOCK-FIX Setup Wizard.exe`
- `LOCK-FIX Console.exe`
- `LOCK-FIX WebUI Service.exe`
- `dist/lockfix-ui.exe`
- `dist/lockfixctl.exe`
- `python/python.exe`
- `webui.py`
- `lockfix/`
- `web/static/`
- `config/`
- `tools/`
- `docs/`
- `runtime/`

The package includes its own Python runtime, so the Web UI can run even when system Python is not installed.

## Web UI Execution Result

The Web UI was started from the extracted package using the bundled Python runtime with safe runtime flags:

```powershell
$env:LOCKFIX_DRY_RUN = "true"
$env:LOCKFIX_OPERATION_MODE = "poc"
.\python\python.exe .\webui.py --host 127.0.0.1 --port 8088 --config .\config\lockfix.example.json
```

Observed result:

- `http://127.0.0.1:8088/` returned HTTP 200.
- The served page title is `LOCK-FIX PoC`.
- The login screen is available.
- The server process listened on `127.0.0.1:8088`.

## Login and RBAC Findings

The Web UI contains a bootstrap administrator login path in `webui.py`.

Observed API behavior:

- Login endpoint: `POST /api/login`
- Session endpoint: `GET /api/session`
- Successful bootstrap login returns an authenticated session with role `SUPER_ADMIN`.
- The session is cookie-based; `/api/session` only reports authenticated when called with the same web request session/cookie.

The managed-user model is implemented in `lockfix/users.py` and stores users under:

```text
runtime/users.json
```

Important RBAC roles observed:

- `SUPER_ADMIN`
- `SECURITY_ADMIN`
- `BACKUP_OPERATOR`
- `HARDWARE_ADMIN`
- `AUDITOR`
- `UI_DESIGNER`
- `DEVELOPER`

Important permissions observed include dashboard, Veeam, report, approval, audit log, user management, system settings, disk online/offline, and hardware control permissions.

## Security Notes

Do not publish the full ZIP package or raw environment-specific configuration to a public repository without review.

Items requiring hardening before production or public distribution:

- Remove or rotate bootstrap/default credentials.
- Avoid committing real Veeam usernames, passwords, tokens, PDU credentials, customer IPs, MAC addresses, hostnames, or repository identifiers.
- Keep `dry_run=true` for demonstrations and analysis.
- Use environment variables or a secure store for Veeam and PDU credentials.
- Review `config/lockfix.example.json` before reuse because it contains site-specific sample values.
- Prefer adding sanitized documentation and configuration templates instead of operational secrets.

## GitHub Upload Recommendation

Recommended safe upload scope:

- Sanitized analysis document under `docs/`.
- Sanitized example config under `config/*.template.json` if needed.
- Small README updates explaining bundled Python and Web UI startup.

Avoid uploading:

- Full installer ZIP binaries unless release storage is intended.
- Logs with local host/user paths.
- Files containing real credentials or infrastructure identifiers.
- Runtime state files generated during testing.

## Current Status

- ZIP structure inspected.
- Web UI launched successfully with bundled Python.
- Local login API verified.
- This document intentionally omits credential values and sensitive environment-specific secrets.
