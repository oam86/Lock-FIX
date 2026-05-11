# PPT Requirements Extract

- Source: `C:\Users\우암전자\Downloads\LOCK-FIX_솔레노이드_제외_1차_PoC_개발정리.pptx`
- Slides: 9
- Media files: 0

## Slide 1
- LOCK-FIX
- 솔레노이드 제외1차 PoC 개발 요구사항
- 백업 완료 → Flush/I/O 확인 → Unmount → 실제 디스크 전원 차단 → UID/Hash 검증 → 정상 시 Online
- 개발 범위: 물리 서버 기반 디스크 전원 차단 · 소프트웨어 제어 · 검증 로직 · 감사 로그
- 제외 범위: 솔레노이드 락 · 물리 탈거 방지 · Limit Switch · 트레이 잠금

## Slide 2
- LOCK-FIX 1차 PoC
- 이번 1차 PoC의 개발 범위
- 우암전자 LOCK-FIX 개발 정리 | 2
- 포함 기능
- 백업 완료 신호 수신Flush / I/O 종료 확인Unmount / OfflineRelay 또는 MOSFET 전원 차단UID 검증 · Hash 검증실패 시 전원 OFF 유지 및 관리자 경보
- 제외 기능
- 솔레노이드 락물리 탈거 방지Limit Switch트레이 잠금 제어비상 물리 해제 키
- 핵심 목표
- 백업 종료 후 디스크를 안전하게 분리하고, 실제 SATA 전원 12V/5V를 차단한다.

## Slide 3
- LOCK-FIX 1차 PoC
- 전체 구성: 물리 서버 + 전원 제어 보드 + 테스트 디스크
- 우암전자 LOCK-FIX 개발 정리 | 3
- 백업 소프트웨어Post-Job Script / API
- LOCK-FIX제어 프로그램
- USB Relay 또는MOSFET 제어보드
- 테스트 HDD/SSDSATA 전원 차단 대상
- 상태 저장 / 로그UID · Hash · ISOLATED 상태 기록
- 구현 포인트: Proxmox/VM 방식은 보조 개발용입니다.
- 실제 전원 차단 PoC는 물리 서버와 전원 제어 보드가 필요합니다.

## Slide 4
- LOCK-FIX 1차 PoC
- 백업 완료 후 격리 절차
- 우암전자 LOCK-FIX 개발 정리 | 4
- 1
- 백업 완료
- 백업 SW가 Post-Job Script 또는 API로 lockfixctl isolate 호출
- 2
- Flush 실행
- OS 쓰기 캐시를 디스크에 모두 기록
- 3
- I/O 종료 확인
- 30~60초 동안 쓰기 I/O 없음 확인
- 4
- Unmount
- 파일시스템·ZFS·LVM을 안전 분리
- 5
- 전원 OFF
- Relay/MOSFET OFF로 SATA 12V/5V 차단
- 격리 상태 정의
- Unmount 완료 + 전원 OFF + OS 접근 불가 + 상태 로그 기록 = ISOLATED
- 주의: 백업 완료 신호만 믿고 바로 전원 차단 금지. 반드시 Flush와 I/O 종료 확인 후 차단합니다.

## Slide 5
- LOCK-FIX 1차 PoC
- 재연결 절차: 검증 전에는 쓰기 금지
- 우암전자 LOCK-FIX 개발 정리 | 5
- 1
- 관리자 요청
- lockfixctl reconnect --slot BAY-01
- 2
- 전원 ON
- Relay/MOSFET ON 후 디스크 인식 대기
- 3
- UID 검증
- 기존 등록 디스크인지 확인
- 4
- Read-Only Mount
- Hash 검증 전 데이터 수정 방지
- 5
- Hash 검증
- 백업 메타데이터·파일 목록 검증
- 모두 정상
- Read-Write Mount 허용백업 저장소 ONLINE 전환
- 실패 시 처리
- UID 불일치 또는 Hash 불일치 → 즉시 Unmount → Relay OFF → QUARANTINE → 관리자 경보

