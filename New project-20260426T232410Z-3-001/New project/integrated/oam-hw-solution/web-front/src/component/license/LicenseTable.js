import React from 'react';

const LicenseTable = ({ data }) => {
  // 오늘 날짜와 만료일 비교
  const today = new Date();
  const expiryDate = new Date(data.expiry_date);
  const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));

  // 상태 계산
  const licenseStatus = daysLeft > 30
    ? { text: '정상', color: 'text-green-600' }
    : daysLeft > 0
      ? { text: `만료 예정 (${daysLeft} Days Left)`, color: 'text-red-600' }
      : { text: '만료됨', color: 'text-red-800' };

  return (
    <div className="w-[120%] max-w-[1000px] mx-auto border border-gray-300 shadow-md rounded-md transform scale-110">
      <h2 className={`text-lg font-bold p-2 bg-blue-500 text-white flex items-center justify-between`}>
        라이선스 정보
        <span className={`text-sm bold ${licenseStatus.color}`}>
          {data.expiry_date ? licenseStatus.text : 'N/A'}
        </span>
      </h2>
      <table className="w-full border-collapse border border-gray-200">
        <tbody>
        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">고객사 정보 End-user information</td>
          <td className="px-5 py-3 text-gray-800">{data.customer_name || 'N/A'}</td>
        </tr>
        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">라이선스 키 Support Code</td>
          <td className="px-5 py-3 text-gray-800">{data.license_key || 'N/A'}</td>
        </tr>

        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">제품명</td>
          <td className="px-5 py-3 text-gray-800">Oam Hardware Detection</td>
        </tr>

        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">버젼 Version</td>
          <td className="px-5 py-3 text-gray-800">0.1</td>
        </tr>

        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">라이선스 유형 Licenses Type</td>
          <td className="px-5 py-3 text-gray-800">Subscription 1 Year</td>
        </tr>

        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">최초 사용 일자</td>
          <td className="px-5 py-3 text-gray-800">{data.start_date || '사용 전 입니다 서버로 갱신 요청을 진행해주세요'}</td>
        </tr>
        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-red-800">만료 일자</td>
          <td className="px-5 py-3 text-red-800">
            {data.expiry_date ? `${data.expiry_date} (${daysLeft > 0 ? `${daysLeft} Days Left` : '만료됨'})` : 'N/A'}
          </td>
        </tr>
        <tr className="border-b last:border-b-0 hover:bg-gray-200 transition-colors duration-200">
          <td className="px-5 py-3 font-semibold text-gray-600">갱신 일자</td>
          <td className="px-5 py-3 text-gray-800">{data.renewal_date || 'N/A'}</td>
        </tr>
        </tbody>
      </table>
    </div>
  );
};

export default LicenseTable;