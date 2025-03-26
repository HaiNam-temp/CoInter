package com.example.CoInter.Service;

import com.example.CoInter.Payload.Request.SignupRequest;

public interface LoginService {
    boolean createUser(SignupRequest signupRequest);
    String authUser(String email, String password);
}
