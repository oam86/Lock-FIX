package gaya.pe.kr.core.document.system_check.component;

import org.apache.poi.xwpf.usermodel.ParagraphAlignment;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STHeightRule;

import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.setCellText;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setTableWidth;

public class CheckSign {

    public XWPFTable createCheckSignTable(XWPFDocument document, int contentWidth) {
        XWPFTable table = document.createTable(1,4); // 헤더 제작
        setTableWidth(table, contentWidth);

        // 첫번째 열
        XWPFTableRow headerTableFirstRow = table.getRow(0);
        setRowHeight(headerTableFirstRow, 1.0, STHeightRule.EXACT); // 병합된 행의 높이 설정

        setCellText(headerTableFirstRow, 0, "점검 담당자", ParagraphAlignment.CENTER);
        setCellText(headerTableFirstRow, 1, "        (인)", ParagraphAlignment.RIGHT);
        setCellText(headerTableFirstRow, 2, "고객사 담당자", ParagraphAlignment.CENTER);
        setCellText(headerTableFirstRow, 3, "        (인)", ParagraphAlignment.RIGHT);

        return table;
    }


}
