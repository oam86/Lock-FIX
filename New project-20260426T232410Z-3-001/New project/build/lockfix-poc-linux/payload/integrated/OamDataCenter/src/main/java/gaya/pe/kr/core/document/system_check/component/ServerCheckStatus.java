package gaya.pe.kr.core.document.system_check.component;

import lombok.Data;
import lombok.ToString;
import org.apache.poi.xwpf.usermodel.*;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STHeightRule;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import static gaya.pe.kr.core.document.util.table.TableCellComponentUtil.*;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setRowHeight;
import static gaya.pe.kr.core.document.util.table.TableComponentUtil.setTableWidth;

@Data
@ToString
public class ServerCheckStatus {

    private final HashMap<SystemType, List<String[]>> data = new HashMap<>();

    public XWPFTable createSystemCheckStatus(XWPFDocument document, int contentWidth) {
        XWPFTable table = document.createTable(1, 5);
        setTableWidth(table, contentWidth);

        // 첫 번째 행: 제목
        XWPFTableRow firstRow = table.getRow(0);
        setCellText(firstRow, 0, "■ 서버 점검내역", ParagraphAlignment.LEFT);
        setRowHeight(firstRow, 0.63, STHeightRule.EXACT);
        mergeCellsHorizontal(table, 0, 0, 4);

        // 두 번째 행: 헤더
        XWPFTableRow secondRow = table.createRow();
        String[] headers = {"구분", "점검사항", "점검내역", "점검항목/기준", "결과"};
        for (int i = 0; i < headers.length; i++) {
            setCellText(secondRow, i, headers[i], ParagraphAlignment.CENTER);
        }

        // 데이터 추가 (H/W, S/W)
        int currentIndex = 2;
        for (SystemType type : SystemType.values()) {
            List<String[]> dataList = data.getOrDefault(type, new ArrayList<>());

            boolean firstIn = true;

            if (!dataList.isEmpty()) {
                int startIdx = currentIndex;
                addSystemTypeData(table, dataList, type, firstIn);
                int endIdx = startIdx + dataList.size();
                mergeCellsVertical(table, 0, startIdx, endIdx - 1);
                currentIndex = endIdx;
            }
        }


        return table;
    }

    private void addSystemTypeData(XWPFTable table, List<String[]> dataList, SystemType type, boolean firstIn) {
        for (String[] rowData : dataList) {
            XWPFTableRow row = table.createRow();
            setRowHeight(row, 0.55, STHeightRule.EXACT);
            for (int i = 0; i < 5; i++) {
                ParagraphAlignment alignment = rowData[i].contains(type.getLabel()) ? ParagraphAlignment.CENTER : ParagraphAlignment.LEFT;

                if ( i == 4 ) {
                    alignment = ParagraphAlignment.CENTER;
                }

                if ( i != 0 ) {
                    // 0 번째는 구분이 적히기 때문에 필요없음
                    setCellText(row, i, rowData[i], alignment);
                } else {
                    if ( firstIn ) {
                        setCellText(row, i, rowData[i], alignment);
                        firstIn = false;
                    }
                }
            }
        }
    }

    public void addRow(SystemType systemType, String checkType, String checkContent, String checkTargetAndStandard, String result) {

        if ( !data.containsKey(systemType) ) {
            data.put(systemType, new ArrayList<>());
        }

        String[] dataArr = new String[5];

        dataArr[0] = systemType.getLabel();
        dataArr[1] = checkType;
        dataArr[2] = checkContent;
        dataArr[3] = checkTargetAndStandard;
        dataArr[4] = result;

        List<String[]> dataList = data.get(systemType);

        dataList.add(dataArr);
    }

    public enum SystemType {
        HW("H/W"), SW("S/W");

        private final String label;


        SystemType(String label) {
            this.label = label;
        }

        public String getLabel() {
            return label;
        }
    }
}