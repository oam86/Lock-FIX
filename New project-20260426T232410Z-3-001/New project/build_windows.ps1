$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Compiler = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$CtlSource = Join-Path $Root "src\LockFixCtl.cs"
$UiSource = Join-Path $Root "src\LockFixUiLauncher.cs"
$ConsoleSource = Join-Path $Root "src\LockFixConsoleWindow.cs"
$SetupSource = Join-Path $Root "src\LockFixSetupWizard.cs"
$Dist = Join-Path $Root "dist"
$InstallerDist = Join-Path $Dist "installer"
$CtlOutput = Join-Path $Dist "lockfixctl.exe"
$UiOutput = Join-Path $Dist "lockfix-ui.exe"
$ConsoleOutput = Join-Path $Dist "LOCK-FIX Console.exe"
$RootConsoleOutput = Join-Path $Root "LOCK-FIX Console.exe"
$SetupOutput = Join-Path $InstallerDist "LOCK-FIX Setup Wizard.exe"

if (-not (Test-Path $Compiler)) {
    $Compiler = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
}

if (-not (Test-Path $Compiler)) {
    throw "Windows C# compiler not found."
}

New-Item -ItemType Directory -Force -Path $Dist, $InstallerDist | Out-Null
& $Compiler /nologo /target:exe /optimize+ /out:$CtlOutput /reference:System.Web.Extensions.dll $CtlSource
& $Compiler /nologo /target:exe /optimize+ /out:$UiOutput $UiSource
& $Compiler /nologo /target:exe /optimize+ /out:$ConsoleOutput /reference:System.Windows.Forms.dll /reference:System.Drawing.dll $ConsoleSource
Copy-Item -LiteralPath $ConsoleOutput -Destination $RootConsoleOutput -Force
& $Compiler /nologo /target:winexe /optimize+ /out:$SetupOutput /reference:System.Windows.Forms.dll /reference:System.Drawing.dll $SetupSource

Write-Host $CtlOutput
Write-Host $UiOutput
Write-Host $ConsoleOutput
Write-Host $RootConsoleOutput
Write-Host $SetupOutput
