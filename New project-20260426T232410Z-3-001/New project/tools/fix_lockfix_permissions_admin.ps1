$ErrorActionPreference = "Continue"

$InstallRoot = "C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX"
$UserName = "WIN-73D1N4MIUQS\Administrator"
$LogPath = Join-Path $InstallRoot "runtime\admin-permission-fix.log"

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

Write-Log "START LOCK-FIX permission repair"

try {
    $service = Get-Service -Name "LOCKFIXWebUI" -ErrorAction SilentlyContinue
    if ($service) {
        Stop-Service -Name "LOCKFIXWebUI" -Force -ErrorAction SilentlyContinue
        Write-Log ("LOCKFIXWebUI service status after stop: " + (Get-Service -Name "LOCKFIXWebUI").Status)
    } else {
        Write-Log "LOCKFIXWebUI service not found"
    }
} catch {
    Write-Log ("Service stop failed: " + $_.Exception.Message)
}

try {
    Write-Log ("Grant ACL target: " + $InstallRoot)
    icacls $InstallRoot /grant "$UserName`:(OI)(CI)F" /T | ForEach-Object { Write-Log $_ }
} catch {
    Write-Log ("ACL grant failed: " + $_.Exception.Message)
}

try {
    $statePath = Join-Path $InstallRoot "runtime\state.json"
    if (Test-Path -LiteralPath $statePath) {
        $raw = Get-Content -Raw -LiteralPath $statePath
        try {
            $null = $raw | ConvertFrom-Json
            Write-Log "runtime state.json is already valid JSON"
        } catch {
            $lastBrace = $raw.LastIndexOf("}")
            if ($lastBrace -gt 0) {
                $fixed = $raw.Substring(0, $lastBrace).TrimEnd() + [Environment]::NewLine
                try {
                    $null = $fixed | ConvertFrom-Json
                    Copy-Item -LiteralPath $statePath -Destination ($statePath + ".corrupt") -Force
                    Set-Content -LiteralPath $statePath -Value $fixed -Encoding UTF8
                    Write-Log "runtime state.json repaired and .corrupt backup created"
                } catch {
                    Write-Log ("runtime state.json repair candidate failed: " + $_.Exception.Message)
                }
            } else {
                Write-Log "runtime state.json repair skipped: no JSON object end found"
            }
        }
    } else {
        Write-Log "runtime state.json not found"
    }
} catch {
    Write-Log ("state repair failed: " + $_.Exception.Message)
}

try {
    $listener = netstat -ano | Select-String ":8088.*LISTENING"
    if ($listener) {
        Write-Log ("8088 listener remains: " + ($listener -join " | "))
    } else {
        Write-Log "8088 has no LISTENING process"
    }
} catch {
    Write-Log ("8088 check failed: " + $_.Exception.Message)
}

Write-Log "END LOCK-FIX permission repair"
Read-Host "Press Enter to close"
