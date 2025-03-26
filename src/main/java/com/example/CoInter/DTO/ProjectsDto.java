package com.example.CoInter.DTO;

import jakarta.persistence.Column;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Builder
public class ProjectsDto {
    private String projectname;
    private String projectdesc;
    private String responsibilities;
}
