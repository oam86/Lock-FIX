param(
    [string]$BaseUrl = $env:LOCKFIX_VEEAM_BASE_URL,
    [string]$Username = $env:LOCKFIX_VEEAM_USER,
    [string]$Password = $env:LOCKFIX_VEEAM_PASSWORD,
    [string]$ApiVersion = $(if ($env:LOCKFIX_VEEAM_API_VERSION) { $env:LOCKFIX_VEEAM_API_VERSION } else { "1.2-rev1" }),
    [string]$JobName = $env:LOCKFIX_VEEAM_JOB_NAME,
    [string]$JobId = $env:LOCKFIX_VEEAM_JOB_ID,
    [switch]$VerifySsl,
    [switch]$NoPythonFallback
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = "https://127.0.0.1:9419"
}
$BaseUrl = $BaseUrl.TrimEnd("/")
$SupportsSkipCertificateCheck = (Get-Command Invoke-RestMethod).Parameters.ContainsKey("SkipCertificateCheck")
if (-not $VerifySsl -and -not $SupportsSkipCertificateCheck) {
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls13
}

function Write-Result {
    param(
        [string]$Step,
        [bool]$Ok,
        [string]$Code,
        [string]$Message
    )
    [pscustomobject]@{
        step = $Step
        ok = $Ok
        code = $Code
        message = $Message
    } | ConvertTo-Json -Compress
}

function Convert-ErrorCode {
    param([object]$ErrorRecord)
    $response = $ErrorRecord.Exception.Response
    if ($response) {
        $statusCode = [int]$response.StatusCode
        if ($statusCode -eq 401) { return "401" }
        if ($statusCode -eq 403) { return "403" }
        if ($statusCode -eq 404) { return "404" }
        return "HTTP_$statusCode"
    }
    $message = $ErrorRecord.Exception.Message
    $inner = ""
    if ($ErrorRecord.Exception.InnerException) {
        $inner = $ErrorRecord.Exception.InnerException.Message
    }
    $combined = "$message $inner"
    if ($combined -match "SSL|certificate|Authentication failed|SEC_E") { return "SSLError" }
    return "ConnectionError"
}

function Invoke-PythonFallback {
    param([string]$Reason)
    if ($NoPythonFallback) {
        return
    }
    $script = Join-Path (Split-Path -Parent $PSScriptRoot) "tools\veeam_python_preflight.py"
    $pythonCandidates = @(
        "C:\Program Files\LOCK-FIX\python\python.exe",
        "python",
        "py"
    )
    foreach ($python in $pythonCandidates) {
        try {
            $cmd = Get-Command $python -ErrorAction SilentlyContinue
            if ($cmd -or (Test-Path $python)) {
                Write-Result -Step "python_fallback" -Ok $true -Code "RUN" -Message "PowerShell REST failed: $Reason. Running LOCK-FIX Python VeeamClient preflight."
                & $python $script
                return
            }
        } catch {
        }
    }
    Write-Result -Step "python_fallback" -Ok $false -Code "NOT_FOUND" -Message "Python runtime was not found for LOCK-FIX fallback."
}

try {
    $uri = [uri]$BaseUrl
    $port = if ($uri.Port -gt 0) { $uri.Port } elseif ($uri.Scheme -eq "https") { 443 } else { 80 }
    $tcp = Test-NetConnection -ComputerName $uri.Host -Port $port -WarningAction SilentlyContinue
    Write-Result -Step "port" -Ok ([bool]$tcp.TcpTestSucceeded) -Code $(if ($tcp.TcpTestSucceeded) { "OK" } else { "ConnectionError" }) -Message "$($uri.Host):$port"
} catch {
    Write-Result -Step "port" -Ok $false -Code "ConnectionError" -Message $_.Exception.Message
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Username) -or [string]::IsNullOrWhiteSpace($Password)) {
    Write-Result -Step "token" -Ok $false -Code "401" -Message "Veeam username/password are missing. Set LOCKFIX_VEEAM_USER and LOCKFIX_VEEAM_PASSWORD."
    exit 1
}

$common = @{
    Headers = @{ "x-api-version" = $ApiVersion }
    TimeoutSec = 10
}
if (-not $VerifySsl -and $SupportsSkipCertificateCheck) {
    $common["SkipCertificateCheck"] = $true
}

try {
    $body = "grant_type=password&username=$([uri]::EscapeDataString($Username))&password=$([uri]::EscapeDataString($Password))"
    $token = Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/api/oauth2/token" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $body `
        @common
    if (-not $token.access_token) {
        Write-Result -Step "token" -Ok $false -Code "401" -Message "Token response did not include access_token."
        exit 1
    }
    Write-Result -Step "token" -Ok $true -Code "OK" -Message "access_token issued. length=$($token.access_token.Length)"
} catch {
    $code = Convert-ErrorCode $_
    Write-Result -Step "token" -Ok $false -Code $code -Message $_.Exception.Message
    Invoke-PythonFallback -Reason $code
    exit 1
}

