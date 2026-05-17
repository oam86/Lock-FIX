# rg(ripgrep) 실행 권한 차단 시 처리 방법

LOCK-FIX 개발 환경에서 `rg` 명령어 실행이 막혀 있을 경우, 대부분 다음 원인 중 하나입니다.

- ripgrep 실행 파일 권한 문제
- 보안 정책 차단
- PATH 미등록
- Windows Defender 또는 백신 차단
- AppLocker, EDR, SmartScreen 정책 차단
- PowerShell 실행 정책 문제

`rg`는 소스코드 전체에서 문자열을 빠르게 검색하는 개발 편의 도구입니다. LOCK-FIX 제품 실행 필수 런타임 구성요소는 아니므로, 고객사 운영 서버에는 기본 요구사항으로 포함하지 않습니다.

## 1. 설치 및 경로 확인

PowerShell 또는 CMD에서 먼저 설치 여부를 확인합니다.

```powershell
where rg
rg --version
```

정상이라면 `rg.exe` 경로와 ripgrep 버전이 표시됩니다.

```text
C:\Users\...\AppData\Local\Microsoft\WinGet\Packages\...\rg.exe
ripgrep 14.x.x
```

아무 결과가 없으면 `rg`가 설치되지 않았거나 PATH에 등록되지 않은 상태입니다.

## 2. 설치 방법

Windows 개발 환경에서는 다음 중 하나로 설치할 수 있습니다.

```powershell
winget install BurntSushi.ripgrep.MSVC
```

```powershell
choco install ripgrep
```

```powershell
scoop install ripgrep
```

설치 후 새 PowerShell 창을 열고 다시 확인합니다.

```powershell
rg --version
```

## 3. PATH 문제 확인

`rg.exe` 파일은 있지만 명령어가 인식되지 않으면 PATH 등록 문제입니다.

```powershell
$env:Path -split ";"
```

`rg.exe`가 있는 폴더가 PATH에 없다면 사용자 또는 시스템 환경 변수에 해당 경로를 추가합니다.

예시:

```text
C:\Program Files\ripgrep
C:\Users\<사용자>\scoop\shims
C:\ProgramData\chocolatey\bin
```

## 4. 실행 권한 차단 확인

다음 메시지가 나오면 Windows 보안 정책 또는 파일 차단 문제일 수 있습니다.

```text
Access is denied
This app has been blocked
Operation did not complete successfully because the file contains a virus or potentially unwanted software
```

파일 차단 해제:

```powershell
Unblock-File "C:\Program Files\ripgrep\rg.exe"
```

관리자 PowerShell에서 실행 확인:

```powershell
Start-Process powershell -Verb runAs
rg --version
```

## 5. PowerShell 실행 정책 확인

PowerShell 실행 정책 때문에 관련 명령이 막히는 경우도 있습니다.

```powershell
Get-ExecutionPolicy -List
```

개발 PC에서만 임시 완화가 필요할 경우:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

고객사 운영 환경에서는 보안 정책을 임의로 변경하지 말고 보안 담당자 승인 후 적용해야 합니다.

## 6. Windows Defender 또는 백신 차단 확인

다음 항목을 확인합니다.

- Windows Defender 보호 기록
- 백신 격리 목록
- EDR 차단 이벤트
- AppLocker 정책
- Windows SmartScreen 차단 여부

정상 개발 도구로 확인되면 최소 범위로 예외 등록을 요청합니다.

예외 등록 대상 예시:

- `rg.exe`
- ripgrep 설치 폴더
- LOCK-FIX 개발 소스 폴더
- `node_modules` 또는 build cache 폴더

전체 드라이브 예외 처리는 금지합니다.

## 7. 기업 보안 정책 차단 시 승인 요청 문구

고객사 또는 회사 내부 정책상 승인되지 않은 `.exe` 실행이 막힐 수 있습니다. 이 경우 임의 우회하지 말고 아래 내용으로 승인 요청합니다.

| 항목 | 내용 |
| --- | --- |
| 요청 도구명 | ripgrep / `rg.exe` |
| 용도 | LOCK-FIX 소스코드 검색 및 개발 디버깅 |
| 실행 위치 | 개발자 PC 또는 개발 서버 |
| 네트워크 통신 여부 | 없음 |
| 관리자 권한 필요 여부 | 일반적으로 불필요 |
| 배포 제품 포함 여부 | 불포함 |
| 보안 요청사항 | 개발 도구 실행 허용 또는 승인된 경로 내 실행 허용 |

## 8. rg 사용 불가 시 대체 명령

`rg`가 막혀도 개발이 중단되면 안 됩니다. 아래 대체 명령을 사용합니다.

PowerShell:

```powershell
Get-ChildItem -Recurse -File | Select-String "검색어"
```

특정 확장자만 검색:

```powershell
Get-ChildItem -Recurse -Include *.ts,*.tsx,*.js,*.json -File | Select-String "검색어"
```

CMD:

```cmd
findstr /S /I /N "검색어" *.*
```

Git Bash:

```bash
grep -Rni "검색어" .
```

## 9. LOCK-FIX 개발 기준

LOCK-FIX 개발 환경에서는 다음 기준을 적용합니다.

1. `rg`는 개발 편의 도구로 분류한다.
2. 제품 실행 필수 구성요소에는 포함하지 않는다.
3. 개발 PC에서는 보안 승인 후 사용한다.
4. 고객사 운영 서버에는 `rg` 설치를 기본 요구사항으로 두지 않는다.
5. `rg` 차단 시 PowerShell `Select-String`, `findstr`, `grep`으로 대체한다.
6. 보안 정책 우회를 위한 파일명 변경, 임의 경로 실행, 우회 실행은 금지한다.

## 개발자 전달 최종 문구

LOCK-FIX 개발 중 `rg` 실행 권한이 막혀 있을 경우, 먼저 설치 여부, PATH 등록 여부, 파일 차단 여부, Windows Defender/백신 차단 여부를 확인해 주세요.

`rg`는 개발 편의용 소스 검색 도구이며 LOCK-FIX 제품 실행 필수 구성요소가 아닙니다. 개발 PC에서는 보안 승인 후 사용하고, 고객사 운영 서버에는 기본 요구사항으로 포함하지 않는 방향이 맞습니다.

조치 순서는 다음과 같습니다.

1. `where rg` / `rg --version`으로 설치 여부 확인
2. PATH 미등록 시 환경 변수 등록
3. `Unblock-File`로 파일 차단 해제
4. Windows Defender, 백신, AppLocker, EDR 차단 여부 확인
5. 보안 정책상 차단이면 `rg.exe` 사용 승인 요청
6. 승인 불가 시 PowerShell `Select-String` 또는 `findstr`로 대체

중요: 보안 정책을 우회하기 위해 파일명을 변경하거나 임의 경로에서 실행하지 마세요. 고객사 환경에서는 반드시 승인된 개발 도구 또는 기본 Windows 명령으로 대체해야 합니다.

요약하면, `rg`가 막히면 개발 편의성은 떨어지지만 LOCK-FIX 개발 자체가 불가능한 것은 아닙니다. 보안 승인을 받아 사용하는 것이 1순위이고, 승인 불가 시에는 `Select-String`, `findstr`, `grep`으로 대체하는 방식이 가장 안전합니다.
