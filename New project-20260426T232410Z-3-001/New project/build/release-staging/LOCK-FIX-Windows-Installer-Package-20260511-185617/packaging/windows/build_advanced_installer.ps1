$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ProjectName = "LOCK-FIX"
$Manufacturer = "OAM"
$Version = "1.0.0"
$PackageName = "LOCK-FIX Setup.msi"

$BuildRoot = Join-Path $Root "build\windows-installer"
$PayloadRoot = Join-Path $BuildRoot "payload"
$InstallerOut = Join-Path $Root "dist\installer"
$AipPath = Join-Path $BuildRoot "LOCK-FIX.aip"
$AicPath = Join-Path $BuildRoot "LOCK-FIX.aic"

function Find-AdvancedInstaller {
    if ($env:ADVINST_COM -and (Test-Path $env:ADVINST_COM)) {
        return $env:ADVINST_COM
    }

    $candidates = @(
        "C:\Program Files (x86)\Caphyon",
        "C:\Program Files\Caphyon"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $found = Get-ChildItem -Path $candidate -Recurse -Filter "AdvancedInstaller.com" -ErrorAction SilentlyContinue |
                Sort-Object FullName -Descending |
                Select-Object -First 1
            if ($found) {
                return $found.FullName
            }
        }
    }

    throw "Advanced Installer command line tool was not found. Install Advanced Installer or set ADVINST_COM to AdvancedInstaller.com."
}

function Copy-ItemClean {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

$AdvancedInstaller = Find-AdvancedInstaller

New-Item -ItemType Directory -Force -Path $BuildRoot, $PayloadRoot, $InstallerOut | Out-Null

& (Join-Path $Root "build_windows.ps1")

Copy-ItemClean -Source (Join-Path $Root "dist") -Destination (Join-Path $PayloadRoot "dist")
Copy-ItemClean -Source (Join-Path $Root "config") -Destination (Join-Path $PayloadRoot "config")
Copy-ItemClean -Source (Join-Path $Root "lockfix") -Destination (Join-Path $PayloadRoot "lockfix")
Copy-ItemClean -Source (Join-Path $Root "web") -Destination (Join-Path $PayloadRoot "web")
Copy-ItemClean -Source (Join-Path $Root "integrated") -Destination (Join-Path $PayloadRoot "integrated")

Copy-Item -LiteralPath (Join-Path $Root "webui.py") -Destination (Join-Path $PayloadRoot "webui.py") -Force
Copy-Item -LiteralPath (Join-Path $Root "lockfixctl.py") -Destination (Join-Path $PayloadRoot "lockfixctl.py") -Force
Copy-Item -LiteralPath (Join-Path $Root "README.md") -Destination (Join-Path $PayloadRoot "README.md") -Force
Copy-Item -LiteralPath (Join-Path $Root "requirements_from_ppt.md") -Destination (Join-Path $PayloadRoot "requirements_from_ppt.md") -Force
Copy-Item -LiteralPath (Join-Path $Root "requirements_from_reports.md") -Destination (Join-Path $PayloadRoot "requirements_from_reports.md") -Force

if (Test-Path $AipPath) {
    Remove-Item -LiteralPath $AipPath -Force
}

& $AdvancedInstaller /newproject $AipPath -lang "en" -overwrite
& $AdvancedInstaller /edit $AipPath /SetProperty "ProductName=$ProjectName"
& $AdvancedInstaller /edit $AipPath /SetProperty "Manufacturer=$Manufacturer"
& $AdvancedInstaller /edit $AipPath /SetVersion $Version
& $AdvancedInstaller /edit $AipPath /SetPackageName (Join-Path $InstallerOut $PackageName)
& $AdvancedInstaller /edit $AipPath /SetOutputType MsiInside
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_INSTALL_TYPE=recommended"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_WEB_PORT=8443"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_WEB_URL=https://localhost:8443"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_SERVICE_NAME=LOCK-FIX Core Service"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_VEEAM_PORT=9419"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_VEEAM_AUTH_TYPE=Windows Authentication"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_ENABLE_CORE=1"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_ENABLE_WEBUI=1"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_ENABLE_VEEAM=1"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_ENABLE_AGENT=1"
& $AdvancedInstaller /edit $AipPath /SetProperty "LOCKFIX_ENABLE_DB=1"

$aic = @"
;aic
AddFolder APPDIR\dist "$($PayloadRoot)\dist"
AddFolder APPDIR\config "$($PayloadRoot)\config"
AddFolder APPDIR\lockfix "$($PayloadRoot)\lockfix"
AddFolder APPDIR\web "$($PayloadRoot)\web"
AddFolder APPDIR\integrated "$($PayloadRoot)\integrated"
AddFile APPDIR "$($PayloadRoot)\webui.py"
AddFile APPDIR "$($PayloadRoot)\lockfixctl.py"
AddFile APPDIR "$($PayloadRoot)\README.md"
AddFile APPDIR "$($PayloadRoot)\requirements_from_ppt.md"
AddFile APPDIR "$($PayloadRoot)\requirements_from_reports.md"
NewShortcut -name "LOCK-FIX" -dir SHORTCUTDIR -target APPDIR\dist\lockfix-ui.exe -mode normal
NewShortcut -name "LOCK-FIX Console" -dir SHORTCUTDIR -target APPDIR\dist\lockfixctl.exe -mode normal
NewShortcut -name "LOCK-FIX" -dir DesktopFolder -target APPDIR\dist\lockfix-ui.exe -mode normal
Save
Rebuild
"@

$utf8Bom = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText($AicPath, $aic, $utf8Bom)

& $AdvancedInstaller /execute $AipPath $AicPath

Write-Host "Advanced Installer project: $AipPath"
Write-Host "MSI output: $(Join-Path $InstallerOut $PackageName)"
