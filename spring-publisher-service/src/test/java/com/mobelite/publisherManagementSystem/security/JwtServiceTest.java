package com.mobelite.publisherManagementSystem.security;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtServiceTest {
    @Test
    void expiredTokenIsRejected() {
        JwtService service = new JwtService("12345678901234567890123456789012", -1, "issuer", "audience");
        String token = service.issue(1L, "admin");
        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(RuntimeException.class);
    }
}