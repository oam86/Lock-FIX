package gaya.pe.kr.infra.util;

import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class GayaDateUtil {

    private static final DateTimeFormatter YEAR_MONTH_DAY_FORMATTER = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일");
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy년 MM월 dd일 HH시mm분ss초");

    public static String getYearMonthDayDate(LocalDateTime localDateTime) {
        return localDateTime.format(YEAR_MONTH_DAY_FORMATTER);
    }

    public static String getFullDateTime(LocalDateTime localDateTime) {
        return localDateTime.format(TIME_FORMATTER);
    }

}
