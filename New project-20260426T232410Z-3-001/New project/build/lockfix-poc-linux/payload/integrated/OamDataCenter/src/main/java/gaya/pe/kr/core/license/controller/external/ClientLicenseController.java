package gaya.pe.kr.core.license.controller.external;


import gaya.pe.kr.core.client.dto.HardwareDTO;
import gaya.pe.kr.core.client.service.HardwareService;
import gaya.pe.kr.core.license.dto.LicenseHardwareRegisterDTO;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.service.LicenseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController()
@RequestMapping("/java_api/external/license")
@Tag(name = "[외부접근] 라이선스 동기화 및 사용", description = "고객사에서 라이선스를 사용하거나, 만료일자 획득을 통해 라이선스 정보를 동기화 하는 API 입니다")
public class ClientLicenseController {

    private final LicenseService licenseService;
    private final HardwareService hardwareService;

    @Autowired
    public ClientLicenseController(LicenseService licenseService, HardwareService hardwareService) {
        this.licenseService = licenseService;
        this.hardwareService = hardwareService;
    }

    @PostMapping("/register")
    @Operation(summary = "라이선스 사용", description = "고객사 측에서 라이선스를 사용하기 위해, 요청을 하는 API 입니다")
    public ResponseEntity<LicenseInfoEntity> useLicense(@Parameter(name = "라이선스 키 값 및 고객사 하드웨어 정보", description = "초기 하드웨어 설정을 위한 데이터와 라이선스 키 값이 내제된 데이터 뭉치입니다") @RequestBody LicenseHardwareRegisterDTO request) {
        String supportCode = request.getSupportCode();
        List<HardwareDTO> hardwareData = request.getHardwareData();

        log.info("Register[Start] License Request Support Code : {}", supportCode);

        Optional<LicenseInfoEntity> licenseInfoEntityOptional = licenseService.getLicenseById(supportCode);

        if ( licenseInfoEntityOptional.isEmpty() ) {
            log.info("{} is not exist support code", supportCode);
            return ResponseEntity.badRequest().body(null);
        }

        LicenseInfoEntity licenseInfo = licenseInfoEntityOptional.get();

        if ( licenseInfo.getUsedAt() != null ) {
            //이미 사용한 라이선스
            log.info("{} is already used", supportCode);
            return ResponseEntity.badRequest().body(null);
        }

        for (HardwareDTO hardwareDatum : hardwareData) {
            log.info("[{}] Request HW : {} ",licenseInfo.getClient().getName() , hardwareDatum);
        }
        hardwareService.addHardware(hardwareData, licenseInfo );
        log.info("[{}] Input all h/w information to database ",licenseInfo.getClient().getName());
        licenseInfo.setUsedAt(LocalDateTime.now());
        licenseService.updateLicense(licenseInfo); // 라이선스 업데잉트
        log.info("{} support code update", supportCode);
        return ResponseEntity.ok(licenseInfoEntityOptional.get());
    }
    @PostMapping("/expireDate")
    @Operation(summary = "라이선스 만료 일자 요청", description = "특정 라이선스의 만료일자를 반환합니다")
    public ResponseEntity<String> getExpireDate(@RequestBody Map<String,String> data) {

        String supportCode = data.get("supportCode");
        Optional<LicenseInfoEntity> licenseInfoEntityOptional = licenseService.getLicenseById(supportCode);
        // 라이선스가 없다면 존재하지 않음을 반환한다.
        return licenseInfoEntityOptional.map(licenseInfo -> ResponseEntity.ok(licenseInfo.getExpirationAt().toString())).orElseGet(() -> ResponseEntity.status(HttpStatusCode.valueOf(400)).body(null));

    }


}
