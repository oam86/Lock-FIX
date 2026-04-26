import React, {useState} from "react";
import {
    MDBBtn,
    MDBInput,
    MDBModal,
    MDBModalBody,
    MDBModalContent,
    MDBModalDialog,
    MDBModalFooter,
    MDBModalHeader,
    MDBModalTitle,
} from "mdb-react-ui-kit";
import axios from "axios";

export default function LicenseRegisterModal({isOpen, onClose, onSuccess}) {

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true,
    });

    const [currentClient, setCurrentClient] = useState({
        clientName: "",
        licenseKey: "",
    });
    const [licenseError, setLicenseError] = useState(null);

    const handleInputChange = (e) => {
        const {name, value} = e.target;
        setCurrentClient((prev) => ({...prev, [name]: value}));
    };

    const handleLicenseSubmit = async () => {
        if (!currentClient.licenseKey || !currentClient.clientName) {
            alert("모든 필드를 채워주세요.");
            return;
        }

        try {
            const response = await api.post("/license_input", currentClient);
            if (response.data.success) {
                setCurrentClient({clientName: "", licenseKey: ""});
                setLicenseError(null);
                onClose(); // 성공 시 모달 닫기
                if (onSuccess) onSuccess(); // 성공 시 부모의 onSuccess 호출
            } else {
                setLicenseError("라이선스 등록 실패");
            }
        } catch (err) {
            setLicenseError("라이선스 등록 중 오류가 발생했습니다.");
        }
    };

    return (
        <MDBModal
            open={isOpen}
            onClose={onClose}
            staticBackdrop={true}
            backdrop={false}
            tabIndex="-1"
        >
            <MDBModalDialog centered>
                <MDBModalContent>
                    <MDBModalHeader>
                        <MDBModalTitle>라이선스가 등록되지 않았습니다</MDBModalTitle>
                    </MDBModalHeader>
                    <MDBModalBody>
                        <MDBInput
                            label="고객사 명"
                            name="clientName"
                            value={currentClient.clientName}
                            onChange={handleInputChange}
                            className="mb-3"
                        />
                        <MDBInput
                            label="라이선스 키"
                            name="licenseKey"
                            value={currentClient.licenseKey}
                            onChange={handleInputChange}
                            className="mb-3"
                        />
                        {licenseError && <p className="text-red-500">{licenseError}</p>}
                    </MDBModalBody>
                    <MDBModalFooter>
                        <MDBBtn color="primary" onClick={handleLicenseSubmit}>
                            등록
                        </MDBBtn>
                    </MDBModalFooter>
                </MDBModalContent>
            </MDBModalDialog>
        </MDBModal>
    );
}