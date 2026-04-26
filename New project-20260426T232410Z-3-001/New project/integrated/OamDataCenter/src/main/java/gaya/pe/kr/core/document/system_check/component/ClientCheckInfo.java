package gaya.pe.kr.core.document.system_check.component;

import com.fasterxml.jackson.annotation.JsonProperty;
import gaya.pe.kr.infra.util.GayaDateUtil;
import lombok.Builder;
import lombok.Data;
import lombok.ToString;
import org.apache.poi.xwpf.usermodel.ParagraphAlignment;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STHeightRule;

import java.text.SimpleDateFormat;
import java.time.LocalDateTime;

import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.setCellText;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setTableWidth;

@Data
@ToString
public class ClientCheckInfo {

    @JsonProperty("clientCompanyName")
    private String clientCompanyName = "";

    @JsonProperty("checkDate")
    private String checkDate = "";

    @JsonProperty("clientName")
    private String clientName = "";

    @JsonProperty("checkPersonName")
    String checkPersonName = ""; // 점검담당자

    @JsonProperty("clientPhone")
    private String clientPhone = "";

    @JsonProperty("checkPersonPhone")
    String checkPersonPhone = ""; // 점검 담당자 연락처

    public XWPFTable createClientCheckInfo(XWPFDocument document, int contentWidth) {
        XWPFTable customerTable = document.createTable(3, 4);

        setTableWidth(customerTable, contentWidth);

        XWPFTableRow customerTableFirstRow = customerTable.getRow(0);
        setRowHeight(customerTableFirstRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(customerTableFirstRow, 0, "고 객 명", ParagraphAlignment.LEFT);
        setCellText(customerTableFirstRow, 1, clientCompanyName, ParagraphAlignment.LEFT);
        setCellText(customerTableFirstRow, 2, "점검일자", ParagraphAlignment.LEFT);
        setCellText(customerTableFirstRow, 3, checkDate, ParagraphAlignment.LEFT); // 점검일자

        XWPFTableRow customerTableSecondRow = customerTable.getRow(1);
        setRowHeight(customerTableSecondRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(customerTableSecondRow, 0, "고객사 담당자", ParagraphAlignment.LEFT);
        setCellText(customerTableSecondRow, 1, clientName, ParagraphAlignment.LEFT);
        setCellText(customerTableSecondRow, 2, "점검담당자", ParagraphAlignment.LEFT);
        setCellText(customerTableSecondRow, 3, checkPersonName, ParagraphAlignment.LEFT);

        XWPFTableRow customerTableThirdRow = customerTable.getRow(2);
        setRowHeight(customerTableThirdRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(customerTableThirdRow, 0, "고객사담당자연락처", ParagraphAlignment.LEFT);
        setCellText(customerTableThirdRow, 1, clientPhone, ParagraphAlignment.LEFT);
        setCellText(customerTableThirdRow, 2, "점검자연락처", ParagraphAlignment.LEFT);
        setCellText(customerTableThirdRow, 3, checkPersonPhone, ParagraphAlignment.LEFT);


        return customerTable;

    }


}
