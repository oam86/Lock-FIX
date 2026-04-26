package gaya.pe.kr.core.document.controller;

import gaya.pe.kr.core.document.entity.DocumentCreateRequest;
import gaya.pe.kr.core.document.entity.ServerCheckStatusDTO;
import gaya.pe.kr.core.document.system_check.SystemCheckDocument;
import gaya.pe.kr.core.document.system_check.component.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;

@RestController
@RequestMapping("/java_api/document")
public class DocumentController {

    private final SystemCheckDocument systemCheckDocument = new SystemCheckDocument();

    /**
     * 🏆 Word 문서 생성 및 다운로드 (파일 저장)
     */
    @PostMapping
    public ResponseEntity<Resource> receiveDocument(@RequestBody DocumentCreateRequest request) {

        System.out.println("Input Data for create : " + request.toString());

        Header header = new Header();
        header.setCheckNumber(1);
        request.setHeaderInfo(header);

        ClientCheckInfo clientCheckInfo = request.getClientCheckInfo();
        ServerInfo serverInfo = request.getServerInfo();

        List<ServerCheckStatusDTO> serverCheckStatusDTO = request.getServerCheckStatusList();
        ServerCheckStatus serverCheckStatus = new ServerCheckStatus();
        for (ServerCheckStatusDTO checkStatusDTO : serverCheckStatusDTO) {
            serverCheckStatus.addRow(
                    checkStatusDTO.getType().contains("HW") ? ServerCheckStatus.SystemType.HW : ServerCheckStatus.SystemType.SW,
                    checkStatusDTO.getCheckType(), checkStatusDTO.getCheckContent(), checkStatusDTO.getCheckTargetAndStandard(), checkStatusDTO.getResult()
            );
        }

        ErrorAndSpecialThings errorAndSpecialThings = new ErrorAndSpecialThings(request.getErrorAndSpecialThings());

        File file = systemCheckDocument.createSystemCheckDocument(header, clientCheckInfo, serverInfo, serverCheckStatus, errorAndSpecialThings);

        if (file == null) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }

        String filename = file.getName();
        String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8).replaceAll("\\+", "%20");
        Resource resource = new FileSystemResource(file);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encodedFilename + "\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(resource);
    }

}