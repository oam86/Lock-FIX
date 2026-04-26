package gaya.pe.kr.core.client.repository;

import gaya.pe.kr.core.client.entity.ClientUserAccountEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ClientUserAccountRepository extends JpaRepository<ClientUserAccountEntity, String> {

    // 이메일과 고객사 코드로 사용자 조회
    Optional<ClientUserAccountEntity> findByEmailAndSupportCode(String email, String supportCode);

    // 특정 고객사의 사용자 목록 조회
    List<ClientUserAccountEntity> findBySupportCode(String supportCode);


}