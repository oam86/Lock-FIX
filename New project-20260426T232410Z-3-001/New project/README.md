## RBAC, Approval, and Audit Automation

LOCK-FIX includes a permission and approval automation module for department-based administration.

Implemented scope:

- RBAC roles and permissions: `SUPER_ADMIN`, `SECURITY_ADMIN`, `BACKUP_OPERATOR`, `HARDWARE_ADMIN`, `AUDITOR`, `UI_DESIGNER`, `DEVELOPER`
- Department and user management with disable-instead-of-delete behavior
- Backend permission guards for protected Web UI APIs
- Dynamic Web UI menu visibility based on session role and permissions
- Approval request workflow for `DISK_ONLINE`, `DISK_OFFLINE`, `POLICY_CHANGE`, `EMERGENCY_UNLOCK`, `HARDWARE_POWER_ON`, `HARDWARE_POWER_OFF`
- Dual approval policy for `DISK_ONLINE`, `POLICY_CHANGE`, `EMERGENCY_UNLOCK`, `HARDWARE_POWER_ON`, `HARDWARE_POWER_OFF`
- Structured audit log model and CSV export
- Approval Requests UI with My Requests, Pending Approval, Approved, Rejected, and Expired tabs
- Regression tests for RBAC, approvals, user management, audit logs, schema contract, and Web UI guards

Security rules enforced by code:

- The request creator cannot approve their own request.
- The same user cannot approve the same request twice.
- Execution APIs are blocked until the required approval count is met.
- Audit logs have no delete API, and `AUDIT_LOG_DELETE` is not defined.
- Unauthorized access is returned as `403 Forbidden` and written to Audit Log.
- Emergency unlock requires a reason, dual approval, and audit logging.
- Super Admin still counts as only one approver and cannot complete dual approval alone.

Database migration:

```text
migrations/001_lockfix_rbac_approval_audit.sql
config/lockfix_schema.sql
```

Core backend files:

```text
lockfix/rbac.py
lockfix/users.py
lockfix/approvals.py
lockfix/audit_log.py
lockfix/schema.py
lockfix/controller.py
webui.py
```

Core frontend files:

```text
web/static/index.html
web/static/app.js
web/static/styles.css
```

Run Web UI:

```powershell
python .\webui.py --host 127.0.0.1 --port 8088 --config .\config\lockfix.example.json
```

Run tests:

```powershell
python -m unittest tests.test_lockfix
```

Remaining hardening items:

- Replace the current JSON runtime stores with a selected production DB engine using the provided migration.
- Add password hashing and login integration for managed users beyond the bootstrap/admin login flow.
- Add operator-facing create/edit forms for all approval request types where the Web UI currently exposes read/approve flow first.
- Add retention, archival, and integrity sealing for long-term audit log operation.

# LOCK-FIX Windows Server Package

Windows Server 전용 LOCK-FIX 설치 패키지 소스입니다.

목표 흐름:

```text
백업 완료 -> Flush/I/O 확인 -> Windows 볼륨 분리 -> 실제 전원 차단
재연결 -> UID 검증 -> Hash 검증 -> 정상 시 Online
```

중요 보호 정책:

