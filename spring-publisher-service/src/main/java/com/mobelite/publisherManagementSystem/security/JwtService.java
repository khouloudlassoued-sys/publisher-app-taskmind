package com.mobelite.publisherManagementSystem.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;

@Service
public class JwtService {
    private final SecretKey key;
    private final long expirationMs;
    private final String issuer;
    private final String audience;

    public JwtService(@Value("${app.jwt.secret}") String secret,
                      @Value("${app.jwt.expiration-ms}") long expirationMs,
                      @Value("${app.jwt.issuer}") String issuer,
                      @Value("${app.jwt.audience}") String audience) {
        if (secret.length() < 32) {
            throw new IllegalArgumentException("JWT secret must contain at least 32 characters");
        }
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expirationMs = expirationMs;
        this.issuer = issuer;
        this.audience = audience;
    }

    public String issue(Long adminId, String username) {
        Instant now = Instant.now();
        return Jwts.builder().subject(adminId.toString()).claim("username", username)
                .claim("authorities", "ROLE_ADMIN").issuer(issuer).audience().add(audience).and()
                .issuedAt(Date.from(now)).expiration(Date.from(now.plusMillis(expirationMs)))
                .signWith(key).compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().verifyWith(key).requireIssuer(issuer).requireAudience(audience)
                .build().parseSignedClaims(token).getPayload();
    }

    public Instant expiresAt() { return Instant.now().plusMillis(expirationMs); }
}