try {
    $sessionParams = @{
        Method = "Get"
        Uri = "$BaseUrl/api/v1/sessions"
        Headers = @{ "x-api-version" = $ApiVersion; "Authorization" = "Bearer $($token.access_token)" }
        TimeoutSec = 10
    }
    if (-not $VerifySsl -and $SupportsSkipCertificateCheck) {
        $sessionParams["SkipCertificateCheck"] = $true
    }
    $sessions = Invoke-RestMethod @sessionParams
    $count = 0
    if ($sessions.data) { $count = @($sessions.data).Count }
    elseif ($sessions.items) { $count = @($sessions.items).Count }
    elseif ($sessions.results) { $count = @($sessions.results).Count }
    Write-Result -Step "sessions" -Ok $true -Code "OK" -Message "/api/v1/sessions query succeeded. count=$count"
} catch {
    $code = Convert-ErrorCode $_
    Write-Result -Step "sessions" -Ok $false -Code $code -Message $_.Exception.Message
    Invoke-PythonFallback -Reason $code
    exit 1
}

function Invoke-VeeamGet {
    param([string]$Path)
    $params = @{
        Method = "Get"
        Uri = "$BaseUrl$Path"
        Headers = @{ "x-api-version" = $ApiVersion; "Authorization" = "Bearer $($token.access_token)" }
        TimeoutSec = 10
    }
    if (-not $VerifySsl -and $SupportsSkipCertificateCheck) {
        $params["SkipCertificateCheck"] = $true
    }
    Invoke-RestMethod @params
}

function Get-ItemCount {
    param([object]$Value)
    if ($null -eq $Value) { return 0 }
    if ($Value.data) { return @($Value.data).Count }
    if ($Value.items) { return @($Value.items).Count }
    if ($Value.results) { return @($Value.results).Count }
    if ($Value.value) { return @($Value.value).Count }
    return 0
}

$jobsOk = $false
$backupsOk = $false
$jobMatched = [string]::IsNullOrWhiteSpace($JobName) -and [string]::IsNullOrWhiteSpace($JobId)

try {
    $jobs = Invoke-VeeamGet -Path "/api/v1/jobs"
    $jobsOk = $true
    $jobCount = Get-ItemCount $jobs
    if (-not $jobMatched) {
        foreach ($item in @($jobs.data) + @($jobs.items) + @($jobs.results) + @($jobs.value)) {
            if ($null -eq $item) { continue }
            $name = [string]$item.name
            if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$item.jobName }
            $id = [string]$item.id
            if ([string]::IsNullOrWhiteSpace($id)) { $id = [string]$item.jobId }
            if ((-not [string]::IsNullOrWhiteSpace($JobName) -and $name -ieq $JobName) -or
                (-not [string]::IsNullOrWhiteSpace($JobId) -and $id -ieq $JobId)) {
                $jobMatched = $true
                break
            }
        }
    }
    Write-Result -Step "jobs" -Ok $true -Code "OK" -Message "/api/v1/jobs query succeeded. count=$jobCount"
} catch {
    $code = Convert-ErrorCode $_
    Write-Result -Step "jobs" -Ok $false -Code $code -Message $_.Exception.Message
}

try {
    $backups = Invoke-VeeamGet -Path "/api/v1/backups"
    $backupsOk = $true
    $backupCount = Get-ItemCount $backups
    if (-not $jobMatched) {
        foreach ($item in @($backups.data) + @($backups.items) + @($backups.results) + @($backups.value)) {
            if ($null -eq $item) { continue }
            $name = [string]$item.name
            if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$item.jobName }
            $id = [string]$item.id
            if ([string]::IsNullOrWhiteSpace($id)) { $id = [string]$item.jobId }
            if ((-not [string]::IsNullOrWhiteSpace($JobName) -and $name -ieq $JobName) -or
                (-not [string]::IsNullOrWhiteSpace($JobId) -and $id -ieq $JobId)) {
                $jobMatched = $true
                break
            }
        }
    }
    Write-Result -Step "backups" -Ok $true -Code "OK" -Message "/api/v1/backups query succeeded. count=$backupCount"
} catch {
    $code = Convert-ErrorCode $_
    Write-Result -Step "backups" -Ok $false -Code $code -Message $_.Exception.Message
}

if (-not $jobsOk -and -not $backupsOk) {
    Write-Result -Step "inventory_permission" -Ok $false -Code "403" -Message "Token was issued, but neither jobs nor backups inventory could be queried. Grant at least Veeam Backup Viewer permission."
    exit 1
}

if ($jobMatched) {
    Write-Result -Step "job_match" -Ok $true -Code "OK" -Message "Configured job identity is present, or no job identity was supplied."
} else {
    Write-Result -Step "job_match" -Ok $false -Code "NO_MATCH" -Message "Configured job name/id was not found. Sessions may be empty on a new server, but the configured Veeam job must exist before automatic LOCK-FIX isolation can match it."
    exit 1
}

Write-Result -Step "install_gate" -Ok $true -Code "OK" -Message "Preflight passed. A missing matching completed session is not an install blocker; LOCK-FIX will wait for the next successful Veeam session."
