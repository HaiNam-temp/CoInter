package com.example.CoInter.Payload.Request;

import com.example.CoInter.DTO.ProjectsDto;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
@Getter
@Setter
public class UploadCvRequest {
    private String position;
    private String university;
    private String summary;
    private String skills;
    private String softskills;
    private String certificate;
    private List<ProjectsDto> projects;
}
