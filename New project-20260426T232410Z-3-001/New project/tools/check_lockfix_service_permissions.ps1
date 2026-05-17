param(
  [string]$ServiceName = "LOCKFIXWebUI",
  [string]$InstallRoot = "C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX",
  [int[]]$Ports = @(8088, 8099),
  [switch]$RestartService,
  [switch]$RegisterFirewallRules
)

$ErrorActionPreference = "Continue"

function Write-Section {
  param([string]$Title)
  Write-Host ""
  Write-Host "=== $Title ==="
}

function Test-Administrator {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-Logged {
  param(
    [string]$Label,
    [scriptblock]$Script
  )
  Write-Host "[$Label]"
  try {
    & $Script
  } catch {
    Write-Host "ERROR: $($_.Exception.Message)"
  }
}

$isAdmin = Test-Administrator
Write-Section "LOCK-FIX Service Permission Preflight"
Write-Host "Administrator shell: $isAdmin"
Write-Host "Service name: $ServiceName"
Write-Host "Install root: $InstallRoot"
Write-Host "Ports: $($Ports -join ', ')"

Write-Section "Windows Identity"
Invoke-Logged "whoami" { whoami }
Invoke-Logged "whoami /groups" { whoami /groups }

Write-Section "Service State"
Invoke-Logged "Get-Service" {
  Get-Service | Where-Object { $_.Name -like "*LOCK*" -or $_.DisplayName -like "*LOCK*" } |
    Select-Object Name,DisplayName,Status,StartType | Format-Table -AutoSize
}
Invoke-Logged "sc queryex" { sc.exe queryex $ServiceName }
Invoke-Logged "sc qc" { sc.exe qc $ServiceName }
Invoke-Logged "sc sdshow" { sc.exe sdshow $ServiceName }

if ($RestartService) {
  Write-Section "Restart Service"
  if (-not $isAdmin) {
    Write-Host "SKIPPED: service restart requires Administrator PowerShell."
  } else {
    Invoke-Logged "Restart-Service" {
      Restart-Service -Name $ServiceName -Force -ErrorAction Stop
      Start-Sleep -Seconds 3
      Get-Service -Name $ServiceName | Select-Object Name,Status,StartType | Format-Table -AutoSize
    }
  }
}

Write-Section "Local Administrators"
Invoke-Logged "Get-LocalGroupMember Administrators" {
  Get-LocalGroupMember Administrators | Select-Object Name,ObjectClass,PrincipalSource | Format-Table -AutoSize
}

Write-Section "PowerShell Policy"
Invoke-Logged "Get-ExecutionPolicy -List" { Get-ExecutionPolicy -List | Format-Table -AutoSize }

Write-Section "Disk Command Permission"
Invoke-Logged "Get-Disk" { Get-Disk -ErrorAction Stop | Select-Object Number,FriendlyName,OperationalStatus,PartitionStyle | Format-Table -AutoSize }
Invoke-Logged "Get-Partition" { Get-Partition -ErrorAction Stop | Select-Object DiskNumber,PartitionNumber,DriveLetter,Type | Format-Table -AutoSize }
Invoke-Logged "Get-Volume" { Get-Volume -ErrorAction Stop | Select-Object DriveLetter,FileSystemLabel,FileSystem,DriveType,HealthStatus | Format-Table -AutoSize }

Write-Section "Port Usage"
foreach ($port in $Ports) {
  Invoke-Logged "netstat :$port" { netstat -ano | findstr ":$port" }
}

Write-Section "Endpoint Check"
foreach ($port in $Ports) {
  Invoke-Logged "http://127.0.0.1:$port/" {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$port/" -TimeoutSec 5
    Write-Host "HTTP $($response.StatusCode)"
  }
}

if ($RegisterFirewallRules) {
  Write-Section "Firewall Rules"
  if (-not $isAdmin) {
    Write-Host "SKIPPED: firewall registration requires Administrator PowerShell."
  } else {
    foreach ($port in $Ports) {
      Invoke-Logged "Firewall TCP $port" {
        $displayName = "Allow LOCK-FIX WebUI TCP $port"
        $existing = Get-NetFirewallRule -DisplayName $displayName -ErrorAction SilentlyContinue
        if (-not $existing) {
          New-NetFirewallRule -DisplayName $displayName -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow | Out-Null
          Write-Host "registered: $displayName"
        } else {
          Write-Host "already exists: $displayName"
        }
      }
    }
  }
}

Write-Section "Installed File Hash"
$files = @(
  "webui.py",
  "web\static\index.html",
  "web\static\app.js",
  "web\static\styles.css"
)
foreach ($file in $files) {
  $path = Join-Path $InstallRoot $file
  Invoke-Logged $file {
    if (Test-Path -LiteralPath $path) {
      Get-FileHash -Algorithm SHA256 -LiteralPath $path | Format-List Path,Hash
    } else {
      Write-Host "MISSING: $path"
    }
  }
}

Write-Section "Result Guide"
Write-Host "If service control is denied, reopen PowerShell as Administrator and rerun this script."
Write-Host "If many CLOSE_WAIT entries remain on 8088, restart the LOCK-FIX WebUI service from an Administrator shell."
Write-Host "If endpoint checks fail while the service is Running, verify the service log and port owner PID."
