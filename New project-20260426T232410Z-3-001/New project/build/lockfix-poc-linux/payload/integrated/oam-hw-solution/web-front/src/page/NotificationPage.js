import React, { useState, useEffect } from "react";
import axios from "axios";
import AdminAccountTable from "../component/notification/AdminAccountTable";

const NotificationPage = (props) => {
    const [tableData, setTableData] = useState([]);

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true,
    });

    useEffect(() => {
        // 유저 목록 가져오기
        const fetchUsers = async () => {
            try {
                const response = await api.get("/users");
                if (response.data.success) {
                    const formattedData = response.data.data.map(user => ({
                        email: user.email,
                        smtpStatus: user.smtp_status, // SMTP 상태
                        smtpMessage: user.smtp_message, // SMTP 메시지
                        networkConnection: user.network_connection, // 필요 시 실제 데이터에 맞게 조정
                        lastLogin: user.last_login, // 마지막 접속 여부
                    }));
                    setTableData(formattedData);
                } else {
                    alert("유저 데이터를 가져올 수 없습니다.");
                }
            } catch (err) {
                console.error("Error fetching users:", err);
            }
        };

        fetchUsers();
    }, []);

    return (
        <div className={props.singlePage ? 'component-animation' : ''}
             style={props.singlePage ? { marginTop: '4%' } : {}}>
            <AdminAccountTable title="Notification" data={tableData} />
        </div>
    );
};

export default NotificationPage;