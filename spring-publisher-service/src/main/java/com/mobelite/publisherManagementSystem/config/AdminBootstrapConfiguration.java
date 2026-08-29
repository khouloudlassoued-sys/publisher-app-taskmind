package com.mobelite.publisherManagementSystem.config;

import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

@Configuration
@Profile("dev")
@ConditionalOnProperty(name = "app.admin-bootstrap-enabled", havingValue = "true")
public class AdminBootstrapConfiguration {

    @Bean
    public CommandLineRunner adminBootstrap(
            AdminRepository repository,
            @Value("${ADMIN_BOOTSTRAP_USERNAME:}") String username,
            @Value("${ADMIN_BOOTSTRAP_PASSWORD_HASH:}") String passwordHash) {
        return args -> {
            if (username.isBlank() || passwordHash.isBlank()) {
                throw new IllegalStateException(
                        "Admin bootstrap requires ADMIN_BOOTSTRAP_USERNAME and ADMIN_BOOTSTRAP_PASSWORD_HASH");
            }
            String normalizedUsername = username.trim().toLowerCase();
            if (!repository.existsByUsername(normalizedUsername)) {
                repository.save(Admin.builder()
                        .username(normalizedUsername)
                        .passwordHash(passwordHash)
                        .build());
            }
        };
    }
}