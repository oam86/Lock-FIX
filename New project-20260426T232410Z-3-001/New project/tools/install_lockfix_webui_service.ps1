param(
    [string]$InstallRoot = "",
    [string]$ServiceName = "LOCKFIXWebUI",
    [int]$WebUiPort = 8088,
    [int[]]$FirewallPorts = @(),
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
        throw "Administrator permission is required to register or control the LOCK-FIX Web UI Windows service. Open PowerShell with 'Start-Process powershell -Verb runAs' and run this script again."
    }
}

Assert-Administrator

function Ensure-FirewallRule {
    param([int]$Port)
    try {
        $displayName = "Allow LOCK-FIX WebUI TCP $Port"
        $existing = Get-NetFirewallRule -DisplayName $displayName -ErrorAction SilentlyContinue
        if (-not $existing) {
            New-NetFirewallRule -DisplayName $displayName -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow | Out-Null
            Write-Host "Firewall rule registered: $displayName"
        } else {
            Write-Host "Firewall rule already exists: $displayName"
        }
    } catch {
        Write-Warning "Firewall rule check failed for TCP ${Port}: $($_.Exception.Message)"
    }
}

function Test-WebUiEndpoint {
    param([int]$Port)
    for ($i = 0; $i -lt 10; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/" -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Host "Web UI endpoint verified: http://127.0.0.1:$Port"
                return
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    throw "Web UI endpoint did not respond on http://127.0.0.1:$Port after service start."
}

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

foreach ($port in $FirewallPorts) {
    Ensure-FirewallRule -Port $port
}

$binPath = '"' + $serviceExe + '"'
& sc.exe create $ServiceName binPath= $binPath start= auto obj= LocalSystem DisplayName= "LOCK-FIX Web UI" | Out-Null
& sc.exe description $ServiceName "Keeps LOCK-FIX Web UI listening on local-only http://127.0.0.1:$WebUiPort using the bundled offline Python runtime." | Out-Null
Start-Service -Name $ServiceName
Write-Host "LOCK-FIX Web UI service registered and started: $ServiceName"
Write-Host "Service account: LocalSystem"
Write-Host "Web UI: http://127.0.0.1:$WebUiPort"
Test-WebUiEndpoint -Port $WebUiPort
