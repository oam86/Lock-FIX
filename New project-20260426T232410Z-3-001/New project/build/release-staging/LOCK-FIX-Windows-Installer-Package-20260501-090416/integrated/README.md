# Integrated OAM Sources

이 디렉터리는 기존 우암전자 개발 소스를 현재 LOCK-FIX PoC와 함께 관리하기 위한 통합 소스 영역입니다.

## 포함 프로젝트

- `oam-hw-solution`: Python Flask 기반 하드웨어 모니터링/로그/라이선스/네트워크 에이전트 서버
- `OamDataCenter`: Java Spring Boot 기반 데이터센터 서버와 React 프론트엔드

## 제외 항목

통합 시 아래 생성물은 제외합니다.

- `.venv`
- `node_modules`
- `target`
- `.idea`
- `__MACOSX`
- `__pycache__`
- 로그 파일

## 다시 가져오기

```powershell
python .\tools\import_oam_sources.py
```

## 현재 LOCK-FIX PoC와 연결 방향

1. `oam-hw-solution`의 실제 CPU/RAM/Disk/Network 수집 API를 현재 `/api/monitoring`에 연결
2. `OamDataCenter`의 라이선스/회원/고객사 관리 API를 현재 로그인/라이선스 화면에 연결
3. 현재 mock UI는 통합 화면 프로토타입으로 유지하고, API만 실제 서비스로 전환
