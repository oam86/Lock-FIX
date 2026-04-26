package gaya.pe.kr.core.client.dto.external;


import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class HardwareChangeEventRequest {
    private List<HardwareChangeEventDTO> events;

    @JsonProperty("support_code")
    private String supportCode;
}