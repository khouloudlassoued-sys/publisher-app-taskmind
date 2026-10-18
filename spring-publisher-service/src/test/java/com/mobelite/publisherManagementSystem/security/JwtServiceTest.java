package com.mobelite.publisherManagementSystem.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtServiceTest {
    private static final String SECRET = "12345678901234567890123456789012";
    private static final long EXPIRATION_MS = 3600000;

    @Test
    void expiredTokenIsRejected() {
        JwtService service = new JwtService(SECRET, -1, "issuer", "audience");
        String token = service.issue(1L, "admin");
        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(RuntimeException.class);
    }

    @Test
    void validTokenIsParsedWithExpectedClaims() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");
        Claims claims = service.parse(service.issue(1L, "admin"));

        assertThat(claims.getSubject()).isEqualTo("1");
        assertThat(claims.get("username", String.class)).isEqualTo("admin");
        assertThat(claims.get("authorities", String.class)).isEqualTo("ROLE_ADMIN");
        assertThat(claims.getIssuer()).isEqualTo("issuer");
        assertThat(claims.getAudience()).contains("audience");
    }

    @Test
    void tokenWithWrongIssuerIsRejected() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");
        JwtService otherIssuerService = new JwtService(SECRET, EXPIRATION_MS, "other-issuer", "audience");
        String token = otherIssuerService.issue(1L, "admin");

        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void tokenWithWrongAudienceIsRejected() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");
        JwtService otherAudienceService = new JwtService(SECRET, EXPIRATION_MS, "issuer", "other-audience");
        String token = otherAudienceService.issue(1L, "admin");

        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void tokenSignedWithAnotherSecretIsRejected() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");
        JwtService otherSecretService = new JwtService("abcdefghijklmnopqrstuvwxyz123456", EXPIRATION_MS,
                "issuer", "audience");
        String token = otherSecretService.issue(1L, "admin");

        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void malformedTokenIsRejected() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");

        assertThatThrownBy(() -> service.parse("not-a-jwt")).isInstanceOf(JwtException.class);
    }

    @Test
    void unsignedTokenIsRejected() {
        JwtService service = new JwtService(SECRET, EXPIRATION_MS, "issuer", "audience");
        String token = Jwts.builder()
                .subject("1")
                .issuer("issuer")
                .audience().add("audience").and()
                .compact();

        assertThatThrownBy(() -> service.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void tooShortSecretIsRejected() {
        assertThatThrownBy(() -> new JwtService("short", EXPIRATION_MS, "issuer", "audience"))
                .isInstanceOf(IllegalArgumentException.class);
    }
}
