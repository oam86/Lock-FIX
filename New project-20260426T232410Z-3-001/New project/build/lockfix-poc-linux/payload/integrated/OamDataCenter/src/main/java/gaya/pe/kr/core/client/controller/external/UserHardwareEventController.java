package gaya.pe.kr.core.client.controller.external;

import gaya.pe.kr.core.client.dto.external.HardwareChangeEventRequest;
import gaya.pe.kr.core.client.entity.ClientEntity;
import gaya.pe.kr.core.company.entity.CompanyComputerManagerEntity;
import gaya.pe.kr.core.company.mail.MailService;
import gaya.pe.kr.core.company.service.CompanyComputerManagerService;
import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import gaya.pe.kr.core.license.service.LicenseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@Slf4j
@RequestMapping("/java_api/external/notify")
@Tag(name = "[외부접근] 하드웨어 변경 감지", description = "고객사 측에서 하드웨어의 변경이 감지되면 호출합니다")
public class UserHardwareEventController {

    private final CompanyComputerManagerService companyComputerManagerService;
    private final MailService mailService;

    private final LicenseService licenseService;

    @Autowired
    public UserHardwareEventController(CompanyComputerManagerService companyComputerManagerService, MailService mailService, LicenseService licenseService) {
        this.companyComputerManagerService = companyComputerManagerService;
        this.mailService = mailService;
        this.licenseService = licenseService;
    }


    @PostMapping("/event")
    @Operation(summary = "하드웨어 감지 호출", description = "감지 신호가 확인되면, 등록된 전산 담당자들에게 이메일이 전송됩니다")
    public ResponseEntity<String> receiveHardwareChangeEvents(@Parameter(name = "하드웨어 변경 데이터", description = "라이선스 키값과 변경된 하드웨어의 전체 데이터 입니다") @RequestBody HardwareChangeEventRequest request) {
        // 받은 데이터 출력

        String supportCode = request.getSupportCode();

        Optional<LicenseInfoEntity> optionalLicenseInfoEntity = licenseService.getLicenseById(supportCode);

        log.info("{} 라이선스으로부터 변경이 감지되었습니다", supportCode);

        StringBuilder hwInfoBuilder = new StringBuilder();

        String customer = String.format("%s - 고객사", supportCode);

        if ( optionalLicenseInfoEntity.isPresent() ) {
            LicenseInfoEntity licenseInfo = optionalLicenseInfoEntity.get();
            ClientEntity client = licenseInfo.getClient();
            customer = String.format("고객사 명 : %s [%s]", client.getName(), client.getAddress());
        }

        request.getEvents().forEach(event -> {
            log.info("Received event:");
            log.info("  Model: " + event.getChangedModel());
            log.info("  Serial: " + event.getChangedSerialNumber());
            log.info("  Type: " + event.getHardwareType());
            log.info("  Change Type: " + event.getChangeType());
            log.info("  Date: " + event.getDate());
            hwInfoBuilder.append(String.format("[%s] (%s)Model: %s [SN-%s]\n"
                    , event.getChangeType(), event.getHardwareType(), event.getChangedModel()
                    , event.getChangedSerialNumber() == null ? "N/A" : event.getChangedSerialNumber()
                    )
            );
        });



        for (CompanyComputerManagerEntity allManager : companyComputerManagerService.getAllManagers()) {
            StringBuilder lastBuilder = new StringBuilder();
            lastBuilder.append(hwInfoBuilder.toString());
            log.info("Mail send to : {}", allManager.getEmail());
            lastBuilder.insert(0, String.format("안녕하세요 %s팀 %s %s님\n %s 에 납품했던 하드웨어에서 변경이 감지되었습니다\n\n <감지내용>\n\n"
                    , allManager.getDepartment()
                    , allManager.getPosition()
                    , allManager.getName()
                    , customer));
            mailService.sendEmail(allManager.getEmail(), "[OAM] H/W Detection 건", lastBuilder.toString());
        }

        // TODO: 데이터 저장 로직 추가 (예: DB에 저장)
        return ResponseEntity.ok("Received " + request.getEvents().size() + " hardware change events.");
    }

}
