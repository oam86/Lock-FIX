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
    MDBInput,
    MDBListGroup,
    MDBListGroupItem
} from "mdb-react-ui-kit";
import { formatDateTime } from "../../component/util/dateutils";

export default function LicenseView({ clientCode }) {
    const [licenses, setLicenses] = useState([]);
    const [editModal, setEditModal] = useState(false);
    const [deleteModal, setDeleteModal] = useState(false);
    const [createModal, setCreateModal] = useState(false);
    const [clientSelectModal, setClientSelectModal] = useState(false);
    const [selectedLicense, setSelectedLicense] = useState(null);
    const [updatedExpirationAt, setUpdatedExpirationAt] = useState("");
    const [newLicense, setNewLicense] = useState({
        support_code: "",
        client_code: clientCode || "",
        expiration_at: "",
    });
    const [optionModal, setOptionModal] = useState(false);


    const [clients, setClients] = useState([]); // 고객사 리스트

    const fetchLicenses = async () => {
        try {
            const url = clientCode
                ? `${process.env.REACT_APP_API_BASE_URL}/licenses/client-list?clientCode=${clientCode}`
                : `${process.env.REACT_APP_API_BASE_URL}/licenses/list`;
            const response = await axios.get(url);
            setLicenses(response.data);
        } catch (error) {
            console.error("라이선스를 가져오는 중 오류가 발생했습니다.", error);
        }
    };

    const fetchClients = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/clients/list`);
            setClients(response.data);
        } catch (error) {
            console.error("고객사 데이터를 가져오는 중 오류가 발생했습니다.", error);
        }
    };


    useEffect(() => {
        fetchLicenses();
        fetchClients();
    }, [clientCode]);

    // 라이선스 생성 모달 열기
    const openCreateModal = () => {
        setNewLicense({ support_code: "", client_code: clientCode || "", expiration_at: "" });
        setCreateModal(true);
    };

    // 라이선스 수정 모달 열기
    const openEditModal = (license) => {
        setSelectedLicense(license);
        setUpdatedExpirationAt(license.expiration_at);
        setEditModal(true);
    };

    // 라이선스 삭제 모달 열기
    const openDeleteModal = (license) => {
        setSelectedLicense(license);
        setDeleteModal(true);
    };

    const openNewTab = (type) => {

        let url

        switch (type) {
            case "hardware":
                url = `/client-hardware-list?supportCode=${selectedLicense.support_code}`
                break
            case "account":
                url = `/client-account?supportCode=${selectedLicense.support_code}`
                break
        }

        window.open(url, "_blank");
        setOptionModal(false);
    };

    // 만료일자 수정 처리 함수
    const handleUpdateExpirationAt = async () => {
        setEditModal(false);

        try {
            selectedLicense.expiration_at = updatedExpirationAt;
            await axios.put(`${process.env.REACT_APP_API_BASE_URL}/licenses/update`, selectedLicense);
            alert("만료일자가 수정되었습니다.");

            setLicenses((prevLicenses) =>
                prevLicenses.map((license) =>
                    license.support_code === selectedLicense.support_code
                        ? { ...license, expiration_at: updatedExpirationAt }
                        : license
                )
            );
        } catch (error) {
            console.error("만료일자 수정 중 오류가 발생했습니다.", error);
            alert("수정 중 오류가 발생했습니다.");
        }
    };

    // 라이선스 삭제 처리 함수
    const handleDeleteLicense = async () => {
        setDeleteModal(false);
        try {
            await axios.post(`${process.env.REACT_APP_API_BASE_URL}/licenses/delete`, selectedLicense);
            alert("라이선스가 삭제되었습니다.");
            setLicenses((prevLicenses) =>
                prevLicenses.filter((license) => license.support_code !== selectedLicense.support_code)
            );
        } catch (error) {
            console.error("라이선스 삭제 중 오류가 발생했습니다.", error);
            alert("삭제 중 오류가 발생했습니다.");
        }
    };

    // 고객사 선택 모달 열기
    const openClientSelectModal = () => {
        setClientSelectModal(true);
    };

    // 고객사 선택 처리
    const handleClientSelect = (client) => {
        setNewLicense({ ...newLicense, client_code: client.client_code });
        setClientSelectModal(false);
    };

    // 라이선스 생성 처리
    const handleCreateLicense = async () => {
        if (!newLicense.support_code || !newLicense.client_code || !newLicense.expiration_at) {
            alert("모든 필드를 입력해주세요.");
            return;
        }

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_BASE_URL}/licenses/create`,
                newLicense
            );
            alert("라이선스가 생성되었습니다.");
            setLicenses((prevLicenses) => [...prevLicenses, response.data]);
            setCreateModal(false);
        } catch (error) {
            console.error("라이선스 생성 중 오류가 발생했습니다.", error);
            alert("라이선스 생성 중 오류가 발생했습니다.");
        }
    };

    const openOptionModal = (license) => {
        setSelectedLicense(license);
        setOptionModal(true);
    };



    return (
        <div className="content-component">
            <MDBBtn color="success" onClick={openCreateModal}>
                라이선스 생성
            </MDBBtn>
            <MDBTable responsive="lg" hover className="mt-3">
                <MDBTableHead>
                    <tr>
                        <th scope="col">지원 코드</th>
                        <th scope="col">고객사</th>
                        <th scope="col">만료일</th>
                        <th scope="col">생성일</th>
                        <th scope="col">갱신일</th>
                        <th scope="col">사용 시작일</th>
                        <th scope="col">관리</th>
                    </tr>
                </MDBTableHead>
                <MDBTableBody>
                    {licenses.map((license) => (
                        <tr key={license.support_code} onClick={() => openOptionModal(license)} style={{ cursor: "pointer" }}>
                            <td>{license.support_code}</td>
                            <td>{license.client?.name || "N/A"}</td>
                            <td>{formatDateTime(license.expiration_at) || "N/A"}</td>
                            <td>{formatDateTime(license.created_at)}</td>
                            <td>{formatDateTime(license.updated_at)}</td>
                            <td>{formatDateTime(license.used_at) || "N/A"}</td>
                            <td>
                                <MDBBtn color="primary" size="sm" onClick={(e) => { e.stopPropagation(); openEditModal(license);                                 }}>
                                    수정
                                </MDBBtn>
                                <MDBBtn color="danger" size="sm" onClick={(e) => { e.stopPropagation(); openDeleteModal(license);                                 }}>
                                    삭제
                                </MDBBtn>
                            </td>
                        </tr>
                    ))}
                </MDBTableBody>
            </MDBTable>

            {/* 라이선스 생성 모달 */}
            <MDBModal open={createModal} onClose={() => setCreateModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>라이선스 생성</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setCreateModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <MDBInput
                                label="지원 코드"
                                type="text"
                                value={newLicense.support_code}
                                onChange={(e) =>
                                    setNewLicense({ ...newLicense, support_code: e.target.value })
                                }
                                className="mb-3"
                            />
                            <MDBInput
                                label="고객 코드"
                                type="text"
                                value={newLicense.client_code}
                                readOnly
                                className="mb-3"
                            />
                            <MDBBtn color="info" onClick={openClientSelectModal}>
                                고객사 선택
                            </MDBBtn>
                            <MDBInput
                                label="만료일자"
                                type="date"
                                value={newLicense.expiration_at}
                                onChange={(e) =>
                                    setNewLicense({ ...newLicense, expiration_at: e.target.value })
                                }
                                className="mb-3"
                            />
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setCreateModal(false)}>
                                취소
                            </MDBBtn>
                            <MDBBtn color="success" onClick={handleCreateLicense}>
                                생성
                            </MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

            {/* 고객사 선택 모달 */}
            <MDBModal open={clientSelectModal} onClose={() => setClientSelectModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>고객사 선택</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setClientSelectModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <MDBListGroup>
                                {clients.map((client) => (
                                    <MDBListGroupItem
                                        key={client.client_code}
                                        onClick={() => handleClientSelect(client)}
                                        style={{ cursor: "pointer" }}
                                    >
                                        {client.name} ({client.client_code})
                                    </MDBListGroupItem>
                                ))}
                            </MDBListGroup>
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setClientSelectModal(false)}>
                                닫기
                            </MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

            {/* 만료일자 수정 모달 */}
            <MDBModal open={editModal} onClose={() => setEditModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>만료일자 수정</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setEditModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <MDBInput
                                label="만료일자"
                                type="date"
                                value={updatedExpirationAt}
                                onChange={(e) => setUpdatedExpirationAt(e.target.value)}
                                className="mb-3"
                            />
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setEditModal(false)}>취소</MDBBtn>
                            <MDBBtn color="primary" onClick={handleUpdateExpirationAt}>저장</MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

            {/* 삭제 확인 모달 */}
            <MDBModal open={deleteModal} onClose={() => setDeleteModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>라이선스 삭제</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setDeleteModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <p>정말로 '{selectedLicense?.support_code}' 라이선스를 삭제하시겠습니까?</p>
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => setDeleteModal(false)}>취소</MDBBtn>
                            <MDBBtn color="danger" onClick={handleDeleteLicense}>삭제</MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

            {/* Option Modal for License/Hardware */}
            <MDBModal open={optionModal} onClose={() => setOptionModal(false)} backdrop={false} tabIndex="-1">
                <MDBModalDialog centered>
                    <MDBModalContent>
                        <MDBModalHeader>
                            <MDBModalTitle>{selectedLicense?.support_code} 의 라이선스 관련 정보 확인</MDBModalTitle>
                            <MDBBtn className="btn-close" color="none" onClick={() => setOptionModal(false)}></MDBBtn>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <p>어떤 정보를 열람하시겠습니까?</p>
                        </MDBModalBody>
                        <MDBModalFooter>
                            <MDBBtn color="secondary" onClick={() => openNewTab("hardware")}>초기 설정 하드웨어 보기</MDBBtn>
                            <MDBBtn color="dark" onClick={() => openNewTab("account")}>관리자 계정보기</MDBBtn>
                        </MDBModalFooter>
                    </MDBModalContent>
                </MDBModalDialog>
            </MDBModal>

        </div>
    );
}