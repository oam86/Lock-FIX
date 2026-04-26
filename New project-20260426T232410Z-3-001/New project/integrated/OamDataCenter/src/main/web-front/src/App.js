import React from "react";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import {GayaSideBar} from "./component/SideBar";
import HardwareClientList from "./page/manage/HardwareClientList";
import ClientManagement from "./page/manage/ClientManagement";
import LicenseManagement from "./page/manage/LicenseManagement";
import CompanyComputerManagerManagement from "./page/manage/CompanyComputerManagerManagement";

import "../src/css/global.css"
import LicenseView from "./page/view/LicenseView";
import HardwareView from "./page/view/HardwareView";
import ClientUserAccountManagement from "./page/manage/ClientUserAccountManagement";
import DocumentWrite from "./page/document/DocumentWrite";

export default function App() {
    return (
        <div translate="no" className="flex h-screen">
            <BrowserRouter>
                <GayaSideBar/>
                <div className="flex-grow p-4 overflow-auto">
                    <Switch>
                        <Route path="/client-hardware-list" component={HardwareClientList}/>
                        <Route path="/client-management" component={ClientManagement} />
                        <Route path="/license-management" component={LicenseManagement} />
                        <Route path="/company-computer-manager-management" component={CompanyComputerManagerManagement} />
                        <Route path="/client-account" component={ClientUserAccountManagement}/>
                        <Route path="/write-document" component={DocumentWrite}/>
                    </Switch>
                </div>
            </BrowserRouter>
        </div>
    );
}