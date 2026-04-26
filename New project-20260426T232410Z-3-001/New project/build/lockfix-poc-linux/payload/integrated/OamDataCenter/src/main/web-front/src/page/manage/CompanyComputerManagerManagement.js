import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    MDBBtn,
    MDBIcon,
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
    MDBTableHead,
    MDBTooltip
} from "mdb-react-ui-kit";

export default function CompanyManagerManagement() {
    const [managers, setManagers] = useState([]);
    const [modal, setModal] = useState(false);
    const [modalType, setModalType] = useState("");
    const [currentManager, setCurrentManager] = useState({
        id: null,
        name: "",
        position: "",
        department: "",
        email: ""
    });

    const fetchManagers = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/managers/list`);
            setManagers(response.data);
        } catch (error) {
            console.error("데이터를 가져오는 중 오류가 발생했습니다.", error);
        }
    };

    useEffect(() => {
        fetchManagers();
    }, []);

    const toggleModal = (type = "", manager = {}) => {
        setModal(!modal);
        setModalType(type);
        setCurrentManager(manager);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setCurrentManager((prev) => ({ ...prev, [name]: value }));
    };

    const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    const handleSave = async () => {
        if ( !currentManager.name || !currentManager.email) {
            alert("모든 필드를 채워주세요.");
            return;
        }

        if (!validateEmail(currentManager.email)) {
            alert("올바른 이메일 형식을 입력해 주세요.");
            return;
        }

        try {
            toggleModal();
            if (modalType === "add") {
                await axios.post(`${process.env.REACT_APP_API_BASE_URL}/managers/create`, currentManager);
                alert("추가가 완료되었습니다");
            } else if (modalType === "edit") {
                await axios.post(`${process.env.REACT_APP_API_BASE_URL}/managers/update`, currentManager);
                alert("수정이 완료되었습니다");
            }
            fetchManagers();
        } catch (error) {
            console.error("데이터 저장 중 오류가 발생했습니다.", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    const handleDelete = async () => {
        try {
            toggleModal();
            await axios.post(`${process.env.REACT_APP_API_BASE_URL}/managers/delete`, currentManager);
            alert("삭제가 완료되었습니다");
            fetchManagers();
        } catch (error) {
            console.error("데이터 삭제 중 오류가 발생했습니다.", error);
            alert("삭제 중 오류가 발생했습니다.");
        }
    };

    return (
        <div className='content-component'>
            <MDBTable responsive="lg" hover>
                <MDBTableHead>
                    <tr>
                        <th scope="col">ID</th>
                        <th scope="col">이름</th>
                        <th scope="col">직위</th>
                        <th scope="col">부서</th>
                        <th scope="col">이메일</th>
                        <td scope="col">관리</td>
                    </tr>
                </MDBTableHead>
                <MDBTableBody style={{ textAlign: "center", verticalAlign: "middle" }}>
                    {managers.map((manager, index) => (
                        <tr key={index}>
                            <td>{manager.id}</td>
                            <td>{manager.name}</td>
                            <td>{manager.position}</td>
                            <td>{manager.department}</td>
                            <td>{manager.email}</td>
                            <td>
                                <MDBBtn color="info" size="sm" onClick={() => toggleModal("edit", manager)}>
                                    수정
                                </MDBBtn>{" "}
                                <MDBBtn color="danger" size="sm" onClick={() => toggleModal("delete", manager)}>
                                    삭제
                                </MDBBtn>
                            </td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

            <div style={{ display: "flex", justifyContent: "flex-end", paddingRight: "30px" }}>
                <MDBBtn color="success" onClick={() => toggleModal("add")}>
                    관리자 추가
                </MDBBtn>
            </div>

            {/* 모달 */}
            <MDBModal open={modal} onClose={() => setModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>
                                {modalType === "add" ? "관리자 추가" : modalType === "edit" ? "관리자 수정" : "관리자 삭제"}
                            </MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => toggleModal()}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            {modalType === "delete" ? (
                                <p>정말로 '{currentManager.name}'을(를) 삭제하시겠습니까?</p>
                            ) : (
                                <>
                                    <MDBInput label="이름" name="name" value={currentManager.name} onChange={handleInputChange} className="mb-3" />
                                    <MDBInput label="직위" name="position" value={currentManager.position} onChange={handleInputChange} className="mb-3" />
                                    <MDBInput label="부서" name="department" value={currentManager.department} onChange={handleInputChange} className="mb-3" />
                                    <MDBInput label="이메일" name="email" value={currentManager.email} onChange={handleInputChange} className="mb-3" />
                                </>
                            )}
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => toggleModal()}>
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
        </div>
    );
}