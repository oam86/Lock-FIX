import psutil
import threading
import time
from src.module.config_option import get_network_bandwidth  # 네트워크 카드별 대역폭 가져오기
from src.module.logging_util import gaya_log
from src.network.network_util import get_active_network_interfaces


class NetworkMonitorThread(threading.Thread):
    """
    1초 간격으로 네트워크 사용량을 모니터링하고 %, kb/s 값을 반환하는 스레드
    """

    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.running = True
        self.network_usage = {}

    def get_network_usage(self):
        """ 현재 네트워크 사용량을 반환하는 함수 (전체 NIC 데이터) """
        return self.network_usage

    def get_total_inbound_usage(self):
        """
        전체 네트워크의 인바운드(%) 사용량을 가중 평균 방식으로 계산
        """
        if not self.network_usage:
            return {"message": "No network data available"}

        total_rx_usage = 0
        total_bandwidth = 0
        total_rx_value = 0

        for data in self.network_usage.values():
            rx_usage = data["RX (%)"]
            max_bandwidth = data["Max Bandwidth (kb/s)"]
            rx_value = data["RX (kb/s)"]


            # 유효한 데이터만 사용
            if max_bandwidth > 0 and rx_usage > 0:
                total_rx_usage += rx_usage * max_bandwidth
                total_bandwidth += max_bandwidth
                total_rx_value += rx_value

        return {
            "rx_usage": (total_rx_usage / total_bandwidth) if total_bandwidth > 0 else 0,
            "total_bandwidth_kb": total_bandwidth,
            "total_rx_value_kb": total_rx_value,
        }

    def run(self):
        while self.running:
            net_io_before = psutil.net_io_counters(pernic=True)
            time.sleep(self.interval)
            net_io_after = psutil.net_io_counters(pernic=True)

            usage_data = {}
            # gaya_log("=" * 40)

            active_nics = get_active_network_interfaces()
            for nic in active_nics:
                before_stats = net_io_before.get(nic)
                after_stats = net_io_after.get(nic)
                if not before_stats or not after_stats:
                    continue

                max_bandwidth_kbps = get_network_bandwidth(nic)

                tx_bytes = after_stats.bytes_sent - before_stats.bytes_sent
                rx_bytes = after_stats.bytes_recv - before_stats.bytes_recv

                # 데이터 오류 방지 (음수 값 제거)
                tx_bytes = max(tx_bytes, 0)
                rx_bytes = max(rx_bytes, 0)

                tx_kbps = (tx_bytes * 8) / 1024  # kb/s 단위 변환
                rx_kbps = (rx_bytes * 8) / 1024

                # 사용률 % 계산 (대역폭 대비)
                tx_usage = (tx_kbps / max_bandwidth_kbps) * 100
                rx_usage = (rx_kbps / max_bandwidth_kbps) * 100

                usage_data[nic] = {
                    "TX (kb/s)": tx_kbps,
                    "RX (kb/s)": rx_kbps,
                    "TX (%)": tx_usage,
                    "RX (%)": rx_usage,
                    "Max Bandwidth (kb/s)": max_bandwidth_kbps
                }

                # if tx_kbps > 0 or rx_kbps > 0:
                    # gaya_log(f'[{nic}] sent : {tx_kbps}kb recv : {rx_kbps}kb')


            self.network_usage = usage_data

            total_inbound = self.get_total_inbound_usage()["rx_usage"]
            # gaya_log(f"🔹 전체 네트워크 인바운드 사용량: {total_inbound:.3f}%")
