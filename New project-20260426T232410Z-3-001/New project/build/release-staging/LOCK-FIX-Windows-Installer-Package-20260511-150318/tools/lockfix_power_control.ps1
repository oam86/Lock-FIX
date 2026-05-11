param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Off", "On", "Status")]
    [string]$Action,

    [Parameter(Mandatory = $true)]
    [string]$SlotId
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Get-LockFixEnvValue {
    param([string[]]$Names)
    foreach ($name in $Names) {
        $value = [Environment]::GetEnvironmentVariable($name, "Machine")
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($name, "User")
        }
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($name, "Process")
        }
        if ($value) {
            return $value
        }
    }
    return $null
}

function ConvertTo-LockFixHashtable {
    param([string]$JsonText)
    $table = @{}
    if (-not $JsonText) {
        return $table
    }
    $object = $JsonText | ConvertFrom-Json
    foreach ($property in $object.PSObject.Properties) {
        $table[$property.Name] = [string]$property.Value
    }
    return $table
}

function ConvertTo-LockFixArgumentList {
    param([string]$JsonText)
    if (-not $JsonText) {
        return @()
    }
    $items = $JsonText | ConvertFrom-Json
    if ($items -is [System.Array]) {
        return @($items | ForEach-Object { [string]$_ })
    }
    return @([string]$items)
}

$slotKey = ($SlotId -replace "[^A-Za-z0-9]", "_").ToUpperInvariant()
$actionKey = $Action.ToUpperInvariant()
$prefixes = @("LOCKFIX_POWER_${slotKey}_${actionKey}", "LOCKFIX_POWER_${actionKey}")

$exe = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_EXE" })
$argsJson = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_ARGS_JSON" })
if ($exe) {
    $arguments = ConvertTo-LockFixArgumentList $argsJson
    Write-Output "LOCK-FIX Power $Action START - slot $SlotId, external controller command."
    $output = & $exe @arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "LOCK-FIX Power $Action ERROR - external controller exited with code $LASTEXITCODE."
    }
    if ($output) {
        Write-Output ($output | Out-String).Trim()
    }
    Write-Output "LOCK-FIX Power $Action OK - slot $SlotId, external controller command completed."
    exit 0
}

$url = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_URL" })
if ($url) {
    $uri = $null
    if (-not [System.Uri]::TryCreate($url, [System.UriKind]::Absolute, [ref]$uri) -or $uri.Scheme -notin @("http", "https")) {
        throw "LOCK-FIX Power $Action URL is invalid for slot $SlotId. Configure a real PDU/relay/storage-controller HTTP URL in LOCKFIX_POWER_${slotKey}_${actionKey}_URL. Current value is not a valid http/https URL."
    }
    $method = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_METHOD" })
    if (-not $method) {
        if ($Action -eq "Status") {
            $method = "GET"
        } else {
            $method = "POST"
        }
    }
    $body = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_BODY_JSON" })
    if (-not $body -and $Action -ne "Status") {
        $body = (@{
            action = $Action.ToLowerInvariant()
            slot_id = $SlotId
            source = "LOCK-FIX"
            timestamp = (Get-Date).ToString("o")
        } | ConvertTo-Json -Compress)
    }

    $headers = ConvertTo-LockFixHashtable (Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_HEADERS_JSON" }))
    $authHeader = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_AUTH_HEADER" })
    $authValue = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_AUTH_VALUE" })
    $bearer = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_BEARER_TOKEN" })
    if ($authHeader -and $authValue) {
        $headers[$authHeader] = $authValue
    }
    if ($bearer) {
        $headers["Authorization"] = "Bearer $bearer"
    }

    $skipCertificateCheck = Get-LockFixEnvValue @($prefixes | ForEach-Object { "${_}_SKIP_CERTIFICATE_CHECK" })
    if ($skipCertificateCheck -and $skipCertificateCheck.Trim().ToLowerInvariant() -in @("1", "true", "yes", "on")) {
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
    }

    Write-Output "LOCK-FIX Power $Action START - slot $SlotId, HTTP controller request."
    if ($Action -eq "Status" -and -not $body) {
        $response = Invoke-RestMethod -Method $method -Uri $url -Headers $headers -ContentType "application/json"
    } else {
        $response = Invoke-RestMethod -Method $method -Uri $url -Headers $headers -ContentType "application/json" -Body $body
    }
    if ($null -ne $response) {
        if ($response -is [string]) {
            Write-Output $response
        } else {
            Write-Output ($response | ConvertTo-Json -Compress)
        }
    }
    Write-Output "LOCK-FIX Power $Action OK - slot $SlotId, HTTP controller request completed."
    exit 0
}

throw "LOCK-FIX Power $Action controller is not configured. Set LOCKFIX_POWER_${slotKey}_${actionKey}_URL or LOCKFIX_POWER_${slotKey}_${actionKey}_EXE."
