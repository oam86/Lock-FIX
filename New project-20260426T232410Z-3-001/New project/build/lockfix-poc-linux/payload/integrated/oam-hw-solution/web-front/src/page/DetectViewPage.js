import React, {useState, useEffect} from 'react';
import axios from 'axios';
import LogViewCard from "../component/detect/LogViewCard";
import LogViewTable from "../component/detect/LogViewTable";
import GayaDatePicker from "../component/common/GayaDatePicker";
import "../css/Global.css";


const DetectView = (props) => {
    const [startDate, setStartDate] = useState(new Date()); // 시작 날짜
    const [endDate, setEndDate] = useState(new Date()); // 종료 날짜
    const [detectData, setDetectData] = useState([]); // 하드웨어 변경 이벤트
    const [warningData, setWarningData] = useState([]); // 성능 초과 이벤트
    const [logsData, setLogsData] = useState([]); // 일반 로그
    const [loading, setLoading] = useState(false); // 로딩 상태 추가

    // Axios 인스턴스 생성
    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true
    });

    // 데이터 가져오기
    useEffect(() => {
        const fetchLogs = async () => {
            setLoading(true); // 로딩 시작
            const start = new Date(Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()))
                .toISOString()
                .split("T")[0];
            const end = new Date(Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()))
                .toISOString()
                .split("T")[0];

            try {
                const [detectResponse, warningResponse, logsResponse] = await Promise.all([
                    api.get('/detect/hardware_change_events', {params: {start_date: start, end_date: end}}),
                    api.get('/detect/performance_excess_events', {params: {start_date: start, end_date: end}}),
                    api.get('/detect/general_logs', {params: {start_date: start, end_date: end}})
                ]);

                setDetectData(detectResponse.data);
                setWarningData(warningResponse.data);
                setLogsData(logsResponse.data);
            } catch (error) {
                console.error('Error fetching logs:', error);
            } finally {
                setLoading(false); // 로딩 종료
            }
        };

        fetchLogs();
    }, [startDate, endDate]); // 날짜 변경 시 fetchLogs 실행

    return (
        <div className={props.singlePage ? 'component-animation' : ''}
             style={props.singlePage ? {marginTop: '7%'} : {}}>
            {/* 날짜 선택기 */}
            {props.singlePage && (
                <div className="flex justify-end mb-4">
                    <GayaDatePicker
                        startDate={startDate}
                        setStartDate={setStartDate}
                        endDate={endDate}
                        setEndDate={setEndDate}
                    />
                </div>
            )}

            {/* 로딩 표시 */}
            {loading ? (
                <div className="text-center mt-4">
                    <p>데이터를 불러오는 중입니다...</p>
                </div>
            ) : (
                <>
                    {/* 카드 뷰 */}
                    {/*<div className="flex justify-content-between space-x-16">*/}
                    <div className="grid grid-cols-3 gap-10">
                        <LogViewCard title="Detect" content="하드웨어의 변경(추가,제거)" badgeText={detectData.length}/>
                        <LogViewCard title="Warning" content="하드웨어의 초과 사용률" badgeText={warningData.length}/>
                        <LogViewCard title="Logs" content="이외의 서버 로그" badgeText={logsData.length}/>
                    </div>

                    {/* 테이블 뷰 */}
                    {props.singlePage && (
                        <div className="grid grid-cols-3 gap-10 p-2 mt-3 ">
                            <LogViewTable
                                title="Detect"
                                data={detectData.map(log => ({
                                    date: log.date,
                                    event: (
                                        <>
                                          <span style={{
                                              color: log.change_type === 'ADD'
                                                  ? 'blue'  // 파란색
                                                  : log.change_type === 'DELETE'
                                                      ? 'red'  // 빨간색
                                                      : 'black'  // 검정색
                                          }}>
                                            [{log.change_type}]  </span> <span>
                                   ({log.hardware_type}) : {log.changed_model}
                                        </span>
                                        </>
                                    )
                                }))}
                            />
                            <LogViewTable
                                title="Warning"
                                data={warningData.map(log => ({
                                    date: log.date,
                                    event: `[${log.hardware_type}] ${log.actual_value}% (임계:${log.threshold}%)`
                                }))}
                            />
                            <LogViewTable
                                title="Logs"
                                data={logsData.map(log => ({
                                    date: log.date,
                                    event: log.log_content // API에서 log_content 필드를 사용
                                }))}
                            />
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default DetectView;