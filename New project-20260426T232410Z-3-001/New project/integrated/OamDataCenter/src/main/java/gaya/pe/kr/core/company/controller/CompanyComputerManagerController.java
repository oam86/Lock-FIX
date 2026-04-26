package gaya.pe.kr.core.company.controller;

import gaya.pe.kr.core.company.entity.CompanyComputerManagerEntity;
import gaya.pe.kr.core.company.service.CompanyComputerManagerService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/java_api/managers")
@Slf4j
@Tag(name = "전산 담당자 관리", description = "전산 담당자를 추가/수정/삭제 할 수 있는 API 입니다")
public class CompanyComputerManagerController {

    @Autowired
    private CompanyComputerManagerService service;

    @GetMapping("/list")
    @Operation(summary = "전산 담당자 전체 목록", description = "서버에 등록된 전산 담당자 전체 목록을 반환합니다")
    public List<CompanyComputerManagerEntity> listAllManagers() {
        return service.getAllManagers();
    }

    @GetMapping("/{id}")
    @Operation(summary = "전산 담당자 목록", description = "서버에 등록된 전산 담당자 중 {id} 값에 해당하는 전산 담당자를 반환합니다")
    public CompanyComputerManagerEntity getManager(@PathVariable long id) {
        return service.getManagerById(id).orElse(null);
    }

    @PostMapping("/create")
    @Operation(summary = "전산 담당자 생성", description = "서버에 전산 담당자를 등록합니다")
    public CompanyComputerManagerEntity createManager(@Parameter(name = "전산 담당자 정보", description = "이름,이메일,부서 직위 등이 내제된 전산 담당자 정보 데이터 입니다") @RequestBody CompanyComputerManagerEntity manager) {
        return service.createManager(manager);
    }

    @PostMapping("/update")
    @Operation(summary = "전산 담당자 업데이트", description = "등록된 전산 담당자의 정보를 갱신합니다")
    public CompanyComputerManagerEntity updateManager(@Parameter(name = "전산 담당자 정보", description = "이름,이메일,부서 직위 등이 내제된 전산 담당자 정보 데이터 입니다") @RequestBody CompanyComputerManagerEntity manager) {
        return service.updateManager(manager);
    }

    @PostMapping("/delete")
    @Operation(summary = "전산 담당자 삭제", description = "등록된 전산 담당자의 정보를 삭제합니다")
    public void deleteManager(@Parameter(name = "전산 담당자 정보", description = "이름,이메일,부서 직위 등이 내제된 전산 담당자 정보 데이터 입니다") @RequestBody CompanyComputerManagerEntity manager) {
        log.info("Delete Company Computer Manager Name : {} Email : {}" ,manager.getName(), manager.getEmail());
        service.deleteManager(manager.getId());
    }
}