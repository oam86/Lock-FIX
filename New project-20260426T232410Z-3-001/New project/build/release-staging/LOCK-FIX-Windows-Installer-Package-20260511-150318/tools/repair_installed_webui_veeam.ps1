param(
    [string]$InstallRoot = "$env:LOCALAPPDATA\Programs\OAM\LOCK-FIX",
    [string]$VeeamHost = "192.168.219.230",
    [int]$VeeamPort = 9419,
    [string]$VeeamUser = "administrator",
    [string]$ApiVersion = "1.2-rev1",
    [switch]$RestartWebUi
)

$ErrorActionPreference = "Stop"

function Convert-SecureStringToPlainText {
    param([Parameter(Mandatory = $true)][Security.SecureString]$Value)
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value)
    try {
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Copy-DirectoryClean {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Source folder not found: $Source"
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    & robocopy $Source $Destination /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Folder copy failed: $Source -> $Destination (robocopy exit code $LASTEXITCODE)"
    }
    $global:LASTEXITCODE = 0
}

$scriptPath = $MyInvocation.MyCommand.Path
$toolsRoot = Split-Path -Parent $scriptPath
$sourceRoot = Split-Path -Parent $toolsRoot

if (-not (Test-Path -LiteralPath $InstallRoot)) {
    throw "LOCK-FIX install folder was not found: $InstallRoot"
}
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot "webui.py"))) {
    throw "Run this repair tool from a LOCK-FIX package or source folder that contains webui.py."
}

$securePassword = Read-Host "Veeam password for $VeeamUser@$VeeamHost" -AsSecureString
$plainPassword = Convert-SecureStringToPlainText $securePassword
if ([string]::IsNullOrWhiteSpace($plainPassword)) {
    throw "Veeam password is required."
}

$runtime = Join-Path $InstallRoot "runtime"
$backupRoot = Join-Path $runtime ("repair-backup-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Force -Path $runtime, $backupRoot | Out-Null

foreach ($relative in @("webui.py", "lockfix", "web")) {
    $target = Join-Path $InstallRoot $relative
    if (Test-Path -LiteralPath $target) {
        Copy-Item -LiteralPath $target -Destination $backupRoot -Recurse -Force
    }
}

Copy-Item -LiteralPath (Join-Path $sourceRoot "webui.py") -Destination (Join-Path $InstallRoot "webui.py") -Force
Copy-DirectoryClean -Source (Join-Path $sourceRoot "lockfix") -Destination (Join-Path $InstallRoot "lockfix")
Copy-DirectoryClean -Source (Join-Path $sourceRoot "web") -Destination (Join-Path $InstallRoot "web")

$configPath = Join-Path $InstallRoot "config\lockfix.example.json"
if (-not (Test-Path -LiteralPath $configPath)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $configPath) | Out-Null
    Copy-Item -LiteralPath (Join-Path $sourceRoot "config\lockfix.example.json") -Destination $configPath -Force
}

$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
if (-not $config.veeam) {
    $config | Add-Member -MemberType NoteProperty -Name veeam -Value ([pscustomobject]@{})
}
$baseUrl = "https://${VeeamHost}:${VeeamPort}"
$config.veeam.enabled = $true
$config.veeam.base_url = $baseUrl
$config.veeam.auto_discover = $true
$config.veeam.discovery_candidates = @($baseUrl)
$config.veeam.discovery_scan_local_subnet = $true
$config.veeam.api_version = $ApiVersion
$config.veeam.username = $VeeamUser
$config.veeam.username_env = "LOCKFIX_VEEAM_USER"
$config.veeam.password_env = "LOCKFIX_VEEAM_PASSWORD"
$config.veeam.verify_ssl = $false
$config | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $configPath -Encoding UTF8

$installProperties = @"
install_type=repair
components=Core Service, Web UI, Veeam Connector, Agent, DB
veeam_host=$VeeamHost
veeam_port=$VeeamPort
veeam_base_url=$baseUrl
veeam_api_version=$ApiVersion
veeam_auth=Windows Authentication
veeam_user=$VeeamUser
veeam_password=$plainPassword
security_key_type=LOCK-FIX License Key
web_ui_url=http://127.0.0.1:8088
"@
$installProperties | Set-Content -LiteralPath (Join-Path $runtime "install.properties") -Encoding UTF8

if ($RestartWebUi) {
    Get-NetTCPConnection -LocalPort 8088 -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $console = Join-Path $InstallRoot "LOCK-FIX Console.exe"
    if (Test-Path -LiteralPath $console) {
        Start-Process -FilePath $console -WorkingDirectory $InstallRoot -WindowStyle Minimized
    }
}

Write-Host "LOCK-FIX installed Web UI Veeam settings repaired."
Write-Host "Install root: $InstallRoot"
Write-Host "Veeam base URL: $baseUrl"
Write-Host "Password stored for local Web UI runtime; password value was not printed."
Write-Host "Restart Web UI to apply the updated runtime settings."
