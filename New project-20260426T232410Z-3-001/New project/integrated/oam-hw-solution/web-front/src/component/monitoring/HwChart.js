import Chart from "react-apexcharts";
import React from "react";

function HwChart({ value = 70, color = "#000", label = "Label", tooltipText = "Tooltip", icon: Icon }) {
  const options = {
    chart: {
      height: 150,
      type: "radialBar",
      maxWidth: "400",
    },
    plotOptions: {
      radialBar: {
        track: {
          strokeWidth: "80%",
        },
        hollow: {
          size: "65%", // 내부 공간 확보
        },
        dataLabels: {
          show: false, // 기본 데이터 라벨 제거
        },
        strokeWidth: "10%",
      },
    },
    fill: {
      colors: [color],
    },
    stroke: {
      lineCap: "round",
    },
    tooltip: {
      enabled: true,
      custom: function ({ series, seriesIndex }) {
        return `
          <div style="
            padding: 10px;
            border-radius: 8px;
            background-color: rgba(0, 0, 0, 0.6);
            color: white;
            font-size: 14px;
            text-align: center;
          ">
            <strong>${tooltipText}</strong><br />
            <span>${series[seriesIndex]}%</span>
          </div>
        `;
      },
    },
  };

  return (
    <div className="relative flex justify-center items-center">
      {/* 차트 컴포넌트 */}
      <Chart options={options} series={[value]} type="radialBar" height={250} />

      {/* 아이콘 + 라벨 + 값 중앙 배치 */}
      <div className="absolute flex flex-col items-center justify-center">
        {Icon && <Icon className="h-12 w-12" style={{ color: color }} />} {/* 기존보다 2배 큰 아이콘 */}
        <span className="text-base font-semibold mt-1" style={{ color: color }}>
          {label}
        </span>
        <span className="text-xl font-bold mt-1" style={{ color: color }}>
          {value}%
        </span>
      </div>
    </div>
  );
}

export default HwChart;