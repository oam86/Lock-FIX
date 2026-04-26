package gaya.pe.kr.core.license.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import gaya.pe.kr.core.client.dto.HardwareDTO;
import lombok.Data;

import java.util.List;

@Data
public class LicenseHardwareRegisterDTO {

    @JsonProperty("supportCode")
    private String supportCode;

    @JsonProperty("hardwareData")
    private List<HardwareDTO> hardwareData;
}
