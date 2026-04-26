import threading
import time
from collections import defaultdict
from datetime import datetime
import psutil

from src.entity.detect.general_log import create_general_log
from src.module.logging_util import gaya_log


class NetworkPacketCaptureWorker(threading.Thread):
    def __init__(self, interval=10, app=None):
        """
        네트워크 패킷 캡처 Worker 초기화
        :param interval: 패킷 데이터 로깅 주기 (초 단위, 기본값: 10초)
        :param app: Flask 애플리케이션 객체
        """
        super().__init__()
        self.interval = interval
        self.running = False
        self.packet_data = defaultdict(lambda: {"sent": 0, "recv": 0})
        self.app = app  # Flask 애플리케이션 객체 저장
        gaya_log("[NetworkWorker] Initialized NetworkPacketCaptureWorker")

    def run(self):
        """
        스레드 실행 메서드: 실시간 네트워크 상태를 수집하고 주기적으로 로깅.
        """
        self.running = True

        while self.running:
            try:
                self.capture_network_data()
                self.log_packet_data()
            except Exception as e:
                gaya_log(f"[NetworkWorker] Error during network data processing: {e}", level="error")

            time.sleep(self.interval)

    def stop(self):
        """
        Worker 중단
        """
        self.running = False
        gaya_log("[NetworkWorker] Stopped NetworkPacketCaptureWorker")

    def capture_network_data(self):
        """
        네트워크 연결 및 I/O 데이터 가져오기
        """
        net_io = psutil.net_io_counters(pernic=False)
        connections = psutil.net_connections(kind='inet')

        # 현재 네트워크 상태를 기반으로 데이터를 갱신
        for conn in connections:
            local_ip = conn.laddr.ip if conn.laddr else None
            remote_ip = conn.raddr.ip if conn.raddr else None

            if local_ip:
                self.packet_data[local_ip]["sent"] = net_io.bytes_sent
                self.packet_data[local_ip]["recv"] = net_io.bytes_recv

            if remote_ip:
                self.packet_data[remote_ip]["sent"] += net_io.bytes_sent
                self.packet_data[remote_ip]["recv"] += net_io.bytes_recv

    def log_packet_data(self):
        """
        주기적으로 패킷 데이터를 로깅
        """
        # gaya_log("[NetworkWorker] Logging captured packet data")
        with self.app.app_context():
            for ip, data in self.packet_data.items():
                pass
                # gaya_log(f"IP: {ip} | Sent: {data['sent']} bytes | Received: {data['recv']} bytes")

        # 데이터 초기화
        self.packet_data = defaultdict(lambda: {"sent": 0, "recv": 0})