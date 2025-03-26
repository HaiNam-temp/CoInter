package com.example.CoInter.Service.imp;

import com.example.CoInter.Entity.Users;
import com.example.CoInter.Exception.ApiException;
import com.example.CoInter.Payload.Request.SignupRequest;
import com.example.CoInter.Repository.UserRepository;
import com.example.CoInter.Service.LoginService;
import com.example.CoInter.Util.JwtUtilHelper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class LoginServiceImp implements LoginService {
    @Autowired
    JwtUtilHelper jwtUtilHelper;
    @Autowired
    PasswordEncoder passwordEncoder;
    @Autowired
    UserRepository userRepository;
    @Override
    public boolean createUser(SignupRequest signupRequest) {
        Users user=userRepository.findUserByEmail(signupRequest.getEmail());
        if(user!=null){
            throw ApiException.ErrExisted().build();
        }
        log.info("[UserServiceImpl - createUser] signupRequest: {}", signupRequest);

        Users newUser=new Users();
        newUser.setEmail(signupRequest.getEmail());
        newUser.setFullname(signupRequest.getFullname());
        newUser.setPassword(passwordEncoder.encode(signupRequest.getPassword()));
        userRepository.save(newUser);
        return true;

    }

    @Override
    public String authUser(String email, String password) {
        Users user=userRepository.findUserByEmail(email);
        if(user==null){
            throw ApiException.ErrBadCredentials().build();
        }
        if(!passwordEncoder.matches(password,user.getPassword())){
            throw ApiException.ErrBadCredentials().build();
        }
        return jwtUtilHelper.generateToken(email);
    }
}
