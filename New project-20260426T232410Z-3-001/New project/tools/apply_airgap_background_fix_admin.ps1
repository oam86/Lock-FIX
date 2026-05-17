param(
    [string]$InstallRoot = "$env:LOCALAPPDATA\Programs\OAM\LOCK-FIX",
    [string]$ServiceName = "LOCKFIXWebUI",
    [int]$Port = 8088
)

$ErrorActionPreference = "Stop"

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Administrator permission is required to apply the LOCK-FIX Air-Gap background execution fix."
    }
}

Assert-Administrator

function Write-Step {
    param([string]$Message)
    Write-Host ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message)
}

function Stop-WebUiListeners {
    param([int]$Port)
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ } |
        ForEach-Object {
            Write-Step "Stopping existing WebUI listener PID $_ on port $Port"
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }
}

$scriptPath = $MyInvocation.MyCommand.Path
$toolsRoot = Split-Path -Parent $scriptPath
$sourceRoot = Split-Path -Parent $toolsRoot
$sourceWebui = Join-Path $sourceRoot "webui.py"
$targetWebui = Join-Path $InstallRoot "webui.py"
$targetTools = Join-Path $InstallRoot "tools"
$targetScript = Join-Path $targetTools (Split-Path -Leaf $scriptPath)

if (-not (Test-Path -LiteralPath $sourceWebui)) {
    throw "Source webui.py was not found: $sourceWebui"
}
if (-not (Test-Path -LiteralPath $InstallRoot)) {
    throw "LOCK-FIX install folder was not found: $InstallRoot"
}

$runtime = Join-Path $InstallRoot "runtime"
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$backup = Join-Path $runtime ("webui-before-airgap-background-fix-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".py")
if (Test-Path -LiteralPath $targetWebui) {
    Write-Step "Backing up installed webui.py"
    Copy-Item -LiteralPath $targetWebui -Destination $backup -Force
}

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service -and $service.Status -ne "Stopped") {
    Write-Step "Stopping service $ServiceName"
    Stop-Service -Name $ServiceName -Force
    Start-Sleep -Seconds 2
}

Stop-WebUiListeners -Port $Port

Write-Step "Applying latest webui.py with Air-Gap duplicate-run prevention"
Copy-Item -LiteralPath $sourceWebui -Destination $targetWebui -Force
New-Item -ItemType Directory -Force -Path $targetTools | Out-Null
Copy-Item -LiteralPath $scriptPath -Destination $targetScript -Force

$sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceWebui).Hash
$targetHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $targetWebui).Hash
if ($sourceHash -ne $targetHash) {
    throw "Installed webui.py hash mismatch after copy. source=$sourceHash target=$targetHash"
}

if ($service) {
    Write-Step "Starting service $ServiceName"
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 4
} else {
    Write-Host "Service was not found. Please start LOCK-FIX Web UI manually after applying the file."
}

if ($service) {
    $service = Get-Service -Name $ServiceName -ErrorAction Stop
    if ($service.Status -ne "Running") {
        throw "Service did not start correctly. Current status: $($service.Status)"
    }
}

$listener = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $listener) {
    Write-Step "No port $Port listener was detected yet. Service may still be starting."
} else {
    Write-Step "WebUI listener detected on port $Port, PID $($listener.OwningProcess)"
}

$installedText = Get-Content -LiteralPath $targetWebui -Raw
foreach ($required in @("AIRGAP_AUTO_ISOLATE_LOCK", "IN_PROGRESS", "veeam.auto_isolate.scheduled")) {
    if ($installedText -notlike "*$required*") {
        throw "Installed webui.py does not contain required Air-Gap fix token: $required"
    }
}

Write-Host "LOCK-FIX Air-Gap background execution fix applied."
Write-Host "Install root: $InstallRoot"
Write-Host "Backup: $backup"
Write-Host "webui.py SHA256: $targetHash"
Write-Host "Web UI: http://127.0.0.1:$Port"
