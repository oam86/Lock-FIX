$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $Root "build\logs"
$RunId = Get-Date -Format "yyyyMMdd-HHmmss"
$LogPath = Join-Path $LogDir "msi-build-$RunId.log"
$AdvancedInstaller = "C:\Program Files (x86)\Caphyon\Advanced Installer 23.6\bin\x86\AdvancedInstaller.com"
$Builder = Join-Path $Root "packaging\windows\build_advanced_installer.ps1"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([Parameter(Mandatory = $true)][string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Invoke-Logged {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    Write-Log "START: $Label"
    & $Command 2>&1 | ForEach-Object {
        $text = $_.ToString()
        Write-Host $text
        Add-Content -LiteralPath $LogPath -Value $text -Encoding UTF8
    }
    if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
    Write-Log "DONE: $Label"
}

Write-Log "LOCK-FIX MSI verbose build started."
Write-Log "Workspace: $Root"
Write-Log "Log file: $LogPath"

if (-not (Test-Path $AdvancedInstaller)) {
    throw "Advanced Installer CLI not found: $AdvancedInstaller"
}
if (-not (Test-Path $Builder)) {
    throw "Build script not found: $Builder"
}

$env:ADVINST_COM = $AdvancedInstaller
Write-Log "Advanced Installer CLI: $AdvancedInstaller"

Invoke-Logged "Build LOCK-FIX Windows executables" {
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "build_windows.ps1")
}

Invoke-Logged "Build Advanced Installer MSI package" {
    powershell -NoProfile -ExecutionPolicy Bypass -File $Builder
}

$MsiPath = Join-Path $Root "dist\installer\LOCK-FIX Setup.msi"
if (Test-Path $MsiPath) {
    $item = Get-Item $MsiPath
    Write-Log ("MSI created: {0} ({1:N0} bytes)" -f $item.FullName, $item.Length)
} else {
    throw "MSI output was not found: $MsiPath"
}

Write-Log "LOCK-FIX MSI verbose build finished."
