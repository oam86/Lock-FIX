import React, { useState, useEffect } from "react";
import axios from "axios";
import NetworkGraph from "../component/network/NetworkGraph";
import {WifiIcon} from "@heroicons/react/16/solid";
import GayaDatePicker from "../component/common/GayaDatePicker";

const api = axios.create({
    baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
    withCredentials: true
});

function NetworkStatusPage() {
    const [networkData, setNetworkData] = useState({});  // 전체 네트워크 카드 데이터
    const [selectedCard, setSelectedCard] = useState(null);  // 선택된 네트워크 카드
    const [graphData, setGraphData] = useState([]); // 그래프 데이터
    const [loading, setLoading] = useState(true); // 로딩 상태

    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());

    // 1️⃣ 네트워크 카드 리스트 가져오기
    useEffect(() => {
        const fetchNetworkCards = async () => {
            try {
                const response = await api.get("/network/realtime");
                const data = response.data;

                setNetworkData(data);

                // 첫 번째 네트워크 카드 자동 선택 (한 번만 실행)
                if (!selectedCard && Object.keys(data).length > 0) {
                    setSelectedCard(Object.keys(data)[0]);
                }
            } catch (error) {
                console.error("Error fetching network cards:", error);
            }
        };

        fetchNetworkCards();
        const interval = setInterval(fetchNetworkCards, 2000); // 2초마다 데이터 갱신
        return () => clearInterval(interval);
    }, [selectedCard]); // ⚡ `selectedCard`를 의존성 배열에서 제거하여 초기 렌더링 시 한 번만 실행

    // 2️⃣ 선택된 네트워크 카드의 트래픽 데이터 가져오기
    useEffect(() => {
        if (!selectedCard) return;

        const fetchTrafficData = async () => {
            try {

                const start = new Date(Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()))
                  .toISOString()
                  .split("T")[0];
                const end = new Date(Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()))
                  .toISOString()
                  .split("T")[0];

                const response = await api.get(`/network/card/${selectedCard}`, { params: { start_date: start, end_date: end } });
                const logs = response.data;

                if (!logs || logs.length === 0) {
                    setGraphData([]);
                    return;
                }

                const duration_seconds = 600; // 10분(600초)


                // 백분율 계산하여 그래프 데이터 변환
                const transformedData = [
                    {
                        name: "RX (%)",
                        data: logs.map((log) => [
                            new Date(log.date).getTime(),
                            ((log.rx_actual_value / (duration_seconds * log.bandwidth_kb)) * 100).toFixed(1)
                        ])
                    },
                    {
                        name: "TX (%)",
                        data: logs.map((log) => [
                            new Date(log.date).getTime(),
                            ((log.tx_actual_value / (duration_seconds * log.bandwidth_kb)) * 100).toFixed(1)
                        ])
                    }
                ];

                setGraphData(transformedData);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching traffic data:", error);
                setLoading(false);
            }
        };

        fetchTrafficData();
    }, [selectedCard]);

    return (
        <div className="component-animation p-4">
            <h2 className="text-lg font-bold mb-4">네트워크 상태 (10분 간격)</h2>

            <div className="flex">
                {/* 왼쪽 60%: 네트워크 트래픽 그래프 */}
                <div className="w-3/5 p-4 bg-white shadow-lg rounded-lg">
                    {loading ? (
                        <p className="text-gray-600">📊 데이터 로딩 중...</p>
                    ) : (
                        <>

                            <h3 className="text-md font-semibold mb-2">{selectedCard} - 트래픽 그래프</h3>

                                                        <GayaDatePicker
                            startDate={startDate}
                            setStartDate={setStartDate}
                            endDate={endDate}
                            setEndDate={setEndDate}
                            />

                            <NetworkGraph data={graphData} />

                        </>
                    )}
                </div>

                {/* 오른쪽 40%: 네트워크 카드 목록 및 실시간 사용량 */}
                <div className="w-2/5 p-4 bg-gray-100 shadow-lg rounded-lg">
                    <h3 className="text-md font-semibold mb-2">네트워크 카드 (실시간)</h3>

                    <div className="grid grid-cols-2 gap-3">
                        {Object.keys(networkData).map((nic) => {
                            const nicData = networkData[nic] || {};
                            return (
                                <div
                                    key={nic}
                                    className={`border p-3 rounded-lg cursor-pointer flex items-center transition duration-200 ease-in-out ${
                                        selectedCard === nic 
                                            ? "border-blue-500 bg-white shadow-xl transform scale-105"
                                            : "border-gray-300 hover:bg-gray-200"
                                    }`}
                                    onClick={() => setSelectedCard(nic)}
                                >
                                    <WifiIcon className="w-10 h-10 text-blue-500 mr-3" /> {/* Heroicons 네트워크 아이콘 */}
                                    <div>
                                        <h4 className="font-semibold text-gray-700">{nic}</h4>
                                        <p className="text-sm text-gray-600">
                                            <strong>TX:</strong> {(nicData["TX (kb/s)"] || 0).toFixed(2)} kb/s &nbsp;
                                            <strong>RX:</strong> {(nicData["RX (kb/s)"] || 0).toFixed(2)} kb/s
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default NetworkStatusPage;