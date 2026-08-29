package com.mobelite.publisherManagementSystem.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mobelite.publisherManagementSystem.dto.response.ApiResponseDto;
import com.mobelite.publisherManagementSystem.security.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.MediaType;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http, JwtAuthenticationFilter jwtFilter, ObjectMapper mapper) throws Exception {
        http.csrf(csrf -> csrf.disable()).cors(cors -> {}).sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth.requestMatchers("/api/v1/auth/login", "/actuator/health", "/swagger-ui/**", "/v3/api-docs/**").permitAll().anyRequest().hasRole("ADMIN"))
                .exceptionHandling(errors -> errors.authenticationEntryPoint((request, response, exception) -> write(response, mapper, 401, "Authentication required"))
                        .accessDeniedHandler((request, response, exception) -> write(response, mapper, 403, "Access denied")))
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    private void write(jakarta.servlet.http.HttpServletResponse response, ObjectMapper mapper, int status, String message) throws java.io.IOException {
        response.setStatus(status); response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write(mapper.writeValueAsString(ApiResponseDto.error(message)));
    }
}