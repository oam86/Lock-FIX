import React from 'react';
import MonitoringPage from "./MonitoringPage";
import DetectViewPage from "./DetectViewPage";
import NotificationPage from "./NotificationPage";
import LogsPage from "./LogsPage";

function DashBoardPage(props) {
    return (
        <div className='component-animation' style={{marginTop: '5%', marginLeft: '5%', marginRight: '5%'}}>
            <div className="mb-[40px] w-full">
                <MonitoringPage singlePage={false} />
            </div>
            <div className="mb-[40px] w-full">
                <DetectViewPage singlePage={false} />
            </div>
            <div className="mb-[40px] w-full">
                <NotificationPage singlePage={false} />
            </div>
            <div className="w-full">
                <LogsPage singlePage={false} />
            </div>
        </div>
    );
}

export default DashBoardPage;