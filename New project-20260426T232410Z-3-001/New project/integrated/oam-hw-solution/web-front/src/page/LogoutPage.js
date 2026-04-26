import React, {useEffect} from 'react';
import PropTypes from 'prop-types';
import axios from "axios";

const LogoutPage = props => {

    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true,
    });

    const handleLogout = async () => {

        const user_id = localStorage.getItem("user_id")

        alert('로그아웃 대상 : ' + user_id)

        try {

            const response = await api.post("/logout", {
                user_id: user_id
            })

            if (response.data.success) {
                localStorage.removeItem("user_id");
                window.location.href = "/";
            } else {
                alert('로그아웃을 재시도해주세요')
            }

        } catch (err) {
            alert(err)
        }


    };

    useEffect(() => {
        handleLogout()
    }, []);

    return (
        <div>

        </div>
    );
};

export default LogoutPage;