import React, {useEffect, useState} from "react";
import axios from "axios";
import { MDBTable, MDBTableBody, MDBTableHead, MDBBtn, MDBModal, MDBModalBody, MDBModalDialog, MDBModalContent, MDBModalFooter, MDBModalHeader, MDBModalTitle, MDBInput } from "mdb-react-ui-kit";
import {formatDateTime} from "../../component/util/dateutils";

export default function HardwareView({ supportCode }) {
    const [hardwareList, setHardwareList] = useState([]);

    const fetchHardware = async () => {
        setHardwareList([])
        try {

            const url = supportCode
                ? `${process.env.REACT_APP_API_BASE_URL}/hardware/list?supportCode=${supportCode}`
                : `${process.env.REACT_APP_API_BASE_URL}/hardware/all`;
            const response = await axios.get(url);
            setHardwareList(response.data);
        } catch (error) {
            console.error("Error fetching hardware data", error);
        }
    };

    useEffect(() => {
        fetchHardware();
    }, []);

    return (
        <div className='content-component'>
            <MDBTable responsive="lg" hover>
                <MDBTableHead>
                    <tr>
                        <th scope="col">고객사 명</th>
                        <th scope="col">라이센스 코드</th>
                        <th scope="col">하드웨어 유형</th>
                        <th scope="col">모델명</th>
                        <th scope="col">시리얼 번호</th>
                        <th scope="col">납품 일자</th>
                        {/*<th scope="col">관리</th>*/}
                    </tr>
                </MDBTableHead>
                <MDBTableBody>
                    {hardwareList.map((hardware) => (
                        <tr key={hardware.id}>
                            <td>{hardware.license_info.client.name}</td>
                            <td>{hardware.license_info.support_code}</td>
                            <td>{hardware.type}</td>
                            <td>{hardware.model}</td>
                            <td>{hardware.serial_number || "N/A"}</td>
                            <td>{ formatDateTime(hardware.delivery_at) || "N/A"}</td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

        </div>
    );
}