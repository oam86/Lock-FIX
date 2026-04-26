import React from 'react';

const LogViewCard = ({ title, content, badgeText }) => {
  // Title에 따른 폰트 색상 설정
  const badgeTextColor = title === 'Detect' ? 'text-yellow-500'
                       : title === 'Warning' ? 'text-orange-500'
                       : 'text-purple-500';

  return (
    <div className="relative border rounded-lg shadow-md p-4">
      {/* 왼쪽 끝의 색상 바 */}
      <div className={`absolute top-0 left-0 h-full w-2 ${badgeTextColor.replace('text-', 'bg-')}`}></div>

      {/* 카드 내용 */}
      <div className="ml-4">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-gray-600">{content}</p>
      </div>

      {/* 배지 */}
      <div className={`absolute top-2 right-2 bg-white ${badgeTextColor} text-6xl font-bold rounded-full px-4 py-2`}>
        {badgeText}
      </div>
    </div>
  );
};

export default LogViewCard;