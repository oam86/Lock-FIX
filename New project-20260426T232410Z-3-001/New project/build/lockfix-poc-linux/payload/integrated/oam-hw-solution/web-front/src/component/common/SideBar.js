import React from "react";
import {Link} from "react-router-dom";
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
    Cog6ToothIcon, MagnifyingGlassCircleIcon, CheckBadgeIcon,
} from "@heroicons/react/24/solid";

import OamLogo from "../../image/oamLogo.png";

import {
    ArrowLeftEndOnRectangleIcon,
    ChartBarSquareIcon,
    MagnifyingGlassIcon,
    RectangleGroupIcon
} from "@heroicons/react/16/solid";
import {
    DocumentArrowDownIcon,
    BellAlertIcon,
    ClipboardDocumentCheckIcon,
    PhoneArrowUpRightIcon,
    SignalIcon
} from "@heroicons/react/24/outline";
import {ArrowLeftOnRectangleIcon} from "@heroicons/react/20/solid";


export function GayaSideBar() {
    return (
        // <Card className="h-full w-[280px] p-4 shadow-xl shadow-blue-gray-900/25 flex flex-col overflow-">
        <Card className="h-full w-[280px] p-4 shadow-xl shadow-blue-gray-900/25 flex flex-col overflow-y-auto overflow-x-hidden">
            <div className="mb-2 p-4 flex items-center justify-center">
                <img src="/oamLogo.png" alt="OAM 로고" className="h-14 w-auto object-contain"/>
            </div>
            <List>
                <Link to="/monitoring">
                <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <ChartBarSquareIcon className="h-8 w-8"/>
                        </ListItemPrefix>
                        <span>Monitoring</span>
                    </ListItem>
                </Link>
                <Link to="/dashboard">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <RectangleGroupIcon className="h-8 w-8"/>
                        </ListItemPrefix>
                        <span>Dashboard</span>
                    </ListItem>
                </Link>
                <Link to="/detect">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <MagnifyingGlassIcon className="h-8 w-8"/>
                        </ListItemPrefix>
                        <span>Detect</span>
                    </ListItem>
                </Link>
                <Link to="/notification">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <BellAlertIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <span>Notification</span>
                    </ListItem>
                </Link>
                <Link to="/logs">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <ClipboardDocumentCheckIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <span>Logs</span>
                    </ListItem>
                </Link>
                <Link to="/contact-service">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <PhoneArrowUpRightIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <span>Contact Service</span>
                    </ListItem>
                </Link>
                <Link to="/license">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <CheckBadgeIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <span>License</span>
                    </ListItem>
                </Link>

                <Link to="/network-status">
                    <ListItem className="flex items-center space-x-2">
                        <ListItemPrefix className="flex items-center">
                            <SignalIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <span>Network Status</span>
                    </ListItem>
                </Link>

                <Link to="/logout">
                    <ListItem className="flex items-center space-x-2" style={{color: "darkred"}}>
                        <ListItemPrefix className="flex items-center">
                            <ArrowLeftEndOnRectangleIcon className="h-7 w-7"/>
                        </ListItemPrefix>
                        <b>
                            <span>Logout</span>
                        </b>
                    </ListItem>
                </Link>

            </List>
        </Card>
    );
}