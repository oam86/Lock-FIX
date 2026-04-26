import React from 'react';

const LogViewTable = ({ title, data }) => {
  return (
    <div className="mt-[5px] mb-[5px] w-full bg-white rounded-lg shadow-md overflow-hidden"> {/* 상하 마진 5px */}
            {/*<div className="mt-[5px] mb-[5px] mx-[35px] flex-1 w-full bg-white rounded-lg shadow-md overflow-hidden"> /!* 상하 마진 5px *!/*/}

      {/* 제목 */}
      <h2 className="text-lg font-semibold p-2 text-center bg-gray-100">{title}</h2> {/* 제목 회색 배경과 가운데 정렬 */}

      <table className="min-w-full border-collapse text-center">
        <thead>
          <tr>
            <th className="px-4 py-2 border-b border-gray-300 text-md font-medium text-gray-700">Date</th>
            <th className="px-4 py-2 border-b border-gray-300 text-md font-medium text-gray-700">Event</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="hover:bg-gray-100">
              <td className="px-4 py-2 border-b border-gray-300 text-sm text-gray-800">{row.date}</td>
              <td className="px-4 py-2 border-b border-gray-300 text-sm text-gray-800">{row.event}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LogViewTable;