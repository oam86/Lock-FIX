import React from 'react';
import {ArrowDownTrayIcon, ChartBarSquareIcon} from "@heroicons/react/16/solid";

const AllLogTable = ({ title, data, onDownloadLogs }) => {
  return (
      <div className="mt-[5px] mb-[5px] mx-[5px] flex-1 w-full bg-white rounded-lg shadow-md overflow-hidden">
          {/* 제목과 데이터 개수 */}

          <div className="flex items-center justify-between bg-gray-100 px-4 py-3">
              <h2 className="font-semibold text-2xl text-purple-500">{title}</h2>
              <div className="flex items-center space-x-4">
                  <span className="text-sm text-red-600">Total: {data.length} logs</span> {/* 데이터 개수 */}
                  <span
                      onClick={onDownloadLogs}
                      className="flex items-center px-3 py-1 bg-blue-500 text-white text-sm rounded cursor-pointer hover:bg-blue-600 hover:shadow-md transition-all"
                  >
              Download <ArrowDownTrayIcon className="h-5 w-5 ml-2"/>
            </span>
              </div>
          </div>

          <table className="min-w-full border-collapse text-center">
              <thead>
              <tr>
                  <th className="px-4 py-2 border border-gray-300 text-md font-medium text-purple-500">Type</th>
                  <th className="px-4 py-2 border border-gray-300 text-md font-medium text-purple-500">Date</th>
                  <th className="px-4 py-2 border border-gray-300 text-md font-medium text-purple-500">Logs</th>
              </tr>
              </thead>
              <tbody>
              {data.map((row, index) => {
                  // Type 색상 결정
                  const typeTextColor =
                      row.type === 'DETECT' ? 'text-yellow-500' :
                          row.type === 'WARNING' ? 'text-orange-500' :
                              'text-purple-500';

                  // Date 포맷: "YYYY-MM-DD HH:mm:ss"
                  const formattedDate = new Date(row.date).toISOString().slice(0, 19).replace('T', ' ');

                  return (
                      <tr key={index} className="hover:bg-gray-100">
                          <td className={`px-4 py-2 border border-gray-300 text-sm ${typeTextColor}`}
                              style={{width: '7%'}}>
                              {row.type}
                          </td>
                          <td className="px-4 py-2 border border-gray-300 text-sm text-gray-800" style={{width: '12%'}}>
                              {formattedDate}
                          </td>
                          <td className="px-4 py-2 border border-gray-300 text-sm text-gray-800">
                              {row.content}
                          </td>
                      </tr>
                  );
              })}
              </tbody>
          </table>
      </div>
  );
};

export default AllLogTable;