package gaya.pe.kr.core.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import gaya.pe.kr.core.client.entity.HardWareEntity;
import jakarta.persistence.Column;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class HardwareDTO {

    @JsonProperty("Type")
    private HardWareEntity.Type type; // 열거형 타입 필드

    @JsonProperty("Model")
    private String model; // 모델 필드


    @JsonProperty("Serial")
    private String serial; // 시리얼 번호 필드


}