- `C:\` Windows OS 볼륨은 절대 분리, 재연결, 전원 격리 대상이 될 수 없습니다.
- 장치 경로 또는 마운트 경로가 `C:`, `C:\`, `C:\...`이면 즉시 차단하고 감사 로그를 남깁니다.
- 설치 패키지는 Windows Server 전용으로 제공되며 다른 OS용 설치/패키징 흐름은 포함하지 않습니다.

1차 PoC 제외 범위:

- 솔레노이드 락
- 물리 탈거 방지
- Limit Switch
- 트레이 잠금 제어

## 구성

- `lockfixctl.py`: CLI 진입점
- `lockfix/`: 상태 머신, 디스크 작업, 전원 제어, UID/Hash 검증
- `config/lockfix.example.json`: Windows Server 설정 예시
- `tests/`: 핵심 로직 테스트
- `requirements_from_ppt.md`: PPT에서 추출한 요구사항 원문

## 빠른 실행

기본 설치 설정은 Windows Server 운영 적용을 위해 `operation_mode: live`, `dry_run: false`입니다. `C:\` Windows OS 볼륨은 코드 레벨에서 항상 차단됩니다.

```powershell
python .\lockfixctl.py status --config .\config\lockfix.example.json
python .\lockfixctl.py isolate --slot BAY-01 --config .\config\lockfix.example.json
python .\lockfixctl.py reconnect --slot BAY-01 --config .\config\lockfix.example.json
```

Windows 실행 파일 빌드:

```powershell
.\build_windows.ps1
.\dist\lockfixctl.exe status --config .\config\lockfix.example.json
.\dist\lockfixctl.exe isolate --slot BAY-01 --config .\config\lockfix.example.json
```

마법사형 Windows 설치 실행 파일:

```powershell
.\dist\installer\LOCK-FIX Setup Wizard.exe
```

배포용 설치 패키지 ZIP 생성:

```powershell
.\build_installer_package.ps1
```

생성 위치:

```text
dist\release\LOCK-FIX-Windows-Installer-Package-YYYYMMDD-HHMMSS.zip
```

## 폐쇄망 설치 기준

LOCK-FIX는 Windows Server 폐쇄망 설치를 기준으로 패키징합니다. 설치 대상 서버에서 인터넷 접속, `pip install`, 외부 다운로드가 없어도 설치와 Web UI 실행이 가능해야 합니다.

오프라인 패키지 포함 항목:

- `python\python.exe`: Web UI와 Veeam REST 연동에 사용하는 내장 Python 런타임
- `LOCK-FIX Setup Wizard.exe`: 설치 마법사
- `LOCK-FIX Console.exe`: Web UI 콘솔 실행기
- `LOCK-FIX WebUI Service.exe`: 8088 Web UI를 유지하는 Windows 서비스 실행 파일
- `dist\lockfix-ui.exe`, `dist\lockfixctl.exe`
- `config`, `lockfix`, `web`, `tools`

Web UI 실행기는 설치 폴더의 `python\python.exe`를 가장 먼저 사용합니다. 따라서 신규 Windows Server가 폐쇄망이고 Python이 사전 설치되어 있지 않아도 LOCK-FIX Web UI를 실행할 수 있습니다.

폐쇄망에서 필요한 통신은 다음으로 제한합니다.

- 로컬 Web UI: `http://127.0.0.1:8088`
- Veeam Backup & Replication REST API: `https://<Veeam Backup Server>:9419`
- Enterprise Manager `9398`은 참고 진단만 수행하며 필수 조건이 아닙니다.

Web UI는 Windows 서비스로 등록해 `8088` 포트를 항상 열어두는 방식을 기준으로 합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install_lockfix_webui_service.ps1
```

설치 마법사 화면 흐름:

```text
1. Welcome
2. System Check
3. Install Type
4. Component Selection
5. Veeam Connection
6. Security Key
7. Summary
8. Install Progress
9. Complete
```

LOCK-FIX 설치 UX는 Visual Studio Installer처럼 카드형 기능 선택 화면을 쓰고, Veeam처럼 설치 전 환경 점검과 설치 요약 화면을 넣는 방식으로 구성합니다.

Advanced Installer 기반 Windows MSI 설치 파일 생성:

```powershell
.\build_msi.ps1
```

생성 목표:

```text
dist\installer\LOCK-FIX Setup.msi
```

UI 실행 파일:

```powershell
.\dist\lockfix-ui.exe
```

실행하면 로컬 웹 서버가 켜지고 기본 브라우저에서 `http://127.0.0.1:8088`이 열립니다.

로컬 웹 UI 실행:

```powershell
python .\webui.py --host 127.0.0.1 --port 8088 --config .\config\lockfix.example.json
```

브라우저에서 `http://127.0.0.1:8088`을 열면 Mock 제어 UI를 볼 수 있습니다.

Veeam REST API 연동 확인:

```powershell
$env:LOCKFIX_VEEAM_BASE_URL = "https://<TARGET_SERVER_IP>:9419"
$env:LOCKFIX_VEEAM_EM_BASE_URL = "https://127.0.0.1:9398"
$env:LOCKFIX_VEEAM_USER = "Veeam계정"
$env:LOCKFIX_VEEAM_PASSWORD = "Veeam비밀번호"
python .\lockfixctl.py veeam-test --config .\config\lockfix.example.json
```

Web UI 연동 비교 검증은 실행 중인 Web UI 서버에 HTTP로만 접근합니다. 이 명령은 `lockfix-ui.exe`, `python webui.py`, 또는 새 Windows 프로세스를 직접 실행하지 않습니다. Web UI 서버는 Windows 서비스 또는 작업 스케줄러에서 별도로 실행되어야 합니다.

```powershell
python .\lockfixctl.py veeam-webui-test --config .\config\lockfix.example.json --url http://127.0.0.1:8088
```

8088 포트가 닫혀 있으면 결과에 `Web UI server is not running`으로 표시하며, 이를 Veeam REST 9419 연동 실패로 처리하지 않습니다. 비교 기준은 `veeam-test` CLI 결과와 `/api/veeam-backup` HTTP 응답의 base_url, token, sessions, jobs, job match, latest session 값입니다.

