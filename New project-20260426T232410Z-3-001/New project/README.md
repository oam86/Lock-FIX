# LOCK-FIX 1차 PoC 개발 소스

PPT 요구사항을 기준으로 만든 LOCK-FIX 1차 PoC CLI입니다.

목표 흐름:

```text
백업 완료 -> Flush/I/O 확인 -> Unmount -> 실제 전원 차단
재연결 -> UID 검증 -> Read-Only Mount -> Hash 검증 -> 정상 시 Online
```

1차 PoC 제외 범위:

- 솔레노이드 락
- 물리 탈거 방지
- Limit Switch
- 트레이 잠금 제어

## 구성

- `lockfixctl.py`: CLI 진입점
- `lockfix/`: 상태 머신, 디스크 작업, 전원 제어, UID/Hash 검증
- `config/lockfix.example.json`: PoC 설정 예시
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

Linux 설치 파일 생성:

```powershell
python .\tools\build_linux_installer.py
```

생성 파일:

```text
dist/lockfix-poc-linux.tar.gz
```

Linux 서버 설치:

```bash
tar -xzf lockfix-poc-linux.tar.gz
cd lockfix-poc-linux
sudo ./install.sh
sudo systemctl start lockfix-poc
```

## 실제 장비 연결 전 확인

실제 Relay/MOSFET 제어 명령을 연결하려면 `config/lockfix.example.json`을 복사한 뒤 다음 값을 현장 환경에 맞게 바꿉니다.

- `dry_run`: 실제 명령 실행 시 `false`
- `slots[].device`: `/dev/disk/by-id/...` 같은 안정적인 디스크 경로
- `slots[].mount_point`: 백업 저장소 마운트 경로
- `slots[].power.off_command`, `on_command`: Relay/MOSFET 제어 명령
- `slots[].expected_uid`: 등록 디스크 UID

주의: `dry_run: false`에서는 `umount`, `mount`, 전원 제어 명령이 실제 실행됩니다.
