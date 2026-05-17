# LOCK-FIX Air-Gap Permission Test Summary

작성일: 2026-05-16

## 목적

Veeam 백업 완료 후 LOCK-FIX Air-Gap 자동 격리가 정상 동작하는지, 그리고 반복 실행/권한 문제를 재발 없이 확인하기 위한 테스트 기준을 정리합니다.

## 현재 확인된 결론

- Veeam 백업 완료 감지는 정상입니다.
- DISK_OFFLINE 자동 승인/강제 승인 절차는 생성됩니다.
- Air-Gap 격리 결과는 `BAY-01 = ISOLATED`로 확인되었습니다.
- Windows 디스크 오프라인 증거도 `disk.offline.proof`로 기록되었습니다.
- 설치된 WebUI 서비스에는 최신 중복 실행 방지 패치 적용이 필요합니다.
- 디스크 제어 명령은 반드시 관리자 권한 또는 LocalSystem 서비스 권한에서 실행되어야 합니다.

## 주요 런타임 확인 파일

- 설치 상태 파일:
  `C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX\runtime\state.json`

- Veeam 자동 격리 마커:
  `C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX\runtime\veeam_auto_isolate.json`

- 승인 기록:
  `C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX\runtime\approvals.json`

- 감사 로그:
  `C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX\runtime\audit.jsonl`

- WebUI 서비스 로그:
  `C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX\runtime\webui-service.log`

## 필수 확인 항목

### 1. WebUI 서비스 권한

확인 기준:

- `LOCKFIXWebUI` 서비스가 존재해야 합니다.
- 서비스 시작 유형은 `Automatic`이어야 합니다.
- 서비스 실행 계정은 `LocalSystem`이어야 합니다.
- 일반 사용자 권한으로 실행된 WebUI는 디스크 제어에 실패할 수 있습니다.

권한 문제 대표 증상:

- `Get-Partition` 접근 거부
- `0x80041003`
- `액세스가 거부되었습니다`
- Air-Gap 단계가 `IO_CHECKING`, `UNMOUNTING`, `ERROR` 근처에서 멈춤

### 2. Veeam 완료 감지

확인 기준:

- Veeam Backup Copy Job 완료 상태가 WebUI에 반영되어야 합니다.
- 최신 세션 식별값이 `veeam_auto_isolate.json`에 기록되어야 합니다.
- 이전 세션과 다른 새 세션일 때만 Air-Gap이 새로 실행되어야 합니다.

### 3. 자동 승인/강제 승인

확인 기준:

- `approvals.json`에 `DISK_OFFLINE` 요청이 생성되어야 합니다.
- 요청자는 `LOCKFIX_AUTO_POLICY`로 기록되어야 합니다.
- 승인자는 `LOCKFIX_FORCE_APPROVER`로 기록되어야 합니다.
- 부서 검토는 `REVIEWED`로 기록되어야 합니다.
- 감사 로그에 `approval.force_approved`가 있어야 합니다.

### 4. Air-Gap 단계 진행

정상 흐름:

1. `BACKUP_COMPLETED`
2. `FLUSHING`
3. `IO_CHECKING`
4. `UNMOUNTING`
5. `DISK_OFFLINING`
6. `ISOLATED`

정상 완료 기준:

- `state.json`에 `"BAY-01": "ISOLATED"`
- `audit.jsonl`에 `disk.offline.proof`
- `proved: true`
- `is_offline: true`
- `path_reachable: false`

### 5. 중복 실행 방지

확인 기준:

- 같은 Veeam 완료 세션은 Air-Gap 격리가 1회만 실행되어야 합니다.
- 실행 중에는 `IN_PROGRESS`로 마커가 남아야 합니다.
- 완료 후에는 `ISOLATED`로 마커가 갱신되어야 합니다.
- 같은 세션 재조회 시 새 격리 작업을 다시 만들면 안 됩니다.

최신 패치 필수 토큰:

- `AIRGAP_AUTO_ISOLATE_LOCK`
- `IN_PROGRESS`
- `veeam.auto_isolate.scheduled`

설치된 WebUI 파일에 위 토큰이 없으면 최신 중복 실행 방지 패치가 아직 적용되지 않은 상태입니다.

## 관리자 적용 스크립트

설치된 WebUI 서비스에 최신 중복 실행 방지 패치를 적용하려면 관리자 권한으로 실행합니다.

실행 파일:

`New project\tools\apply_airgap_background_fix_admin.cmd`

수행 내용:

- `LOCKFIXWebUI` 서비스 중지
- 기존 설치 `webui.py` 백업
- 최신 `webui.py` 설치 폴더에 복사
- 적용 스크립트도 설치 폴더에 복사
- 해시 검증
- 서비스 재시작
- 8088 리스너 확인
- 필수 패치 토큰 확인

## 테스트 절차

### 테스트 1. 설치 서비스 상태 확인

예상 결과:

- 서비스 상태: `Running`
- 시작 유형: `Automatic`
- 실행 계정: `LocalSystem`

### 테스트 2. Air-Gap 최종 상태 확인

확인 파일:

`runtime\state.json`

예상 결과:

```json
{
  "BAY-01": "ISOLATED"
}
```

### 테스트 3. 디스크 오프라인 증거 확인

확인 파일:

`runtime\audit.jsonl`

필수 이벤트:

- `disk.offline.proof`
- `proved: true`
- `is_offline: true`
- `path_reachable: false`

### 테스트 4. 자동 승인 확인

확인 파일:

`runtime\approvals.json`

필수 값:

- `requestType: DISK_OFFLINE`
- `requesterUserId: LOCKFIX_AUTO_POLICY`
- `status: APPROVED`
- `forceApprovedBy: LOCKFIX_FORCE_APPROVER`
- `departmentReviewStatus: REVIEWED`

### 테스트 5. 중복 실행 방지 확인

확인 파일:

`runtime\veeam_auto_isolate.json`

예상 결과:

- 같은 `session_key`는 `processed_session_keys`에 1회만 기록됩니다.
- 같은 세션을 다시 조회해도 Air-Gap 격리가 새로 시작되지 않습니다.
- 실행 중에는 `state: IN_PROGRESS`, 완료 후에는 `state: ISOLATED`로 표시됩니다.

### 테스트 6. 권한 오류 확인

권한 오류가 있으면 다음 메시지가 나타날 수 있습니다.

- `Get-Partition access denied`
- `0x80041003`
- `액세스가 거부되었습니다`

조치:

- WebUI를 일반 사용자 콘솔로 실행하지 않습니다.
- `LOCKFIXWebUI` 서비스를 `LocalSystem`으로 실행합니다.
- 관리자 권한으로 `apply_airgap_background_fix_admin.cmd`를 실행합니다.

## 최종 판정 기준

PASS:

- Veeam 완료 세션이 감지됩니다.
- DISK_OFFLINE 자동 승인 기록이 생성됩니다.
- Air-Gap 상태가 `ISOLATED`가 됩니다.
- `disk.offline.proof`가 기록됩니다.
- 같은 세션 재조회 시 중복 격리가 실행되지 않습니다.
- WebUI 서비스가 관리자/LocalSystem 권한으로 디스크 제어를 수행합니다.

FAIL:

- `approval required: DISK_OFFLINE`로 멈춥니다.
- `Get-Partition` 권한 거부가 발생합니다.
- 같은 Veeam 세션으로 Air-Gap 작업이 반복 시작됩니다.
- `state.json`이 `IO_CHECKING`, `UNMOUNTING`, `ERROR`에 머뭅니다.
- 설치된 `webui.py`에 중복 실행 방지 토큰이 없습니다.
