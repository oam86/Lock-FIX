$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ReleaseRoot = Join-Path $Root "dist\release"
$StagingRoot = Join-Path $Root "build\release-staging"
$PackageName = "LOCK-FIX-Windows-Installer-Package-$Stamp"
$PackageRoot = Join-Path $StagingRoot $PackageName
$ZipPath = Join-Path $ReleaseRoot "$PackageName.zip"

function Copy-ItemClean {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Package source not found: $Source"
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    & robocopy $Source $Destination /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Folder copy failed: $Source -> $Destination (robocopy exit code $LASTEXITCODE)"
    }
    $global:LASTEXITCODE = 0
}

New-Item -ItemType Directory -Force -Path $ReleaseRoot, $StagingRoot, $PackageRoot | Out-Null

& (Join-Path $Root "build_windows.ps1")

Copy-Item -LiteralPath (Join-Path $Root "dist\installer\LOCK-FIX Setup Wizard.exe") -Destination (Join-Path $PackageRoot "LOCK-FIX Setup Wizard.exe") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $PackageRoot "dist"), (Join-Path $PackageRoot "dist\installer") | Out-Null
Copy-Item -LiteralPath (Join-Path $Root "dist\lockfix-ui.exe") -Destination (Join-Path $PackageRoot "dist\lockfix-ui.exe") -Force
Copy-Item -LiteralPath (Join-Path $Root "dist\LOCK-FIX Console.exe") -Destination (Join-Path $PackageRoot "LOCK-FIX Console.exe") -Force
Copy-Item -LiteralPath (Join-Path $Root "dist\LOCK-FIX Console.exe") -Destination (Join-Path $PackageRoot "dist\LOCK-FIX Console.exe") -Force
Copy-Item -LiteralPath (Join-Path $Root "dist\lockfixctl.exe") -Destination (Join-Path $PackageRoot "dist\lockfixctl.exe") -Force
Copy-Item -LiteralPath (Join-Path $Root "dist\installer\LOCK-FIX Setup Wizard.exe") -Destination (Join-Path $PackageRoot "dist\installer\LOCK-FIX Setup Wizard.exe") -Force
Copy-ItemClean -Source (Join-Path $Root "config") -Destination (Join-Path $PackageRoot "config")
Copy-ItemClean -Source (Join-Path $Root "lockfix") -Destination (Join-Path $PackageRoot "lockfix")
Copy-ItemClean -Source (Join-Path $Root "web") -Destination (Join-Path $PackageRoot "web")
Copy-ItemClean -Source (Join-Path $Root "tools") -Destination (Join-Path $PackageRoot "tools")
New-Item -ItemType Directory -Force -Path (Join-Path $PackageRoot "integrated") | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Root "integrated") -File -ErrorAction SilentlyContinue |
    Copy-Item -Destination (Join-Path $PackageRoot "integrated") -Force
Copy-ItemClean -Source (Join-Path $Root "packaging\windows") -Destination (Join-Path $PackageRoot "packaging\windows")

Copy-Item -LiteralPath (Join-Path $Root "webui.py") -Destination (Join-Path $PackageRoot "webui.py") -Force
Copy-Item -LiteralPath (Join-Path $Root "lockfixctl.py") -Destination (Join-Path $PackageRoot "lockfixctl.py") -Force
Copy-Item -LiteralPath (Join-Path $Root "README.md") -Destination (Join-Path $PackageRoot "README.md") -Force
Copy-Item -LiteralPath (Join-Path $Root "requirements_from_ppt.md") -Destination (Join-Path $PackageRoot "requirements_from_ppt.md") -Force
Copy-Item -LiteralPath (Join-Path $Root "requirements_from_reports.md") -Destination (Join-Path $PackageRoot "requirements_from_reports.md") -Force

$InstallGuide = @'
# LOCK-FIX Windows Installer Package

Windows Server 전용 설치 패키지입니다. 다른 OS용 설치 파일과 패키징 스크립트는 포함하지 않습니다.

보호 정책:

