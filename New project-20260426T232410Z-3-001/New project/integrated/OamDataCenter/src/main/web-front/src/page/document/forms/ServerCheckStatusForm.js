import React, { useState, useEffect } from "react";
import {
    MDBContainer, MDBRow, MDBCol, MDBInput, MDBDropdown, MDBDropdownToggle, MDBDropdownMenu, MDBDropdownItem,
    MDBBtn, MDBTable, MDBTableHead, MDBTableBody, MDBTextArea, MDBCard, MDBCardBody
} from "mdb-react-ui-kit";


const defaultCheckList = [
    { type: "HW", checkType: "시스템 LED", checkContent: "전면 PANEL LED", checkTargetAndStandard: "적색등 유무", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "Power Supply", checkContent: "Power Supply 육안확인", checkTargetAndStandard: "녹색등 유무", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "Disk", checkContent: "LED 육안확인", checkTargetAndStandard: "적색등 유무", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "Disk", checkContent: "Raid Status", checkTargetAndStandard: "Online 유무", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "Memory", checkContent: "Log 확인", checkTargetAndStandard: "Status Check", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "CPU", checkContent: "Log 확인", checkTargetAndStandard: "Status Check", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "Adapter", checkContent: "LED 및 Cable 연결상태", checkTargetAndStandard: "적색등 유무", result: "정상 ( ) 이상 ( )" },
    { type: "HW", checkType: "시스템 Log", checkContent: "Log 확인", checkTargetAndStandard: "Error 유무", result: "정상 ( ) 이상 ( )" },

    { type: "SW", checkType: "error 확인", checkContent: "more /var/log/messages", checkTargetAndStandard: "Error 유무", result: "정상 ( ) 이상 ( )" },
    { type: "SW", checkType: "Disk 사용량", checkContent: "/, /backup, /data", checkTargetAndStandard: "각 파티션 사용량 확인", result: "정상 ( ) 이상 ( )" },
    { type: "SW", checkType: "성능측정", checkContent: "vmstat, top", checkTargetAndStandard: "과다 사용여부", result: "정상 ( ) 이상 ( )" },
    { type: "SW", checkType: "Processor", checkContent: "% 사용량", checkTargetAndStandard: "이상 사용 유무", result: "정상 ( ) 이상 ( )" },
    { type: "SW", checkType: "Memory", checkContent: "% 사용량", checkTargetAndStandard: "이상 사용 유무", result: "정상 ( ) 이상 ( )" },
    { type: "SW", checkType: "시스템 가동시간", checkContent: "uptime", checkTargetAndStandard: "시스템 가동시간 확인", result: "Days" }
];

const ServerCheckStatusForm = ({ setServerCheckData }) => {
    const [serverCheckList, setServerCheckList] = useState(defaultCheckList);
    const [newCheck, setNewCheck] = useState({ type: "HW", checkType: "", checkContent: "", checkTargetAndStandard: "", result: "" });
    const [dropdownLabel, setDropdownLabel] = useState("H/W"); // 선택한 값 표시

    /** 점검 항목 변경 시 데이터 업데이트 */
    useEffect(() => {
        setServerCheckData(serverCheckList);
    }, [serverCheckList, setServerCheckData]);

    /** 입력 값 변경 핸들러 */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setNewCheck((prev) => ({ ...prev, [name]: value }));
    };

    /** 새로운 점검 항목 추가 */
    const handleAddRow = () => {
        if (Object.values(newCheck).every((val) => val.trim() !== "")) {
            setServerCheckList((prevList) => [...prevList, { ...newCheck }]);
            setNewCheck({ type: "HW", checkType: "", checkContent: "", checkTargetAndStandard: "", result: "" });
            setDropdownLabel("H/W");
        }
    };

    /** 개별 점검 항목 삭제 */
    const handleDeleteRow = (index) => {
        setServerCheckList((prevList) => prevList.filter((_, i) => i !== index));
    };

    /** 전체 점검 항목 삭제 */
    const handleClearAll = () => {
        if (window.confirm("모든 항목을 삭제하시겠습니까?")) {
            setServerCheckList([]);
        }
    };

    /** 드롭다운 값 선택 핸들러 */
    const handleSelect = (value, label) => {
        setNewCheck((prev) => ({ ...prev, type: value }));
        setDropdownLabel(label);
    };

    return (
        <MDBContainer className="bg-light p-4 rounded-4 shadow">
            <h3 className="text-center mb-4">서버 점검 내역</h3>

            {/* 기존 점검 항목 리스트 */}
            <MDBTable align="middle">
                <MDBTableHead light>
                    <tr>
                        <th>구분</th>
                        <th>점검사항</th>
                        <th>점검내역</th>
                        <th>점검항목/기준</th>
                        <th>결과</th>
                        <th>삭제</th>
                    </tr>
                </MDBTableHead>
                <MDBTableBody>
                    {serverCheckList.map((row, index) => (
                        <tr key={index}>
                            <td>{row.type}</td>
                            <td>{row.checkType}</td>
                            <td>{row.checkContent}</td>
                            <td>{row.checkTargetAndStandard}</td>
                            <td>{row.result}</td>
                            <td>
                                <MDBBtn color="danger" size="sm" onClick={() => handleDeleteRow(index)}>
                                    삭제
                                </MDBBtn>
                            </td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

            {/* 버튼 영역 */}
            <MDBRow className="justify-content-between mt-3">
                <MDBCol md="4">
                    <MDBBtn color="danger" className="w-100" onClick={handleClearAll}>
                        전체 삭제
                    </MDBBtn>
                </MDBCol>
            </MDBRow>

            {/* 새 점검 항목 추가 폼 */}
            <h4 className="text-md font-semibold mt-4">새 점검 항목 추가</h4>
            <MDBCard className="p-3">
                <MDBCardBody>
                    <MDBRow className="mb-3">
                        <MDBCol md="2">
                            <MDBDropdown>
                                <MDBDropdownToggle color="primary" className="w-100">
                                    {dropdownLabel}
                                </MDBDropdownToggle>
                                <MDBDropdownMenu>
                                    <MDBDropdownItem link onClick={() => handleSelect("HW", "H/W")}>H/W</MDBDropdownItem>
                                    <MDBDropdownItem link onClick={() => handleSelect("SW", "S/W")}>S/W</MDBDropdownItem>
                                </MDBDropdownMenu>
                            </MDBDropdown>
                        </MDBCol>
                        <MDBCol md="2">
                            <MDBInput label="점검사항" name="checkType" value={newCheck.checkType} onChange={handleChange} />
                        </MDBCol>
                        <MDBCol md="3">
                            <MDBTextArea label="점검내역 (여러 줄 입력 가능)" name="checkContent" rows={3} value={newCheck.checkContent} onChange={handleChange} />
                        </MDBCol>
                        <MDBCol md="3">
                            <MDBTextArea label="점검항목/기준 (여러 줄 입력 가능)" name="checkTargetAndStandard" rows={3} value={newCheck.checkTargetAndStandard} onChange={handleChange} />
                        </MDBCol>
                        <MDBCol md="2">
                            <MDBInput label="결과" name="result" value={newCheck.result} onChange={handleChange} />
                        </MDBCol>
                    </MDBRow>
                    <MDBRow className="justify-content-center">
                        <MDBCol md="3">
                            <MDBBtn color="success" className="w-100" onClick={handleAddRow}>
                                추가
                            </MDBBtn>
                        </MDBCol>
                    </MDBRow>
                </MDBCardBody>
            </MDBCard>
        </MDBContainer>
    );
};

export default ServerCheckStatusForm;