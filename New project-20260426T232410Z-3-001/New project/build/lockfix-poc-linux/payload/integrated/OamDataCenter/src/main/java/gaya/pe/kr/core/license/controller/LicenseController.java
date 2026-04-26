package gaya.pe.kr.core.license.controller;

import gaya.pe.kr.core.client.entity.ClientEntity;
import gaya.pe.kr.core.client.service.ClientService;
import gaya.pe.kr.core.license.dto.LicenseInfoDTO;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.service.LicenseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/java_api/licenses")
@Slf4j
@Tag(name = "라이선스 관리", description = "고객사의 라이선스를 추가, 수정, 삭제 및 조회할 수 있는 API입니다.")
public class LicenseController {

    private final LicenseService licenseInfoService;
    private final ClientService clientService;

    @Autowired
    public LicenseController(LicenseService licenseInfoService, ClientService clientService) {
        this.licenseInfoService = licenseInfoService;
        this.clientService = clientService;
    }

    @GetMapping("/list")
    @Operation(summary = "전체 라이선스 목록", description = "서버에 등록된 모든 라이선스의 목록을 반환합니다.")
    public List<LicenseInfoEntity> getAllLicenses() {
        return licenseInfoService.getAllLicenses();
    }

    @GetMapping("/client-list")
    @Operation(summary = "고객사의 라이선스 목록", description = "특정 고객사의 라이선스 목록을 반환합니다")
    public List<LicenseInfoEntity> getLicensesByClientCode(
            @Parameter(name = "고객사 코드", description = "라이선스를 조회할 고객사의 코드")
            @RequestParam String clientCode) {
        return licenseInfoService.getLicensesByClientCode(clientCode);
    }

    @PostMapping("/create")
    @Operation(summary = "라이선스 생성", description = "고객사에 새로운 라이선스를 생성하고 등록합니다")
    public ResponseEntity<LicenseInfoEntity> createLicense(
            @Parameter(name = "라이선스 정보", description = "고객사 코드, 지원 코드, 만료일자 등의 정보가 포함된 DTO")
            @RequestBody LicenseInfoDTO licenseDTO) {


        // clientCode를 기반으로 ClientEntity 조회
        Optional<ClientEntity> client = clientService.getClientById(licenseDTO.getClientCode());
        if (client.isEmpty()) {
            log.error("{} client code is not exist", licenseDTO.getClientCode());
            return ResponseEntity.badRequest().build();
        }

        // 중복된 라이선스 지원 코드 확인
        Optional<LicenseInfoEntity> existingLicense = licenseInfoService.getLicenseById(licenseDTO.getSupportCode());
        if (existingLicense.isPresent()) {
            log.error("{} support code is already exist", licenseDTO.getSupportCode());
            return ResponseEntity.badRequest().body(existingLicense.get());
        }

        // DTO를 LicenseInfoEntity로 변환
        LicenseInfoEntity license = new LicenseInfoEntity();
        license.setSupportCode(licenseDTO.getSupportCode());
        license.setClient(client.get()); // 매핑된 ClientEntity 설정
        license.setExpirationAt(licenseDTO.getExpirationAt());

        // 라이선스 생성 및 등록
        LicenseInfoEntity newLicense = licenseInfoService.createLicense(license);
        log.info("Create new license : {}", newLicense);
        return ResponseEntity.ok(newLicense);
    }

    @PutMapping("/update")
    @Operation(summary = "라이선스 업데이트", description = "등록된 라이선스 정보를 갱신합니다")
    public ResponseEntity<LicenseInfoEntity> updateLicense(
            @Parameter(name = "라이선스 정보", description = "수정할 라이선스 정보가 포함된 엔티티")
            @RequestBody LicenseInfoEntity license) {
        licenseInfoService.updateLicense(license);
        return ResponseEntity.ok(license);
    }

    @PostMapping("/delete")
    @Operation(summary = "라이선스 삭제", description = "등록된 라이선스 정보를 삭제합니다.")
    public ResponseEntity<Boolean> deleteLicense(
            @Parameter(name = "라이선스 정보", description = "삭제할 라이선스 정보가 포함된 엔티티")
            @RequestBody LicenseInfoEntity license) {
        licenseInfoService.deleteLicense(license);
        return ResponseEntity.ok(true);
    }
}