## Slide 6
- LOCK-FIX 1차 PoC
- UID / Hash 검증 설계
- 우암전자 LOCK-FIX 개발 정리 | 6
- UID 검증
- 목적: 같은 디스크인지 확인입력값: Disk Serial, Model, WWN, Partition UUID, Slot ID예: UID = SHA-256(Serial + Model + WWN + Slot ID)실패 시: 다른 디스크 가능성 → Relay OFF
- Hash 검증
- 목적: 백업 데이터 변조 여부 확인PoC 대상: 백업 파일 목록, 파일 크기, 수정 시간, 메타데이터권장: 먼저 Read-Only Mount 후 검증실패 시: 데이터 변조 의심 → Quarantine
- 검증 순서 원칙
- 전원 ON → 디스크 인식 → UID 확인 → Read-Only Mount → Hash 확인 → 정상 시 Read-Write 전환

## Slide 7
- LOCK-FIX 1차 PoC
- 상태값 기준으로 개발하기
- 우암전자 LOCK-FIX 개발 정리 | 7
- BACKUP_RUNNING
- BACKUP_COMPLETED
- FLUSHING
- RECONNECT_REQUESTED
- POWERING_ON
- WAITING_DISK
- VERIFYING_UID
- MOUNTED_READONLY
- VERIFYING_HASH
- ONLINE_VERIFIED_RW
- 예외 상태
- QUARANTINE: UID/Hash 실패로 전원 OFF 유지ERROR: Relay·Unmount·Mount 실패 등 수동 점검 필요
- 개발 원칙
- 순차 스크립트보다 상태 머신 구조가 안전합니다. 각 상태 전환마다 로그와 실패 처리 조건을 남깁니다.
- ISOLATED
- POWERING_OFF
- UNMOUNTING
- IO_CHECKING

## Slide 8
- LOCK-FIX 1차 PoC
- 실패 시 처리 기준
- 우암전자 LOCK-FIX 개발 정리 | 8
- 실패 상황
- 처리 기준
- Flush 실패
- 전원 차이 구성안대로 PPT단 금지 · 관리자 알림
- I/O 사용 중
- 전원 차단 보류 · 재확인
- Unmount 실패
- 전원 차단 금지 또는 관리자 승인 필요
- Relay OFF 실패
- Critical Alert · 수동 점검
- 디스크 인식 실패
- Relay OFF 후 오류 처리
- UID 불일치
- Relay OFF · QUARANTINE · 관리자 경보
- Hash 불일치
- Unmount · Relay OFF · QUARANTINE
- 관리자 승인 실패
- Reconnect 금지
- 상세 내용
- 처리 기준

## Slide 9
- LOCK-FIX 1차 PoC
- 개발자에게 전달할 최종 구현 문장
- 우암전자 LOCK-FIX 개발 정리 | 9
- 1차 PoC에서는 솔레노이드 락을 제외합니다.
- 목표는 물리 서버에서 백업 완료 후 테스트 디스크를 안전하게 Flush/Unmount한 뒤, Relay 또는 MOSFET으로 SATA 전원 12V/5V를 실제 차단하는 것입니다.
- 재연결 시에는 관리자 승인 후 전원을 다시 공급하고, 디스크 UID를 확인하여 기존 디스크가 맞는지 검증합니다. UID가 정상일 경우 먼저 Read-Only로 Mount한 뒤 백업 메타데이터와 파일 목록 기반 Hash를 검증합니다.
- UID 또는 Hash가 불일치하면 즉시 Unmount하고 Relay OFF를 수행하여 다시 전원 차단 상태로 돌립니다. 검증이 모두 성공한 경우에만 Read-Write Mount를 허용하고 백업 저장소를 Online 상태로 전환합니다.
- 한 줄 결론
- 백업 완료 → Flush/I/O 확인 → Unmount → 실제 전원 차단 → 재연결 시 UID/Hash 검증 → 정상일 때만 Online
