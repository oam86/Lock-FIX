param(
    [string]$TargetDrive = "D",
    [string]$AuditPath = ""
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Write-Output $line
}

function Write-Audit {
    param(
        [string]$Event,
        [bool]$Ok,
        [hashtable]$Data = @{}
    )
    if (-not $AuditPath) {
        return
    }
    $record = [ordered]@{
        ts = (Get-Date).ToUniversalTime().ToString("o")
        event = $Event
        ok = $Ok
        source = "manual_mount_d_volume.ps1"
    }
    foreach ($key in $Data.Keys) {
        $record[$key] = $Data[$key]
    }
    $json = $record | ConvertTo-Json -Compress
    Add-Content -LiteralPath $AuditPath -Value $json -Encoding UTF8
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Step "관리자 권한이 없어 D: 온라인/마운트 작업을 중단합니다."
    Write-Audit "manual.disk.mount_denied" $false @{ reason = "not_admin"; target_drive = $TargetDrive }
    exit 5
}

$driveRoot = "$TargetDrive`:\"
Write-Step "LOCK-FIX 수동 복구 시작 - 대상 드라이브: $driveRoot"

if ($TargetDrive.ToUpperInvariant() -eq "C") {
    Write-Step "C:는 보호 대상이므로 작업하지 않습니다."
    Write-Audit "manual.disk.mount_blocked" $false @{ reason = "c_drive_protected"; target_drive = $TargetDrive }
    exit 6
}

if (Test-Path -LiteralPath $driveRoot) {
    $volume = Get-Volume -DriveLetter $TargetDrive -ErrorAction Stop
    Write-Step "$driveRoot 는 이미 마운트되어 있습니다. 상태: $($volume.HealthStatus) / $($volume.OperationalStatus)"
    Write-Audit "manual.disk.mount_already_online" $true @{
        target_drive = $TargetDrive
        file_system = [string]$volume.FileSystem
        label = [string]$volume.FileSystemLabel
    }
    exit 0
}

$offlineDisks = @(
    Get-Disk -ErrorAction Stop |
        Where-Object { $_.IsOffline -and -not $_.IsBoot -and -not $_.IsSystem }
)

if ($offlineDisks.Count -eq 1) {
    $disk = $offlineDisks[0]
    Write-Step "오프라인 후보 디스크 #$($disk.Number)를 온라인으로 전환합니다."
    Set-Disk -Number $disk.Number -IsOffline $false -ErrorAction Stop
    if ($disk.IsReadOnly) {
        Set-Disk -Number $disk.Number -IsReadOnly $false -ErrorAction Stop
    }
    Start-Sleep -Seconds 2
} elseif ($offlineDisks.Count -gt 1) {
    Write-Step "오프라인 비시스템 디스크 후보가 여러 개입니다. 안전을 위해 자동 선택하지 않습니다."
    Write-Audit "manual.disk.mount_blocked" $false @{ reason = "multiple_offline_candidates"; count = $offlineDisks.Count; target_drive = $TargetDrive }
    exit 7
}

$partitions = @(
    Get-Partition -ErrorAction Stop |
        Where-Object {
            -not $_.DriveLetter -and
            $_.Type -notin @("Reserved", "System", "Recovery") -and
            (($_ | Get-Disk -ErrorAction SilentlyContinue) -ne $null)
        } |
        Where-Object {
            $candidateDisk = $_ | Get-Disk -ErrorAction SilentlyContinue
            $candidateDisk -and -not $candidateDisk.IsBoot -and -not $candidateDisk.IsSystem
        }
)

if ($partitions.Count -ne 1) {
    Write-Step "D:로 지정 가능한 비시스템 파티션 후보 수: $($partitions.Count). 후보가 1개가 아니므로 중단합니다."
    Write-Audit "manual.disk.mount_blocked" $false @{ reason = "candidate_count_not_one"; count = $partitions.Count; target_drive = $TargetDrive }
    exit 8
}

$partition = $partitions[0]
$diskForPartition = $partition | Get-Disk -ErrorAction Stop

if ($diskForPartition.IsBoot -or $diskForPartition.IsSystem) {
    Write-Step "부팅/시스템 디스크는 보호 대상이므로 작업하지 않습니다."
    Write-Audit "manual.disk.mount_blocked" $false @{ reason = "system_disk_protected"; disk = $diskForPartition.Number; target_drive = $TargetDrive }
    exit 9
}

Write-Step "파티션을 $driveRoot 로 연결합니다. Disk #$($partition.DiskNumber), Partition #$($partition.PartitionNumber)"
Add-PartitionAccessPath -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -AccessPath $driveRoot -ErrorAction Stop
Start-Sleep -Seconds 2

$mountedVolume = Get-Volume -DriveLetter $TargetDrive -ErrorAction Stop
Write-Step "$driveRoot 온라인/마운트 완료 - Label=$($mountedVolume.FileSystemLabel), FS=$($mountedVolume.FileSystem), Health=$($mountedVolume.HealthStatus)"
Write-Audit "manual.disk.mount_completed" $true @{
    target_drive = $TargetDrive
    disk = $partition.DiskNumber
    partition = $partition.PartitionNumber
    file_system = [string]$mountedVolume.FileSystem
    label = [string]$mountedVolume.FileSystemLabel
}
