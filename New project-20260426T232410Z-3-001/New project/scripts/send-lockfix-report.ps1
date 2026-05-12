param(
    [string]$ConfigPath = "$PSScriptRoot\..\config\lockfix.example.json",
    [string]$PythonPath = "",
    [string]$EmailTo = "rich.kim@oam.co.kr",
    [string]$VeeamBaseUrl = "",
    [string]$VeeamUser = "",
    [string]$VeeamPassword = "",
    [switch]$SendOnIssue,
    [switch]$NoRecover
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\.."
if (-not $PythonPath) {
    $bundled = Join-Path $root "python\python.exe"
    if (Test-Path $bundled) {
        $PythonPath = $bundled
    } else {
        $PythonPath = "python"
    }
}

$argsList = @(
    "-m", "lockfix.daily_revalidation",
    "--config", (Resolve-Path $ConfigPath).Path,
    "--email-to", $EmailTo
)
if ($SendOnIssue) { $argsList += "--send-on-issue" }
if ($NoRecover) { $argsList += "--no-recover" }
if ($VeeamBaseUrl) { $env:LOCKFIX_VEEAM_BASE_URL = $VeeamBaseUrl }
if ($VeeamUser) { $env:LOCKFIX_VEEAM_USER = $VeeamUser }
if ($VeeamPassword) { $env:LOCKFIX_VEEAM_PASSWORD = $VeeamPassword }

Push-Location $root
try {
    & $PythonPath @argsList
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($exitCode -eq 2) {
    Write-Warning "LOCK-FIX daily revalidation detected an issue. Check reports\daily-report-yyyyMMdd.html and runtime\daily-revalidation-yyyyMMdd.json."
    exit 2
}
exit $exitCode
