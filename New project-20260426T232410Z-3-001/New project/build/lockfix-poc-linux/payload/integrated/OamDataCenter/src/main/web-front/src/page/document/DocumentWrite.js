import { useState } from "react";
import ClientInfoForm from "./forms/ClientInfoForm";
import ServerInfoForm from "./forms/ServerInfoForm";
import ErrorAndSpecialThingsForm from "./forms/ErrorAndSpecialThingsForm";
import ServerCheckStatusForm from "./forms/ServerCheckStatusForm";

const CheckForm = () => {
    const [headerInfo, setHeaderInfo] = useState({
        checkNumber: 1,
        headerName: "시스템 점검표"
    });

    const [clientCheckInfo, setClientCheckInfo] = useState({});
    const [serverInfo, setServerInfo] = useState({});
    const [errorAndSpecialThings, setErrorAndSpecialThings] = useState([]);
    const [serverCheckStatusList, setServerCheckStatusList] = useState([]);

    const handleDownload = async (e) => {
        e.preventDefault();

        const documentCreateRequest = {
            headerInfo,
            clientCheckInfo,
            serverInfo,
            errorAndSpecialThings,
            serverCheckStatusList
        };

        try {
            const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/document`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(documentCreateRequest),
            });

            if (!response.ok) throw new Error("Download failed");

            const blob = await response.blob();
            const contentDisposition = response.headers.get("Content-Disposition");

            let filename = "System_Check_Report.docx"; // 기본값 설정

            // 🔹 서버에서 제공하는 파일명을 추출
            if (contentDisposition) {
                const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?"?([^";]*)"?/);
                if (match && match[1]) {
                    filename = decodeURIComponent(match[1]); // URL 디코딩하여 한글 처리
                }
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename; // 서버에서 제공한 파일명 사용
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            alert("서버 오류가 발생했습니다");
        }
    };


    return (
        <div className="content-component">
            <div className="max-w-7xl mx-auto bg-gray p-6 rounded-lg shadow-lg mt-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">시스템 점검표</h2>

                {/* `setClientData`가 아니라 `setClientCheckInfo`를 전달해야 함 */}
                <ClientInfoForm setClientData={setClientCheckInfo} />
                <ServerInfoForm setServerData={setServerInfo} />
                <ErrorAndSpecialThingsForm setErrorData={setErrorAndSpecialThings} />
                <ServerCheckStatusForm setServerCheckData={setServerCheckStatusList} />

                <div className="flex justify-center mt-4 space-x-4">
                    <button onClick={handleDownload} className="bg-blue-500 text-white px-6 py-2 rounded-lg shadow-md hover:bg-blue-600 transition">
                        다운로드
                    </button>
                </div>

            </div>
        </div>

    );
};

export default CheckForm;