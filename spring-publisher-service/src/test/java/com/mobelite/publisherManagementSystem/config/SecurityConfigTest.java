package com.mobelite.publisherManagementSystem.config;

import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import com.mobelite.publisherManagementSystem.security.JwtService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Optional;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.mockito.Mockito.when;

@SpringBootTest
@AutoConfigureMockMvc
class SecurityConfigTest {
    private static final Long ADMIN_ID = 1L;
    private static final String TEST_ADMIN_USERNAME = "test-admin";
    private static final String BASE64_URL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

    @Autowired
    private MockMvc mvc;

    @Autowired
    private JwtService jwtService;

    @MockitoBean
    private AdminRepository adminRepository;

    @Value("${app.jwt.secret}")
    private String jwtSecret;

    @Value("${app.jwt.issuer}")
    private String jwtIssuer;

    @Value("${app.jwt.audience}")
    private String jwtAudience;

    @Test
    void protectedEndpointRejectsUnauthenticatedRequest() throws Exception {
        mvc.perform(get("/api/v1/auth/me")).andExpect(status().isUnauthorized());
    }

    @Test
    void catalogueGetEndpointsReturnOkWithoutAuthentication() throws Exception {
        mvc.perform(get("/api/v1/authors")).andExpect(status().isOk());
        mvc.perform(get("/api/v1/books")).andExpect(status().isOk());
        mvc.perform(get("/api/v1/magazines")).andExpect(status().isOk());
        mvc.perform(get("/api/v1/publications")).andExpect(status().isOk());
    }

    @Test
    void validAdminJwtCanAccessCurrentAdminEndpoint() throws Exception {
        when(adminRepository.findById(ADMIN_ID)).thenReturn(Optional.of(
                Admin.builder().id(ADMIN_ID).username(TEST_ADMIN_USERNAME).build()));
        String token = jwtService.issue(ADMIN_ID, TEST_ADMIN_USERNAME);

        mvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk());
    }

    @Test
    void jwtWithAlteredSignatureIsRejectedOnCurrentAdminEndpoint() throws Exception {
        String token = jwtService.issue(ADMIN_ID, TEST_ADMIN_USERNAME);
        String alteredToken = alterLastCharacter(token);

        mvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + alteredToken))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void expiredJwtIsRejectedOnCurrentAdminEndpoint() throws Exception {
        JwtService expiredTokenService = new JwtService(jwtSecret, -1, jwtIssuer, jwtAudience);
        String token = expiredTokenService.issue(ADMIN_ID, TEST_ADMIN_USERNAME);

        mvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + token))
                .andExpect(status().isUnauthorized());
    }

    private String alterLastCharacter(String token) {
        int lastCharacterIndex = token.length() - 1;
        int encodedCharacterIndex = BASE64_URL_ALPHABET.indexOf(token.charAt(lastCharacterIndex));
        char alteredLastCharacter = BASE64_URL_ALPHABET.charAt(encodedCharacterIndex ^ 16);
        return token.substring(0, lastCharacterIndex) + alteredLastCharacter;
    }
}