import React, { useState } from "react";
import { MDBContainer, MDBRow, MDBCol, MDBInput } from "mdb-react-ui-kit";

const ClientInfoForm = ({ setClientData }) => {
    const [clientForm, setClientForm] = useState({
        clientCompanyName: "기본 고객사", // 기본값
        checkDate: new Date().toISOString().split("T")[0], // 오늘 날짜 기본값
        clientName: "홍길동",
        clientPhone: "010-1234-5678",
        checkPersonName: "점검 담당자",
        checkPersonPhone: "010-9876-5432",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setClientForm((prevForm) => {
            const updatedForm = { ...prevForm, [name]: value };
            setClientData(updatedForm); // 상위 컴포넌트로 데이터 전달
            return updatedForm;
        });
    };

    return (
        <MDBContainer className="bg-light p-4 rounded-4 shadow">
            <h3 className="text-center mb-4">고객사 담당 정보</h3>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="고객사명" name="clientCompanyName" placeholder={clientForm.clientCompanyName} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBInput label="점검 일자" type="date" name="checkDate" placeholder={clientForm.checkDate} onChange={handleChange} />
                </MDBCol>
            </MDBRow>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="고객사 담당자" name="clientName" placeholder={clientForm.clientName} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBInput label="고객사 연락처" type="tel" name="clientPhone" placeholder={clientForm.clientPhone} onChange={handleChange} />
                </MDBCol>
            </MDBRow>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="점검 담당자" name="checkPersonName" placeholder={clientForm.checkPersonName} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBInput label="점검 담당자 연락처" type="tel" name="checkPersonPhone" placeholder={clientForm.checkPersonPhone} onChange={handleChange} />
                </MDBCol>
            </MDBRow>
        </MDBContainer>
    );
};

export default ClientInfoForm;