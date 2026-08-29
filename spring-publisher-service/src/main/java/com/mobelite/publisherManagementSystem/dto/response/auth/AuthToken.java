package com.mobelite.publisherManagementSystem.dto.response.auth;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

@Getter
@Builder
@AllArgsConstructor
public class AuthToken {
    private String accessToken;
    private String tokenType;
    private Instant expiresAt;
    private Long adminId;
}