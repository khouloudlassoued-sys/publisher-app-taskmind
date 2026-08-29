package com.mobelite.publisherManagementSystem.controller;

import com.mobelite.publisherManagementSystem.dto.request.auth.AuthenticationRequest;
import com.mobelite.publisherManagementSystem.dto.response.ApiResponseDto;
import com.mobelite.publisherManagementSystem.dto.response.auth.AdminResponse;
import com.mobelite.publisherManagementSystem.dto.response.auth.AuthToken;
import com.mobelite.publisherManagementSystem.service.AdminAuthenticationService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    private final AdminAuthenticationService service;
    public AuthController(AdminAuthenticationService service) { this.service = service; }

    @PostMapping("/login")
    public ApiResponseDto<AuthToken> login(@Valid @RequestBody AuthenticationRequest request) {
        return ApiResponseDto.success(service.authenticate(request), "Login successful");
    }

    @GetMapping("/me")
    public ApiResponseDto<AdminResponse> me(Authentication authentication) {
        return ApiResponseDto.success(service.current(authentication.getName()), "Authenticated admin");
    }

    @PostMapping("/logout")
    public ApiResponseDto<Void> logout() { return ApiResponseDto.success(null, "Logout successful"); }
}