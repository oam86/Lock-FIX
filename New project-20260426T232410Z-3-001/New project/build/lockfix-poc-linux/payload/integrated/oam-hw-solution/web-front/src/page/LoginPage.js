import React, {useEffect, useState} from "react";
import axios from "axios";
import {
    MDBBtn,
} from "mdb-react-ui-kit";
import LicenseRegisterModal from "../component/license/LicenceRegisterModal";
import RegisterModal from "../component/login/RegisterModal";

export default function LoginPage({onLogin, licenseData, licenseValid}) {

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true
    })

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [licenseModalOpen, setLicenseModalOpen] = useState(false);
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);

    useEffect(() => {
        if (!licenseValid) {
            setLicenseModalOpen(true);
        }
    }, [licenseValid]); // licenseValid 변경 시 실행

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post("/login", {
                email,
                password,
                support_code: licenseData?.license_key,
            });

            if (response.data.success) {
                setError(null);
                onLogin(response.data.user);
            } else {
                setError(response.data.message || "로그인 실패");
            }
        } catch (err) {
            setError("로그인 중 오류가 발생했습니다. 다시 시도해주세요.");
        }
    };
    return (
        <div className="flex items-center justify-center h-screen">
            <div className="flex w-[1100px] max-w-full h-[600px] bg-white rounded-lg shadow-lg overflow-hidden">
                {/* 왼쪽 섹션 40% */}
                <div className="w-2/5 p-8 flex flex-col justify-center bg-white-100">
                    <h1 className="text-2xl font-bold mb-6 text-gray-800">Please Login:</h1>
                    <form onSubmit={handleLoginSubmit} className="space-y-5">
                        <input
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        {error && <p className="text-red-500">{error}</p>}

                        <MDBBtn
                            type="submit"
                            className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition"
                            disabled={!licenseValid}
                        >
                            LOGIN
                        </MDBBtn>
                    </form>

                    <div className="text-center mt-6 text-sm text-gray-700">
                        <p>
                            Don't have an account?{" "}
                            <button
                                onClick={() => setIsRegisterModalOpen(true)}
                                className="text-red-500 hover:underline"
                            >
                                Register account
                            </button>
                        </p>
                    </div>

                </div>

                {/* 오른쪽 섹션 60% */}
                <div className="w-3/5 bg-blue-500 p-8 flex flex-col justify-between text-white">
                    <h2 className="text-lg font-semibold mb-6">
                        라이선스가 30일 이내일 경우 라이선스 갱신 요청을 진행합니다
                    </h2>
                    <div className="grid grid-cols-1 gap-4">
                        <div className="bg-white text-black p-4 rounded-lg shadow flex items-center">
                            <img
                                src="https://via.placeholder.com/50"
                                alt="Bonus 1"
                                className="mr-4 w-12 h-12 rounded"
                            />
                            <p>우암전자 - 1</p>
                        </div>
                        <div className="bg-white text-black p-4 rounded-lg shadow flex items-center">
                            <img
                                src="https://via.placeholder.com/50"
                                alt="Bonus 2"
                                className="mr-4 w-12 h-12 rounded"
                            />
                            <p>우암전자 - 2</p>
                        </div>
                        <div className="bg-white text-black p-4 rounded-lg shadow flex items-center">
                            <img
                                src="https://via.placeholder.com/50"
                                alt="Bonus 3"
                                className="mr-4 w-12 h-12 rounded"
                            />
                            <p>우암전자 - 3</p>
                        </div>
                    </div>
                </div>
            </div>

            <LicenseRegisterModal
                isOpen={licenseModalOpen}
                onClose={() => setLicenseModalOpen(false)}
                onSuccess={() => {
                    alert("성공적으로 라이선스가 등록되었습니다. 새로고침을 진행해주세요");
                    setLicenseModalOpen(false);
                }}
            />
            <RegisterModal
                licenseData={licenseData}
                isOpen={isRegisterModalOpen}
                onClose={() => setIsRegisterModalOpen(false)}
            />

        </div>
    );
}