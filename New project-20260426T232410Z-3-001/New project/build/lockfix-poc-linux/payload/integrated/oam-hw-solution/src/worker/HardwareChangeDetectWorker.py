import threading
import time
from datetime import datetime
from collections import defaultdict

import requests

from src.module.config_option import OAM_DATA_CENTER_API_URL
from src.entity.detect.general_log import create_general_log
from src.entity.detect.hardware_change_event import create_hardware_change_event
from src.entity.init_hardware_info import InitHardwareInfo
from src.entity.license_info import LicenseInfo
from src.module.hw_info import get_all_hardware_info
from src.module.logging_util import gaya_log


class HardwareChangeDetectWorker(threading.Thread):
    def __init__(self, interval=600, app=None):
        """
        하드웨어 감지 Worker 초기화
        :param interval: 작업 주기 (초 단위, 기본값: 600초 = 10분)
        :param app: Flask 애플리케이션 객체
        """
        super().__init__()
        self.interval = interval
        self.running = False
        self.app = app  # Flask 애플리케이션 객체 저장
        gaya_log(f'Start Worker')

    def run(self):
        """
        스레드 실행 메서드: 주기적으로 하드웨어 감지 작업을 수행
        """
        self.running = True
        while self.running:
            try:
                self.detect_hardware_changes()
            except Exception as e:
                gaya_log(f"[Worker] Error during hardware detection: {str(e)}", level="error")

            time.sleep(self.interval)

    def stop(self):
        """
        Worker 중단
        """
        self.running = False

    def detect_hardware_changes(self):
        """
        하드웨어 변경 감지 및 처리
        """
        gaya_log(f"[Worker] Detecting hardware changes at {datetime.now()}")
        # Flask 애플리케이션 컨텍스트를 활용
        with self.app.app_context():
            try :
                existing_hardware_data = self.get_existing_hardware_data()

                if existing_hardware_data:
                    new_hardware_data = get_all_hardware_info()

                    # 기존 하드웨어 데이터 출력
                    gaya_log(f"[Worker] Existing hardware data (from DB):")
                    for hw in existing_hardware_data:
                        gaya_log(f"Type: {hw.hardware_type}, Model: {hw.model_name}, Serial: {hw.serial_number}")
                    #
                    # # 새로운 하드웨어 데이터 출력
                    gaya_log(f"[Worker] New hardware data (collected from system) : {new_hardware_data}")
                    # for hw in new_hardware_data:
                    #     gaya_log(f"Type: {hw.get('Type')}, Model: {hw.get('Model')}, Serial: {hw.get('Serial')}")

                    # 변경 사항 처리
                    self.process_hardware_changes(existing_hardware_data, new_hardware_data)
                else:
                    gaya_log(f"[Worker] No existing hardware data HW 감지 이벤트를 발생시키지 않습니다")

            except Exception as e:
                create_general_log(f"하드웨어 감지 스레드 오류 발생 : {str(e)}")



    @staticmethod
    def get_existing_hardware_data():
        """
        데이터베이스에서 기존 하드웨어 정보 로드
        :return: InitHardwareInfo 객체 리스트
        """
        return InitHardwareInfo.query.all()

    @staticmethod
    def process_hardware_changes(existing_data, new_data):
        """
        하드웨어 변경 사항을 타입별로 처리하고, 반환값이 있는 데이터만 POST 요청으로 전송.
        """
        # 기존 데이터와 새로운 데이터를 타입별로 그룹화
        existing_grouped = defaultdict(set)
        for hw in existing_data:
            existing_grouped[hw.hardware_type].add((hw.model_name, hw.serial_number))

        new_grouped = defaultdict(set)
        for hw in new_data:
            new_grouped[hw['Type']].add((hw['Model'], hw['Serial']))

        # 수집된 이벤트
        collected_events = []

        # 타입별로 비교
        for hardware_type in set(existing_grouped.keys()).union(new_grouped.keys()):
            existing_set = existing_grouped.get(hardware_type, set())
            new_set = new_grouped.get(hardware_type, set())

            # 추가 및 삭제된 하드웨어 항목 식별
            added = new_set - existing_set
            deleted = existing_set - new_set

            # 추가된 하드웨어 처리
            for hw in added:
                gaya_log(f"[Worker] Adding hardware: Type={hardware_type}, Model={hw[0]}, Serial={hw[1]}")
                event = create_hardware_change_event(
                    changed_model=hw[0],
                    changed_serial_number=hw[1],
                    hardware_type=hardware_type,
                    change_type='ADD'
                )
                if event:  # 반환값이 있는 경우 리스트에 추가
                    collected_events.append(event)

            # 삭제된 하드웨어 처리
            for hw in deleted:
                gaya_log(f"[Worker] Deleting hardware: Type={hardware_type}, Model={hw[0]}, Serial={hw[1]}")
                event = create_hardware_change_event(
                    changed_model=hw[0],
                    changed_serial_number=hw[1],
                    hardware_type=hardware_type,
                    change_type='DELETE'
                )
                if event:  # 반환값이 있는 경우 리스트에 추가
                    collected_events.append(event)

        # JSON 직렬화 가능한 형태로 변환
        collected_events_dicts = [event.to_dict() for event in collected_events]

        # 수집된 데이터가 있는 경우 백엔드로 전송
        if collected_events_dicts:
            try:
                gaya_log("[Worker] Sending notification to backend...")
                url = f"{OAM_DATA_CENTER_API_URL}/java_api/external/notify/event"  # 백엔드 URL

                license_info = LicenseInfo.query.first()

                payload = {"events": collected_events_dicts, "support_code": license_info.license_key}
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()  # 오류 발생 시 예외 처리
                gaya_log(f'Payload : {payload}')
                gaya_log(f"[Worker] Notification sent successfully: {response.status_code}")
                create_general_log(f"H/W 변경 감지 메일 요청")

            except requests.exceptions.RequestException as e:
                gaya_log(f"[Worker] Failed to send notification: {str(e)}", level="error")
                create_general_log(f"변경 감지 메일 요청 하는데에 문제가 발생했습니다 : {str(e)}")
