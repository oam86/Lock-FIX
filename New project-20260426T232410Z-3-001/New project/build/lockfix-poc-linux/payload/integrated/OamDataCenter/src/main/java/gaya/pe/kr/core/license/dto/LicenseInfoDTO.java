package gaya.pe.kr.core.license.dto;


import lombok.Data;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class LicenseInfoDTO {

    private String supportCode;
    private String clientCode; // clientCode를 직접 전달받음
    private LocalDate expirationAt;
}