param(
    [string]$ConfigPath = "$PSScriptRoot\..\config\lockfix.example.json",
    [string]$PythonPath = ""
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
    "-m", "lockfix.offline_reconnect_validation",
    "--config", (Resolve-Path $ConfigPath).Path
)

Push-Location $root
try {
    & $PythonPath @argsList
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($exitCode -eq 2) {
    Write-Warning "LOCK-FIX offline/emergency reconnect validation detected an issue. Check reports\offline-reconnect-report-yyyyMMdd-HHmmss.html and runtime\offline-reconnect-validation-yyyyMMdd-HHmmss.json."
    exit 2
}
exit $exitCode
