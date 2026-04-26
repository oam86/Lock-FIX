import React from "react";
import {useLocation} from "react-router-dom";
import ClientUserAccountView from "../view/ClientUserAccountView"; // 위에서 만든 컴포넌트 경로를 사용

export default function ClientUserAccountManagement() {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const supportCode = queryParams.get("supportCode");

    return (
        <div className="page-container">
            <ClientUserAccountView supportCode={supportCode} />
        </div>
    );
}