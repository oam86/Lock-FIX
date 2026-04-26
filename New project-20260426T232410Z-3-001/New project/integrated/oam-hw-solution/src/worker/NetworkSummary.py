import psutil
import threading
import time
import platform
from src.module.config_option import get_network_bandwidth
from src.network.network_util import get_active_network_interfaces
from src.module.logging_util import gaya_log


class NetworkUsageSummaryThread(threading.Thread):
    """
    10초 간격으로 전체 및 개별 NIC 네트워크 사용량(%)을 요약하는 스레드 (대역폭 가중 평균 방식 적용, TX/RX 분리)
    """

    def __init__(self, interval=10):  # 기본 10초 (테스트용)
        super().__init__()
        self.interval = interval
        self.running = True
        self.time_count = 0
        self.usage_data_tx = {}  # TX 데이터를 NIC 이름 기준으로 저장
        self.usage_data_rx = {}  # RX 데이터를 NIC 이름 기준으로 저장

    def get_network_summary(self):
        """
        현재까지의 데이터를 기반으로 평균값을 반환.
        10초가 지나지 않았더라도 지금까지 측정된 값을 반영하여 반환 가능.
        """
        return self._calculate_summary()


    def get_nic_performance_data(self):
        """
        활성화된 NIC 목록을 가져와 RX, TX 속도 및 대역폭(Kbps) 데이터를 반환
        """
        nic_data = {}
        active_nics = get_active_network_interfaces()
        nic_io_counters = psutil.net_io_counters(pernic=True)

        for nic_name in active_nics:
            stats = nic_io_counters.get(nic_name)
            if not stats:
                continue

            rx_kbps = (stats.bytes_recv * 8) / 1024
            tx_kbps = (stats.bytes_sent * 8) / 1024
            bandwidth_kb = get_network_bandwidth(nic_name)

            nic_data[nic_name] = {
                "rx_kbps": rx_kbps,
                "tx_kbps": tx_kbps,
                "bandwidth_kb": bandwidth_kb
            }

        return nic_data

    def _calculate_summary(self):
        """ 현재까지 수집된 데이터 기반으로 총합을 계산하는 내부 함수 """
        summary_result = {
            "overall": {
                "Avg TX (kb/s)": 0,
                "Avg RX (kb/s)": 0,
                "Avg TX (%)": 0,
                "Avg RX (%)": 0,
                "Total TX (kb/s)": 0,
                "Total RX (kb/s)": 0,
                "Total TX Bandwidth (kb/s)": 0,
                "Total RX Bandwidth (kb/s)": 0,
            }
        }

        if not self.usage_data_tx and not self.usage_data_rx:
            return summary_result  # 아직 수집된 데이터가 없는 경우 기본값 반환

        total_tx = total_rx = total_tx_weighted = total_rx_weighted = 0
        total_tx_bandwidth = sum(get_network_bandwidth(nic) for nic in self.usage_data_tx.keys())
        total_rx_bandwidth = sum(get_network_bandwidth(nic) for nic in self.usage_data_rx.keys())
        elapsed_time = self.time_count

        for nic, tx_values in self.usage_data_tx.items():
            nic_bandwidth = get_network_bandwidth(nic)
            total_nic_tx = sum(tx_values)
            if total_nic_tx > 0:
                total_tx += total_nic_tx
                total_tx_weighted += (total_nic_tx / nic_bandwidth) * (nic_bandwidth / total_tx_bandwidth) * 100

        for nic, rx_values in self.usage_data_rx.items():
            nic_bandwidth = get_network_bandwidth(nic)
            total_nic_rx = sum(rx_values)
            if total_nic_rx > 0:
                total_rx += total_nic_rx
                total_rx_weighted += (total_nic_rx / nic_bandwidth) * (nic_bandwidth / total_rx_bandwidth) * 100

        summary_result["overall"] = {
            "Avg TX (kb/s)": total_tx / elapsed_time if elapsed_time > 0 else 0,
            "Avg RX (kb/s)": total_rx / elapsed_time if elapsed_time > 0 else 0,
            "Weighted Avg TX (%)": total_tx_weighted if total_tx > 0 else 0,
            "Weighted Avg RX (%)": total_rx_weighted if total_rx > 0 else 0,
            "Total TX (kb/s)": total_tx,
            "Total RX (kb/s)": total_rx,
            "Total TX Bandwidth (kb/s)": total_tx_bandwidth,
            "Total RX Bandwidth (kb/s)": total_rx_bandwidth,
        }

        return summary_result

    def run(self):
        while self.running:
            while self.time_count < self.interval:
                self.time_count += 1
                net_io_before = psutil.net_io_counters(pernic=True)
                time.sleep(1)  # 1초 간격 측정
                net_io_after = psutil.net_io_counters(pernic=True)

                active_nics = get_active_network_interfaces()
                for nic in active_nics:
                    before_stats = net_io_before.get(nic)
                    after_stats = net_io_after.get(nic)
                    if not before_stats or not after_stats:
                        continue

                    tx_bytes = after_stats.bytes_sent - before_stats.bytes_sent
                    rx_bytes = after_stats.bytes_recv - before_stats.bytes_recv

                    tx_bytes = max(tx_bytes, 0)
                    rx_bytes = max(rx_bytes, 0)

                    tx_kbps = (tx_bytes * 8) / 1024
                    rx_kbps = (rx_bytes * 8) / 1024

                    if tx_kbps > 0:
                        if nic not in self.usage_data_tx:
                            self.usage_data_tx[nic] = []
                        self.usage_data_tx[nic].append(tx_kbps)

                    if rx_kbps > 0:
                        if nic not in self.usage_data_rx:
                            self.usage_data_rx[nic] = []
                        self.usage_data_rx[nic].append(rx_kbps)

            summary = self._calculate_summary()

            gaya_log("=" * 50)
            gaya_log("🕐 10초 평균 네트워크 사용량 요약 완료")
            gaya_log(f"📊 전체 네트워크 평균 사용량: {summary['overall']}")
            gaya_log(f"🔹 총 송신(TX): {summary['overall']['Total TX (kb/s)']:.2f} kb/s")
            gaya_log(f"🔹 총 수신(RX): {summary['overall']['Total RX (kb/s)']:.2f} kb/s")
            gaya_log(f"🎯 가중 TX 전체 : {summary['overall']['Total TX Bandwidth (kb/s)']:.2f} / 평균 TX (%): {summary['overall']['Weighted Avg TX (%)']:.2f}%")
            gaya_log(f"🎯 가중 RX 전체 : {summary['overall']['Total RX Bandwidth (kb/s)']:.2f} / 평균 RX (%): {summary['overall']['Weighted Avg RX (%)']:.2f}%")

            self.usage_data_tx.clear()
            self.usage_data_rx.clear()
            self.time_count = 0
