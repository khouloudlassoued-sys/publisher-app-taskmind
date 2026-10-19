package com.mobelite.publisherManagementSystem.service;

import com.mobelite.publisherManagementSystem.dto.request.auth.AuthenticationRequest;
import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import com.mobelite.publisherManagementSystem.security.JwtService;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class AdminAuthenticationServiceInvalidPasswordTest {
    @Test
    void rejectsIncorrectPasswordWithoutIssuingToken() {
        AdminRepository repository = mock(AdminRepository.class);
        PasswordEncoder passwordEncoder = mock(PasswordEncoder.class);
        JwtService jwtService = mock(JwtService.class);
        AdminAuthenticationService service = new AdminAuthenticationService(repository, passwordEncoder, jwtService);
        Admin admin = Admin.builder().id(1L).username("admin").passwordHash("stored-hash").build();
        AuthenticationRequest request = new AuthenticationRequest();
        request.setUsername("admin");
        request.setPassword("incorrect");
        when(repository.findByUsername("admin")).thenReturn(Optional.of(admin));
        when(passwordEncoder.matches("incorrect", "stored-hash")).thenReturn(false);

        assertThatThrownBy(() -> service.authenticate(request))
                .isInstanceOf(BadCredentialsException.class)
                .hasMessage("Invalid username or password");
        verify(jwtService, never()).issue(1L, "admin");
    }
}
