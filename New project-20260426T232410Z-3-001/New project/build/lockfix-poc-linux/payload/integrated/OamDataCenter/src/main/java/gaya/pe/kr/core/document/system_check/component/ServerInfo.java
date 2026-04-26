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

import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.mergeCellsHorizontal;
import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.setCellText;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setTableWidth;

@Data
@ToString
public class ServerInfo {


    // 4열 5행

    // 서버 기본 정보 4열을 하나로 통합
    //3

    @JsonProperty("osVersion")
    private String osVersion = "";

    @JsonProperty("cpu")
    private String cpu = "";

    @JsonProperty("memory")
    private String memory = "";

    @JsonProperty("disk")
    private String disk = "";

    @JsonProperty("hostname")
    private String hostname = "";

    @JsonProperty("supportWork")
    String supportWork = ""; // 지원업무

    @JsonProperty("model")
    String model = ""; // 모델명

    @JsonProperty("serialNumber")
    String serialNumber = ""; // 시리얼번호

    public XWPFTable createServerInfo(XWPFDocument document, int contentWidth) {

        XWPFTable serverInfoTable = document.createTable(5, 4);
        setTableWidth(serverInfoTable, contentWidth);

        XWPFTableRow firstRow = serverInfoTable.getRow(0);
        setCellText(firstRow, 0, "■ 서버 기본정보", ParagraphAlignment.LEFT);
        mergeCellsHorizontal(serverInfoTable, 0, 0, 3); // 셀 병합
        setRowHeight(firstRow, 0.63, STHeightRule.EXACT); // 서버 기본정보는 높이가 높음

        XWPFTableRow secondRow = serverInfoTable.getRow(1);
        setRowHeight(secondRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(secondRow, 0, "OS Version", ParagraphAlignment.LEFT);
        setCellText(secondRow, 1, osVersion, ParagraphAlignment.LEFT);
        setCellText(secondRow, 2, "CPU", ParagraphAlignment.LEFT);
        setCellText(secondRow, 3, cpu, ParagraphAlignment.CENTER);

        XWPFTableRow thirdRow = serverInfoTable.getRow(2);
        setRowHeight(thirdRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(thirdRow, 0, "지원업무", ParagraphAlignment.LEFT);
        setCellText(thirdRow, 1, supportWork, ParagraphAlignment.LEFT);
        setCellText(thirdRow, 2, "Memory", ParagraphAlignment.LEFT);
        setCellText(thirdRow, 3, memory, ParagraphAlignment.CENTER);

        XWPFTableRow forthRow = serverInfoTable.getRow(3);
        setRowHeight(forthRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(forthRow, 0, "Model", ParagraphAlignment.LEFT);
        setCellText(forthRow, 1, model, ParagraphAlignment.LEFT);
        setCellText(forthRow, 2, "Disk", ParagraphAlignment.LEFT);
        setCellText(forthRow, 3, disk, ParagraphAlignment.CENTER);

        XWPFTableRow fifthRow = serverInfoTable.getRow(4);
        setRowHeight(fifthRow, 0.54, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(fifthRow, 0, "S/N", ParagraphAlignment.LEFT);
        setCellText(fifthRow, 1, serialNumber, ParagraphAlignment.LEFT);
        setCellText(fifthRow, 2, "Hostname", ParagraphAlignment.LEFT);
        setCellText(fifthRow, 3, hostname, ParagraphAlignment.CENTER);

        return serverInfoTable;

    }

}
