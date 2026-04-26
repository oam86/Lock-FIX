import React, { useEffect, useState } from 'react';
import LicenseTable from "../component/license/LicenseTable";
import axios from "axios";

const LicensePage = (props) => {
  const [loading, setLoading] = useState(true); // 로딩 상태
  const [data, setData] = useState(null); // 라이선스 데이터
  const [error, setError] = useState(null); // 에러 상태

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true
    });

  useEffect(() => {
    const fetchLicenseData = async () => {
      try {
        const response = await api.get('/license_info'); // Flask API 엔드포인트
        setData(response.data); // 첫 번째 라이선스 데이터 가져오기
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false); // 로딩 상태 종료
      }
    };

    fetchLicenseData();
  }, []);

  // 로딩 상태 처리
  if (loading) {
    return <div className="text-center mt-4">Loading...</div>;
  }

  // 에러 상태 처리
  if (error) {
    return <div className="text-center mt-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="component-animation" style={{ marginTop: '7%' }}>
      <LicenseTable data={data || {}} /> {/* 데이터를 LicenseTable로 전달 */}
    </div>
  );
};

export default LicensePage;