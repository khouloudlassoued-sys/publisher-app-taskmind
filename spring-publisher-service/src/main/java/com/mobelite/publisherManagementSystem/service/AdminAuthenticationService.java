package com.mobelite.publisherManagementSystem.service;

import com.mobelite.publisherManagementSystem.dto.request.auth.AuthenticationRequest;
import com.mobelite.publisherManagementSystem.dto.response.auth.AdminResponse;
import com.mobelite.publisherManagementSystem.dto.response.auth.AuthToken;
import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import com.mobelite.publisherManagementSystem.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AdminAuthenticationService {
    private final AdminRepository repository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AdminAuthenticationService(AdminRepository repository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.repository = repository; this.passwordEncoder = passwordEncoder; this.jwtService = jwtService;
    }

    public AuthToken authenticate(AuthenticationRequest request) {
        String username = request.getUsername().trim().toLowerCase();
        Admin admin = repository.findByUsername(username)
                .filter(candidate -> passwordEncoder.matches(request.getPassword(), candidate.getPasswordHash()))
                .orElseThrow(() -> new org.springframework.security.authentication.BadCredentialsException("Invalid username or password"));
        return AuthToken.builder().accessToken(jwtService.issue(admin.getId(), admin.getUsername()))
                .tokenType("Bearer").expiresAt(jwtService.expiresAt()).adminId(admin.getId()).build();
    }

    public AdminResponse current(String subject) {
        Admin admin = repository.findById(Long.valueOf(subject)).orElseThrow();
        return new AdminResponse(admin.getId(), admin.getUsername());
    }
}