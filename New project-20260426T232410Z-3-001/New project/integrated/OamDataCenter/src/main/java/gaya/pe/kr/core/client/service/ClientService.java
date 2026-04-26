package gaya.pe.kr.core.client.service;

import gaya.pe.kr.core.client.dto.ClientDTO;
import gaya.pe.kr.core.client.entity.ClientEntity;
import gaya.pe.kr.core.client.repository.ClientRepository;
import gaya.pe.kr.core.client.repository.ClientUserAccountRepository;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.service.LicenseService;
import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class ClientService {

    @Autowired
    private ClientRepository clientRepository;

    @Autowired
    private LicenseService licenseService;

    @Autowired
    private HardwareService hardwareService;

    @Autowired
    private ClientUserAccountRepository userAccountRepository;


    // 모든 고객사 목록 가져오기
    public List<ClientEntity> getAllClients() {
        return clientRepository.findAll();
    }

    // 고객사 ID로 특정 고객사 정보 가져오기
    public Optional<ClientEntity> getClientById(String clientCode) {
        return clientRepository.findById(clientCode);
    }

    // 고객사 정보 생성
    public ClientEntity createClient(ClientDTO clientDTO) {

        ClientEntity client = new ClientEntity();
        client.setClientCode(RandomStringUtils.randomAlphabetic(8));
        client.setCreatedAt(LocalDateTime.now());
        client.setName(clientDTO.getName());
        client.setAddress(clientDTO.getAddress());

        return clientRepository.save(client);
    }

    // 고객사 정보 업데이트
    public ClientEntity updateClient(ClientEntity client) {
        return clientRepository.save(client);
    }

    // 고객사 삭제
    @Transactional
    public void deleteClient(String clientCode) {

        for (LicenseInfoEntity licenseInfoEntity : licenseService.getLicensesByClientCode(clientCode)) {
            userAccountRepository.deleteAll(userAccountRepository.findBySupportCode(licenseInfoEntity.getSupportCode()));
            licenseService.deleteLicense(licenseInfoEntity);
        }

        clientRepository.deleteById(clientCode); // 최종 제거
    }

    // 이름 중복 확인
    public boolean isNameDuplicate(String name) {
        return clientRepository.existsByName(name);
    }


}