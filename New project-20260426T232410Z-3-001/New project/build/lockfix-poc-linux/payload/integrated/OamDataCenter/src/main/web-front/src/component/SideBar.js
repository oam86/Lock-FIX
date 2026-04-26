import React from "react";
import { Link } from "react-router-dom";
import {
    Card,
    Typography,
    List,
    ListItem,
    ListItemPrefix,
    ListItemSuffix,
    Chip,
} from "@material-tailwind/react";
import {
    InboxIcon,
    UserCircleIcon,
    Cog6ToothIcon, BellAlertIcon, CircleStackIcon, CpuChipIcon,
} from "@heroicons/react/24/solid";


import {DocumentDuplicateIcon, HandRaisedIcon} from "@heroicons/react/16/solid";

export function GayaSideBar() {
    return (
        <Card className="h-full w-[300px] p-4 shadow-xl shadow-blue-gray-900/25 flex flex-col">
            <div className="mb-2 p-4 flex items-center justify-center">
                {/*<img src={OamLogo} alt="OAM 로고" className="h-14 w-auto object-contain" />*/}
                <img src="/oamLogo.png" alt="OAM 로고" className="h-14 w-auto object-contain" />
            </div>
            <List>
                <Link to="/client-management">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <UserCircleIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">고객사 관리</span>
                    </ListItem>
                </Link>
                <Link to="/license-management">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <CircleStackIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">라이선스 관리</span>
                    </ListItem>
                </Link>
                <Link to="/client-hardware-list">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <CpuChipIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">납품한 하드웨어 목록</span>
                    </ListItem>
                </Link>
                <Link to="/company-computer-manager-management">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <BellAlertIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">전산 담당자 관리</span>
                    </ListItem>
                </Link>
                <Link to="/client-account">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <HandRaisedIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">고객사 계정 확인</span>
                    </ListItem>
                </Link>
                <Link to="/write-document">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <DocumentDuplicateIcon className="h-6 w-6" />
                        </ListItemPrefix>
                        <span className="truncate hidden sm:inline">보고서 작성</span>
                    </ListItem>
                </Link>
            </List>
        </Card>
    );
}