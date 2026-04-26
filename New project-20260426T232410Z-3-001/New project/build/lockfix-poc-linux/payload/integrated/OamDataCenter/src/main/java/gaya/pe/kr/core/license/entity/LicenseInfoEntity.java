package gaya.pe.kr.core.license.entity;

import gaya.pe.kr.core.client.entity.ClientEntity;
import gaya.pe.kr.core.client.entity.HardWareEntity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "oam_customer_license")
@Getter
@Setter
@ToString
public class LicenseInfoEntity {

    @Id
    @Column(length = 300, nullable = false)
    private String supportCode;

    @ManyToOne
    @JoinColumn(name = "client_code", referencedColumnName = "clientCode")
    private ClientEntity client;

    private LocalDate expirationAt;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private LocalDateTime usedAt;

    @PrePersist
    public void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public void startUsage() {
        this.usedAt = LocalDateTime.now();
    }

    @Override
    public String toString() {
        return "LicenseInfoEntity{" +
                "supportCode='" + supportCode + '\'' +
                ", client=" + client +
                ", expirationAt=" + expirationAt +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                ", usedAt=" + usedAt +
                '}';
    }
}