package com.example.CoInter.Controller;

import com.example.CoInter.Payload.Request.SigninRequest;
import com.example.CoInter.Payload.Request.SignupRequest;
import com.example.CoInter.Payload.ResponseData;
import com.example.CoInter.Service.LoginService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/login")
public class LoginController {
    @Autowired
    LoginService loginService;
    @PostMapping("/signup")
    public ResponseEntity<ResponseData> createUser(@RequestBody SignupRequest signupRequest) {
        ResponseData responseData = ResponseData.resp();
        boolean success = loginService.createUser(signupRequest);
        return ResponseEntity.ok(responseData);
    }
    @GetMapping("/signin")
    public ResponseEntity<ResponseData> authUser(@RequestParam String email, @RequestParam String password) {
        ResponseData responseData = ResponseData.resp();
        String token=loginService.authUser(email,password);
        responseData.setData(token);
        return ResponseEntity.ok(responseData);
    }

}
