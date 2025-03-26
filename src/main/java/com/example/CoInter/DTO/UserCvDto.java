package com.example.CoInter.DTO;

import com.example.CoInter.Entity.Users;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
@Getter
@Setter
@Builder
public class UserCvDto {
    private String fullname;
    private String position;
    private String university;
    private String summary;
    private String skills;
    private String softskills;
    private String certificate;
    private List<ProjectsDto> projects;
}
