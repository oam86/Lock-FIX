param(
    [string]$SourceRoot = "",
    [string]$InstallRoot = "$env:LOCALAPPDATA\Programs\OAM\LOCK-FIX",
    [string]$ServiceName = "LOCKFIXWebUI",
    [string]$VeeamHost = "192.168.219.230",
    [int]$VeeamPort = 9419,
    [string]$VeeamUser = "administrator",
    [string]$ApiVersion = "1.2-rev1",
    [string]$JobName = "Agent_backup",
    [string]$JobId = "a61d20b5-2555-4635-ab65-86b6fc2bf449",
    [ValidateSet("simulation", "live")]
    [string]$OperationMode = "live"
)

$ErrorActionPreference = "Stop"

function Assert-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Administrator permission is required. Open PowerShell as Administrator and run this script again."
    }
}

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

function Read-InstallProperties {
    param([string]$Path)
    $props = @{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $props
    }
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*#' -or $line -notmatch '=') {
            continue
        }
        $key, $value = $line -split '=', 2
        $props[$key.Trim()] = $value
    }
    return $props
}

function Write-InstallProperties {
    param(
        [string]$Path,
        [hashtable]$Props
    )
    $ordered = @(
        "install_type",
        "operation_mode",
        "dry_run",
        "components",
        "veeam_host",
        "veeam_port",
        "veeam_base_url",
        "veeam_api_version",
        "veeam_auth",
        "veeam_user",
        "veeam_password",
        "security_key_type",
        "web_ui_url"
    )
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($key in $ordered) {
        if ($Props.ContainsKey($key)) {
            $lines.Add("$key=$($Props[$key])")
        }
    }
    foreach ($key in ($Props.Keys | Sort-Object)) {
        if ($ordered -notcontains $key) {
            $lines.Add("$key=$($Props[$key])")
        }
    }
    $lines | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Set-ObjectProperty {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)]$Value
    )
    if ($Object.PSObject.Properties[$Name]) {
        $Object.$Name = $Value
    }
    else {
        $Object | Add-Member -MemberType NoteProperty -Name $Name -Value $Value
    }
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Value
    )
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Value, $encoding)
}

function Repair-StateJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return "state.json not found"
    }
    $raw = Get-Content -LiteralPath $Path -Raw
    try {
        $null = $raw | ConvertFrom-Json
        return "state.json valid"
    }
    catch {
        $decoder = New-Object System.Text.UTF8Encoding($false)
        $trimmed = $raw.Trim()
        $depth = 0
        $endIndex = -1
        for ($i = 0; $i -lt $trimmed.Length; $i++) {
            $ch = $trimmed[$i]
            if ($ch -eq '{') { $depth++ }
            elseif ($ch -eq '}') {
                $depth--
                if ($depth -eq 0) {
                    $endIndex = $i
                    break
                }
            }
        }
        if ($endIndex -lt 0) {
            throw "state.json is corrupt and could not be repaired automatically."
        }
        $clean = $trimmed.Substring(0, $endIndex + 1)
        $backup = "$Path.corrupt"
        Copy-Item -LiteralPath $Path -Destination $backup -Force
        [System.IO.File]::WriteAllText($Path, $clean + [Environment]::NewLine, $decoder)
        return "state.json repaired; backup: $backup"
    }
}

function Copy-RequiredFiles {
    param(
        [string]$Source,
        [string]$Destination
    )
    $files = @(
        "webui.py",
        "lockfix\command.py",
        "lockfix\controller.py",
        "lockfix\state_store.py",
        "lockfix\disk.py",
        "lockfix\hashcheck.py",
        "lockfix\power.py",
        "lockfix\identity.py",
        "lockfix\config.py",
        "lockfix\veeam_client.py",
        "lockfix\veeam_console_logs.py",
        "lockfix\veeam_diagnostics.py",
        "lockfix\veeam_factory.py",
        "lockfix\veeam_watcher.py",
        "lockfix\veeam_webui_check.py",
        "web\static\app.js",
        "web\static\styles.css",
        "config\lockfix.example.json"
    )
    foreach ($rel in $files) {
        $from = Join-Path $Source $rel
        $to = Join-Path $Destination $rel
        if (-not (Test-Path -LiteralPath $from)) {
            throw "Source file missing: $from"
        }
        New-Item -ItemType Directory -Path (Split-Path $to -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $from -Destination $to -Force
        Write-Host "Copied $rel"
    }
}

function Update-VeeamConfig {
    param(
        [string]$ConfigPath,
        [string]$BaseUrl,
        [string]$OperationMode
    )
    New-Item -ItemType Directory -Path (Split-Path $ConfigPath -Parent) -Force | Out-Null
    if (Test-Path -LiteralPath $ConfigPath) {
        $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    }
    else {
        $config = [pscustomobject]@{}
    }
    if (-not $config.PSObject.Properties["veeam"]) {
        $config | Add-Member -MemberType NoteProperty -Name veeam -Value ([pscustomobject]@{})
    }
    $effectiveDryRun = $OperationMode -ne "live"
    Set-ObjectProperty -Object $config -Name operation_mode -Value $OperationMode
    Set-ObjectProperty -Object $config -Name dry_run -Value $effectiveDryRun
    $config.veeam.enabled = $true
    $config.veeam.base_url = $BaseUrl
    $config.veeam.api_version = $ApiVersion
    $config.veeam.username = $VeeamUser
    $config.veeam.username_env = "LOCKFIX_VEEAM_USER"
    $config.veeam.password_env = "LOCKFIX_VEEAM_PASSWORD"
    $config.veeam.verify_ssl = $false
    $config.veeam.job_name = $JobName
    $config.veeam.job_id = $JobId
    $config.veeam.poll_interval_seconds = 1
    $config.veeam.isolate_on_status = @("Success")
    $config.veeam.auto_discover = $true
    $config.veeam.discovery_candidates = @($BaseUrl)
    $config.veeam.discovery_scan_local_subnet = $true
    Write-Utf8NoBom -Path $ConfigPath -Value (($config | ConvertTo-Json -Depth 20) + [Environment]::NewLine)
}

Assert-Administrator

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $scriptPath = $MyInvocation.MyCommand.Path
    $toolsRoot = Split-Path -Parent $scriptPath
    $SourceRoot = Split-Path -Parent $toolsRoot
}

$SourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
if (-not (Test-Path -LiteralPath $InstallRoot)) {
    throw "LOCK-FIX install folder not found: $InstallRoot"
}
if (-not (Test-Path -LiteralPath (Join-Path $SourceRoot "webui.py"))) {
    throw "SourceRoot does not look like LOCK-FIX source/package root: $SourceRoot"
}

$baseUrl = "https://${VeeamHost}:${VeeamPort}"
$runtime = Join-Path $InstallRoot "runtime"
$installPropsPath = Join-Path $runtime "install.properties"
$logRoot = Join-Path $SourceRoot "build\logs"
$logPath = Join-Path $logRoot ("apply-latest-webui-update-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".log")
New-Item -ItemType Directory -Path $runtime, $logRoot -Force | Out-Null
Start-Transcript -Path $logPath -Force | Out-Null

try {
    Write-Host "START LOCK-FIX installed Web UI update"
    Write-Host "SourceRoot: $SourceRoot"
    Write-Host "InstallRoot: $InstallRoot"
    Write-Host "Veeam base URL: $baseUrl"
    Write-Host "Operation mode: $OperationMode"

    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls $InstallRoot /grant "${identity}:(OI)(CI)F" /T | Out-Host

    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -ne "Stopped") {
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Host "Stopped $ServiceName"
    }

    Copy-RequiredFiles -Source $SourceRoot -Destination $InstallRoot
    Write-Host (Repair-StateJson -Path (Join-Path $runtime "state.json"))

    Update-VeeamConfig -ConfigPath (Join-Path $InstallRoot "config\lockfix.example.json") -BaseUrl $baseUrl -OperationMode $OperationMode
    $props = Read-InstallProperties -Path $installPropsPath
    $props["install_type"] = "repair"
    $props["operation_mode"] = $OperationMode
    $props["dry_run"] = if ($OperationMode -eq "live") { "false" } else { "true" }
    $props["components"] = "Core Service, Web UI, Veeam Connector, Agent, DB"
    $props["veeam_host"] = $VeeamHost
    $props["veeam_port"] = [string]$VeeamPort
    $props["veeam_base_url"] = $baseUrl
    $props["veeam_api_version"] = $ApiVersion
    $props["veeam_auth"] = "Windows Authentication"
    $props["veeam_user"] = $VeeamUser
    $props["web_ui_url"] = "http://127.0.0.1:8088"
    if (-not $props.ContainsKey("veeam_password") -or [string]::IsNullOrWhiteSpace($props["veeam_password"])) {
        $securePassword = Read-Host "Veeam password for $VeeamUser@$VeeamHost" -AsSecureString
        $props["veeam_password"] = Convert-SecureStringToPlainText $securePassword
    }
    Write-InstallProperties -Path $installPropsPath -Props $props
    Write-Host "Updated installed Veeam settings. Password was not printed."

    $env:LOCKFIX_VEEAM_USER = $VeeamUser
    $env:LOCKFIX_VEEAM_PASSWORD = $props["veeam_password"]
    $python = Join-Path $InstallRoot "python\python.exe"
    $ctl = Join-Path $InstallRoot "lockfixctl.py"
    if ((Test-Path -LiteralPath $python) -and (Test-Path -LiteralPath $ctl)) {
        Write-Host "Running installed veeam-test..."
        & $python $ctl veeam-test | Out-Host
    }
    else {
        Write-Host "Installed Python CLI was not found; skipping installed veeam-test."
    }

    if ($service) {
        Start-Service -Name $ServiceName
        Write-Host "Started $ServiceName"
    }
    else {
        $console = Join-Path $InstallRoot "LOCK-FIX Console.exe"
        if (Test-Path -LiteralPath $console) {
            Start-Process -FilePath $console -WorkingDirectory $InstallRoot -WindowStyle Minimized
            Write-Host "Started LOCK-FIX Console fallback"
        }
        else {
            Write-Host "No Web UI service or console executable found."
        }
    }

    $listening = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        $conn = Get-NetTCPConnection -LocalPort 8088 -State Listen -ErrorAction SilentlyContinue
        if ($conn) {
            $listening = $true
            break
        }
    }
    if ($listening) {
        Write-Host "8088 LISTENING"
        try {
            $api = Invoke-RestMethod -Uri "http://127.0.0.1:8088/api/veeam-backup" -Method Get -TimeoutSec 10
            $api | ConvertTo-Json -Depth 8 | Out-Host
        }
        catch {
            Write-Host "Web UI API check failed: $($_.Exception.Message)"
        }
    }
    else {
        Write-Host "Web UI server is not running on 8088"
    }

    Write-Host "END LOCK-FIX installed Web UI update"
    Write-Host "Log file: $logPath"
}
finally {
    Stop-Transcript | Out-Null
}
