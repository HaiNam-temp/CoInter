package com.example.CoInter.Controller;

import com.example.CoInter.Payload.Request.UploadCvRequest;
import com.example.CoInter.Service.UserService;
import com.example.CoInter.Util.JwtUtilHelper;
import com.example.CoInter.Exception.ApiException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.context.request.WebRequest;

@RestController
@RequestMapping("/user")
public class UserController {
    @Autowired
    JwtUtilHelper jwtUtil;
    @Autowired
    UserService userService;
    private String getTokenFromHeader(WebRequest request) {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            return header.substring(7);
        }
        return null;
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUserIfo(WebRequest request){
        String token=getTokenFromHeader(request);
        if(token==null){
            throw ApiException.ErrForbidden().build();
        }
        if(!jwtUtil.verifyToken(token)){
            throw ApiException.ErrForbidden().build();
        }
        String email= jwtUtil.getEmail(token);
        return new ResponseEntity<>(userService.getCurrentUserIfo(email), HttpStatus.OK);
    }
    @PostMapping("/cv")
    public ResponseEntity<?> UploadCV(WebRequest request, @RequestBody UploadCvRequest uploadCvRequest){
        String token=getTokenFromHeader(request);
        if(token==null){
            throw ApiException.ErrForbidden().build();
        }
        if(!jwtUtil.verifyToken(token)){
            throw ApiException.ErrForbidden().build();
        }
        String email= jwtUtil.getEmail(token);
        return  new ResponseEntity<>(userService.UploadCv(email,uploadCvRequest), HttpStatus.OK);
    }
    @GetMapping("/cv")
    public ResponseEntity<?>GetCV(WebRequest request){
        String token=getTokenFromHeader(request);
        if(token==null){
            throw ApiException.ErrForbidden().build();
        }
        if(!jwtUtil.verifyToken(token)){
            throw ApiException.ErrForbidden().build();
        }
        String email= jwtUtil.getEmail(token);
        return new ResponseEntity<>(userService.getCurrentUserCv(email), HttpStatus.OK);
    }
}
