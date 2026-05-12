# LOCK-FIX Operation Guide

## Daily Revalidation

Run the daily revalidation after the expected Veeam Backup Copy window.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\send-lockfix-report.ps1 -SendOnIssue
```

The check validates:

1. Today's Veeam Backup Copy job result is `Success` or `Warning`.
2. The repository disk is offline.
3. The repository drive letter is removed.
4. The repository volume mount point is removed.
5. No administrator-approved online window is active.
6. Today's audit log is compared with yesterday's log.
7. Recoverable storage exposure is retried by unmounting and setting the disk offline.
8. Non-recoverable issues can be sent to `rich.kim@oam.co.kr`.

## Outputs

- `reports\daily-report-yyyyMMdd.html`
- `runtime\daily-revalidation-yyyyMMdd.json`
- `runtime\audit.jsonl`

## Email Configuration

The script sends email only when an issue is detected and `-SendOnIssue` is provided. Configure SMTP through environment variables:

```powershell
$env:LOCKFIX_SMTP_HOST = "smtp.example.local"
$env:LOCKFIX_SMTP_PORT = "587"
$env:LOCKFIX_SMTP_USER = "lockfix@example.local"
$env:LOCKFIX_SMTP_PASSWORD = "change-me"
$env:LOCKFIX_SMTP_FROM = "lockfix@example.local"
$env:LOCKFIX_SMTP_TLS = "true"
```

If SMTP is not configured, the report and JSON log are still generated and the email result is recorded as not sent.

If the script is run from a source checkout instead of an installed LOCK-FIX package, pass Veeam credentials explicitly or set the same environment variables:

```powershell
.\scripts\send-lockfix-report.ps1 `
  -VeeamBaseUrl "https://<VEEAM_SERVER_IP>:9419" `
  -VeeamUser "<VEEAM_USER>" `
  -VeeamPassword "<VEEAM_PASSWORD>" `
  -SendOnIssue
```

## Scheduler Example

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\send-lockfix-report.ps1`" -SendOnIssue"
$trigger = New-ScheduledTaskTrigger -Daily -At 23:50
Register-ScheduledTask -TaskName "LOCK-FIX Daily Revalidation" -Action $action -Trigger $trigger -RunLevel Highest -Description "Validate Veeam backup and air-gap repository isolation."
```

## Safety Rules

- `C:\` is never a valid LOCK-FIX repository isolation target.
- Daily recovery does not open an online access window.
- If an administrator-approved online window is active, daily recovery records a warning and does not force the disk offline.
- If disk identity is ambiguous, the check fails and requires manual confirmation.
