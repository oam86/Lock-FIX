package gaya.pe.kr.core.document.util.initailizer;

import org.apache.poi.xwpf.usermodel.ParagraphAlignment;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.*;

import java.math.BigInteger;

public class PageUtil {

    // 섹션 속성 초기화 메서드
    public static void initializeSectionProperties(XWPFDocument document) {
        CTBody body = document.getDocument().getBody();
        if (!body.isSetSectPr()) {
            body.addNewSectPr();
        }
        CTSectPr sectPr = body.getSectPr();
        if (!sectPr.isSetPgSz()) {
            CTPageSz pageSize = sectPr.addNewPgSz();
            pageSize.setW(BigInteger.valueOf(11906));
            pageSize.setH(BigInteger.valueOf(16838));
        }
        if (!sectPr.isSetPgMar()) {
            CTPageMar pageMargins = sectPr.addNewPgMar();
            pageMargins.setLeft(BigInteger.valueOf(1440));
            pageMargins.setRight(BigInteger.valueOf(1440));
            pageMargins.setTop(BigInteger.valueOf(1440));
            pageMargins.setBottom(BigInteger.valueOf(1440));
        }
    }

    // 여백 추가 메서드
//    public static void addBlankLines(XWPFDocument document, int numLines) {
//        for (int i = 0; i < numLines; i++) {
//            document.createParagraph().createRun().addBreak();
//        }
//    }

    public static void addBlankLines(XWPFDocument document, int spacing) {
        XWPFParagraph paragraph = document.createParagraph();
        paragraph.setSpacingAfter(1); // 여백 설정 (단위: 1/20 pt)
    }

    public static void addHorizontalLine(XWPFDocument document) {
        XWPFParagraph paragraph = document.createParagraph();
        paragraph.setAlignment(ParagraphAlignment.CENTER); // 수평선 중앙 정렬

        CTP ctp = paragraph.getCTP();
        CTPBdr border = ctp.addNewPPr().addNewPBdr();
        border.addNewBottom().setVal(STBorder.SINGLE); // 단락의 아래쪽 테두리를 추가하여 선처럼 보이게 설정
    }


}
