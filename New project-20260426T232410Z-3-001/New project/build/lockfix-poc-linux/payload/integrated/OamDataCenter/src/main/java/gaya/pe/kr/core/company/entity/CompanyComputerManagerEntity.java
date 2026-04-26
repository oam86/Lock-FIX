package gaya.pe.kr.core.company.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Table (name = "oam_manager")
@Entity
@Getter
@Setter
public class CompanyComputerManagerEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // ID를 자동 생성
    private Long id;

    String name;

    String position;

    String department;

    String email;

}
