package gaya.pe.kr.core.client.controller.external;

import gaya.pe.kr.core.client.entity.ClientUserAccountEntity;
import gaya.pe.kr.core.client.repository.ClientUserAccountRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/java_api/external/user")
@Slf4j
@Tag(name = "[외부 접근] 특정 고객사의 계정 인증/생성", description = "고객사의 하드웨어 웹 솔루션에서의 로그인 및 회원가입 정보를 동기화하는 API 입니다")
public class ClientUserController {

    private final ClientUserAccountRepository userAccountRepository;

    @Autowired
    public ClientUserController(ClientUserAccountRepository userAccountRepository) {
        this.userAccountRepository = userAccountRepository;
    }

    // 특정 고객사 또는 전체 사용자 목록 가져오기
    // 로그인 정보 맞는지 확인
    @PostMapping("/login")
    @Operation(
            summary = "로그인",
            description = "고객사 계정의 로그인 승인 및 관련 정보 동기화를 담당합니다"
    )
    public ResponseEntity<String> loginUser(@Parameter(description = "라이선스 키 번호", required = true)  @RequestParam String supportCode
            ,@Parameter(description = "계정 Email", required = true) @RequestParam String email
            ,@Parameter(description = "비밀번호", required = true) @RequestParam String password) {
        Optional<ClientUserAccountEntity> userAccount = userAccountRepository.findByEmailAndSupportCode(email, supportCode);

        if (userAccount.isPresent() && userAccount.get().getPassword().equals(password)) {
            ClientUserAccountEntity user = userAccount.get();
            user.setLastLoginAt(java.time.LocalDateTime.now());
            userAccountRepository.save(user); // 마지막 로그인 시간 업데이트
            log.info("고객사 {} 의 ID {} PW {} Login Sucess", supportCode, email, password);
            return ResponseEntity.ok("로그인 성공");
        } else {
            log.info("고객사 {} 의 ID {} PW {} Login Fail ( Email / Password wrong )", supportCode, email, password);
            return ResponseEntity.status(401).body("이메일 또는 비밀번호가 잘못되었습니다.");
        }
    }

    // 회원가입 시켜주세요
    @PostMapping("/register")
    @Operation(summary = "회원가입", description = "고객사 계정 회원가입을 위한 API 입니다")
    public ResponseEntity<String> registerUser(@Parameter(description = "라이선스 키 번호", required = true)  @RequestParam String supportCode
            ,@Parameter(description = "계정 Email", required = true) @RequestParam String email
            ,@Parameter(description = "비밀번호", required = true) @RequestParam String password) {
        Optional<ClientUserAccountEntity> existingUser = userAccountRepository.findByEmailAndSupportCode(email, supportCode);

        if (existingUser.isPresent()) {
            log.info("고객사 {} 의 ID {} PW {} Failed Register (Already exist email)", supportCode, email, password);
            return ResponseEntity.status(409).body("이미 존재하는 이메일입니다.");
        }

        log.info("Register Request : {}-{}-{}", supportCode, email, password);

        ClientUserAccountEntity newUser = new ClientUserAccountEntity();
        newUser.setSupportCode(supportCode);
        newUser.setEmail(email);
        newUser.setPassword(password);
        newUser.setCreatedAt(LocalDateTime.now());

        userAccountRepository.save(newUser);
        log.info("Success Register : {}", email);

        return ResponseEntity.ok("회원가입 성공");
    }



}