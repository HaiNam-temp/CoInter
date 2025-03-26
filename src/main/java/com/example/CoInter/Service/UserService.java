package com.example.CoInter.Service;

import com.example.CoInter.DTO.UserCvDto;
import com.example.CoInter.DTO.UserInfoDto;
import com.example.CoInter.Payload.Request.UploadCvRequest;
import com.example.CoInter.Payload.ResponseData;

public interface UserService {
    UserInfoDto getCurrentUserIfo(String email);
    UserCvDto getCurrentUserCv(String email);
    ResponseData UploadCv(String email,UploadCvRequest uploadCvRequest);
}
