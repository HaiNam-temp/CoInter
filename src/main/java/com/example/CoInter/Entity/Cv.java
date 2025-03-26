package com.example.CoInter.Entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UuidGenerator;

import java.util.List;

@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Entity(name="cv")
public class Cv {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long cvid;
    @Column(name="position")
    private String position;
    @Column(name="university")
    private String university;
    @Column(name="summary")
    private String summary;
    @Column(name="skills")
    private String skills;
    @Column(name="softskills")
    private String softskills;
    @Column(name="certificate")
    private String certificate;
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "userid", referencedColumnName = "userid")
    private Users users;

    @OneToMany(mappedBy = "cv")
    private List<Projects> projects;
}