- `C:\` Windows OS 볼륨은 절대 분리, 재연결, 전원 격리 대상이 될 수 없습니다.
- 장치 경로 또는 마운트 경로가 `C:`, `C:\`, `C:\...`이면 코드 레벨에서 즉시 차단하고 감사 로그를 남깁니다.
- 백업 격리 대상은 `D:\`, `E:\` 같은 별도 백업 전용 Windows 볼륨으로 지정해야 합니다.

## 실행 방법

1. 이 ZIP 파일을 원하는 폴더에 압축 해제합니다.
2. `LOCK-FIX Setup Wizard.exe`를 실행합니다.
3. 설치 마법사 화면에 따라 설치를 진행합니다.

## 설치 마법사 흐름

1. Welcome
2. System Check
3. Install Type
4. Component Selection
5. Veeam Connection
6. Security Key
7. Installation Path
8. Summary
9. Install Progress
10. Complete

## Web UI

콘솔 실행:

```text
LOCK-FIX Console.exe
```

설치 완료 화면에 표시되는 접속 주소:

```text
https://localhost:8443
```

현재 PoC 실행 주소:

```text
http://127.0.0.1:8088
```

## Veeam REST API 사전진단

Veeam 계정과 비밀번호를 환경변수로 설정한 뒤 실행합니다.

```powershell
$env:LOCKFIX_VEEAM_BASE_URL = "https://127.0.0.1:9419"
$env:LOCKFIX_VEEAM_EM_BASE_URL = "https://127.0.0.1:9398"
$env:LOCKFIX_VEEAM_USER = "Veeam계정"
$env:LOCKFIX_VEEAM_PASSWORD = "Veeam비밀번호"
powershell -ExecutionPolicy Bypass -File .\tools\veeam_preflight.ps1
```

PowerShell의 Windows TLS 경로가 실패하면 위 스크립트는 자동으로 LOCK-FIX Python VeeamClient 검증을 시도합니다. 제품 연동 정상 여부는 Python 결과의 `token` 및 `sessions` 성공 여부를 기준으로 판단합니다.

LOCK-FIX Veeam 연동의 기준 API는 VBR REST `9419`입니다. `/api/v1/sessions`, `/api/v1/sessions/{id}/logs`, `/api/v1/taskSessions`를 조회해 `Name / Status / Action / Duration`을 구성합니다. Enterprise Manager REST `9398`은 참고 진단만 수행하며 필수 조건이 아닙니다.

PowerShell/curl 실패는 Windows Schannel 진단 이슈일 수 있으므로 실제 제품 검증은 LOCK-FIX Python HTTPS 클라이언트의 `9419` 호출 결과로 판단합니다. 비밀번호는 환경변수에서만 읽으며 로그에 출력하지 않습니다.

운영 설정에서는 Veeam Job ID를 알 수 있으면 이름보다 정확하므로 `job_id`를 함께 지정합니다.

필수 연동 흐름:

1. `https://<VeeamServer>:9419/api/v1`을 VBR REST API 기준 URL로 사용합니다.
2. `/api/oauth2/token`에서 OAuth2 access token을 발급합니다.
3. 모든 요청에 `x-api-version`을 적용합니다. 기본값은 `1.2-rev1`이며 현장 Swagger/API Reference에 맞게 `config.veeam.api_version`에서 변경할 수 있습니다.
4. `/api/v1/jobs`와 `/api/v1/sessions`를 조회합니다.
5. `job_id`를 우선 매칭하고, 없으면 `job_name`을 exact, case-insensitive, normalized 순서로 보조 매칭합니다.
6. 최신 session의 `result/status`가 `Success`이면 `controller.isolate()`를 호출합니다.
7. 같은 `session_id`는 runtime state에 기록해 중복 isolate를 방지합니다.
8. PoC에서는 `verify_ssl=false`로 자체 서명 인증서를 허용할 수 있고, 운영에서는 Veeam REST 인증서를 Windows 신뢰 저장소에 등록한 뒤 `verify_ssl=true`를 사용합니다.
9. `veeam-test`는 9419, 참고용 9398, token, jobs, sessions, job match, isolate 조건을 한 번에 진단합니다.

```json
"veeam": {
  "job_name": "Agent_backup",
  "job_id": "실제 Veeam Job ID"
}
```

PowerShell 7 또는 Windows `curl.exe`만 실패하고 LOCK-FIX Python 검증은 성공하는 경우, Windows Schannel/TLS 경로를 별도로 진단합니다.

```powershell
$env:LOCKFIX_VEEAM_BASE_URL = "https://127.0.0.1:9419"
$env:LOCKFIX_VEEAM_USER = "Veeam계정"
$env:LOCKFIX_VEEAM_PASSWORD = "Veeam비밀번호"
powershell -ExecutionPolicy Bypass -File .\tools\veeam_schannel_diagnostics.ps1 -TestCurl
```

`SchUseStrongCrypto` 또는 `SystemDefaultTlsVersions`가 `missing`이고 PowerShell/curl에서 `SEC_E_NO_CREDENTIALS`가 발생하면 관리자 PowerShell에서 다음을 적용한 뒤 PowerShell 창을 다시 열거나 서버를 재부팅합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\veeam_schannel_diagnostics.ps1 -ApplyStrongCrypto
```

운영 환경에서는 Veeam REST 인증서를 로컬 컴퓨터의 신뢰할 수 있는 루트 인증 기관에 등록하고, 가능하면 `https://127.0.0.1:9419` 대신 인증서 이름과 맞는 `https://localhost:9419`, 서버명, 또는 FQDN을 사용합니다.

결과 코드는 다음 기준으로 분류됩니다.

- `401`: 인증 실패
- `403`: Veeam 권한 부족
- `ConnectionError`: 포트, 방화벽, 서비스 문제
- `SSLError`: 인증서 또는 TLS 문제
- `404`: API 경로 또는 `x-api-version` 문제

연동이 성공하면 `lockfixctl.py veeam-test`와 `lockfixctl.py veeam-watch --once`로 LOCK-FIX isolate 연동을 확인합니다.

## 포함 파일

- `LOCK-FIX Setup Wizard.exe`
- `LOCK-FIX Console.exe`
- `dist\lockfix-ui.exe`
- `dist\lockfixctl.exe`
- `config`
- `lockfix`
- `web`
- `integrated`
- `packaging\windows`
'@

$InstallGuide | Set-Content -LiteralPath (Join-Path $PackageRoot "INSTALL_GUIDE.md") -Encoding UTF8

Compress-Archive -Path (Join-Path $PackageRoot "*") -DestinationPath $ZipPath -Force

Write-Host "Package folder: $PackageRoot"
Write-Host "Package zip: $ZipPath"
