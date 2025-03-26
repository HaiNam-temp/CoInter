package com.example.CoInter.Repository;

import com.example.CoInter.Entity.Users;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<Users, Integer> {
    Users findUserByEmail(String email);
}
