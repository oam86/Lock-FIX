import React, { useState } from "react";
import {MDBContainer, MDBRow, MDBCol, MDBInput, MDBTextArea} from "mdb-react-ui-kit";

const ServerInfoForm = ({ setServerData }) => {
    const [serverForm, setServerForm] = useState({
        osVersion: "Windows Server 2022",  // 기본값 설정
        cpu: "Intel Xeon 3.5GHz",
        memory: "16GB",
        disk: "SAS-",
        hostname: "Server-01",
        supportWork: "회원관리 DB",  // ✅ 지원업무 추가
        model: "",        // ✅ 모델명 추가
        serialNumber: ""  // ✅ 시리얼번호 추가
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setServerForm((prevForm) => {
            const updatedForm = { ...prevForm, [name]: value };
            setServerData(updatedForm); // 상위 컴포넌트로 데이터 전달
            return updatedForm;
        });
    };

    return (
        <MDBContainer className="bg-light p-4 rounded-4 shadow">
            <h3 className="text-center mb-4">서버 기본 정보</h3>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="OS 정보" name="osVersion" placeholder={serverForm.osVersion} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBInput label="CPU 정보" name="cpu" placeholder={serverForm.cpu} onChange={handleChange} />
                </MDBCol>
            </MDBRow>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="지원업무" name="supportWork" placeholder={serverForm.supportWork} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBTextArea label="메모리 정보" name="memory" placeholder={serverForm.memory} onChange={handleChange} />
                </MDBCol>
            </MDBRow>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="모델명" name="model" placeholder={serverForm.model} onChange={handleChange} />

                </MDBCol>
                <MDBCol md="6">
                    <MDBTextArea label="디스크 정보" name="disk" placeholder={serverForm.disk} onChange={handleChange} />
                </MDBCol>
            </MDBRow>

            <MDBRow className="mb-3">
                <MDBCol md="6">
                    <MDBInput label="시리얼번호" name="serialNumber" placeholder={serverForm.serialNumber} onChange={handleChange} />
                </MDBCol>
                <MDBCol md="6">
                    <MDBInput label="호스트 이름" name="hostname" placeholder={serverForm.hostname} onChange={handleChange} />
                </MDBCol>
            </MDBRow>
        </MDBContainer>
    );
};

export default ServerInfoForm;