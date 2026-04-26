import math
import threading
import time
from datetime import datetime

from flask import current_app

from src.entity.detect.general_log import create_general_log
from src.entity.detect.network_card_performance_log import NetworkCardPerformanceLog, \
    create_network_card_performance_log
from src.entity.detect.performance_excess_event import create_performance_excess_event
from src.entity.detect.performance_log import create_performance_log
from src.module.hw_performance_util import get_current_cpu_usage, get_total_disk_usage, get_current_memory_usage
from src.module.logging_util import gaya_log
from src.worker.NetworkRealtime import NetworkMonitorThread
from src.worker.NetworkSummary import NetworkUsageSummaryThread


class PerformanceLogWorker(threading.Thread):
    def __init__(self, interval=600, cpu_threshold=80, mem_threshold=80, disk_threshold=80, network_threshold=80, app=None):

        """
        성능 로그를 기록하는 Worker 초기화
        :param interval: 작업 주기 (초 단위, 기본값: 600초 = 10분)
        :param cpu_threshold: CPU 사용률 임계값 (기본값: 80%)
        :param mem_threshold: 메모리 사용률 임계값 (기본값: 80%)
        :param disk_threshold: 디스크 사용률 임계값 (기본값: 80%)
        """

        super().__init__()
        self.interval = interval
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.disk_threshold = disk_threshold
        self.network_threshold = network_threshold

        self.network_worker:NetworkMonitorThread = app.config.get("network_worker")
        self.network_summary:NetworkUsageSummaryThread = app.config.get("summary_worker") # 네트워크 요약 ( 5분 동안의 )

        self.running = False
        self.app = app  # Flask 애플리케이션 객체 저장
        gaya_log("PerformanceLogWorker initialized.")

    def run(self):
        """
        스레드 실행 메서드: 주기적으로 성능 로그를 기록
        """
        self.running = True
        while self.running:
            try:
                self.record_performance_log()
            except Exception as e:
                gaya_log(f"[Worker Error] Error during performance logging: {e}")
            time.sleep(self.interval)

    def stop(self):
        """
        Worker 중단
        """
        self.running = False
        gaya_log("PerformanceLogWorker stopped.")

    def record_performance_log(self):
        """
        현재 성능 데이터를 수집하고 데이터베이스에 기록
        """
        with self.app.app_context():
            # 데이터 수집
            try:

                cpu_usage = get_current_cpu_usage()
                mem_usage = get_current_memory_usage()
                disk_usage = get_total_disk_usage()

                total_network_usage_summary = self.network_summary.get_network_summary()

                total_rx = total_network_usage_summary['overall']['Weighted Avg RX (%)']
                total_tx = total_network_usage_summary['overall']['Weighted Avg TX (%)']

                # 메모리 및 디스크 사용량 계산
                mem_percent = (mem_usage["used_gb"] / mem_usage["total_gb"]) * 100
                disk_percent = (disk_usage["used_gb"] / disk_usage["total_gb"]) * 100

                gaya_log(f"Performance logged: CPU={cpu_usage}%, MEM={mem_percent}%, DISK={disk_percent}% NIC-RX{total_rx}% NIC-TX{total_tx}%")

                # 로그 기록
                create_performance_log(
                    round(cpu_usage, 1),
                    round(mem_percent, 1),
                    round(disk_percent, 1),
                    math.ceil(total_rx * 10) / 10,
                    math.ceil(total_tx * 10) / 10
                )


                # 임계값 초과 확인 및 이벤트 트리거
                self.check_thresholds_and_log("CPU", cpu_usage, self.cpu_threshold)
                self.check_thresholds_and_log("MEMORY", mem_percent, self.mem_threshold)
                self.check_thresholds_and_log("DISK", disk_percent, self.disk_threshold)
                self.check_thresholds_and_log("NIC-RX", total_rx, self.network_threshold)
                self.check_thresholds_and_log("NIC-TX", total_tx, self.network_threshold)

                #NIC 카드 저장
                nic_data = self.network_summary.get_nic_performance_data()
                for nic, data in nic_data.items():
                    create_network_card_performance_log(
                        nic_name=nic,
                        rx_actual_value=data["rx_kbps"],
                        tx_actual_value=data["tx_kbps"],
                        bandwidth_kb=data["bandwidth_kb"]
                    )

            except Exception as e:
                create_general_log(f"성능 기록 중 문제 발생 : {str(e)}")
                gaya_log(f"[Worker Error] Error during performance logging: {e}")


    def check_thresholds_and_log(self, hardware_type, actual_value, threshold):
        """
        하드웨어 사용량이 임계값을 초과했는지 확인하고 로그 및 이벤트 생성
        :param hardware_type: 하드웨어 유형 (예: 'CPU', 'MEMORY', 'DISK')
        :param actual_value: 실제 사용량 (백분율 또는 GB)
        :param threshold: 임계값
        """
        if actual_value > threshold:
            gaya_log(f"[HW Exceed] {hardware_type} usage {actual_value}% exceeded the threshold of {threshold}%")
            create_performance_excess_event(hardware_type, threshold, actual_value)