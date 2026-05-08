# LOCK-FIX Windows Installer

이 폴더는 Advanced Installer 기반 Windows 설치 파일을 만들기 위한 패키징 구성입니다.

## 목표 산출물

```text
dist\installer\LOCK-FIX Setup.msi
```

## 설치 마법사 구성

- 제품명: LOCK-FIX
- 제조사: OAM
- 설치 형식: MSI
- 기본 설치 경로: `Program Files\OAM\LOCK-FIX`
- 시작 메뉴 바로가기: LOCK-FIX
- 바탕화면 바로가기: LOCK-FIX
- 포함 실행 파일:
  - `dist\lockfix-ui.exe`
  - `dist\lockfixctl.exe`
- 포함 리소스:
  - `webui.py`
  - `config`
  - `lockfix`
  - `web`
  - `integrated`
  - README/요구사항 문서

## 설치 화면 흐름

LOCK-FIX 설치 UX는 Visual Studio Installer의 카드형 기능 선택과 Veeam의 설치 전 환경 점검/요약 방식을 기준으로 구성합니다.

1. Welcome: LOCK-FIX 설치 시작
2. System Check: Windows 버전, PowerShell, WinRM, 방화벽, 관리자 권한 점검
3. Install Type: 권장 설치 / 고급 설치 선택
4. Component Selection: Core Service / Web UI / Veeam Connector / Agent / DB 선택
5. Veeam Connection: Veeam Server IP, Port 9419, 인증 방식 입력
6. Security Key: LOCK-FIX License Key 또는 API Key 입력
7. Summary: 설치 경로, 서비스명, 포트, Veeam 서버 정보 최종 확인
8. Install Progress: 설치 진행률 표시
9. Complete: Web UI 접속 주소 표시, 예: `https://localhost:8443`

현재 저장소의 `dist\installer\LOCK-FIX Setup Wizard.exe`는 위 흐름을 먼저 구현한 마법사형 실행 파일입니다. Advanced Installer MSI도 같은 흐름을 기준으로 제작합니다.

세부 MSI Dialog Editor 기준은 아래 문서를 따릅니다.

- `LOCK-FIX_MSI_UX_SPEC.md`
- `LOCK-FIX_MSI_DIALOG_PLAN.md`

## 빌드 방법

1. Advanced Installer를 설치합니다.
2. PowerShell에서 프로젝트 루트로 이동합니다.
3. 아래 명령을 실행합니다.

```powershell
.\packaging\windows\build_advanced_installer.ps1
```

Advanced Installer 22.0 이상에서는 `ADVINST_COM` 환경 변수를 통해 `AdvancedInstaller.com`을 자동으로 찾습니다.

## 참고

현재 저장소에는 Advanced Installer 프로그램 자체가 포함되어 있지 않습니다. 이 스크립트는 설치된 Advanced Installer를 사용해 `.aip` 프로젝트와 `.msi` 산출물을 생성합니다.
