package com.example.CoInter.Entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.boot.autoconfigure.amqp.RabbitConnectionDetails;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
@Entity(name="projects")
public class Projects {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int projectsid;
    @Column(name="projectname")
    private String projectname;
    @Column(name="projectdesc")
    private String projectdesc;
    @Column(name="responsibilities")
    private String responsibilities;

    @ManyToOne
    @JoinColumn(name="cvid")
    private Cv cv;
}
