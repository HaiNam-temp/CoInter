package com.example.CoInter.Service.imp;

import com.example.CoInter.DTO.ProjectsDto;
import com.example.CoInter.DTO.UserCvDto;
import com.example.CoInter.DTO.UserInfoDto;
import com.example.CoInter.Entity.Cv;
import com.example.CoInter.Entity.Projects;
import com.example.CoInter.Exception.ApiException;
import com.example.CoInter.Entity.Users;
import com.example.CoInter.Payload.Request.UploadCvRequest;
import com.example.CoInter.Payload.ResponseData;
import com.example.CoInter.Repository.CvRepository;
import com.example.CoInter.Repository.ProjectRepository;
import com.example.CoInter.Repository.UserRepository;
import com.example.CoInter.Service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class UserServiceImp implements UserService {
    @Autowired
    UserRepository userRepository;
    @Autowired
    CvRepository cvRepository;
    @Autowired
    ProjectRepository projectRepository;
    @Override
    public UserInfoDto getCurrentUserIfo(String email) {
        Users user = userRepository.findUserByEmail(email);
        if (user == null) {
            throw ApiException.ErrBadCredentials().build();
        }
        UserInfoDto userInfoDto = UserInfoDto.builder()
                .fullname(user.getFullname())
                .email(user.getEmail())
                .build();
        return userInfoDto;
    }

    @Override
    public UserCvDto getCurrentUserCv(String email) {
        Users user = userRepository.findUserByEmail(email);
        if (user == null) {
            throw ApiException.ErrBadCredentials().build();
        }
        Cv cv = user.getCv();

        List<Projects> projects=cv.getProjects();
        List<ProjectsDto> projectsDtoList=new ArrayList<>();
        for(Projects project:projects){
            ProjectsDto projectsDto=ProjectsDto.builder()
                    .projectname(project.getProjectname())
                    .projectdesc(project.getProjectdesc())
                    .responsibilities(project.getResponsibilities())
                    .build();
            projectsDtoList.add(projectsDto);
        }

        UserCvDto userCvDto=UserCvDto.builder()
                .fullname(user.getFullname())
                .position(cv.getPosition())
                .summary(cv.getSummary())
                .skills(cv.getSkills())
                .certificate(cv.getCertificate())
                .softskills(cv.getSoftskills())
                .university(cv.getUniversity())
                .projects(projectsDtoList)
                .build();
        return userCvDto;
    }

    @Override
    public ResponseData UploadCv(String email, UploadCvRequest uploadCvRequest) {
        Users user = userRepository.findUserByEmail(email);
        if (user == null) {
            throw ApiException.ErrBadCredentials().build();
        }
        ResponseData responseData = new ResponseData();
        responseData.resp();
        List<Projects>projectsList=new ArrayList<>();
        Cv cv =Cv.builder()
                .users(user)
                .certificate(uploadCvRequest.getCertificate())
                .position(uploadCvRequest.getPosition())
                .summary(uploadCvRequest.getSummary())
                .skills(uploadCvRequest.getSkills())
                .university(uploadCvRequest.getUniversity())
                .softskills(uploadCvRequest.getSoftskills())
                .build();
        cvRepository.save(cv);
        for(ProjectsDto projectsDto:uploadCvRequest.getProjects()){
            Projects projects=Projects.builder()
                    .projectname(projectsDto.getProjectname())
                    .projectdesc(projectsDto.getProjectdesc())
                    .responsibilities(projectsDto.getResponsibilities())
                    .cv(cv)
                    .build();
            projectRepository.save(projects);
            projectsList.add(projects);
        }
        cv.setProjects(projectsList);
        cvRepository.save(cv);
        responseData.setMessage("Upload CV thành công");
        return responseData;
    }
}
