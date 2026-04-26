package gaya.pe.kr.core.client.repository;

import gaya.pe.kr.core.client.entity.HardWareEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface HardwareRepository extends JpaRepository<HardWareEntity, Long> {
    // `licenseInfo`를 경유하여 `client.clientCode`에 접근
    List<HardWareEntity> findByLicenseInfo_Client_ClientCode(String clientCode); // 특정 clientCode의 하드웨어 목록 조회
    List<HardWareEntity> findByLicenseInfo_SupportCode(String supportCode);


}   