이미 설치된 Web UI가 `LOCKFIX_VEEAM_PASSWORD`를 못 읽는 경우에는 설치본 복구 도구를 관리자 PowerShell에서 실행합니다. 이 도구는 비밀번호를 프롬프트로 입력받고, 값을 화면에 출력하지 않습니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\repair_installed_webui_veeam.ps1 -RestartWebUi
```

Veeam Backup Server IP는 Agent 대상 서버 IP와 별개입니다. Agent IP가 서버마다 바뀌더라도 LOCK-FIX는 `auto_discover=true`일 때 실제 토큰 발급이 되는 Veeam Backup Server REST 9419 주소를 자동 선택합니다.

자동 탐지 우선순위:

1. `LOCKFIX_VEEAM_BASE_URL` 환경변수
2. `config.veeam.discovery_candidates`
3. `LOCKFIX_VEEAM_CANDIDATES` 환경변수
4. `config.veeam.base_url`
5. `127.0.0.1`, `localhost`
6. 로컬 IPv4 대역의 9419 포트 탐지

예:

```json
"veeam": {
  "base_url": "https://<TARGET_SERVER_IP>:9419",
  "auto_discover": false,
  "discovery_candidates": [
    "https://<TARGET_SERVER_IP>:9419"
  ],
  "discovery_scan_local_subnet": false
}
```

LOCK-FIX Veeam 연동의 기준 API는 VBR REST `9419`입니다. PowerShell/curl 실패는 Windows Schannel 진단 이슈일 수 있으므로 실제 제품 검증은 Python HTTPS 클라이언트의 `9419` 호출 결과로 판단합니다. Enterprise Manager `9398`은 참고 진단만 수행하며 필수 조건이 아닙니다.

운영 설정에서는 Veeam Job ID를 알 수 있으면 이름보다 정확하므로 `job_id`를 함께 지정합니다.

필수 연동 흐름:

1. `https://<VeeamServer>:9419/api/v1`을 VBR REST API 기준 URL로 사용합니다.
2. `/api/oauth2/token`에서 OAuth2 access token을 발급합니다.
3. 모든 요청에 `x-api-version`을 적용합니다. 기본값은 `1.2-rev1`이며 현장 Swagger/API Reference에 맞게 `config.veeam.api_version`에서 변경할 수 있습니다.
4. `/api/v1/jobs`와 `/api/v1/sessions`를 조회합니다.
5. `job_id`를 우선 매칭하고, 없으면 `job_name`을 exact, case-insensitive, normalized 순서로 보조 매칭합니다.
6. 최신 session의 `result/status`가 `Success`이면 `controller.isolate()`를 호출합니다.
7. Agent 백업이 `/api/v1/sessions`에 직접 노출되지 않는 환경에서는 `/api/v1/backups`, `/api/v1/backups/{id}/objects`, `/api/v1/backupObjects/{id}/restorePoints`를 조회해 최신 restore point를 백업 완료 증거로 사용합니다.
8. LOCK-FIX의 Air-Gap 1단계 완료 기준은 Backup Copy가 `C:\`가 아닌 대상 저장소에 최종 restore point를 생성한 시점입니다. 대상 저장소는 `target_repository_id`, `target_repository_name`, `target_repository_path`로 지정하며, `C:\` 저장소는 코드 레벨에서 제외됩니다.
9. 같은 `session_id` 또는 restore point ID는 runtime state에 기록해 중복 isolate를 방지합니다.
10. PoC에서는 `verify_ssl=false`로 자체 서명 인증서를 허용할 수 있고, 운영에서는 Veeam REST 인증서를 Windows 신뢰 저장소에 등록한 뒤 `verify_ssl=true`를 사용합니다.
11. `veeam-test`는 9419, 참고용 9398, token, jobs, sessions, backups, repositories, job match, isolate 조건을 한 번에 진단합니다.

```json
"veeam": {
  "job_name": "Agent_backup",
  "job_id": "실제 Veeam Job ID"
}
```

PowerShell 7 또는 Windows `curl.exe`만 실패하고 Python 검증은 성공하면 Windows Schannel/TLS 경로를 별도로 확인합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\veeam_schannel_diagnostics.ps1 -TestCurl
```

## 실제 장비 연결 전 확인

실제 Relay/MOSFET 제어 명령을 연결하려면 `config/lockfix.example.json`을 복사한 뒤 다음 값을 Windows Server 현장 환경에 맞게 바꿉니다.

- `dry_run`: 실제 명령 실행 시 `false`
- `slots[].device`: `D:\`, `E:\` 같은 백업 전용 Windows 볼륨
- `slots[].mount_point`: 백업 전용 Windows 볼륨 경로
- `slots[].power.off_command`, `on_command`: Relay/MOSFET 제어 명령
- `slots[].expected_uid`: 등록 디스크 UID

주의: `dry_run: false`에서는 Windows Server 볼륨 분리와 전원 제어 명령이 실제 실행됩니다. `C:\` OS 볼륨은 코드 레벨에서 항상 차단됩니다.
