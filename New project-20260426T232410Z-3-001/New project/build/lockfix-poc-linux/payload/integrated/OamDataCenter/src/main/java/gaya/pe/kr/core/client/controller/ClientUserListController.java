package gaya.pe.kr.core.client.controller;

import gaya.pe.kr.core.client.dto.ClientUserDeleteRequestDTO;
import gaya.pe.kr.core.client.entity.ClientUserAccountEntity;
import gaya.pe.kr.core.client.repository.ClientUserAccountRepository;
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
@Slf4j
@RequestMapping("/java_api/client/user")
@Tag(name = "특정 고객사의 계정 관리 및 확인", description = "특정 고객사의 계정에 대해 확인하거나 삭제하는 API 입니다")
public class ClientUserListController {

    private final ClientUserAccountRepository userAccountRepository;

    @Autowired
    public ClientUserListController(ClientUserAccountRepository userAccountRepository) {
        this.userAccountRepository = userAccountRepository;
    }

    @GetMapping("/list")
    @Operation(summary = "고객사 계정 목록", description = "우암전자 웹 솔루션에 등롣괸 특정 고객사의 계정 목록을 확인합니다 호출 값인 라이선스가 없다면, 전체 고객사 계정 목록을 반환합니다.")
    public ResponseEntity<List<ClientUserAccountEntity>> listUsers(@Parameter(name = "라이선스 키", description = "특정 고객사를 지칭하기 위한 라이선스 값입니다", required = false) @RequestParam(required = false) String supportCode) {
        List<ClientUserAccountEntity> users;
        if (supportCode != null && !supportCode.isEmpty()) {
            users = userAccountRepository.findBySupportCode(supportCode);
        } else {
            users = userAccountRepository.findAll();
        }

        return ResponseEntity.ok(users);
    }

    @PostMapping("/delete")
    @Operation(summary = "고객사 계정 삭제", description = "특정 고객사의 계정을 삭제합니다")
    public ResponseEntity<String> deleteUser(@Parameter(name = "고객사 정보 및 계정",description = "특정 고객사의 정보인 라이선스 값과 계정 정보 중 이메일이 내제된 데이터 입니다") @RequestBody ClientUserDeleteRequestDTO request) {
        log.info("User account delete request supportCode={}, email={}", request.getSupportCode(), request.getEmail());

        Optional<ClientUserAccountEntity> userToDelete = userAccountRepository.findByEmailAndSupportCode(
                request.getEmail(), request.getSupportCode()
        );

        if (userToDelete.isPresent()) {
            userAccountRepository.delete(userToDelete.get());
            log.info("[Success]: supportCode={}, email={}", request.getSupportCode(), request.getEmail());
            return ResponseEntity.ok("사용자 계정이 삭제되었습니다.");
        } else {
            log.warn("[Not found - Fail delete]: supportCode={}, email={}", request.getSupportCode(), request.getEmail());
            return ResponseEntity.badRequest().body("사용자 계정을 찾을 수 없습니다.");
        }
    }


}
