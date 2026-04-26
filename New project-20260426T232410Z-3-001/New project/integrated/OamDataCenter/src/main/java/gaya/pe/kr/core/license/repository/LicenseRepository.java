package gaya.pe.kr.core.license.repository;

import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LicenseRepository extends JpaRepository<LicenseInfoEntity, String> {
    List<LicenseInfoEntity> findByClientClientCode(String clientCode);
}