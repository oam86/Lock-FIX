package gaya.pe.kr.core.client.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "oam_client_user_account",
        uniqueConstraints = @UniqueConstraint(columnNames = {"supportCode", "email"}) // 복합 유니크 제약 조건
)
@Getter
@Setter
@ToString
public class ClientUserAccountEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 자동 생성 ID
    private Long id; // 새로운 Primary Key

    @Column(length = 300, nullable = false)
    private String supportCode;

    @Column(nullable = false)
    private String email;

    private String password;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime lastLoginAt;

    @PrePersist
    public void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    @Override
    public String toString() {
        return "ClientUserAccountEntity{" +
                "id=" + id +
                ", supportCode='" + supportCode + '\'' +
                ", email='" + email + '\'' +
                ", password='" + password + '\'' +
                ", createdAt=" + createdAt +
                ", lastLoginAt=" + lastLoginAt +
                '}';
    }
}