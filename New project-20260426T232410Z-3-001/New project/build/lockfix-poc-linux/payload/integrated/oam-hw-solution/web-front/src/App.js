import React, {useEffect, useState} from "react";
import {BrowserRouter, Route, Switch} from "react-router-dom";
import {GayaSideBar} from "./component/common/SideBar";
import ContactServicePage from "./page/ContactServicePage";
import DashBoardPage from "./page/DashBoardPage";
import DetectViewPage from "./page/DetectViewPage";
import LicensePage from "./page/LicensePage";
import LogsPage from "./page/LogsPage";
import MonitoringPage from "./page/MonitoringPage";
import NotificationPage from "./page/NotificationPage";
import LoginPage from "./page/LoginPage";
import axios from "axios";
import LogoutPage from "./page/LogoutPage";
import NetworkStatusPage from "./page/NetworkStatusPage";

export default function App() {
    const api = axios.create({
        baseURL: process.env.REACT_APP_LOCAL_APP_API_BASE_URL,
        withCredentials: true,
    });

    const [licenseValid, setLicenseValid] = useState(false);
    const [licenseData, setLicenseData] = useState(null);
    const [isLicenseLoaded, setIsLicenseLoaded] = useState(false);

    const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem("user_id"));
    const [user, setUser] = useState(null); // user 상태 추가


    useEffect(() => {
        fetchLicense();
    }, [isLoggedIn]);

    const handleLogin = (userData) => {
        setIsLoggedIn(true);
        setUser(userData); // 로그인한 사용자 정보 저장
        localStorage.setItem("user_id", userData.email);
    };

    const fetchLicense = async () => {
        try {

            const response = await api.get("/license_info");

            const license = response.data;

            if (!license) {
                alert('라이선스 없음')
                return
            }

            setLicenseData(license);

            const expiryDate = new Date(license.expiry_date);
            const today = new Date();
            const timeDifference = expiryDate - today;
            const daysRemaining = Math.ceil(timeDifference / (1000 * 60 * 60 * 24)) - 1;

            if (today > expiryDate) {
                alert("라이선스가 만료되었습니다.");
                setIsLicenseLoaded(true);
                return;
            }

            if (daysRemaining <= 30) {
                alert(`라이선스 만료까지 ${daysRemaining}일 남았습니다.`);
            }

            setLicenseValid(true);
        } catch (err) {

            if (err.status === 401) {
                alert('만료되거나 삭제된 라이선스 입니다')
                localStorage.removeItem("user_id")
                setIsLoggedIn(false)
            } else if (err.status === 404) {
                setIsLicenseLoaded(true);
                setIsLoggedIn(false)
                localStorage.removeItem("user_id")
            }

        } finally {
            setIsLicenseLoaded(true);
        }
    };

    if (!isLicenseLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <BrowserRouter>
            {!isLoggedIn ? (
                <div className="flex items-center justify-center min-h-screen bg-gray-100">
                    <LoginPage onLogin={handleLogin} licenseData={licenseData} licenseValid={licenseValid}/>
                </div>
            ) : (
                // <div className="flex h-screen">
                <div className="grid grid-cols-[280px_1fr] h-screen">
                    <GayaSideBar/>
                    <div className="flex-grow p-4 overflow-auto">
                        <Switch>
                            <Route path="/contact-service" component={ContactServicePage}/>
                            <Route path="/dashboard" component={DashBoardPage}/>
                            <Route path="/detect"
                                   render={(props) => <DetectViewPage {...props} singlePage={true}/>}/>
                            <Route path="/license" component={LicensePage}/>
                            <Route path="/logs" render={(props) => <LogsPage {...props} singlePage={true}/>}/>
                            <Route path="/monitoring"
                                   render={(props) => <MonitoringPage {...props} singlePage={true}/>}/>
                            <Route path="/notification"
                                   render={(props) => <NotificationPage {...props} singlePage={true}/>}/>
                            <Route path="/network-status" component={NetworkStatusPage}/>
                            <Route path="/logout" component={LogoutPage}/>
                        </Switch>
                    </div>
                </div>
            )}
        </BrowserRouter>
    );
}