package gaya.pe.kr.core.document.entity;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Data
@NoArgsConstructor
@ToString
public class ServerCheckStatusDTO {

    @JsonProperty("type")
    private String type;

    @JsonProperty("checkType")
    private String checkType;

    @JsonProperty("checkContent")
    private String checkContent;

    @JsonProperty("checkTargetAndStandard")
    private String checkTargetAndStandard;

    @JsonProperty("result")
    private String result;


}
