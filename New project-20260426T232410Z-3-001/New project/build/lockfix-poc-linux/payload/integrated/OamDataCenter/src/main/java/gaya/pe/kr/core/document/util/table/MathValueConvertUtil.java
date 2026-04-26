package gaya.pe.kr.core.document.util.table;

public class MathValueConvertUtil {

    // cm를 Twips 단위로 변환하는 메서드
    public static int cmToTwips(double cm) {
        return (int) Math.round(cm * 567);
    }

    // cm 단위를 EMU 단위로 변환하는 메서드
    public static int convertToEMU(double cm) {
        return (int) Math.round(cm * 360000);
    }

}
