import psutil
from datetime import datetime

def get_current_cpu_usage():
    """
    현재 CPU 사용률 반환
    :return: CPU 사용률 (float)
    """
    return psutil.cpu_percent(interval=1)


def get_current_memory_usage():
    """
    현재 메모리 상태 반환
    :return: dict (현재 사용량, 전체 용량)
    """
    mem = psutil.virtual_memory()
    mem_used_gb = round((mem.total - mem.available) / (1024**3), 2)  # 실제 사용량
    mem_total_gb = round(mem.total / (1024**3), 2)  # 전체 용량
    return {"used_gb": mem_used_gb, "total_gb": mem_total_gb}

def get_total_disk_usage():
    """
    전체 마운트 포인트의 디스크 사용량을 합산
    :return: dict (전체 사용량, 전체 용량)
    """
    total_used = 0
    total_size = 0

    for partition in psutil.disk_partitions(all=True):  # 모든 마운트 포인트 확인
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            # print(f"Partition: {partition.device}, Mountpoint: {partition.mountpoint}")
            # print(f"Used: {round(usage.used / (1024 ** 3), 2)} GB, Total: {round(usage.total / (1024 ** 3), 2)} GB")

            total_used += usage.used
            total_size += usage.total
        except PermissionError:
            # 접근 권한 문제로 일부 마운트 포인트는 제외
            print(f"Permission denied for {partition.device}")
            continue

    return {
        "used_gb": round(total_used / (1024 ** 3), 2),
        "total_gb": round(total_size / (1024 ** 3), 2)
    }
