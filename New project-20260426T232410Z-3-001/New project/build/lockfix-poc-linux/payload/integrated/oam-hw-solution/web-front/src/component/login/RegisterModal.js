import React, {useState} from "react";
import axios from "axios";
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

export default function RegisterModal({isOpen, onClose, licenseData}) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true
    })

const handleSubmit = async (e) => {
    e.preventDefault();

    try {
        const response = await api.post("/register_user", {
            email: email,
            password: password,
            support_code: licenseData.license_key
        });

        if (response.data.success) {
            setSuccess("User registered successfully!");
            setError(null);
            setEmail("");
            setPassword("");
            onClose(true)
            alert('회원가입이 완료되었습니다')
        } else {
            // Flask에서 반환된 에러 메시지 표시
            setError(response.data.message || "Failed to register user.");
            setSuccess(null);
        }
    } catch (err) {
        // Flask 에러 메시지가 있는 경우 표시
        if (err.response && err.response.data && err.response.data.message) {
            setError(err.response.data.message);
        } else {
            setError("An unexpected error occurred. Please try again.");
        }
        setSuccess(null);
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
                        <MDBModalTitle>회원가입</MDBModalTitle>
                        <MDBBtn
                            className="btn-close"
                            color="none"
                            onClick={onClose}
                        ></MDBBtn>
                    </MDBModalHeader>
                    <MDBModalBody>
                        <form onSubmit={handleSubmit} className="space-y-4">

                            {licenseData ? (
                                <>
                                    <MDBInput
                                        label="라이선스 키"
                                        value={licenseData.license_key}
                                        type="text"
                                        className="mb-3"
                                        disabled={true}
                                    />

                                    <MDBInput
                                        label="Email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="mb-3"
                                        required
                                    />
                                    <MDBInput
                                        label="Password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="mb-3"
                                        required
                                    />
                                    {error && <p className="text-red-500">{error}</p>}
                                    {success && <p className="text-green-500">{success}</p>}

                                </>
                            ) : (
                                <>
                                    <span style={{color: "red"}}>
                                        라이선스를 먼저 등록해주세요
                                    </span>
                                </>
                            )}


                        </form>
                    </MDBModalBody>
                    <MDBModalFooter>
                        <MDBBtn color="danger" onClick={onClose}>
                            취소
                        </MDBBtn>
                        <MDBBtn color="primary" onClick={handleSubmit}>
                            가입 요청
                        </MDBBtn>
                    </MDBModalFooter>
                </MDBModalContent>
            </MDBModalDialog>
        </MDBModal>
    );
}