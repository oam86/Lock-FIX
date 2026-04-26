package gaya.pe.kr.core.document.util.table;

import org.apache.poi.xwpf.usermodel.*;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.*;

import java.math.BigInteger;

import static gaya.pe.kr.core.document.util.table.MathValueConvertUtil.cmToTwips;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeightRule;


public class TableCellComponentUtil {

    // 셀 병합 메서드 (가로)
    public static void mergeCellsHorizontal(XWPFTable table, int row, int fromCol, int toCol) {
        XWPFTableRow tableRow = table.getRow(row);
        for (int colIndex = fromCol; colIndex <= toCol; colIndex++) {
            XWPFTableCell cell = tableRow.getCell(colIndex);
            if (colIndex == fromCol) {
                cell.getCTTc().addNewTcPr().addNewHMerge().setVal(STMerge.RESTART);
            } else {
                cell.getCTTc().addNewTcPr().addNewHMerge().setVal(STMerge.CONTINUE);
            }
        }
    }

    // 셀 병합 메서드 (세로)
    public static void mergeCellsVertical(XWPFTable table, int col, int fromRow, int toRow) {
        for (int rowIndex = fromRow; rowIndex <= toRow; rowIndex++) {
            XWPFTableRow tableRow = table.getRow(rowIndex);
            XWPFTableCell cell = tableRow.getCell(col);
            if (rowIndex == fromRow) {
                cell.getCTTc().addNewTcPr().addNewVMerge().setVal(STMerge.RESTART);
            } else {
                cell.getCTTc().addNewTcPr().addNewVMerge().setVal(STMerge.CONTINUE);
            }
        }
    }

    // 특정 열의 가로 길이를 설정하는 메서드 (width를 double 단위로 받음, cm 단위 사용)
    public static void setColumnWidth(XWPFTable table, int columnIndex, double widthInCm) {
        int widthInTwips = cmToTwips(widthInCm); // cm 단위를 Twips로 변환
        for (XWPFTableRow row : table.getRows()) {
            XWPFTableCell cell = row.getCell(columnIndex);
            if (cell != null) {
                CTTcPr tcPr = cell.getCTTc().isSetTcPr() ? cell.getCTTc().getTcPr() : cell.getCTTc().addNewTcPr();
                CTTblWidth tblWidth = tcPr.isSetTcW() ? tcPr.getTcW() : tcPr.addNewTcW();
                tblWidth.setW(BigInteger.valueOf(widthInTwips)); // Twips 단위로 설정
                tblWidth.setType(STTblWidth.DXA); // Twips 단위 사용
            }
        }
    }

    public static void setCellText(XWPFTableRow tableRow, int cellIndex, String text, ParagraphAlignment alignment) {

        if ( cellIndex < 0 )
            return;

        XWPFTableCell cell = tableRow.getCell(cellIndex);

        if ( cell == null ) {
            cell = tableRow.createCell();
        }

        // 기존 문단 제거
        cell.removeParagraph(0);

        XWPFParagraph paragraph = cell.addParagraph();
        XWPFRun textRun = paragraph.createRun();

        // 🔹 줄 간격 최소화
        paragraph.setSpacingAfter(0); // 이쁘게 띄어짐

        paragraph.setAlignment(alignment);
        cell.setVerticalAlignment(XWPFTableCell.XWPFVertAlign.CENTER);

        if ( alignment == ParagraphAlignment.LEFT ) {
            paragraph.setIndentationLeft(cmToTwips(0.18)); // 왼쪽 여행 추가
        }
        else if ( alignment == ParagraphAlignment.RIGHT ) {
            paragraph.setIndentationRight(cmToTwips(0.18)); // 왼쪽 여행 추가
        }

        // 🔹 줄바꿈 처리
        if (text.contains("\n")) {
            String[] lines = text.split("\n");
            for (int i = 0; i < lines.length; i++) {
                textRun.setText(lines[i]);
                if (i < lines.length - 1) {
                    textRun.addBreak(); // 줄 바꿈
                }
            }
            setRowHeightRule(tableRow, STHeightRule.AT_LEAST);
        } else {
            textRun.setText(text);
        }


        // 🔹 폰트 설정
        textRun.setFontSize(10);
        textRun.setFontFamily("나눔고딕");
    }


}
