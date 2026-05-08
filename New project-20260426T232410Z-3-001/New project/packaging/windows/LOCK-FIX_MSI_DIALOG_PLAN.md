# LOCK-FIX MSI Dialog Plan

Advanced Installer Dialog Editor에서 아래 순서로 First Time Install 시퀀스를 구성합니다.

## Dialog Sequence

```text
WelcomeDlg
LockFixSystemCheckDlg
LockFixInstallTypeDlg
LockFixComponentsDlg
LockFixVeeamConnectionDlg
LockFixSecurityKeyDlg
VerifyReadyDlg / LockFixSummaryDlg
ProgressDlg
ExitDialog
```

## Dialog Details

### LockFixSystemCheckDlg

Controls:

- Windows Version status row
- PowerShell status row
- WinRM status row
- Firewall status row
- Administrator permission status row

Properties:

- `LOCKFIX_SYSTEMCHECK_STATUS`

### LockFixInstallTypeDlg

Controls:

- Radio button: Recommended
- Radio button: Advanced

Properties:

- `LOCKFIX_INSTALL_TYPE`

### LockFixComponentsDlg

Controls:

- Checkbox card: Core Service
- Checkbox card: Web UI
- Checkbox card: Veeam Connector
- Checkbox card: Agent
- Checkbox card: DB

Properties:

- `LOCKFIX_ENABLE_CORE`
- `LOCKFIX_ENABLE_WEBUI`
- `LOCKFIX_ENABLE_VEEAM`
- `LOCKFIX_ENABLE_AGENT`
- `LOCKFIX_ENABLE_DB`

### LockFixVeeamConnectionDlg

Controls:

- Edit box: Veeam Server IP
- Edit box: Port
- Combo box: Authentication Type
- Edit box: User
- Password edit box: Password or Token

Properties:

- `LOCKFIX_VEEAM_HOST`
- `LOCKFIX_VEEAM_PORT`
- `LOCKFIX_VEEAM_AUTH_TYPE`
- `LOCKFIX_VEEAM_USER`
- `LOCKFIX_VEEAM_SECRET`

### LockFixSecurityKeyDlg

Controls:

- Combo box: LOCK-FIX License Key / API Key
- Password edit box: Key

Properties:

- `LOCKFIX_SECURITY_KEY_TYPE`
- `LOCKFIX_SECURITY_KEY`

### LockFixSummaryDlg

Displays:

- Install Path
- Service Name
- Web UI Port
- Web UI URL
- Veeam Server
- Authentication Type
- Selected Components

Properties:

- `APPDIR`
- `LOCKFIX_SERVICE_NAME`
- `LOCKFIX_WEB_PORT`
- `LOCKFIX_WEB_URL`
- `LOCKFIX_VEEAM_HOST`
- `LOCKFIX_VEEAM_PORT`

### ExitDialog

Displays:

- Installation completed
- Web UI URL: `https://localhost:8443`

Option:

- Launch LOCK-FIX Web UI
