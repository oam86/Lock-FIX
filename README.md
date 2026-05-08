# LOCK-FIX

LOCK-FIX는 백업 디스크를 논리적으로 분리하고 재연결 시 UID/Hash 검증을 수행하는 1차 PoC 프로젝트입니다.

현재 저장소 기준 작업 위치:

```text
C:\Users\Administrator\Documents\GitHub\Lock-FIX
```

실제 PoC 소스 위치:

```text
New project-20260426T232410Z-3-001\New project
```

## 최근 업데이트 요약

- LOCK-FIX CLI 제어 흐름 정리: `status`, `isolate`, `reconnect`, `uid`
- Mock 기반 안전 실행 설정 추가: 기본 `dry_run: true`
- 백업 완료 후 Flush, I/O 확인, Unmount, 전원 차단 상태 흐름 구현
- 재연결 후 UID 검증, Read-Only Mount, Hash 검증, 정상 시 Online 전환 흐름 구현
- 로컬 웹 UI 추가: Monitoring, Dashboard, Report, Logs, License, Network Status, Settings
- 보고서 기능 추가: Word, CSV, Excel 다운로드
- 우암전자 DataCenter + Hardware Web Solution 통합 PoC 화면 구성
- Windows 실행 파일 산출물 추가: `lockfixctl.exe`, `lockfix-ui.exe`
- Linux 설치 패키지 생성 스크립트 및 설치 파일 구성
- 핵심 상태 전환/UID 검증 테스트 추가

상세 정리는 [UPDATE_NOTES.md](UPDATE_NOTES.md)를 참고하세요.

## 빠른 실행

아래 명령은 실제 장비를 건드리지 않는 Mock 설정 기준입니다.

```powershell
cd "C:\Users\Administrator\Documents\GitHub\Lock-FIX\New project-20260426T232410Z-3-001\New project"
python .\lockfixctl.py status --config .\config\lockfix.example.json
python .\lockfixctl.py isolate --slot BAY-01 --config .\config\lockfix.example.json
python .\lockfixctl.py reconnect --slot BAY-01 --config .\config\lockfix.example.json
```

웹 UI 실행:

```powershell
python .\webui.py --host 127.0.0.1 --port 8088 --config .\config\lockfix.example.json
```

Windows 실행 파일:

```powershell
.\dist\lockfixctl.exe status --config .\config\lockfix.example.json
.\dist\lockfix-ui.exe
```

## 주요 폴더

```text
config/       PoC 설정 예시
dist/         Windows 실행 파일 산출물
lockfix/      상태 머신, 디스크, 전원, UID/Hash 검증 로직
packaging/    Linux 설치 스크립트
src/          Windows 실행 파일 런처 소스
tests/        핵심 로직 테스트
tools/        설치 파일 생성 및 자료 추출 도구
web/static/   웹 UI 정적 파일
```

## 주의 사항

기본 설정은 안전한 Mock 모드입니다. 실제 장비와 연결하려면 `config/lockfix.example.json`을 복사한 뒤 현장 환경에 맞게 `dry_run`, 디스크 경로, 마운트 경로, 전원 제어 명령, 등록 UID를 수정해야 합니다.
