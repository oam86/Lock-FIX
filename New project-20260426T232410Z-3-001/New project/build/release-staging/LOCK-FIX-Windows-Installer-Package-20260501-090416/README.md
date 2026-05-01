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

기본 설정은 실제 장비를 건드리지 않는 `dry_run: true`, `mock` 전원 제어입니다.

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
$env:LOCKFIX_VEEAM_BASE_URL = "https://127.0.0.1:9419"
$env:LOCKFIX_VEEAM_EM_BASE_URL = "https://127.0.0.1:9398"
$env:LOCKFIX_VEEAM_USER = "Veeam계정"
$env:LOCKFIX_VEEAM_PASSWORD = "Veeam비밀번호"
python .\lockfixctl.py veeam-test --config .\config\lockfix.example.json
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
7. 같은 `session_id`는 runtime state에 기록해 중복 isolate를 방지합니다.
8. PoC에서는 `verify_ssl=false`로 자체 서명 인증서를 허용할 수 있고, 운영에서는 Veeam REST 인증서를 Windows 신뢰 저장소에 등록한 뒤 `verify_ssl=true`를 사용합니다.
9. `veeam-test`는 9419, 참고용 9398, token, jobs, sessions, job match, isolate 조건을 한 번에 진단합니다.

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
