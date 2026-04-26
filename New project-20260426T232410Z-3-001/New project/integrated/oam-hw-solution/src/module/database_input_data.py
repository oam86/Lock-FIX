import random
from datetime import datetime, timedelta

from src.database.database_manager import db
from src.entity.detect.general_log import GeneralLog
from src.entity.detect.hardware_change_event import HardwareChangeEvent
from src.entity.detect.performance_excess_event import PerformanceExcessEvent
from src.entity.detect.performance_log import PerformanceLog
from src.entity.license_info import create_license_info


def populate_general_logs():
    # 오늘 날짜 기준
    today = datetime.now()
    # 3개월 전 날짜 계산
    three_months_ago = today - timedelta(days=90)

    # 380개의 로그 생성
    for _ in range(380):
        # 무작위 날짜 생성 (3개월 전부터 오늘 전날까지)
        random_date = three_months_ago + timedelta(days=random.randint(0, 89))

        # 로그 내용 생성
        log_content = f"Log created on {random_date.strftime('%Y-%m-%d %H:%M:%S')}"

        # GeneralLog 인스턴스 생성 및 추가
        log = GeneralLog(date=random_date, log_content=log_content)
        db.session.add(log)

    # 데이터베이스 커밋
    db.session.commit()
    print("380개의 로그가 성공적으로 생성되었습니다.")


def populate_hardware_change_events():
    # 가능한 하드웨어 타입과 변경 타입
    hardware_types = ['CPU', 'MEMORY', 'DISK', 'HBA', 'NIC', 'SAS_CARD']
    change_types = ['ADD', 'DELETE']

    # 가능한 모델 이름과 시리얼 번호 목록 (무작위 생성용)
    models = [f"Model-{i}" for i in range(1, 21)]
    serial_numbers = [f"SN-{random.randint(1000, 9999)}" for _ in range(20)]

    # 오늘 기준 3개월 이내 날짜 범위
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)

    # 52개의 로그 생성
    for _ in range(52):
        random_date = three_months_ago + timedelta(days=random.randint(0, 89))  # 무작위 날짜
        random_model = random.choice(models)  # 무작위 모델
        random_serial = random.choice(serial_numbers)  # 무작위 시리얼 번호
        random_hardware_type = random.choice(hardware_types)  # 무작위 하드웨어 타입
        random_change_type = random.choice(change_types)  # 무작위 변경 타입

        # HardwareChangeEvent 인스턴스 생성 및 추가
        event = HardwareChangeEvent(
            date=random_date,
            changed_model=random_model,
            changed_serial_number=random_serial,
            hardware_type=random_hardware_type,
            change_type=random_change_type
        )
        db.session.add(event)

    # 데이터베이스 커밋
    db.session.commit()
    print("52개의 하드웨어 변경 이벤트가 성공적으로 생성되었습니다.")


def populate_performance_excess_events():
    # 가능한 하드웨어 타입
    hardware_types = ['CPU', 'MEMORY', 'DISK', 'HBA', 'NIC', 'SAS_CARD']

    # 오늘 기준 3개월 이내 날짜 범위
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)

    # 72개의 로그 생성
    for _ in range(72):
        random_date = three_months_ago + timedelta(days=random.randint(0, 89))  # 무작위 날짜
        random_hardware_type = random.choice(hardware_types)  # 무작위 하드웨어 타입
        random_threshold = round(random.uniform(70, 90), 2)  # 70~90 사이의 무작위 임계값
        random_actual_value = round(random.uniform(91, 110), 2)  # 91~110 사이의 무작위 실제 값

        # PerformanceExcessEvent 인스턴스 생성 및 추가
        event = PerformanceExcessEvent(
            date=random_date,
            hardware_type=random_hardware_type,
            threshold=random_threshold,
            actual_value=random_actual_value
        )
        db.session.add(event)

    # 데이터베이스 커밋
    db.session.commit()
    print("72개의 성능 초과 이벤트가 성공적으로 생성되었습니다.")

def create_license():
    # 라이선스 생성 예제
    create_license_info(
        license_key="ABC123XYZ",
        customer_name="Oam Company",
        expiry_date=None,
        renewal_date=None,
        start_date=None
    )
    print("License created successfully!")
    pass


def populate_performance_logs():
    today = datetime.now()
    start_date = today - timedelta(days=90)

    logs_per_day = 144  # 하루에 144개의 로그 (10분 간격)
    interval_minutes = 10  # 10분 간격

    # 초기값 설정 (첫날 0시 기준)
    previous_cpu_usage = random.uniform(5, 30)  # 5% ~ 30% 범위로 시작
    previous_mem_usage_gb = random.uniform(1, 8)  # 1GB ~ 8GB 범위로 시작
    previous_disk_usage_gb = random.uniform(10, 50)  # 10GB ~ 50GB 범위로 시작

    for day in range(90):
        day_start_time = start_date + timedelta(days=day)

        for log_index in range(logs_per_day):
            log_time = day_start_time + timedelta(minutes=log_index * interval_minutes)

            # CPU, Memory, Disk 사용량을 이전 값에서 점진적으로 변경
            cpu_usage = round(previous_cpu_usage + random.uniform(-3, 3), 2)
            cpu_usage = max(5, min(95, cpu_usage))  # 5% ~ 95%로 제한

            mem_usage_gb = round(previous_mem_usage_gb + random.uniform(-0.5, 0.5), 2)
            mem_usage_gb = max(1, min(32, mem_usage_gb))  # 1GB ~ 32GB로 제한

            disk_usage_gb = round(previous_disk_usage_gb + random.uniform(-1, 1), 2)
            disk_usage_gb = max(10, min(500, disk_usage_gb))  # 10GB ~ 500GB로 제한

            # PerformanceLog 인스턴스 생성 및 추가
            log = PerformanceLog(
                date=log_time,
                cpu_usage=cpu_usage,
                mem_usage_gb=mem_usage_gb,
                disk_usage_gb=disk_usage_gb
            )
            db.session.add(log)

            # 이전 값 업데이트
            previous_cpu_usage = cpu_usage
            previous_mem_usage_gb = mem_usage_gb
            previous_disk_usage_gb = disk_usage_gb

        # 하루 단위로 커밋
        db.session.commit()
        print(f"{day + 1}/90일 로그가 생성되었습니다.")

    print("총 12,960개의 로그가 성공적으로 생성되었습니다.")  # 144 * 90 = 12,960