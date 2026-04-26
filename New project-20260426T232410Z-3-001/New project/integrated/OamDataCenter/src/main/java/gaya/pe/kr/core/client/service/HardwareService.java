package gaya.pe.kr.core.client.service;

import gaya.pe.kr.core.client.dto.HardwareDTO;
import gaya.pe.kr.core.client.entity.HardWareEntity;
import gaya.pe.kr.core.client.repository.HardwareRepository;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Slf4j
public class HardwareService {

    private final HardwareRepository hardwareRepository;

    public HardwareService(HardwareRepository hardwareRepository) {
        this.hardwareRepository = hardwareRepository;
    }

    // 전체 하드웨어 목록 조회
    public List<HardWareEntity> getAllHardware() {
        return hardwareRepository.findAll();
    }

    // 특정 고객사의 하드웨어 목록 조회
    public List<HardWareEntity> getHardwareByClientCode(String clientCode) {
        return hardwareRepository.findByLicenseInfo_Client_ClientCode(clientCode);
    }

    public List<HardWareEntity> getHardwareByClientCode(LicenseInfoEntity licenseInfo) {
        return hardwareRepository.findByLicenseInfo_SupportCode(licenseInfo.getSupportCode());
    }

    @Transactional
    public boolean addHardware(List<HardwareDTO> list, LicenseInfoEntity licenseInfo) {

        for (HardwareDTO hardwareDTO : list) {
            HardWareEntity hardWareEntity = new HardWareEntity();
            hardWareEntity.setType(hardwareDTO.getType());
            hardWareEntity.setModel(hardwareDTO.getModel());
            hardWareEntity.setDeliveryAt(LocalDateTime.now());
            hardWareEntity.setSerialNumber(hardwareDTO.getSerial());
            hardWareEntity.setLicenseInfo(licenseInfo);
            log.info("HW ADD {} : {}", licenseInfo.getSupportCode(), hardWareEntity.toString());
            hardwareRepository.save(hardWareEntity);
        }

        return true;


    }

    public void save(HardWareEntity hardWareEntity){
        hardwareRepository.save(hardWareEntity);
    }

    @Transactional
    public void delete(List<HardWareEntity> hardWareEntities) {
        hardwareRepository.deleteAll(hardWareEntities);
    }

    // 특정 라이선스에 단일 하드웨어 추가
//    public HardWareEntity addHardwareToLicense(String supportCode, HardWareEntity hardware) {
//        Optional<LicenseInfoEntity> licenseOpt = licenseService.getLicenseById(supportCode);
//
//        if (licenseOpt.isPresent()) {
//            LicenseInfoEntity license = licenseOpt.get();
//            hardware.setLicenseInfo(license);
//            hardware.setDeliveryAt(LocalDateTime.now()); // 납품 일자를 현재 시간으로 설정
//            return hardwareRepository.save(hardware); // 하드웨어 저장
//        } else {
//            throw new IllegalArgumentException("해당 라이선스 코드가 존재하지 않습니다: " + supportCode);
//        }
//    }
//
//    // 특정 라이선스에 다수의 하드웨어 추가
//    public List<HardWareEntity> addMultipleHardwareToLicense(String supportCode, List<HardWareEntity> hardwareList) {
//        Optional<LicenseInfoEntity> licenseOpt = licenseService.getLicenseById(supportCode);
//
//        if (licenseOpt.isPresent()) {
//            LicenseInfoEntity license = licenseOpt.get();
//
//            // 각 하드웨어에 라이선스 정보 및 납품 일자를 설정하고 저장
//            hardwareList.forEach(hardware -> {
//                hardware.setLicenseInfo(license);
//                hardware.setDeliveryAt(LocalDateTime.now());
//            });
//
//            return hardwareRepository.saveAll(hardwareList);
//        } else {
//            throw new IllegalArgumentException("해당 라이선스 코드가 존재하지 않습니다: " + supportCode);
//        }
//    }
}