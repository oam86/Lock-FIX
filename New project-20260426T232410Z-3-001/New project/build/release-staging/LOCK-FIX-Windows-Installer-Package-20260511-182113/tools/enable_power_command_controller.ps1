param(
    [string]$InstallRoot = "$env:LOCALAPPDATA\Programs\OAM\LOCK-FIX",
    [string]$SlotId = "BAY-01",
    [string]$OffUrl = "",
    [string]$OnUrl = "",
    [string]$StatusUrl = "",
    [string]$OffExe = "",
    [string]$OnExe = "",
    [string]$StatusExe = "",
    [string]$OffArgsJson = "",
    [string]$OnArgsJson = "",
    [string]$StatusArgsJson = "",
    [string]$AuthHeader = "",
    [string]$AuthValue = "",
    [switch]$RestartWebUi
)

$ErrorActionPreference = "Stop"

function Set-MachineEnvIfValue {
    param([string]$Name, [string]$Value)
    if ($Value) {
        [Environment]::SetEnvironmentVariable($Name, $Value, "Machine")
        [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
    }
}

function Restart-LockFixWebUi {
    $service = Get-Service -Name "LOCK-FIX WebUI" -ErrorAction SilentlyContinue
    if ($service) {
        Restart-Service -Name $service.Name -Force
        return
    }
    Get-Process -Name "LOCK-FIX WebUI Service", "lockfix-ui" -ErrorAction SilentlyContinue | Stop-Process -Force
}

$install = Resolve-Path -LiteralPath $InstallRoot
$configPath = Join-Path $install "config\lockfix.example.json"
$toolSource = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "lockfix_power_control.ps1"
$toolDir = Join-Path $install "tools"
$toolTarget = Join-Path $toolDir "lockfix_power_control.ps1"

if (-not (Test-Path -LiteralPath $configPath)) {
    throw "LOCK-FIX config was not found: $configPath"
}
if (-not (Test-Path -LiteralPath $toolSource)) {
    throw "Power controller script was not found: $toolSource"
}

New-Item -ItemType Directory -Force -Path $toolDir | Out-Null
Copy-Item -LiteralPath $toolSource -Destination $toolTarget -Force

$slotKey = ($SlotId -replace "[^A-Za-z0-9]", "_").ToUpperInvariant()
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_OFF_URL" $OffUrl
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_ON_URL" $OnUrl
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_STATUS_URL" $StatusUrl
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_OFF_EXE" $OffExe
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_ON_EXE" $OnExe
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_STATUS_EXE" $StatusExe
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_OFF_ARGS_JSON" $OffArgsJson
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_ON_ARGS_JSON" $OnArgsJson
Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_STATUS_ARGS_JSON" $StatusArgsJson
if ($AuthHeader -and $AuthValue) {
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_OFF_AUTH_HEADER" $AuthHeader
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_OFF_AUTH_VALUE" $AuthValue
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_ON_AUTH_HEADER" $AuthHeader
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_ON_AUTH_VALUE" $AuthValue
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_STATUS_AUTH_HEADER" $AuthHeader
    Set-MachineEnvIfValue "LOCKFIX_POWER_${slotKey}_STATUS_AUTH_VALUE" $AuthValue
}

$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$slot = $config.slots | Where-Object { $_.slot_id -eq $SlotId } | Select-Object -First 1
if (-not $slot) {
    throw "LOCK-FIX slot was not found: $SlotId"
}

$slot.power.type = "command"
$slot.power.off_command = @(
    "powershell",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $toolTarget,
    "-Action",
    "Off",
    "-SlotId",
    $SlotId
)
$slot.power.on_command = @(
    "powershell",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $toolTarget,
    "-Action",
    "On",
    "-SlotId",
    $SlotId
)
$slot.power.status_command = @(
    "powershell",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $toolTarget,
    "-Action",
    "Status",
    "-SlotId",
    $SlotId
)
$slot.power.off_status_values = @("off", "powered_off")

$config | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $configPath -Encoding UTF8

if ($RestartWebUi) {
    Restart-LockFixWebUi
}

Write-Output "LOCK-FIX power controller is set to command for $SlotId."
Write-Output "Config: $configPath"
Write-Output "Controller: $toolTarget"
