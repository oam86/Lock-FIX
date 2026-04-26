package gaya.pe.kr.core.document.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import gaya.pe.kr.core.document.system_check.component.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
public class DocumentCreateRequest {

    @JsonProperty("headerInfo")
    private Header headerInfo;

    @JsonProperty("clientCheckInfo")
    private ClientCheckInfo clientCheckInfo;

    @JsonProperty("serverInfo")
    private ServerInfo serverInfo;

    @JsonProperty("errorAndSpecialThings")
    private List<String> errorAndSpecialThings; // ✅ JSON 배열과 일치하도록 수정

    @JsonProperty("serverCheckStatusList")
    private List<ServerCheckStatusDTO> serverCheckStatusList; // ✅ DTO 리스트 유지

    @Override
    public String toString() {
        return "DocumentCreateRequest{" +
                "headerInfo=" + headerInfo +
                ", clientCheckInfo=" + clientCheckInfo +
                ", serverInfo=" + serverInfo +
                ", errorAndSpecialThings=" + errorAndSpecialThings +
                ", serverCheckStatusList=" + serverCheckStatusList +
                '}';
    }
}