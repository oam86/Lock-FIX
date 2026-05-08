# LOCK-FIX 업데이트 내역

작성일: 2026-04-29

## 작업 기준

- 원격 저장소: `https://github.com/oam86/Lock-FIX.git`
- 로컬 저장소: `C:\Users\Administrator\Documents\GitHub\Lock-FIX`
- 실제 소스 폴더: `New project-20260426T232410Z-3-001\New project`

## 최근 작업 정리

### 1. LOCK-FIX PoC 핵심 제어 흐름

- 백업 완료 이후 디스크 분리 절차를 상태 머신으로 정리했습니다.
- 처리 흐름은 `BACKUP_COMPLETED -> FLUSHING -> IO_CHECKING -> UNMOUNTING -> POWERING_OFF -> ISOLATED` 구조입니다.
- 재연결 흐름은 `RECONNECT_REQUESTED -> POWERING_ON -> WAITING_DISK -> VERIFYING_UID -> MOUNTED_READONLY -> VERIFYING_HASH -> ONLINE_VERIFIED_RW` 구조입니다.
- UID 또는 Hash 검증 실패 시 `QUARANTINE` 상태로 전환되도록 구성했습니다.

### 2. CLI 콘솔

- `lockfixctl.py` 진입점을 구성했습니다.
- 지원 명령:
  - `status`: 슬롯 상태 조회
  - `isolate`: 백업 디스크 분리 흐름 실행
  - `reconnect`: 디스크 재연결 및 검증 흐름 실행
  - `uid`: 슬롯 기준 UID 계산
- Windows 실행 파일 `dist\lockfixctl.exe` 산출물을 포함했습니다.

### 3. 안전한 Mock 실행 환경

- 기본 설정 파일 `config\lockfix.example.json`은 `dry_run: true`로 구성했습니다.
- 전원 제어는 기본적으로 mock 타입을 사용합니다.
- 실제 장비 제어 전까지는 명령이 직접 실행되지 않도록 PoC 검증 중심으로 설정했습니다.

### 4. 웹 UI

- `webui.py` 기반 로컬 웹 UI를 구성했습니다.
- 기본 접속 주소는 `http://127.0.0.1:8088`입니다.
- 주요 화면:
  - Monitoring
  - Dashboard
  - Detect
  - Notification
  - Logs
  - Contact Service
  - License
  - Network Status
  - Report
  - Source / Integrated View
  - Settings
- Windows 실행 파일 `dist\lockfix-ui.exe`로 웹 UI를 바로 실행할 수 있게 구성했습니다.

### 5. 보고서 기능

- CPU, Memory, Disk, Network 사용률 기반 점검 리포트를 구성했습니다.
- 고객/점검 정보, 서버 기본 정보, 자원 사용 상세, 점검 체크리스트, 엔지니어 의견, 서명 영역을 포함했습니다.
- 다운로드 형식:
  - Word: `/api/report.docx`
  - CSV: `/api/report.csv`
  - Excel: `/api/report.xlsx`

### 6. 통합 PoC 화면

- 우암전자 DataCenter와 Hardware Web Solution을 한 화면에서 요약하는 통합 PoC 정보를 추가했습니다.
- 서버 자원, 하드웨어 관제, 로그, 라이선스, 네트워크 연결 상태를 Mock 데이터 기반으로 표시합니다.

### 7. 설치 및 배포 산출물

- Windows 산출물:
  - `dist\lockfixctl.exe`
  - `dist\lockfix-ui.exe`
- Linux 산출물:
  - `dist\lockfix-poc-linux.tar.gz`
  - `packaging\linux\install.sh`
  - `packaging\linux\uninstall.sh`
- Linux 패키지 생성 도구:
  - `tools\build_linux_installer.py`

### 8. 테스트

- 핵심 로직 테스트를 `tests\test_lockfix.py`에 구성했습니다.
- 검증 항목:
  - UID 계산 안정성
  - isolate 실행 후 `ISOLATED` 상태 도달
  - UID 불일치 시 `QUARANTINE` 전환

## 다음 업데이트 후보

- 실제 Relay/MOSFET 장비 연결 설정 분리
- 현장 디스크 UID 등록/관리 화면 추가
- 운영 로그 검색 및 기간 필터 강화
- 보고서 양식 현장 제출본 기준으로 추가 정리
- Git 저장소 루트의 압축 파일 정리 및 소스 폴더 구조 단순화
