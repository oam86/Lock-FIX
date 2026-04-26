import React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function GayaDatePicker({ startDate, setStartDate, endDate, setEndDate }) {
  const today = new Date(); // 오늘 날짜

  // 스타일 추가를 위한 공용 클래스 설정
  const customInputStyle = {
    textAlign: "center", // 텍스트 가운데 정렬
    width: "130px",
    fontSize: "16px",
    fontWeight: "bold",
  };

  return (
    <div
      style={{
        display: "flex",
        // justifyContent: "flex-end", // 우측 상단 정렬
        alignItems: "center",
        margin: "5px", // 상단과 여백 추가
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "20px",
          padding: "10px 20px",
          border: "1px solid #ddd",
          borderRadius: "12px",
          background: "#fff",
          boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.1)", // 심플한 그림자 효과
        }}
      >
        {/* 시작 날짜 */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <label
            style={{
              fontWeight: "bold",
              fontSize: "14px",
              color: "#555",
              marginBottom: "5px",
            }}
          >
            시작 날짜
          </label>
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="시작 날짜를 선택해주세요"
            maxDate={today} // 오늘 이전 날짜만 선택 가능
            showMonthYearDropdown
            customInput={<input style={customInputStyle} />} // 텍스트 가운데 정렬 적용
          />
        </div>

        {/* 종료 날짜 */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <label
            style={{
              fontWeight: "bold",
              fontSize: "14px",
              color: "#555",
              marginBottom: "5px",
            }}
          >
            종료 날짜
          </label>
          <DatePicker
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="종료 날짜를 선택해주세요"
            minDate={startDate} // 시작 날짜 이후만 선택 가능
            maxDate={today} // 오늘 이전 날짜만 선택 가능
            showMonthYearDropdown
            customInput={<input style={customInputStyle} />} // 텍스트 가운데 정렬 적용
          />
        </div>
      </div>
    </div>
  );
}

export default GayaDatePicker;