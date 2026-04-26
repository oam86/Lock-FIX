package gaya.pe.kr.core.license.service;

import gaya.pe.kr.core.client.entity.ClientUserAccountEntity;
import gaya.pe.kr.core.client.repository.ClientUserAccountRepository;
import gaya.pe.kr.core.client.service.HardwareService;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.repository.LicenseRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class LicenseService {

    private final LicenseRepository licenseRepository;
    private final HardwareService hardwareService;

    private final ClientUserAccountRepository clientUserAccountRepository;

    @Autowired
    public LicenseService(LicenseRepository licenseRepository, HardwareService hardwareService, ClientUserAccountRepository clientUserAccountRepository) {
        this.licenseRepository = licenseRepository;
        this.hardwareService = hardwareService;
        this.clientUserAccountRepository = clientUserAccountRepository;
    }

    public List<LicenseInfoEntity> getAllLicenses() {
        return licenseRepository.findAll();
    }

    public List<LicenseInfoEntity> getLicensesByClientCode(String clientCode) {
        return licenseRepository.findByClientClientCode(clientCode);
    }

    public Optional<LicenseInfoEntity> getLicenseById(String supportCode) {
        return licenseRepository.findById(supportCode);
    }

    public LicenseInfoEntity createLicense(LicenseInfoEntity license) {
        return licenseRepository.save(license);
    }

    public LicenseInfoEntity updateLicense(LicenseInfoEntity license) {
        return licenseRepository.save(license);
    }

    public void deleteLicense(LicenseInfoEntity licenseInfo) {
        hardwareService.delete(hardwareService.getHardwareByClientCode(licenseInfo));
        licenseRepository.deleteById(licenseInfo.getSupportCode());
    }

    @Transactional
    public void deleteLicense(List<LicenseInfoEntity> licenseInfoEntities) {


        for (LicenseInfoEntity licenseInfoEntity : licenseInfoEntities) {
            hardwareService.delete(hardwareService.getHardwareByClientCode(licenseInfoEntity)); // 하드웨어 제거
            List<ClientUserAccountEntity> clientUserList = clientUserAccountRepository.findBySupportCode(licenseInfoEntity.getSupportCode());
            clientUserAccountRepository.deleteAll(clientUserList); // 라이선스와 연계된 관리자 계정 제거
        }
        licenseRepository.deleteAll(licenseInfoEntities); // 라이선스 최종 제거

    }

}