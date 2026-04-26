import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    MDBTable,
    MDBTableBody,
    MDBTableHead,
    MDBBtn,
    MDBModal,
    MDBModalBody,
    MDBModalDialog,
    MDBModalContent,
    MDBModalFooter,
    MDBModalHeader,
    MDBModalTitle,
} from "mdb-react-ui-kit";

export default function ClientUserAccountView({ supportCode }) {
    const [userAccounts, setUserAccounts] = useState([]);
    const [deleteModal, setDeleteModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);

    // 사용자 계정 데이터 가져오기
    const fetchUserAccounts = async () => {
        try {
            const url = supportCode
                ? `${process.env.REACT_APP_API_BASE_URL}/client/user/list?supportCode=${supportCode}`
                : `${process.env.REACT_APP_API_BASE_URL}/client/user/list`;
            const response = await axios.get(url);
            setUserAccounts(response.data);
        } catch (error) {
            console.error("사용자 계정 데이터를 가져오는 중 오류 발생", error);
        }
    };

    // 삭제 요청 처리
    const handleDeleteUser = async () => {
        if (!selectedUser) return;

        try {
            await axios.post(`${process.env.REACT_APP_API_BASE_URL}/client/user/delete`, {
                support_code: selectedUser.support_code,
                email: selectedUser.email
            });
            alert("사용자 계정이 삭제되었습니다.");
            setUserAccounts((prevAccounts) =>
                prevAccounts.filter((user) => user.id !== selectedUser.id)
            );
            setDeleteModal(false);
            setSelectedUser(null);
        } catch (error) {
            console.error("사용자 계정 삭제 중 오류 발생", error);
            alert("삭제 중 오류가 발생했습니다.");
        }
    };

    useEffect(() => {
        fetchUserAccounts();
    }, [supportCode]);

    return (
        <div className="content-component">
            <MDBTable responsive="lg" hover>
                <MDBTableHead>
                    <tr>
                        <th>이메일</th>
                        <th>라이선스 코드</th>
                        <th>생성일</th>
                        <th>마지막 로그인</th>
                        <th>관리</th>
                    </tr>
                </MDBTableHead>
                <MDBTableBody>
                    {userAccounts.map((user) => (
                        <tr key={user.id}>
                            <td>{user.email}</td>
                            <td>{user.support_code}</td>
                            <td>{new Date(user.created_at).toLocaleString()}</td>
                            <td>{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "N/A"}</td>
                            <td>
                                <MDBBtn
                                    color="danger"
                                    size="sm"
                                    onClick={() => {
                                        setSelectedUser(user);
                                        setDeleteModal(true);
                                    }}
                                >
                                    삭제
                                </MDBBtn>
                            </td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

            {/* 삭제 확인 모달 */}
            <MDBModal open={deleteModal} onClose={() => setDeleteModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>계정 삭제</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setDeleteModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <p>
                                정말로 '{selectedUser?.email}' 계정을 삭제하시겠습니까?
                            </p>
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setDeleteModal(false)}>
                                취소
                            </MDBBtn>
                            <MDBBtn color="danger" onClick={handleDeleteUser}>
                                삭제
                            </MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>
        </div>
    );
}