package com.mobelite.publisherManagementSystem.service;

import com.mobelite.publisherManagementSystem.dto.request.auth.AuthenticationRequest;
import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import com.mobelite.publisherManagementSystem.security.JwtService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AdminAuthenticationServiceTest {
    @Mock AdminRepository repository;
    @Mock PasswordEncoder passwordEncoder;
    @Mock JwtService jwtService;
    @InjectMocks AdminAuthenticationService service;

    @Test
    void authenticatesNormalizedUsername() {
        Admin admin = Admin.builder().id(1L).username("admin").passwordHash("hash").build();
        AuthenticationRequest request = new AuthenticationRequest();
        request.setUsername(" ADMIN "); request.setPassword("secret");
        when(repository.findByUsername("admin")).thenReturn(Optional.of(admin));
        when(passwordEncoder.matches("secret", "hash")).thenReturn(true);
        when(jwtService.issue(1L, "admin")).thenReturn("token");
        assertThat(service.authenticate(request).getAccessToken()).isEqualTo("token");
    }

    @Test
    void rejectsUnknownOrInvalidCredentials() {
        AuthenticationRequest request = new AuthenticationRequest();
        request.setUsername("admin"); request.setPassword("secret");
        when(repository.findByUsername("admin")).thenReturn(Optional.empty());
        assertThatThrownBy(() -> service.authenticate(request)).isInstanceOf(BadCredentialsException.class)
                .hasMessage("Invalid username or password");
    }
}