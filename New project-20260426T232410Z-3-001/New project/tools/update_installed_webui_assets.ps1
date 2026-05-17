param(
  [string]$SourceRoot = "",
  [string]$InstallRoot = "C:\Users\Administrator\AppData\Local\Programs\OAM\LOCK-FIX",
  [string]$ServiceName = "LOCKFIXWebUI",
  [int]$WebUiPort = 8088
)

$ErrorActionPreference = "Stop"

if (-not $SourceRoot) {
  $packageRoot = Split-Path -Parent $PSScriptRoot
  if (Test-Path -LiteralPath (Join-Path $packageRoot "webui.py")) {
    $SourceRoot = $packageRoot
  } else {
    $SourceRoot = Split-Path -Parent $packageRoot
  }
}

$logDir = Join-Path $SourceRoot "runtime"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "installed-webui-update.log"

function Write-Log {
  param([string]$Message)
  $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
  Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
  Write-Host $line
}

function Test-Administrator {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Assert-Administrator {
  if (-not (Test-Administrator)) {
    throw "Administrator permission is required to update installed LOCK-FIX WebUI assets and restart the Windows service. Open PowerShell with 'Start-Process powershell -Verb runAs' and run this script again."
  }
}

function Write-ServiceDiagnostics {
  param([string]$Name)
  try {
    Write-Log "SERVICE_QC_BEGIN $Name"
    (& sc.exe qc $Name) | ForEach-Object { Write-Log "SERVICE_QC $_" }
  } catch {
    Write-Log "SERVICE_QC_WARN $($_.Exception.Message)"
  }
  try {
    Write-Log "SERVICE_SDSHOW_BEGIN $Name"
    (& sc.exe sdshow $Name) | ForEach-Object { Write-Log "SERVICE_SDSHOW $_" }
  } catch {
    Write-Log "SERVICE_SDSHOW_WARN $($_.Exception.Message)"
  }
}

function Write-PortSnapshot {
  param([int[]]$Ports)
  foreach ($port in $Ports) {
    try {
      $rows = @(netstat -ano | Select-String ":$port")
      if ($rows.Count -eq 0) {
        Write-Log "PORT_SNAPSHOT TCP $port no entries"
      } else {
        $rows | ForEach-Object { Write-Log "PORT_SNAPSHOT TCP $port $($_.Line.Trim())" }
      }
    } catch {
      Write-Log "PORT_SNAPSHOT_WARN TCP $port $($_.Exception.Message)"
    }
  }
}

function Copy-Checked {
  param(
    [string]$RelativePath
  )
  $src = Join-Path $SourceRoot $RelativePath
  $dst = Join-Path $InstallRoot $RelativePath
  if (-not (Test-Path -LiteralPath $src)) {
    throw "Source file missing: $src"
  }
  $dstDir = Split-Path -Parent $dst
  New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
  Copy-Item -LiteralPath $src -Destination $dst -Force
  $srcHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $src).Hash
  $dstHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dst).Hash
  if ($srcHash -ne $dstHash) {
    throw "Hash mismatch after copy: $RelativePath"
  }
  Write-Log "SYNC_OK $RelativePath $dstHash"
}

function Get-WebUiPortProcessIds {
  try {
    $connections = @(Get-NetTCPConnection -LocalPort $WebUiPort -State Listen -ErrorAction Stop)
    return @($connections | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ })
  } catch {
    Write-Log "PORT_SCAN_WARN Get-NetTCPConnection failed: $($_.Exception.Message)"
    try {
      $matches = @(netstat -ano | Select-String "127\.0\.0\.1:$WebUiPort\s+.*LISTENING")
      $pids = @()
      foreach ($match in $matches) {
        $parts = -split $match.Line.Trim()
        $pidText = $parts[-1]
        $pid = 0
        if ([int]::TryParse($pidText, [ref]$pid) -and $pid -gt 0) {
          $pids += $pid
        }
      }
      return @($pids | Select-Object -Unique)
    } catch {
      Write-Log "PORT_SCAN_WARN netstat fallback failed: $($_.Exception.Message)"
      return @()
    }
  }
}

