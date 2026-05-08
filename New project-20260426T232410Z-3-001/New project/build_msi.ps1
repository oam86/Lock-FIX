$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Builder = Join-Path $Root "packaging\windows\build_advanced_installer.ps1"

if (-not (Test-Path $Builder)) {
    throw "Advanced Installer build script not found: $Builder"
}

& $Builder
