# LOCK-FIX Agent/Service 권한 분리 구조

LOCK-FIX WebUI는 관리자 권한이 필요한 디스크 제어를 직접 실행하지 않는다.

## 실행 책임 분리

- WebUI/Backend
  - 사용자 요청 수신
  - RBAC 권한 확인
  - 부서 검토 및 2인 승인 상태 확인
  - 정책 조건 확인
  - LOCK-FIX Agent/Service 요청 큐에 작업 등록

- LOCK-FIX Agent/Service
  - Windows Service로 실행
  - Disk Offline
  - Drive Letter/access path 제거
  - Volume Dismount
  - Flush 확인
  - I/O quiet 확인
  - Veeam REST API 조회
  - Emergency reconnect
  - 실행 결과와 감사 로그 기록

## 서비스 계정

기본 PoC/설치 기준 서비스 계정은 다음 중 하나를 사용한다.

- LocalSystem
- 전용 `lockfix-svc` 계정

상용 배포에서는 고객사 보안 정책에 따라 `lockfix-svc` 전용 계정으로 전환하고, 필요한 최소 권한만 부여한다.

## 요청 흐름

1. WebUI가 사용자 권한, 승인 상태, 정책 조건을 확인한다.
2. WebUI가 `runtime/agent_service/requests`에 요청 JSON을 생성한다.
3. LOCK-FIX Agent/Service가 요청을 읽는다.
4. Agent/Service가 실제 디스크/Veeam 작업을 수행한다.
5. Agent/Service가 `runtime/agent_service/responses`에 결과 JSON을 기록한다.
6. WebUI는 결과만 읽어서 화면에 표시한다.

## 운영 모드

| 모드 | 목적 | 권한 정책 | 감사 로그 |
| --- | --- | --- | --- |
| `poc` | 기능 검증 | 관리자 권한 실행 또는 LocalSystem 서비스 실행을 허용한다. `dry_run=true`에서는 제한적 inline fallback을 허용한다. | fallback 사용 시 `poc.admin_execution`을 남긴다. |
| `commercial` | 상용 제품 운영 | 실제 Disk Offline, Dismount, Drive Letter 제거, Flush, Veeam API 조회는 LOCK-FIX Agent/Service에서만 수행한다. WebUI는 요청/승인/정책 상태만 전달한다. | 모든 관리자 권한 작업과 실패를 남긴다. |
| `delivery` | 고객사 납품/설치 검증 | 설치 전후 preflight로 권한 부족과 제한 기능을 화면에 표시한다. 고객사 보안 정책 확인이 필요한 항목을 분리한다. | 권한 부족은 감사로그와 관리자 알림에 남긴다. |

기본 운영 모드는 `commercial`이다. 기존 `live`, `production`, `prod` 값도 `commercial`로 해석한다.

## Preflight 진단 항목

Agent/Service preflight는 다음 항목을 점검한다.

- LOCK-FIX Agent/Service 실행 여부
- 서비스 실행 계정
- Local Administrators 또는 LocalSystem 권한 여부
- PowerShell 디스크 명령 실행 가능 여부: `Get-Disk`, `Get-Partition`, `Get-Volume`, `Write-VolumeCache`, `mountvol`
- Veeam REST API 권한과 연결 상태
- UAC, ExecutionPolicy, Firewall, WinRM 상태

## 권한 요구사항 / 제한 기능 / 해결 방법

| 권한 요구사항 | 부족 시 제한 기능 | 해결 방법 |
| --- | --- | --- |
| 서비스 실행 계정이 LocalSystem 또는 권한 부여된 `lockfix-svc` | Disk Offline, Drive Letter 제거, Volume Dismount, Flush 확인 불가 | 서비스 계정을 LocalSystem 또는 전용 계정으로 설정하고 필요한 로컬 관리자/저장소 권한을 부여한다. |
| PowerShell Storage 명령 실행 가능 | `Get-Partition`/`Get-Volume` 기반 볼륨 식별, 온라인/오프라인 검증 실패 | Storage/WMI 서비스, 실행 정책, PowerShell 모듈 권한을 점검한다. |
| Veeam REST API 계정 권한 | Backup Copy 세션, Repository, Restore Point 조회 실패 | Veeam API 계정 권한과 9419 접근, 설치 IP 기준 설정값을 확인한다. |
| Firewall/WinRM 정책 충족 | 원격 상태 확인 또는 관리 자동화 제한 | 고객사 방화벽/WinRM 정책 예외를 사전 승인하고 설치 문서에 반영한다. |
| 승인 워크플로우 완료 | DISK_ONLINE, EMERGENCY_UNLOCK, POLICY_CHANGE 등 critical operation 차단 | 부서 검토 완료 후 서로 다른 관리자 2인이 승인한다. 요청자는 본인 요청을 승인할 수 없다. |

## 운영 원칙

- 상용/납품 모드에서 WebUI는 디스크 작업을 직접 실행하지 않는다.
- POC 모드에서만 제한적 inline fallback을 허용한다.
- Agent/Service가 응답하지 않으면 WebUI는 작업을 실패 처리하고 제한 기능을 표시한다.
- critical operation 실행 근거는 감사 로그에 남긴다.
