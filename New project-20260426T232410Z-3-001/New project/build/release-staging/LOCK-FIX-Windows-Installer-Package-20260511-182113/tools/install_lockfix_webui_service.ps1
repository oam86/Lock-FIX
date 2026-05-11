param(
    [string]$InstallRoot = "",
    [string]$ServiceName = "LOCKFIXWebUI",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

$scriptPath = $MyInvocation.MyCommand.Path
$toolsRoot = Split-Path -Parent $scriptPath
if ([string]::IsNullOrWhiteSpace($InstallRoot)) {
    $InstallRoot = Split-Path -Parent $toolsRoot
}
$InstallRoot = (Resolve-Path -LiteralPath $InstallRoot).Path
$serviceExe = Join-Path $InstallRoot "LOCK-FIX WebUI Service.exe"

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Administrator permission is required to register the LOCK-FIX Web UI Windows service."
    }
}

Assert-Administrator

if ($Uninstall) {
    $existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($existing) {
        if ($existing.Status -ne "Stopped") {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
        & sc.exe delete $ServiceName | Out-Null
    }
    Write-Host "LOCK-FIX Web UI service removed: $ServiceName"
    exit 0
}

if (-not (Test-Path -LiteralPath $serviceExe)) {
    throw "LOCK-FIX Web UI service executable was not found: $serviceExe"
}
$pythonCandidates = @(
    (Join-Path $InstallRoot "python\python.exe"),
    (Join-Path $env:ProgramFiles "LOCK-FIX\python\python.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "LOCK-FIX\python\python.exe")
)
$pythonFound = $false
foreach ($candidate in $pythonCandidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
        $pythonFound = $true
        break
    }
}
if (-not $pythonFound) {
    throw "Python runtime was not found. The offline package must contain python\python.exe, or an existing LOCK-FIX Python runtime must be installed."
}

$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    if ($existing.Status -ne "Stopped") {
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    & sc.exe delete $ServiceName | Out-Null
    Start-Sleep -Seconds 2
}

$binPath = '"' + $serviceExe + '"'
& sc.exe create $ServiceName binPath= $binPath start= auto DisplayName= "LOCK-FIX Web UI" | Out-Null
& sc.exe description $ServiceName "Keeps LOCK-FIX Web UI listening on http://127.0.0.1:8088 using the bundled offline Python runtime." | Out-Null
Start-Service -Name $ServiceName
Write-Host "LOCK-FIX Web UI service registered and started: $ServiceName"
Write-Host "Web UI: http://127.0.0.1:8088"
