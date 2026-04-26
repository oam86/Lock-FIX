import React from "react";
import { useLocation } from "react-router-dom";
import LicenseView from "../view/LicenseView"; // LicenseView 컴포넌트 임포트

export default function LicenseManagement() {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const clientCode = queryParams.get("clientCode");

    return (
        <div>
            <LicenseView clientCode={clientCode} />
        </div>
    );
}