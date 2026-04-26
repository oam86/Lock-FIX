import React, {useState, useEffect} from "react";
import axios from "axios";
import "../css/Global.css";
import HwGraph from "../component/monitoring/HwGraph";
import HwChart from "../component/monitoring/HwChart";
import GayaDatePicker from "../component/common/GayaDatePicker";
import {
  CpuChipIcon,
  ServerStackIcon,
  CircleStackIcon,
  ServerIcon
} from "@heroicons/react/24/outline";
const api = axios.create({
    baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
    withCredentials: true,
});

function MonitoringPage(props) {
    const [graphData, setGraphData] = useState([]);
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [currentStats, setCurrentStats] = useState({
        cpuUsage: 0,
        memUsage: {
            usedGb: 0,
            totalGb: 0,
        },
        diskUsage: {
            usedGb: 0,
            totalGb: 0,
        },
    });
    const [loading, setLoading] = useState(false); // 로딩 상태 추가

    // 날짜 범위로 데이터 가져오기
useEffect(() => {
  const fetchLogs = async () => {
    setLoading(true);
    const start = new Date(Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()))
      .toISOString()
      .split("T")[0];
    const end = new Date(Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()))
      .toISOString()
      .split("T")[0];

    try {
      const response = await api.get("/performance_logs", { params: { start_date: start, end_date: end } });
      const logs = response.data;

      if (!logs || logs.length === 0) {
        console.warn("No logs received");
        setGraphData([]);
        return;
      }

      const transformedData = [
        {
          name: "CPU 사용량",
          data: logs.map((log) => [new Date(log.date).getTime(), log.cpu_usage]),
        },
        {
          name: "Memory 사용량",
          data: logs.map((log) => [new Date(log.date).getTime(), log.mem_usage]),
        },
        {
          name: "DISK 사용량",
          data: logs.map((log) => [new Date(log.date).getTime(), log.disk_usage]),
        },
          {
          name: "Network 사용량(RX)",
          data: logs.map((log) => [new Date(log.date).getTime(), log.network_rx_usage]),
        },
      ];

      setGraphData(transformedData);
    } catch (error) {
      console.error("Error fetching performance logs:", error);
    } finally {
      setLoading(false);
    }
  };

  fetchLogs();
}, [startDate, endDate]);

    // 현재 상태 가져오기 (5초마다 갱신)
    useEffect(() => {
        const fetchCurrentStatus = async () => {
            try {
                const response = await api.get("/current_status");
                const data = response.data;
                setCurrentStats({
                    cpuUsage: data.cpu_usage,
                    memUsage: {
                        usedGb: data.mem_usage.used_gb,
                        totalGb: data.mem_usage.total_gb,
                    },
                    diskUsage: {
                        usedGb: data.disk_usage.used_gb,
                        totalGb: data.disk_usage.total_gb,
                    },

                    networkUsage: {
                        total_rx: data.network_inbound_usage.rx_usage, // 전체 퍼센트,
                        total_bandwidth_kb: data.network_inbound_usage.total_bandwidth_kb,
                        total_rx_value_kb: data.network_inbound_usage.total_rx_value_kb
                    }
                });
            } catch (error) {
                console.error("Error fetching current status:", error);
            }
        };

        fetchCurrentStatus();
        const intervalId = setInterval(fetchCurrentStatus, 5000);

        return () => clearInterval(intervalId);
    }, []);

    return (
        <div
            className={props.singlePage ? "component-animation" : ""}
            style={props.singlePage ? {marginTop: "5%", marginLeft: "5%", marginRight: "5%"} : {}}
        >


            {props.singlePage && (
                <>
                    {/* 날짜 선택기 */}
                    <div className="flex justify-end mb-4">
                        <GayaDatePicker
                            startDate={startDate}
                            setStartDate={setStartDate}
                            endDate={endDate}
                            setEndDate={setEndDate}
                        />
                    </div>
                </>

            )}


            {/* 로딩 표시 */}
            {loading ? (
                <div className="text-center mt-4">
                    <p>데이터를 불러오는 중입니다...</p>
                </div>
            ) : (
                <>
                    {/* 그래프 컴포넌트 */}
                    <HwGraph data={graphData}/>

                    {props.singlePage && (
                        <>
                            <div className="mt-5 mb-6" style={{marginTop: "2.5%"}}>
                                <h2 className="text-xl font-semibold text-center text-gray-600 border-b-2 border-gray-600 pb-2">
                                    현재 상태
                                </h2>
                            </div>

                            {/* 카드 컴포넌트 */}
                            <div className="flex justify-between p-1 gap-x-2">
                                <HwChart
                                    icon={CpuChipIcon}
                                    label="CPU 사용량"
                                    value={currentStats.cpuUsage}
                                    color="#1E90FF"
                                    tooltipText={`${currentStats.cpuUsage}% 사용`}
                                />
                                <HwChart
                                    icon={ServerStackIcon}
                                    label="메모리 사용량"
                                    value={
                                        currentStats.memUsage.totalGb > 0
                                            ? parseFloat(((currentStats.memUsage.usedGb / currentStats.memUsage.totalGb) * 100).toFixed(1))
                                            : 0
                                    }
                                    color="#28A745"
                                    tooltipText={`전체 ${currentStats.memUsage.totalGb}GB 중 ${currentStats.memUsage.usedGb}GB 사용`}
                                />
                                <HwChart
                                    icon={CircleStackIcon}
                                    label="디스크 사용량"
                                    value={
                                        currentStats.diskUsage.totalGb > 0
                                            ? parseFloat(((currentStats.diskUsage.usedGb / currentStats.diskUsage.totalGb) * 100).toFixed(1))
                                            : 0
                                    }
                                    color="#FFA500"
                                    tooltipText={`전체 ${currentStats.diskUsage.totalGb}GB 중 ${currentStats.diskUsage.usedGb}GB 사용`}
                                />

                                <HwChart
                                    icon={ServerIcon}
                                    label="Network 사용량(RX)"
                                    value={ parseFloat(currentStats.networkUsage?.total_rx).toFixed(2) ?? 0}
                                    color="RED"
                                    tooltipText={`전체 NIC ${currentStats.networkUsage?.total_bandwidth_kb/1000 ?? 0}MB 대역폭에서 ${currentStats.networkUsage?.total_rx_value_kb/1000 ?? 0}MB 사용`}
                                />

                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}

export default MonitoringPage;