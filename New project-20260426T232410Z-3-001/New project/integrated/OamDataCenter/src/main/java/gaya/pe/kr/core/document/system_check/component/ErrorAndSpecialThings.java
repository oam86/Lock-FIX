package gaya.pe.kr.core.document.system_check.component;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;
import org.apache.poi.xwpf.usermodel.ParagraphAlignment;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STHeightRule;

import java.util.ArrayList;
import java.util.List;

import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.setCellText;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setTableWidth;

@Data
@NoArgsConstructor
@ToString
public class ErrorAndSpecialThings {

    private List<String> dataList = new ArrayList<>();

    public ErrorAndSpecialThings(List<String> dataList) {
        this.dataList = dataList;
    }

    public XWPFTable createErrorAndSpecialThings(XWPFDocument document, int contentWidth) {
        XWPFTable table = document.createTable(2, 1);  // 빈 데이터 추가 방지
        setTableWidth(table, contentWidth);

        // 첫 번째 행: 제목
        XWPFTableRow firstRow = table.getRow(0);
        setCellText(firstRow, 0, "■ 특이사항 및 장애현황", ParagraphAlignment.LEFT);
        setRowHeight(firstRow, 0.63, STHeightRule.EXACT);

        // 두 번째 행 추가
        XWPFTableRow secondRow = table.getRow(1);
        setRowHeight(secondRow, 2.0, STHeightRule.AT_LEAST);

        // 데이터 문자열 결합
        StringBuilder stringBuilder = new StringBuilder();
        for (String s : dataList) {
            stringBuilder.append("- ").append(s).append("\n");
        }

        setCellText(secondRow, 0, stringBuilder.toString(), ParagraphAlignment.LEFT);
        return table;
    }
}