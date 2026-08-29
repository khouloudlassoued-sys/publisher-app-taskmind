package com.mobelite.publisherManagementSystem.controller;

import com.mobelite.publisherManagementSystem.dto.response.auth.AuthToken;
import com.mobelite.publisherManagementSystem.service.AdminAuthenticationService;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class AuthControllerTest {
    private final AdminAuthenticationService service = mock(AdminAuthenticationService.class);
    private final MockMvc mvc = MockMvcBuilders.standaloneSetup(new AuthController(service)).build();

    @Test
    void loginAcceptsValidRequest() throws Exception {
        when(service.authenticate(any())).thenReturn(AuthToken.builder().accessToken("token").build());
        mvc.perform(post("/api/v1/auth/login").contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"admin\",\"password\":\"secret\"}"))
                .andExpect(status().isOk());
    }

    @Test
    void incompleteLoginIsRejected() throws Exception {
        mvc.perform(post("/api/v1/auth/login").contentType(MediaType.APPLICATION_JSON)
                .content("{\"username\":\"\",\"password\":\"\"}"))
                .andExpect(status().isBadRequest());
    }
}