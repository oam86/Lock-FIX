package gaya.pe.kr.core.client.repository;

import gaya.pe.kr.core.client.entity.ClientEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClientRepository extends JpaRepository<ClientEntity, String> {

    boolean existsByName(String name); // 이름 중복 검사
}