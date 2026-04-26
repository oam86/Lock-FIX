package gaya.pe.kr.core.document.system_check.component;

import com.fasterxml.jackson.annotation.JsonProperty;
import gaya.pe.kr.infra.util.GayaDateUtil;
import lombok.Builder;
import lombok.Data;
import lombok.ToString;
import org.apache.poi.xwpf.usermodel.*;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STHeightRule;

import static gaya.pe.kr.core.document.util.initailizer.PageUtil.addBlankLines;
import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.setCellText;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.*;

@Data
@ToString
public class Header {

    // 점검 순번
    // 시스템 점검표
    // 사진

    @JsonProperty("checkNumber")
    private int checkNumber;

    @JsonProperty("headerName")
    private String headerName = "";


    public XWPFTable createHeaderTable(XWPFDocument document, int contentWidth) {
        XWPFTable headerTable = document.createTable(1,3); // 헤더 제작
        setTableWidth(headerTable, contentWidth);

        // 첫번째 열
        XWPFTableRow headerTableFirstRow = headerTable.getRow(0);
        setRowHeight(headerTableFirstRow, 1.25, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(headerTableFirstRow, 0, String.format("점검순번 #%d", checkNumber), ParagraphAlignment.CENTER);
        setCellText(headerTableFirstRow, 1, "시스템 점검표", ParagraphAlignment.CENTER);
        setCellText(headerTableFirstRow, 2, "이곳에 이미지를 넣어주세요", ParagraphAlignment.CENTER);

        return headerTable;
    }


}
