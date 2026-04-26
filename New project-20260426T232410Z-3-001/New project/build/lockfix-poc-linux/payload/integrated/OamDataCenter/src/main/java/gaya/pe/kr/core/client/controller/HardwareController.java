package gaya.pe.kr.core.client.controller;

import gaya.pe.kr.core.client.entity.HardWareEntity;
import gaya.pe.kr.core.client.service.HardwareService;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.service.LicenseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/java_api/hardware")
@Slf4j
@Tag(name = "납품한 하드웨어 관리", description = "외부 접근을 통해 전달된 고객사의 하드웨어 정보를 확인하는 API 입니다")
public class HardwareController {

    private final HardwareService hardwareService;
    private final LicenseService licenseService;

    @Autowired
    public HardwareController(HardwareService hardwareService, LicenseService licenseService) {
        this.hardwareService = hardwareService;
        this.licenseService = licenseService;
    }

    // 전체 하드웨어 목록 조회 엔드포인트
    @GetMapping("/all")
    @Operation(summary = "하드웨어 전체 목록 반환", description = "서버에 등록된 전체 고객사의 전체 하드웨어 목록을 반환합니다")
    public List<HardWareEntity> getAllHardware() {
        return hardwareService.getAllHardware(); // 전체 하드웨어 목록
    }

    @GetMapping("/list")
    @Operation(summary = "하드웨어 목록 반환", description = "서버에 등록된 특정 고객사의 전체 하드웨어 목록을 반환합니다")
    public List<HardWareEntity> getAllHardwareBySupportCode(@Parameter(name = "라이선스 키", description = "특정 고객사를 지칭하기 위한 라이선스 값입니다", required = true) @RequestParam String supportCode) {

        Optional<LicenseInfoEntity> licenseInfoEntityOptional = licenseService.getLicenseById(supportCode);

        if (licenseInfoEntityOptional.isPresent()) {
            LicenseInfoEntity licenseInfo = licenseInfoEntityOptional.get();
            return hardwareService.getHardwareByClientCode(licenseInfo);
        } else {
            return List.of();
        }
    }

}