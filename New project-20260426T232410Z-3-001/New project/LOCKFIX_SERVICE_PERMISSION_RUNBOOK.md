# LOCK-FIX 서비스 권한 / 포트 검증 런북

## 현재 검증 기준

- 설치 패키지와 release-staging 파일은 해시 동일 여부를 기준으로 동기화한다.
- 설치 후 실행 검증은 Windows 서비스 제어 권한, 서비스 실행 계정, WebUI 포트 응답, 방화벽 규칙을 함께 확인한다.
- LOCK-FIX WebUI 기본 확인 포트는 8088이며, 내부 기준 포트 이력이 있는 8099도 점검 대상에 포함한다.

## 관리자 권한 실행

서비스 시작, 중지, 재시작, 재등록, 방화벽 규칙 등록은 관리자 권한 PowerShell에서 수행해야 한다.

```powershell
Start-Process powershell -Verb runAs
```

관리자 PowerShell에서 점검 스크립트를 실행한다.

```powershell
cd "C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX"
.\tools\check_lockfix_service_permissions.ps1 -RestartService -RegisterFirewallRules
```

패키지 폴더에서 실행할 경우:

```powershell
cd "<LOCK-FIX 설치 패키지 폴더>"
.\tools\check_lockfix_service_permissions.ps1 -RestartService -RegisterFirewallRules
```

## 반드시 확인할 항목

| 항목 | 정상 기준 | 문제 시 조치 |
| --- | --- | --- |
| 서비스명 | `LOCKFIXWebUI` 확인 | 서비스 재등록 |
| 실행 계정 | `LocalSystem` 또는 승인된 전용 서비스 계정 | 설치 스크립트 관리자 실행 |
| 서비스 제어 | Restart-Service 성공 | 관리자 PowerShell에서 재시도 |
| 8088 포트 | LISTENING + HTTP 응답 | 서비스 재시작, 포트 점유 PID 확인 |
| 8099 포트 | 필요 시 허용/미사용 확인 | 내부 정책에 맞춰 방화벽 등록 |
| 방화벽 | TCP 8088/8099 허용 규칙 | 관리자 권한으로 규칙 등록 |
| 설치 폴더 | 서비스 계정 읽기, 로그 폴더 쓰기 가능 | ACL 보정 |
| PowerShell 디스크 명령 | Get-Disk/Get-Partition/Get-Volume 실행 가능 | 서비스 계정 권한 확인 |

## 서비스 직접 확인 명령

```powershell
Get-Service | Where-Object {$_.Name -like "*LOCK*" -or $_.DisplayName -like "*LOCK*"}
sc.exe queryex LOCKFIXWebUI
sc.exe qc LOCKFIXWebUI
sc.exe sdshow LOCKFIXWebUI
```

재시작:

```powershell
Restart-Service -Name LOCKFIXWebUI -Force
```

포트 확인:

```cmd
netstat -ano | findstr :8088
netstat -ano | findstr :8099
tasklist /FI "PID eq <포트점유PID>"
```

## 설치 스크립트 반영 기준

`tools\install_lockfix_webui_service.ps1`는 다음 기준을 적용한다.

- 관리자 권한이 아니면 설치/재등록 차단
- 서비스 실행 계정을 `LocalSystem`으로 명시
- TCP 8088/8099 방화벽 규칙 등록 시도
- 서비스 시작 후 `http://127.0.0.1:8088/` 응답 확인
- Python 런타임과 WebUI 서비스 실행 파일 존재 여부 확인

## 설치 후 최신 화면 파일 반영

실행 중인 설치 폴더에 최신 화면 파일을 반영하려면 관리자 권한 PowerShell에서 실행한다.

```powershell
cd "<LOCK-FIX 설치 패키지 폴더>"
.\tools\update_installed_webui_assets.ps1
```

이 스크립트는 다음을 수행한다.

- 관리자 권한 확인
- 서비스 설정과 서비스 권한 출력
- 8088/8099 포트 상태 기록
- 서비스 중지
- 최신 WebUI 파일 복사 및 해시 검증
- 서비스 시작
- WebUI cache version 응답 확인

## 현재 PC에서 관찰된 증상 예시

```text
LOCKFIXWebUI 서비스는 Running 상태
SERVICE_START_NAME은 LocalSystem
8088 포트는 PID가 LISTENING
8088에 CLOSE_WAIT 연결이 다수 누적
서비스 제어는 현재 셸 권한으로 거부
```

이 경우 기능 파일 동기화 문제가 아니라, 관리자 권한으로 서비스 재시작이 필요한 상태로 판단한다.

## 개발자 회신 체크리스트

```text
1. LOCK-FIX 서비스명:
2. 서비스 실행 계정:
3. 관리자 권한 Restart-Service 성공 여부:
4. 서비스 제어 거부 시 정확한 오류:
5. 8088 직접 실행 또는 서비스 응답 성공 여부:
6. 8099 포트 사용 여부:
7. WebUI 접속 URL:
8. 방화벽 규칙 등록 여부:
9. 설치 패키지에서 서비스 권한 자동 설정 가능 여부:
10. 향후 설치 시 관리자 권한 체크 로직 반영 여부:
```
