package gaya.pe.kr.core.document.system_check;

import gaya.pe.kr.core.document.system_check.component.*;
import gaya.pe.kr.core.document.util.initailizer.PageUtil;
import org.apache.pdfbox.pdmodel.font.PDType0Font;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.docx4j.openpackaging.exceptions.Docx4JException;
import org.docx4j.openpackaging.packages.WordprocessingMLPackage;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTPageMar;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTPageSz;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;

import java.io.*;
import java.math.BigInteger;
import java.util.Random;

import static gaya.pe.kr.core.document.util.initailizer.PageUtil.*;

public class SystemCheckDocument {

    // 운영 체제에 따른 폰트 경로 설정
    private String getSystemFontPath() {
        String os = System.getProperty("os.name").toLowerCase();

        if (os.contains("win")) {
            return "C:/Windows/Fonts/NanumGothic.ttf"; // Windows 폰트 경로
        } else if (os.contains("mac")) {
            return "/Library/Fonts/Arial Unicode.ttf"; // macOS 폰트 경로
        } else {
            return "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"; // Linux 폰트 경로
        }
    }


    public File createSystemCheckDocument(Header header, ClientCheckInfo clientCheckInfo, ServerInfo serverInfo, ServerCheckStatus serverCheckStatus, ErrorAndSpecialThings errorAndSpecialThings) {

        // 문서 생성
        XWPFDocument document = new XWPFDocument();

        // 섹션 속성 초기화 페이지 설정
        initializeSectionProperties(document);

        // 페이지 크기 및 여백 설정
        CTPageSz pageSize = document.getDocument().getBody().getSectPr().getPgSz();
        CTPageMar pageMargins = document.getDocument().getBody().getSectPr().getPgMar();

        int pageWidth = ((BigInteger) pageSize.getW()).intValue();
        int leftMargin = ((BigInteger) pageMargins.getLeft()).intValue();
        int rightMargin = ((BigInteger) pageMargins.getRight()).intValue();
        int contentWidth = pageWidth - leftMargin - rightMargin;

        /** Header 만들기 표 1:3 **/
        header.createHeaderTable(document, contentWidth);
        addBlankLines(document, 1);

        /** 고객명 정보 표 (3:4 비율) **/
        clientCheckInfo.createClientCheckInfo(document, contentWidth);
        addBlankLines(document, 1);

        /** 서버 기본정보 (4:4 비율) **/
        serverInfo.createServerInfo(document, contentWidth);
        addBlankLines(document, 1);

        /** 서버 상태 점검 (5:5) **/
        serverCheckStatus.createSystemCheckStatus(document, contentWidth);
        addBlankLines(document, 1);

        /** 특이사항 및 장애 현황 **/
        errorAndSpecialThings.createErrorAndSpecialThings(document, contentWidth);
        addBlankLines(document, 1);

        CheckSign checkSign = new CheckSign();
        checkSign.createCheckSignTable(document, contentWidth);

        PageUtil.addHorizontalLine(document);


        String os = serverInfo.getOsVersion();

        String fileNameOs = "";

        if ( os.contains("Linux") ) {
            fileNameOs = "리눅스";
        }
        else if ( os.contains("Ubuntu") ) {
            fileNameOs = "우분투";
        }
        else if ( os.contains("Windows") ) {
            fileNameOs = "윈도우";
        }
        else {
            fileNameOs = os;
        }

        // 문서 저장
        String fileName = String.format("%s_정기점검_서버_%s_2025.docx", clientCheckInfo.getClientName(), fileNameOs);
        File file = new File(fileName);

        try (FileOutputStream out = new FileOutputStream(file)) {
            document.write(out);
            System.out.println(fileName + " Word 파일이 성공적으로 생성되었습니다!");
        } catch (IOException e) {
            e.printStackTrace();
        }

        return file;
    }

}