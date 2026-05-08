param(
    [string]$BaseUrl = $env:LOCKFIX_VEEAM_BASE_URL,
    [string]$Username = $env:LOCKFIX_VEEAM_USER,
    [string]$Password = $env:LOCKFIX_VEEAM_PASSWORD,
    [string]$ApiVersion = $(if ($env:LOCKFIX_VEEAM_API_VERSION) { $env:LOCKFIX_VEEAM_API_VERSION } else { "1.2-rev1" }),
    [switch]$ApplyStrongCrypto,
    [switch]$TestCurl,
    [switch]$ExportVeeamCertificate
)

$ErrorActionPreference = "Stop"

if (-not $BaseUrl) {
    $BaseUrl = "https://127.0.0.1:9419"
}

function Write-Check {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Message
    )
    [pscustomobject]@{
        check = $Name
        status = $Status
        message = $Message
    }
}

function Get-RegistryValueText {
    param([string]$Path, [string]$Name)
    try {
        $item = Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop
        return [string]$item.$Name
    } catch {
        return "missing"
    }
}

function Set-StrongCrypto {
    $paths = @(
        "HKLM:\SOFTWARE\Microsoft\.NETFramework\v4.0.30319",
        "HKLM:\SOFTWARE\Wow6432Node\Microsoft\.NETFramework\v4.0.30319"
    )
    foreach ($path in $paths) {
        New-Item -Path $path -Force | Out-Null
        New-ItemProperty -Path $path -Name "SchUseStrongCrypto" -Value 1 -PropertyType DWord -Force | Out-Null
        New-ItemProperty -Path $path -Name "SystemDefaultTlsVersions" -Value 1 -PropertyType DWord -Force | Out-Null
    }
}

function Test-PowerShellRest {
    param([string]$Shell)
    $script = @"
`$ErrorActionPreference = 'Stop'
`$Body = @{ grant_type = 'password'; username = '$Username'; password = '$Password' }
try {
    `$Token = Invoke-RestMethod -Method Post -Uri '$BaseUrl/api/oauth2/token' -Headers @{ 'x-api-version' = '$ApiVersion' } -ContentType 'application/x-www-form-urlencoded' -Body `$Body -SkipCertificateCheck -TimeoutSec 10
    [pscustomobject]@{ ok = `$true; token_length = (`$Token.access_token).Length; error = '' } | ConvertTo-Json -Compress
} catch {
    `$messages = @()
    `$e = `$_.Exception
    while (`$e) {
        `$messages += (`$e.GetType().FullName + ': ' + `$e.Message)
        `$e = `$e.InnerException
    }
    [pscustomobject]@{ ok = `$false; token_length = 0; error = (`$messages -join ' | ') } | ConvertTo-Json -Compress
}
"@
    $bytes = [Text.Encoding]::Unicode.GetBytes($script)
    $encoded = [Convert]::ToBase64String($bytes)
    & $Shell -NoProfile -EncodedCommand $encoded
}

$results = New-Object System.Collections.Generic.List[object]
$uri = [Uri]$BaseUrl

try {
    $tcp = New-Object Net.Sockets.TcpClient
    $async = $tcp.BeginConnect($uri.Host, $uri.Port, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne(3000)
    if ($ok -and $tcp.Connected) {
        $results.Add((Write-Check "port" "ok" "Veeam REST API port is reachable: $($uri.Host):$($uri.Port)"))
    } else {
        $results.Add((Write-Check "port" "fail" "Veeam REST API port is not reachable: $($uri.Host):$($uri.Port)"))
    }
    $tcp.Close()
} catch {
    $results.Add((Write-Check "port" "fail" $_.Exception.Message))
}

$results.Add((Write-Check "dotnet-strong-crypto-x64" "info" ("SchUseStrongCrypto=" + (Get-RegistryValueText "HKLM:\SOFTWARE\Microsoft\.NETFramework\v4.0.30319" "SchUseStrongCrypto") + "; SystemDefaultTlsVersions=" + (Get-RegistryValueText "HKLM:\SOFTWARE\Microsoft\.NETFramework\v4.0.30319" "SystemDefaultTlsVersions"))))
$results.Add((Write-Check "dotnet-strong-crypto-x86" "info" ("SchUseStrongCrypto=" + (Get-RegistryValueText "HKLM:\SOFTWARE\Wow6432Node\Microsoft\.NETFramework\v4.0.30319" "SchUseStrongCrypto") + "; SystemDefaultTlsVersions=" + (Get-RegistryValueText "HKLM:\SOFTWARE\Wow6432Node\Microsoft\.NETFramework\v4.0.30319" "SystemDefaultTlsVersions"))))

if ($ApplyStrongCrypto) {
    try {
        Set-StrongCrypto
        $results.Add((Write-Check "apply-strong-crypto" "ok" "Strong crypto and system default TLS versions were enabled. Restart PowerShell or reboot before retesting."))
    } catch {
        $results.Add((Write-Check "apply-strong-crypto" "fail" $_.Exception.Message))
    }
}

$certs = Get-ChildItem Cert:\LocalMachine\My -ErrorAction SilentlyContinue |
    Where-Object { $_.Subject -like "*Veeam*" -or $_.DnsNameList -match $uri.Host } |
    Sort-Object NotAfter -Descending

foreach ($cert in $certs | Select-Object -First 5) {
    $trusted = [bool](Get-ChildItem Cert:\LocalMachine\Root -ErrorAction SilentlyContinue | Where-Object { $_.Thumbprint -eq $cert.Thumbprint })
    $results.Add((Write-Check "certificate" "info" ("Subject=$($cert.Subject); Thumbprint=$($cert.Thumbprint); TrustedRoot=$trusted; NotAfter=$($cert.NotAfter)")))
}

if ($ExportVeeamCertificate -and $certs) {
    $exportPath = Join-Path $PWD "veeam-rest-api.cer"
    Export-Certificate -Cert $certs[0] -FilePath $exportPath -Force | Out-Null
    $results.Add((Write-Check "export-certificate" "ok" "Exported certificate to $exportPath. Import into LocalMachine Root if Schannel tools must trust it."))
}

if ($Username -and $Password) {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh) {
        $results.Add((Write-Check "powershell-7-token" "info" (Test-PowerShellRest $pwsh.Source)))
    } else {
        $results.Add((Write-Check "powershell-7-token" "skip" "PowerShell 7 was not found."))
    }

    if ($TestCurl) {
        $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
        if ($curl) {
            $curlResult = & $curl.Source -k --ssl-no-revoke -s -o NUL -w "HTTP=%{http_code} SSL=%{ssl_verify_result} ERR=%{errormsg}" -X POST "$BaseUrl/api/oauth2/token" -H "x-api-version: $ApiVersion" -H "Content-Type: application/x-www-form-urlencoded" --data "grant_type=password&username=$Username&password=$Password"
            $results.Add((Write-Check "curl-token" "info" $curlResult))
        } else {
            $results.Add((Write-Check "curl-token" "skip" "curl.exe was not found."))
        }
    }
} else {
    $results.Add((Write-Check "token-tests" "skip" "Set LOCKFIX_VEEAM_USER and LOCKFIX_VEEAM_PASSWORD to test token issuance."))
}

$results | ConvertTo-Json -Depth 5
