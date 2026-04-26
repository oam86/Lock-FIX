package gaya.pe.kr.core.client.controller;

import gaya.pe.kr.core.client.dto.ClientDTO;
import gaya.pe.kr.core.client.entity.ClientEntity;
import gaya.pe.kr.core.client.repository.ClientRepository;
import gaya.pe.kr.core.client.service.ClientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/java_api/clients")
@Slf4j
@Tag(name = "고객사 관리", description = "우암전자 측의 고객사 관리 및 확인을 위한 API 입니다")
public class ClientController {

    private final ClientService clientService;

    @Autowired
    public ClientController(ClientService clientService) {
        this.clientService = clientService;
    }

    @GetMapping("/list")
    @Operation(summary = "전체 고객사", description = "전체 고객사를 반환합니다")
    public List<ClientEntity> listAllClients() {
        return clientService.getAllClients();
    }
    @GetMapping("/check-duplicate-name")
    @Operation(summary = "고객사 중복 확인", description = "고객사명으로 중복을 확인합니다")
    public Map<String, Boolean> checkDuplicateName(@RequestParam String name) {
        boolean isDuplicate = clientService.isNameDuplicate(name);
        Map<String, Boolean> response = new HashMap<>();
        response.put("isDuplicate", isDuplicate);
        return response;
    }

    @PostMapping("/create")
    @Operation(summary = "고객사 생성", description = "고객사를 생성합니다")
    public void createClient(@Parameter(name = "고객사 정보", description = "고객사 코드를 제외한 고객사명과 주소가 내제된 데이터 입니다") @RequestBody ClientDTO clientDTO) {
        clientService.createClient(clientDTO);
    }

    @PostMapping("/update")
    @Operation(summary = "고객사 업데이트", description = "전송된 고객사 정보를 토대로 특정 고객사의 정보를 업데이트 합니다")
    public ResponseEntity<String> updateClient(@RequestBody ClientEntity client) {
        clientService.updateClient(client);
        return ResponseEntity.ok("");
    }

    @PostMapping("/delete")
    @Operation(summary = "고객사 삭제", description = "🚨 특정 고객사의 정보를 삭제합니다. 주의: 라이선스와 연계된 모든 정보도 함께 삭제됩니다! 🚨")
    public void deleteClient(@RequestBody ClientEntity client) {
        log.info("Request Delete : {}[{}]", client.getName(), client.getClientCode());
        clientService.deleteClient(client.getClientCode() );
    }




}