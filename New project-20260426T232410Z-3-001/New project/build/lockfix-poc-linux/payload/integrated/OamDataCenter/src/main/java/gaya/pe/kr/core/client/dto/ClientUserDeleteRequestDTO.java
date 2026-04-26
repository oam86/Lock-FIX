package gaya.pe.kr.core.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ClientUserDeleteRequestDTO {

    @JsonProperty("support_code")
    private String supportCode;
    @JsonProperty("email")
    private String email;
}
