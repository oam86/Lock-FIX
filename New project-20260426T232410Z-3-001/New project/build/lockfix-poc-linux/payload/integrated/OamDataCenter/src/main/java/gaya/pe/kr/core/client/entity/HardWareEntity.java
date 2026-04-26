package gaya.pe.kr.core.client.entity;

import gaya.pe.kr.core.license.entity.LicenseInfoEntity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import java.time.LocalDateTime;

@Entity
@Table(name = "oam_client_hardware")
@Getter
@Setter
@NoArgsConstructor
@ToString
public class HardWareEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "support_code", referencedColumnName = "supportCode")
    private LicenseInfoEntity licenseInfo; // 라이선스와의 관계 (이전에 licenseInfoEntity로 잘못 지정됨)

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Type type;

    @Column(nullable = false)
    private String model;

    @Column(nullable = true)
    private String serialNumber;

    @Column(nullable = false)
    private LocalDateTime deliveryAt;

    public enum Type {
        CPU,
        MEMORY,
        HBA,
        DISK,
        NIC,
        SAS_CARD
    }

    @Override
    public String toString() {
        return "HardWareEntity{" +
                "id=" + id +
                ", licenseInfo=" + licenseInfo +
                ", type=" + type +
                ", model='" + model + '\'' +
                ", serialNumber='" + serialNumber + '\'' +
                ", deliveryAt=" + deliveryAt +
                '}';
    }
}