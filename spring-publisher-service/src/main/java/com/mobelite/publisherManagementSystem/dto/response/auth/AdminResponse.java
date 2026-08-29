package com.mobelite.publisherManagementSystem.dto.response.auth;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class AdminResponse {
    private Long adminId;
    private String username;
}