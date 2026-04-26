package gaya.pe.kr.core.client.entity;

import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "oam_client")
@Getter
@Setter
@ToString
public class ClientEntity {

    @Id
    @Column(length = 8, nullable = false)
    private String clientCode;

    private String name;

    private String address;

    @Column(updatable = false)
    private LocalDateTime createdAt;
    @PrePersist
    public void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}