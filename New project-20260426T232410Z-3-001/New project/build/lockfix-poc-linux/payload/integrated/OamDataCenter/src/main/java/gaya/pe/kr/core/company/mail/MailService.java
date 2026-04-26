package gaya.pe.kr.core.company.mail;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.Properties;

import java.util.Properties;

@Service
@Slf4j
public class MailService {

    private final JavaMailSender mailSender;

    @Autowired
    public MailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendEmailWithAttachment(String to, String subject, String text, MultipartFile attachment) throws MessagingException {
        // MimeMessage 객체 생성
        MimeMessage message = mailSender.createMimeMessage();

        // MimeMessageHelper를 사용하여 첨부파일을 추가할 수 있는 이메일 설정
        MimeMessageHelper helper = new MimeMessageHelper(message, true);
        helper.setTo(to);
        helper.setSubject(subject);
        helper.setText(text);
        helper.setFrom("rich.kim@oam.co.kr");

        // 첨부파일 추가
        helper.addAttachment(attachment.getName(), attachment);

        // 이메일 전송
        mailSender.send(message);

    }

    public void sendEmail(String to, String subject, String text) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(text);
        message.setFrom("rich.kim@oam.co.kr"); // 발신자 주소
        mailSender.send(message);
    }

}
