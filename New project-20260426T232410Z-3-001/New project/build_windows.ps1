$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Compiler = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$CtlSource = Join-Path $Root "src\LockFixCtl.cs"
$UiSource = Join-Path $Root "src\LockFixUiLauncher.cs"
$Dist = Join-Path $Root "dist"
$CtlOutput = Join-Path $Dist "lockfixctl.exe"
$UiOutput = Join-Path $Dist "lockfix-ui.exe"

if (-not (Test-Path $Compiler)) {
    $Compiler = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
}

if (-not (Test-Path $Compiler)) {
    throw "Windows C# compiler not found."
}

New-Item -ItemType Directory -Force -Path $Dist | Out-Null
& $Compiler /nologo /target:exe /optimize+ /out:$CtlOutput /reference:System.Web.Extensions.dll $CtlSource
& $Compiler /nologo /target:exe /optimize+ /out:$UiOutput $UiSource

Write-Host $CtlOutput
Write-Host $UiOutput
