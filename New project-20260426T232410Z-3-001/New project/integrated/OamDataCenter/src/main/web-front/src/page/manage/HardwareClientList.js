import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import HardwareView from "../view/HardwareView";

export default function HardwareClientList() {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const supportCode = queryParams.get("supportCode");

    return (
        <div>
            <HardwareView supportCode={supportCode} />
        </div>
    );
}