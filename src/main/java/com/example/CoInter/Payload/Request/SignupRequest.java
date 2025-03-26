package com.example.CoInter.Payload.Request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SignupRequest {
    private String email;
    private String fullname;
    private String password;
}
