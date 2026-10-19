package com.mobelite.publisherManagementSystem.config;

import com.mobelite.publisherManagementSystem.entity.Admin;
import com.mobelite.publisherManagementSystem.repository.AdminRepository;
import org.junit.jupiter.api.Test;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Profile;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class AdminBootstrapConfigurationTest {
    @Test
    void bootstrapIsRestrictedToDevAndExplicitlyEnabled() {
        Profile profile = AdminBootstrapConfiguration.class.getAnnotation(Profile.class);
        ConditionalOnProperty enabled = AdminBootstrapConfiguration.class.getAnnotation(ConditionalOnProperty.class);

        assertThat(profile.value()).containsExactly("dev");
        assertThat(enabled.name()).containsExactly("app.admin-bootstrap-enabled");
        assertThat(enabled.havingValue()).isEqualTo("true");
    }

    @Test
    void createsAdminUsingNormalizedUsernameWhenMissing() throws Exception {
        AdminRepository repository = mock(AdminRepository.class);
        when(repository.existsByUsername("admin")).thenReturn(false);
        CommandLineRunner runner = new AdminBootstrapConfiguration().adminBootstrap(repository, " Admin ", "hashed-value");

        runner.run();

        org.mockito.ArgumentCaptor<Admin> saved = org.mockito.ArgumentCaptor.forClass(Admin.class);
        verify(repository).save(saved.capture());
        assertThat(saved.getValue().getUsername()).isEqualTo("admin");
        assertThat(saved.getValue().getPasswordHash()).isEqualTo("hashed-value");
    }

    @Test
    void doesNotCreateDuplicateAdmin() throws Exception {
        AdminRepository repository = mock(AdminRepository.class);
        when(repository.existsByUsername("admin")).thenReturn(true);
        CommandLineRunner runner = new AdminBootstrapConfiguration().adminBootstrap(repository, "admin", "hashed-value");

        runner.run();

        verify(repository, never()).save(org.mockito.ArgumentMatchers.any(Admin.class));
    }

    @Test
    void rejectsMissingBootstrapCredentialsBeforeRepositoryAccess() {
        AdminRepository repository = mock(AdminRepository.class);
        CommandLineRunner runner = new AdminBootstrapConfiguration().adminBootstrap(repository, " ", "hashed-value");

        assertThatThrownBy(runner::run)
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("ADMIN_BOOTSTRAP_USERNAME");
        verify(repository, never()).existsByUsername(org.mockito.ArgumentMatchers.anyString());
    }
}
