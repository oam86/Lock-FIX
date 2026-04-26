import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    MDBBtn,
    MDBInput,
    MDBModal,
    MDBModalBody,
    MDBModalContent,
    MDBModalDialog,
    MDBModalFooter,
    MDBModalHeader,
    MDBModalTitle,
    MDBTable,
    MDBTableBody,
    MDBTableHead
} from "mdb-react-ui-kit";
import {formatDateTime} from "../../component/util/dateutils";

export default function ClientManagement() {
    const [clients, setClients] = useState([]);
    const [modal, setModal] = useState(false);
    const [optionModal, setOptionModal] = useState(false);
    const [modalType, setModalType] = useState("");
    const [currentClient, setCurrentClient] = useState({
        client_code: "",
        name: "",
        address: "",
        created_at: ""
    });

    const fetchClients = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/clients/list`);
            setClients(response.data);
        } catch (error) {
            console.error("고객사 데이터를 가져오는 중 오류가 발생했습니다.", error);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    const toggleModal = (type = "", client = { clientCode: "", name: "", address: "", createdAt: "" }) => {
        setModalType(type);
        setCurrentClient(client);
        setModal(!modal);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setCurrentClient((prev) => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        if ( !currentClient.name || !currentClient.address) {
            alert("모든 필드를 채워주세요.");
            return;
        }

        try {
            toggleModal();
            const url = modalType === "edit"
                ? `${process.env.REACT_APP_API_BASE_URL}/clients/update`
                : `${process.env.REACT_APP_API_BASE_URL}/clients/create`;
            await axios.post(url, currentClient);
            alert(modalType === "edit" ? "수정이 완료되었습니다." : "추가가 완료되었습니다.");
            fetchClients();
        } catch (error) {
            console.error("고객사 저장 중 오류가 발생했습니다.", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    const handleDelete = async () => {
        try {
            toggleModal();
            await axios.post(`${process.env.REACT_APP_API_BASE_URL}/clients/delete`, currentClient);
            alert("삭제가 완료되었습니다.");
            fetchClients();
        } catch (error) {
            console.error("고객사 삭제 중 오류가 발생했습니다.", error);
            alert("삭제 중 오류가 발생했습니다.");
        }
    };

    const openNewTab = (type) => {

        let url

        switch (type) {
            case "license":
                url = `/license-management?clientCode=${currentClient.client_code}`
                break
        }

        window.open(url, "_blank");
        setOptionModal(false);
    };

    const openOptionModal = (client) => {
        setCurrentClient(client);
        setOptionModal(true);
    };

    return (
        <div className='content-component'>
            <MDBTable responsive="lg" hover>
                <MDBTableHead>
                    <tr>
                        <th scope="col">고객사 코드</th>
                        <th scope="col">이름</th>
                        <th scope="col">주소</th>
                        <th scope="col">생성일자</th>
                        <th scope="col">관리</th>
                    </tr>
                </MDBTableHead>
                <MDBTableBody style={{ textAlign: "center", verticalAlign: "middle" }}>
                    {clients.map((client, index) => (
                        <tr key={index} onClick={() => openOptionModal(client)} style={{ cursor: "pointer" }}>
                            <td>{client.client_code}</td>
                            <td>{client.name}</td>
                            <td>{client.address}</td>
                            <td>{formatDateTime(client.created_at)}</td>
                            <td>
                                <MDBBtn color="primary" size="sm" onClick={(e) => { e.stopPropagation(); toggleModal("edit", client); }}>
                                    수정
                                </MDBBtn>
                                <MDBBtn color="danger" size="sm" onClick={(e) => { e.stopPropagation(); toggleModal("delete", client); }}>
                                    삭제
                                </MDBBtn>
                            </td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

            {/* 고객사 추가 버튼 */}
            <div style={{ display: "flex", justifyContent: "flex-end", padding: "20px 30px" }}>
                <MDBBtn color="success" onClick={() => toggleModal("add")}>
                    고객사 추가
                </MDBBtn>
            </div>

            {/* Client Edit/Delete/Add Modal */}
            <MDBModal open={modal} onClose={() => setModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>
                                고객사 {modalType === "add" ? "추가" : modalType === "edit" ? "수정" : "삭제"}
                            </MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            {modalType === "delete" ? (
                                <p>정말로 '{currentClient.name}' 고객사를 삭제하시겠습니까?</p>
                            ) : (
                                <>
                                    <MDBInput
                                        label="고객사 코드"
                                        name="clientCode"
                                        value={currentClient.client_code}
                                        onChange={handleInputChange}
                                        disabled={true}
                                        className="mb-3"
                                    />
                                    <MDBInput
                                        label="이름"
                                        name="name"
                                        value={currentClient.name}
                                        onChange={handleInputChange}
                                        className="mb-3"
                                    />
                                    <MDBInput
                                        label="주소"
                                        name="address"
                                        value={currentClient.address}
                                        onChange={handleInputChange}
                                        className="mb-3"
                                    />
                                </>
                            )}
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setModal(false)}>
                                취소
                            </MDBBtn>
                            {modalType === "delete" ? (
                                <MDBBtn color="danger" onClick={handleDelete}>
                                    삭제
                                </MDBBtn>
                            ) : (
                                <MDBBtn color="primary" onClick={handleSave}>
                                    저장
                                </MDBBtn>
                            )}
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

            {/* Option Modal for License/Hardware */}
            <MDBModal open={optionModal} onClose={() => setOptionModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>{currentClient.name}의 정보 보기 {currentClient.client_code}</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setOptionModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <p>어떤 정보를 열람하시겠습니까?</p>
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="info" onClick={() => openNewTab("license")}>라이선스 보기</MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>
        </div>
    );
}