package gaya.pe.kr.infra.util;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class GayaStringUtils {

    // 이메일 형식에 맞는 정규 표현식
    private static final String EMAIL_REGEX = "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$";

    public static boolean isValidEmail(String email) {
        Pattern pattern = Pattern.compile(EMAIL_REGEX);
        Matcher matcher = pattern.matcher(email);
        return matcher.matches();
    }

}
