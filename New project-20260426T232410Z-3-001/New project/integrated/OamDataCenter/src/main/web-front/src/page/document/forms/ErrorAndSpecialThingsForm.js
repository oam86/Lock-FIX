import React, { useState } from "react";
import { MDBContainer, MDBRow, MDBCol, MDBInput, MDBBtn, MDBListGroup, MDBListGroupItem } from "mdb-react-ui-kit";

const ErrorAndSpecialThingsForm = ({ setErrorData }) => {
    const [errorList, setErrorList] = useState([]);
    const [inputValue, setInputValue] = useState("");

    const handleAddError = () => {
        if (inputValue.trim() !== "") {
            const newErrors = [...errorList, inputValue];
            setErrorList(newErrors);
            setErrorData(newErrors);
            setInputValue("");
        }
    };

    const handleDeleteError = (index) => {
        const newErrors = errorList.filter((_, i) => i !== index);
        setErrorList(newErrors);
        setErrorData(newErrors);
    };

    return (
        <MDBContainer className="bg-light p-4 rounded-4 shadow">
            <h3 className="text-center mb-4">특이사항 및 장애현황</h3>

            <MDBRow className="mb-3">
                <MDBCol size="9">
                    <MDBInput label="항목 입력" value={inputValue} onChange={(e) => setInputValue(e.target.value)} />
                </MDBCol>
                <MDBCol size="3">
                    <MDBBtn color="primary" className="w-100" onClick={handleAddError}>
                        추가
                    </MDBBtn>
                </MDBCol>
            </MDBRow>

            <MDBListGroup>
                {errorList.map((error, index) => (
                    <MDBListGroupItem key={index} className="d-flex justify-content-between align-items-center">
                        {error}
                        <MDBBtn color="danger" size="sm" onClick={() => handleDeleteError(index)}>
                            삭제
                        </MDBBtn>
                    </MDBListGroupItem>
                ))}
            </MDBListGroup>
        </MDBContainer>
    );
};

export default ErrorAndSpecialThingsForm;