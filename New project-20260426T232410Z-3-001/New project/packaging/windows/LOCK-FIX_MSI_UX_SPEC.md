# LOCK-FIX Advanced Installer MSI UX Spec

LOCK-FIX MSI는 Visual Studio Installer의 카드형 기능 선택 화면과 Veeam의 설치 전 환경 점검/요약 화면을 기준으로 제작합니다.

## Installer Flow

1. Welcome
   - LOCK-FIX 설치 시작
   - 제품명, 제조사, 설치 목적 표시

2. System Check
   - Windows 버전
   - PowerShell 사용 가능 여부
   - WinRM 상태
   - 방화벽 규칙 준비 상태
   - 관리자 권한 또는 사용자 설치 모드 확인

3. Install Type
   - 권장 설치
   - 고급 설치

4. Component Selection
   - Core Service
   - Web UI
   - Veeam Connector
   - Agent
   - DB

5. Veeam Connection
   - Veeam Server IP
   - Port: `9419`
   - Authentication: Windows Authentication / API Token / Basic Account
   - User
   - Password or Token

6. Security Key
   - LOCK-FIX License Key
   - LOCK-FIX API Key

7. Summary
   - 설치 경로
   - 서비스명: `LOCK-FIX Core Service`
   - Web UI 포트: `8443`
   - Web UI 주소: `https://localhost:8443`
   - Veeam 서버 정보
   - 선택 구성 요소

8. Install Progress
   - 설치 진행률
   - 파일 복사
   - 설정 저장
   - 바로가기 생성
   - 서비스/방화벽 준비

9. Complete
   - Web UI 접속 주소 표시
   - `https://localhost:8443`

## MSI Public Properties

Advanced Installer Dialog Editor에서 아래 Public Property를 사용합니다.

```text
LOCKFIX_INSTALL_TYPE
LOCKFIX_INSTALL_PATH
LOCKFIX_WEB_PORT
LOCKFIX_WEB_URL
LOCKFIX_SERVICE_NAME
LOCKFIX_VEEAM_HOST
LOCKFIX_VEEAM_PORT
LOCKFIX_VEEAM_AUTH_TYPE
LOCKFIX_VEEAM_USER
LOCKFIX_VEEAM_SECRET
LOCKFIX_SECURITY_KEY_TYPE
LOCKFIX_SECURITY_KEY
LOCKFIX_ENABLE_CORE
LOCKFIX_ENABLE_WEBUI
LOCKFIX_ENABLE_VEEAM
LOCKFIX_ENABLE_AGENT
LOCKFIX_ENABLE_DB
```

## Default Values

```text
LOCKFIX_INSTALL_TYPE=recommended
LOCKFIX_WEB_PORT=8443
LOCKFIX_WEB_URL=https://localhost:8443
LOCKFIX_SERVICE_NAME=LOCK-FIX Core Service
LOCKFIX_VEEAM_PORT=9419
LOCKFIX_VEEAM_AUTH_TYPE=Windows Authentication
LOCKFIX_ENABLE_CORE=1
LOCKFIX_ENABLE_WEBUI=1
LOCKFIX_ENABLE_VEEAM=1
LOCKFIX_ENABLE_AGENT=1
LOCKFIX_ENABLE_DB=1
```

## Feature Mapping

```text
Core Service      -> lockfix/, lockfixctl.py, dist/lockfixctl.exe
Web UI            -> web/, webui.py, dist/lockfix-ui.exe
Veeam Connector   -> Veeam connection configuration and future connector service
Agent             -> runtime agent configuration and future endpoint agent
DB                -> runtime state, audit, report, and install configuration
```

## Advanced Installer Notes

- Custom dialog creation requires Advanced Installer Dialog Editor.
- Advanced Installer documentation states custom dialogs are created from the Dialog Editor page, and the custom dialog tutorial notes these options require Enterprise edition/project type.
- The current repository includes a C# setup wizard implementing the same flow first, so the UX can be validated before the MSI Dialog Editor layout is finalized.
