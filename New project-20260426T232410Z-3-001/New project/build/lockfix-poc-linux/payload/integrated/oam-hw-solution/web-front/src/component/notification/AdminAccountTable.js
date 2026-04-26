import React from 'react';

const AdminAccountTable = ({ title, data }) => {
  return (
    <div className="mt-[5px] mb-[5px] mx-[5px] flex-1 w-full bg-white rounded-lg shadow-md overflow-hidden"> {/* 상하 마진 5px */}
      {/* 제목 */}
      <h2 className="font-semibold p-4 text-2xl text-left bg-gray-100">{title}</h2> {/* 제목 회색 배경과 가운데 정렬 */}

      <table className="min-w-full border-collapse text-center">
        <thead>
        <tr>
          <th className="px-4 py-2 border border-gray-300 text-md font-medium text-gray-700">Email</th>
          <th className="px-4 py-2 border border-gray-300 text-md font-medium text-gray-700">SMTP Status</th>
          <th className="px-4 py-2 border border-gray-300 text-md font-medium text-gray-700">Network Connection</th>
          <th className="px-4 py-2 border border-gray-300 text-md font-medium text-gray-700">Last Login</th>
        </tr>
        </thead>
        <tbody>
        {data.length > 0 ? (
            data.map((row, index) => (
                <tr
                    key={index}
                    className={`hover:bg-gray-100 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}
                >
                  <td className="px-4 py-2 border border-gray-300 text-sm text-gray-800">
                    <a
                        href={`mailto:${row.email}`}
                        className="text-blue-500 hover:underline"
                  >
                    {row.email}
                  </a>
                </td>
                <td
                  className={`px-4 py-2 border border-gray-300 text-sm font-semibold ${
                    row.smtpStatus ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {row.smtpStatus ? 'Connected' : 'Disconnected'}
                </td>
                <td
                  className={`px-4 py-2 border border-gray-300 text-sm font-semibold ${
                    row.networkConnection ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {row.networkConnection ? 'GOOD' : 'NOT Connection'}
                </td>
                <td className="px-4 py-2 border border-gray-300 text-sm text-gray-800">
                  {row.lastLogin ? (
                    <span className="text-green-600">{row.lastLogin}</span>
                  ) : (
                    <span className="text-red-600">Never</span>
                  )}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td
                colSpan="4"
                className="px-4 py-4 border border-gray-300 text-sm text-gray-500"
              >
                데이터 로딩 중입니다..
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AdminAccountTable;