function Stop-WebUiPortProcesses {
  param([object[]]$ProcessIds)
  foreach ($candidate in $ProcessIds) {
    $processId = 0
    if (-not [int]::TryParse([string]$candidate, [ref]$processId)) {
      Write-Log "PROCESS_STOP_SKIP non-numeric PID value: $candidate"
      continue
    }
    try {
      $process = Get-Process -Id $processId -ErrorAction Stop
      Write-Log "Stopping WebUI process PID=$processId Name=$($process.ProcessName)"
      Stop-Process -Id $processId -Force -ErrorAction Stop
      Write-Log "PROCESS_STOPPED PID=$processId"
    } catch {
      Write-Log "PROCESS_STOP_WARN PID=$processId $($_.Exception.Message)"
    }
  }
}

function Start-WebUiProcessFallback {
  $python = Join-Path $InstallRoot "python\python.exe"
  $webui = Join-Path $InstallRoot "webui.py"
  if (-not (Test-Path -LiteralPath $python)) {
    Write-Log "FALLBACK_START_SKIPPED python not found: $python"
    return
  }
  if (-not (Test-Path -LiteralPath $webui)) {
    Write-Log "FALLBACK_START_SKIPPED webui.py not found: $webui"
    return
  }
  Write-Log "Starting fallback WebUI process on port $WebUiPort"
  Start-Process -FilePath $python -ArgumentList @($webui) -WorkingDirectory $InstallRoot -WindowStyle Hidden | Out-Null
}

function Assert-InstalledEndpointVersion {
  $expectedIndex = Join-Path $SourceRoot "web\static\index.html"
  $expectedContent = Get-Content -LiteralPath $expectedIndex -Raw -Encoding UTF8
  $expectedVersion = [regex]::Match($expectedContent, "app\.js\?v=([^`"']+)").Groups[1].Value
  if (-not $expectedVersion) {
    Write-Log "ENDPOINT_VERIFY_WARN latest app cache version not found in source index"
    return
  }
  for ($i = 0; $i -lt 12; $i++) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$WebUiPort/" -TimeoutSec 2
      $runningVersion = [regex]::Match($response.Content, "app\.js\?v=([^`"']+)").Groups[1].Value
      if ($runningVersion -eq $expectedVersion) {
        Write-Log "ENDPOINT_VERIFY_OK app.js?v=$runningVersion"
        return
      }
      Write-Log "ENDPOINT_VERIFY_WAIT expected=$expectedVersion running=$runningVersion"
    } catch {
      Write-Log "ENDPOINT_VERIFY_WAIT $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 1
  }
  throw "Installed WebUI endpoint did not serve latest cache version: expected $expectedVersion"
}

Write-Log "START installed WebUI update"
Write-Log "SourceRoot=$SourceRoot"
Write-Log "InstallRoot=$InstallRoot"
Assert-Administrator
Write-PortSnapshot -Ports @($WebUiPort, 8099)

if (-not (Test-Path -LiteralPath $InstallRoot)) {
  throw "Install root not found: $InstallRoot"
}

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
$portPids = Get-WebUiPortProcessIds
$files = @(
  "webui.py",
  "lockfix\controller.py",
  "lockfix\approvals.py",
  "web\static\app.js",
  "web\static\styles.css",
  "web\static\lockfix-global-logo.svg",
  "web\static\index.html"
)

foreach ($file in $files) {
  $src = Join-Path $SourceRoot $file
  if (-not (Test-Path -LiteralPath $src)) {
    throw "Source file missing before service stop: $src"
  }
}

if ($service) {
  Write-ServiceDiagnostics -Name $ServiceName
  Write-Log "Stopping service $ServiceName"
  Stop-Service -Name $ServiceName -Force -ErrorAction Stop
  $service.WaitForStatus("Stopped", "00:00:30")
  Write-Log "SERVICE_STOPPED $ServiceName"
} else {
  Write-Log "SERVICE_NOT_FOUND $ServiceName"
}
Stop-WebUiPortProcesses -ProcessIds $portPids

foreach ($file in $files) {
  Copy-Checked -RelativePath $file
}

if ($service) {
  Write-Log "Starting service $ServiceName"
  Start-Service -Name $ServiceName -ErrorAction Stop
  (Get-Service -Name $ServiceName).WaitForStatus("Running", "00:00:30")
  Write-Log "SERVICE_RUNNING $ServiceName"
} else {
  Start-WebUiProcessFallback
}

Assert-InstalledEndpointVersion
Write-Log "DONE installed WebUI update"
