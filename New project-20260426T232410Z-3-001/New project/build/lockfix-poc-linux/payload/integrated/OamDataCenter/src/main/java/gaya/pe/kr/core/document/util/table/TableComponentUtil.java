package gaya.pe.kr.core.document.util.table;

import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.*;

import java.math.BigInteger;

import static gaya.pe.kr.core.document.util.table.MathValueConvertUtil.cmToTwips;

public class TableComponentUtil {


    public static void setRowHeight(XWPFTableRow row, double heightInCm, STHeightRule.Enum stHeightRule) {
        if (row == null) return;
        // Twips 단위로 높이 설정
        int heightTwips = cmToTwips(heightInCm);
        // CTRow에서 CTTrPr 가져오기
        CTRow ctRow = row.getCtRow();
        CTTrPr trPr = ctRow.isSetTrPr() ? ctRow.getTrPr() : ctRow.addNewTrPr();
        // 높이 설정
        CTHeight ht = trPr.sizeOfTrHeightArray() > 0 ? trPr.getTrHeightArray(0) : trPr.addNewTrHeight();
        ht.setVal(BigInteger.valueOf(heightTwips)); // 높이 값 설정
        // 높이 고정
        ht.setHRule(stHeightRule); // EXACT로 설정하여 정확한 높이 적용
    }

    public static void setRowHeightRule(XWPFTableRow row, STHeightRule.Enum stHeightRule) {
        if (row == null) return;
        // Twips 단위로 높이 설정
        // CTRow에서 CTTrPr 가져오기
        CTRow ctRow = row.getCtRow();
        CTTrPr trPr = ctRow.isSetTrPr() ? ctRow.getTrPr() : ctRow.addNewTrPr();
        // 높이 설정
        CTHeight ht = trPr.sizeOfTrHeightArray() > 0 ? trPr.getTrHeightArray(0) : trPr.addNewTrHeight();
        // 높이 고정
        ht.setHRule(stHeightRule); // EXACT로 설정하여 정확한 높이 적용
    }


    // 테이블 너비 설정 메서드
    public static void setTableWidth(XWPFTable table, int width) {
        table.getCTTbl().getTblPr().getTblW().setW(width);
        table.getCTTbl().getTblPr().getTblW().setType(STTblWidth.DXA);
    }

    /**
     * 고객 정보 테이블의 높이를 전체 페이지 높이의 일정 비율(%)로 설정하는 메서드
     * @param document Word 문서
     * @param table 테이블
     * @param heightRatio 설정할 비율 (예: 0.3 = 30%)
     */
    public static void setTableHeight(XWPFDocument document, XWPFTable table, double heightRatio) {
        CTBody body = document.getDocument().getBody();
        CTSectPr sectPr = body.getSectPr();
        CTPageSz pageSize = sectPr.getPgSz();
        CTPageMar pageMargins = sectPr.getPgMar();

        // 📌 A4 기준 높이 설정 (twip 단위)
        int pageHeight = ((BigInteger) pageSize.getH()).intValue();
        int topMargin = ((BigInteger) pageMargins.getTop()).intValue();
        int bottomMargin = ((BigInteger) pageMargins.getBottom()).intValue();

        // 🛠️ 전체 콘텐츠 영역 높이 계산
        int contentHeight = pageHeight - (topMargin + bottomMargin);

        // 📌 테이블의 총 높이 = 콘텐츠 높이 * 비율(%)
        int tableHeight = (int) (contentHeight * heightRatio);

        // 🛠️ 테이블의 행 개수 가져오기
        int rowCount = table.getNumberOfRows();
        if (rowCount == 0) return;

        // 📌 각 행의 높이를 균등하게 배분하여 설정
        int rowHeight = tableHeight / rowCount;

        for (int i = 0; i < rowCount; i++) {
            XWPFTableRow row = table.getRow(i);
            if (row != null) {
                row.setHeight(rowHeight);
            }
        }
    }


}
