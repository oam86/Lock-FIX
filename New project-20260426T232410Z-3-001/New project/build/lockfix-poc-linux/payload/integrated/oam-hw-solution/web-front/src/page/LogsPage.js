import React, { useState, useEffect } from 'react';
import axios from 'axios';
import GayaDatePicker from "../component/common/GayaDatePicker";
import AllLogTable from "../component/log/AllLogTable";



function LogsPage(props) {
  const [startDate, setStartDate] = useState(new Date()); // 시작 날짜
  const [endDate, setEndDate] = useState(new Date()); // 종료 날짜
  const [logsData, setLogsData] = useState([]); // 전체 로그 데이터
  const [loading, setLoading] = useState(false); // 로딩 상태 추가

  const api = axios.create({
    baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
    withCredentials: true,
  });

  // 날짜 범위로 데이터 가져오기
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
        const response = await api.get('/detect/all_logs', { params: { start_date: start, end_date: end } });
        setLogsData(response.data || []); // 데이터 설정, 빈 배열로 초기화 방지
      } catch (error) {
        console.error("Error fetching logs:", error);
        setLogsData([]); // 에러 발생 시 빈 배열로 초기화
      } finally {
        setLoading(false); // 로딩 종료
      }
    };

    fetchLogs();
  }, [startDate, endDate]); // 날짜 변경 시 fetchLogs 실행

  const handleLogsDownload = async () => {
        try {
            // Flask 서버에 POST 요청
            const start = new Date(Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()))
                .toISOString()
                .split("T")[0];
            const end = new Date(Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()))
                .toISOString()
                .split("T")[0];

            const response = await api.post(
                "/to_excel",
                {
                    start_date: start,
                    end_date: end
                },
                {
                    responseType: "blob", // 서버에서 바이너리 데이터를 받음
                }
            );

            // Blob 객체 생성
            const blob = new Blob([response.data], {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            });

            // Blob URL 생성
            const url = window.URL.createObjectURL(blob);

            // 링크를 생성하고 다운로드 트리거
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", `[${start} ~ ${end}] 전체_로그.xlsx`);
            document.body.appendChild(link);
            link.click();

            // 메모리 정리
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error("엑셀 파일 다운로드 실패:", error);
            alert(error)
        }
    };


  // singlePage일 경우 데이터 제한
  const displayedLogs = props.singlePage ? logsData : logsData.slice(0, 5);

  return (
    <div className={props.singlePage ? 'component-animation' : ''} style={props.singlePage ? { marginTop: '4%' } : {}}>
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
        <AllLogTable
          title="Logs"
          data={displayedLogs.map(log => ({
            type: log.type, // Type 추가
            date: new Date(log.date).toISOString().slice(0, 19).replace('T', ' '), // 날짜와 시간 변환
            content: log.content,
          }))}
          onDownloadLogs={handleLogsDownload} // 다운로드 함수 전달
        />
      )}
    </div>
  );
}

export default LogsPage;