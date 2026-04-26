package gaya.pe.kr.core.client.dto.external;


import jakarta.validation.constraints.NotBlank;
import lombok.Data;


import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class HardwareChangeEventDTO {
    @NotBlank
    private String changedModel;

    private String changedSerialNumber;

    @NotBlank
    private String hardwareType;

    @NotBlank
    private String changeType;

    @NotBlank
    private String date;
}