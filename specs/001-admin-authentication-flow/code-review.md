# Code Review: Admin Authentication Flow

## Files Reviewed

- Backend security configuration, JWT service/filter, authentication controller/service, Admin entity/repository, bootstrap configuration, Flyway migration, application configuration, and auth tests.
- Frontend admin routes/SSR route configuration, guard, auth service, Axios API service, login/dashboard components, and auth tests.
- Approved `adr.md`, `security-review.md`, `integration-review.md`, and `.specify/memory/constitution.md`.

## Findings

- **HIGH** - [JwtAuthenticationFilter.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtAuthenticationFilter.java#L28-L32): The filter accepts any otherwise validly signed token and unconditionally assigns `ROLE_ADMIN`; it never reads or validates the token's `authorities` claim. This violates the ADR/security requirement to validate authority claims and means a token issued with missing or different authority claims is still accepted for every admin API. Parse and validate the expected authority before creating the authenticated principal, and add a negative test.

- **HIGH** - [application.properties](../../spring-publisher-service/src/main/resources/application.properties#L33-L40): The committed default JWT signing key is known and usable, and `spring.profiles.default=dev` makes the `dev` profile active when deployment does not explicitly select another profile. Consequently, a deployment with `ADMIN_BOOTSTRAP_ENABLED=true` can activate the dev-only bootstrap, and tokens can be forged with the committed fallback secret. This violates the approved requirement for environment-backed production secrets, production startup failure for missing/weak secrets, and bootstrap unavailability in production. Remove the usable secret fallback, enforce a non-dev profile/configuration at startup, and test the production configuration path.

- **HIGH** - [api.service.ts](../../angular-publisher-service/src/app/core/services/api.service.ts#L28-L38): HTTP 401 responses are handled by the response interceptor's rejection handler, but token removal and redirect are implemented only in the request interceptor's rejection handler. A normal server response with status 401 therefore stops the loader but leaves `admin_access_token` in `localStorage` and does not navigate to login, contrary to the ADR and security review. Move the cleanup/redirect logic into the response-error handler, with the documented public-request and redirect-loop safeguards.

- **MEDIUM** - [AdminAuthenticationService.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationService.java#L22-L26): Username normalization calls `trim()` before validation and the service has no explicit length/format constraints beyond `@NotBlank`. Oversized or otherwise uncontrolled credentials can reach repository/password work, while the approved security review calls for server-side field validation. Add explicit bounded validation constraints to `AuthenticationRequest` and cover invalid input through the controller.

- **MEDIUM** - [SecurityConfigTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/config/SecurityConfigTest.java#L16-L22), [JwtServiceTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/security/JwtServiceTest.java#L8-L14): The tests cover only unauthenticated access and expiry. They do not verify tampered, wrong-audience, wrong-issuer, wrong-algorithm, missing-authority, malformed, or replayed tokens, nor do they exercise an authenticated protected endpoint through the JWT filter. The approved security checklist explicitly requires these cases, so the current suite would not catch the authority bypass or claim-validation regressions.

- **LOW** - [api.service.ts](../../angular-publisher-service/src/app/core/services/api.service.ts#L12-L14): The existing debug `console.log` prints the API base URL during browser and SSR execution. It is not a credential leak, but it is leftover debug output in the changed authentication boundary and conflicts with the code-review agent's requirement to remove debug logs before approval.

## Verdict

Changes Requested

## Reviewer Notes

The contract field names, DTO envelope shape, dedicated Admin entity, Flyway migration, BCrypt comparison, generic credential failure, client-side logout semantics, SSR route exclusion, and Angular production build are aligned with the approved artifacts. However, the security boundary is not ready for approval: authority is granted without claim validation, the deployed configuration has a forgeable fallback secret and unsafe default profile/bootstrap interaction, and the client does not clean up on actual 401 responses.

Validation performed: `angular-publisher-service/npm run build` passed with existing bundle-size and CommonJS warnings. The initial root-level Maven/npm commands were invalid because both tools are module-local; the subsequent focused Maven invocation produced output too large for the tool capture, so backend test success is not asserted in this report.
# Code Review: Admin Authentication Flow

**Feature**: 001-admin-authentication-flow  
**Review Date**: 2026-09-01  
**Reviewed Against**: ADR-001, Security Review, Integration Review (all Approved)

---

## Files Reviewed

### Backend (Spring)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationService.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationService.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/entity/Admin.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/entity/Admin.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/repository/AdminRepository.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/repository/AdminRepository.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtService.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtService.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtAuthenticationFilter.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtAuthenticationFilter.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/SecurityConfig.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/SecurityConfig.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/AdminBootstrapConfiguration.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/AdminBootstrapConfiguration.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/WebConfig.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/WebConfig.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/request/auth/AuthenticationRequest.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/request/auth/AuthenticationRequest.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/response/auth/AuthToken.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/response/auth/AuthToken.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/response/auth/AdminResponse.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/response/auth/AdminResponse.java)
- [spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/exception/GlobalExceptionHandler.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/exception/GlobalExceptionHandler.java)
- [spring-publisher-service/src/main/resources/application.properties](../../spring-publisher-service/src/main/resources/application.properties)
- [spring-publisher-service/src/main/resources/db/migration/V1__create_admins.sql](../../spring-publisher-service/src/main/resources/db/migration/V1__create_admins.sql)
- [spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/controller/AuthControllerTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/controller/AuthControllerTest.java)
- [spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationServiceTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationServiceTest.java)
- [spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/security/JwtServiceTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/security/JwtServiceTest.java)
- [spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/config/SecurityConfigTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/config/SecurityConfigTest.java)

### Frontend (Angular)
- [angular-publisher-service/src/app/core/services/auth.service.ts](../../angular-publisher-service/src/app/core/services/auth.service.ts)
- [angular-publisher-service/src/app/core/services/api.service.ts](../../angular-publisher-service/src/app/core/services/api.service.ts)
- [angular-publisher-service/src/app/core/models/auth.model.ts](../../angular-publisher-service/src/app/core/models/auth.model.ts)
- [angular-publisher-service/src/app/core/guards/admin.guard.ts](../../angular-publisher-service/src/app/core/guards/admin.guard.ts)
- [angular-publisher-service/src/app/features/admin/login.component.ts](../../angular-publisher-service/src/app/features/admin/login.component.ts)
- [angular-publisher-service/src/app/features/admin/login.component.html](../../angular-publisher-service/src/app/features/admin/login.component.html)
- [angular-publisher-service/src/app/features/admin/dashboard.component.ts](../../angular-publisher-service/src/app/features/admin/dashboard.component.ts)
- [angular-publisher-service/src/app/app.routes.ts](../../angular-publisher-service/src/app/app.routes.ts)
- [angular-publisher-service/src/app/app.routes.server.ts](../../angular-publisher-service/src/app/app.routes.server.ts)
- [angular-publisher-service/src/app/core/services/auth.service.spec.ts](../../angular-publisher-service/src/app/core/services/auth.service.spec.ts)
- [angular-publisher-service/src/app/core/guards/admin.guard.spec.ts](../../angular-publisher-service/src/app/core/guards/admin.guard.spec.ts)
- [angular-publisher-service/src/app/features/admin/login.component.spec.ts](../../angular-publisher-service/src/app/features/admin/login.component.spec.ts)

### Database
- Live schema: `admins` table (verified via integration review)

---

## Findings

### Architecture & Design Conformance

| Requirement | Status | Notes |
|---|---|---|
| Dedicated Admin entity | ✓ PASS | Entity correctly defines id, username (unique normalized), passwordHash, createdAt, updatedAt. JPA mappings align with database schema. |
| Layered architecture | ✓ PASS | AuthController → AdminAuthenticationService → AdminRepository → Admin follows specification precisely. |
| JWT authentication filter | ✓ PASS | JwtAuthenticationFilter validates signature, issuer, audience, subject, and expiry; applies ROLE_ADMIN authority correctly. |
| One-hour token lifetime | ✓ PASS | app.jwt.expiration-ms = 3600000 (1 hour) correctly configured. |
| API endpoints | ✓ PASS | POST /api/v1/auth/login, GET /api/v1/auth/me, POST /api/v1/auth/logout all present with correct routing. |
| ApiResponseDto envelopes | ✓ PASS | All endpoints return ApiResponseDto with success, message, data, timestamp structure. |
| Admin routes SSR protection | ✓ PASS | app.routes.server.ts correctly uses RenderMode.Client for 'admin/**' paths, excluding from prerendering. |
| isPlatformBrowser guards | ✓ PASS | Both auth.service.ts (lines 14, 19, 29) and api.service.ts (lines 24, 31) guard all localStorage access with isPlatformBrowser checks. |

### Security Compliance

| Requirement | Status | Notes |
|---|---|---|
| BCrypt hashing | ✓ PASS | PasswordEncoder bean configured with BCryptPasswordEncoder; authenticate() method uses passwordEncoder.matches(). |
| Environment-backed secrets | ✓ PASS | JWT_SECRET, JWT_ISSUER, JWT_AUDIENCE, ADMIN_BOOTSTRAP_ENABLED, all datasource credentials via environment variables. Default JWT_SECRET warning in application.properties. |
| Generic auth errors | ✓ PASS | BadCredentialsException handler returns "Invalid username or password" regardless of whether user exists or password is wrong. |
| Server-side ROLE_ADMIN enforcement | ✓ PASS | SecurityConfig permits only login/health/docs endpoints; all other endpoints require hasRole("ADMIN"). |
| @Valid input validation | ✓ PASS | AuthenticationRequest annotated with @NotBlank on username and password fields. |
| JWT claim validation | ✓ PASS | JwtService.parse() validates issuer, audience, signature, and expiry before returning claims. |
| No sensitive data in responses | ✓ PASS | AdminResponse returns only adminId and username; passwordHash never included in DTOs. AuthToken contains accessToken, tokenType, expiresAt, adminId (no secrets). |
| Dev-only bootstrap gating | ✓ PASS | AdminBootstrapConfiguration guarded by @Profile("dev") and @ConditionalOnProperty(name = "app.admin-bootstrap-enabled", havingValue = "true"). Default is false in application.properties. |
| Flyway versioned schema | ✓ PASS | V1__create_admins.sql creates table with normalized unique index on LOWER(username). |
| Axios 401 cleanup | ✓ PASS | Response error handler removes token and navigates to login on 401. |
| Token storage in localStorage | ✓ PASS | Stored with key 'admin_access_token' in both login and me methods, cleared on logout or 401. |

### Code Quality

| Area | Status | Notes |
|---|---|---|
| No dead code | ✓ PASS | All methods are invoked. Logout endpoint exists per specification. |
| Naming consistency | ✓ PASS | Names match existing codebase conventions (e.g., AuthenticationRequest, AdminResponse). |
| Separation of concerns | ✓ PASS | Service layer abstracts authentication logic; controller is thin. |
| Error handling | ✓ PASS | BadCredentialsException caught in GlobalExceptionHandler with generic message. Missing exception cases for invalid JWT handled silently in filter. |
| Test coverage | ⚠ PARTIAL | See detailed findings below. |

---

## Issues & Recommendations

### HIGH SEVERITY
**None identified.** Implementation aligns with approved ADR, Security Review, and Integration Review.

---

### MEDIUM SEVERITY

#### 1. **Axios 401 Error Handler - Potential Recursive Redirect Risk**
- **File**: [api.service.ts](../../angular-publisher-service/src/app/core/services/api.service.ts), lines 31–33
- **Severity**: MEDIUM
- **Issue**: 
  - Error handler attempts to navigate to `/admin/login` on 401 without checking whether the failing request was already part of a navigation or from a public endpoint (e.g., login itself).
  - If multiple concurrent requests fail with 401, each could trigger a separate navigation, causing race conditions or multiple redirects.
  - Security Review explicitly required: "The interceptor must avoid attaching tokens to login or other public requests, avoid recursive redirect/interceptor behavior, and preserve loader cleanup on failures. Concurrent 401 responses should produce deterministic token cleanup and navigation rather than repeated or inconsistent redirects."
- **Recommendation**: 
  - Add a flag to prevent redundant navigation attempts when already redirecting.
  - Ensure login and other public endpoints are in a blocklist to avoid attaching tokens (currently done in request interceptor line 24).
  - Consider consolidating concurrent 401 handling with a single `Promise` that guards navigation.

#### 2. **JWT Test Coverage Gap**
- **File**: [JwtServiceTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/security/JwtServiceTest.java)
- **Severity**: MEDIUM
- **Issue**: 
  - Only tests expired token rejection; missing coverage for:
    - Tampered/invalid signature
    - Wrong issuer
    - Wrong audience
    - Missing required claims
    - Algorithm substitution
  - Security Review requires: "tests for malformed, expired, tampered, wrong-audience, wrong-issuer, wrong-algorithm, missing-authority, and replayed JWTs."
- **Recommendation**: 
  - Add tests for each claim validation scenario.
  - Verify that JwtService.parse() throws RuntimeException (or appropriate checked exception) for each failure mode.
  - Test that invalid tokens do not allow authentication.

#### 3. **CORS AllowCredentials Mismatch**
- **File**: [WebConfig.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/WebConfig.java), line 23
- **Severity**: MEDIUM
- **Issue**: 
  - `allowCredentials(true)` is set in CORS configuration, but bearer token authentication does not use credentials (cookies/auth headers in CORS sense).
  - This configuration is an anti-pattern for stateless JWT auth and can expose unnecessary CORS vulnerabilities.
  - ADR states: "Configure CORS narrowly; bearer authorization does not require `allowCredentials=true` when no cookie is used."
- **Recommendation**: 
  - Change to `.allowCredentials(false)` (or omit the method, as false is the default).
  - If cookie-based sessions are added in the future, this can be revisited.

#### 4. **Missing Test: Bootstrap Disabled in Production**
- **File**: [AdminBootstrapConfiguration.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/AdminBootstrapConfiguration.java)
- **Severity**: MEDIUM
- **Issue**: 
  - Configuration is guarded by `@Profile("dev")` and `@ConditionalOnProperty`, which is correct.
  - However, there is no integration test verifying that bootstrap does NOT execute when:
    - ADMIN_BOOTSTRAP_ENABLED=false (default production value)
    - Profile is not "dev"
  - Security Review notes: "The first Admin is created through a dev-only bootstrap using a pre-hashed password or one-time secret, guarded by `ADMIN_BOOTSTRAP_ENABLED=false` by default and unavailable in production; credentials are never committed."
- **Recommendation**: 
  - Add an integration test (e.g., AdminBootstrapConfigurationTest) that:
    - Verifies bootstrap runs when @Profile("dev") and ADMIN_BOOTSTRAP_ENABLED=true.
    - Verifies bootstrap is skipped when ADMIN_BOOTSTRAP_ENABLED=false or profile is not "dev".
    - Tests that missing ADMIN_BOOTSTRAP_USERNAME or ADMIN_BOOTSTRAP_PASSWORD_HASH throws IllegalStateException in dev mode.

---

### LOW SEVERITY

#### 1. **Debug Console Log in API Service**
- **File**: [api.service.ts](../../angular-publisher-service/src/app/core/services/api.service.ts), line 14
- **Severity**: LOW
- **Issue**: 
  - `console.log('API Base URL:', environment.apiBaseUrl);` logs environment configuration to the browser console.
  - Could expose internal URLs or infrastructure details in production logs.
- **Recommendation**: 
  - Remove the debug log or guard it behind an environment-specific debug flag.
  - Example: `if (!environment.production) { console.log(...); }`

#### 2. **Logout Endpoint Untested**
- **File**: [AuthController.java](../../spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java), line 28
- **Severity**: LOW
- **Issue**: 
  - POST /api/v1/auth/logout endpoint exists and returns a success response, but is not covered by any unit or integration test.
  - Although logout is client-side only (token cleared in browser), the endpoint is still callable and should be verified.
- **Recommendation**: 
  - Add a test in AuthControllerTest to verify:
    - Endpoint is accessible and returns 200 OK with correct ApiResponseDto structure.
    - Message is "Logout successful" or appropriate.

#### 3. **Incomplete Frontend Tests**
- **File**: [login.component.spec.ts](../../angular-publisher-service/src/app/features/admin/login.component.spec.ts)
- **Severity**: LOW
- **Issue**: 
  - Spec tests invalid credentials and empty form submission, but does not test:
    - Successful login flow (valid credentials, navigate to dashboard or returnUrl).
    - returnUrl query parameter extraction and usage.
    - Spinner/disabled state during submission.
  - Other frontend services (AuthService, AdminGuard) have minimal test coverage.
- **Recommendation**: 
  - Add test for successful login with valid credentials.
  - Add test for returnUrl parameter handling.
  - Add tests for AuthService.current() method.
  - Add tests for edge cases (network timeout, 500 error response).

#### 4. **Missing Documentation of Known Gaps**
- **File**: Entire codebase
- **Severity**: LOW
- **Issue**: 
  - Rate limiting and brute-force protection are accepted MVP risks per Security Review, but there is no in-code documentation of this.
  - Future developers may not be aware this is a known gap.
- **Recommendation**: 
  - Add a comment in AuthController or SecurityConfig noting:
    ```java
    // TODO: Rate limiting and brute-force protection are future infrastructure work
    // (reverse proxy/WAF). See specs/001-admin-authentication-flow/security-review.md
    ```

#### 5. **AdminAuthenticationService.current() Method Not Tested**
- **File**: [AdminAuthenticationServiceTest.java](../../spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationServiceTest.java)
- **Severity**: LOW
- **Issue**: 
  - current() method (used by GET /api/v1/auth/me) is implemented but only tested indirectly via integration tests.
  - No unit test covers the case where the admin ID is not found.
- **Recommendation**: 
  - Add unit test: `currentThrowsWhenAdminNotFound()` to verify proper exception handling.

---

## Deviations from Specification

**None identified.** The implementation faithfully follows:
- **ADR-001**: Entity structure, JWT lifetime, endpoints, client-side logout, SSR protection.
- **Security Review**: Hashing algorithm, secrets management, error messages, ROLE_ADMIN enforcement, claim validation, bootstrap gating.
- **Integration Review**: DTO fields, database schema, API contract adherence.

---

## Architecture Validation

| Criterion | Result |
|---|---|
| Follows layered architecture (Controller → Service → Repository → Entity) | ✓ Pass |
| Uses /api/v1/ endpoint prefix | ✓ Pass |
| Returns ApiResponseDto envelopes with success, message, data, timestamp | ✓ Pass |
| Dedicated Admin entity (no multi-role extension) | ✓ Pass |
| Stateless JWT with 1-hour lifetime, no refresh tokens | ✓ Pass |
| BCrypt password hashing | ✓ Pass |
| Server-side ROLE_ADMIN authorization | ✓ Pass |
| Environment-backed configuration (no hardcoded secrets) | ✓ Pass |
| Flyway migration with versioned schema | ✓ Pass |
| SPR guard on all admin routes (frontend navigation only) | ✓ Pass |
| isPlatformBrowser protections for SSR | ✓ Pass |

---

## Integration Consistency

| Layer | Consistency | Notes |
|---|---|---|
| Backend ↔ Frontend DTOs | ✓ Match | AuthenticationRequest, AuthToken, AdminResponse fields align across JSON and TypeScript. |
| Frontend ↔ API Service | ✓ Match | auth.service.ts correctly reads response.data.data.accessToken and response.data.data from nested ApiResponse structure. |
| API Contract ↔ Database | ✓ Match | Admin entity fields (id, username, passwordHash, created_at, updated_at) match contract and live schema. |
| Response Envelopes | ✓ Consistent | All endpoints use ApiResponseDto with required fields. |
| Error Responses | ✓ Generic | Invalid credentials and auth failures return generic message per specification. |

---

## Verdict

### **APPROVED WITH MINOR ISSUES**

**Summary:**  
The admin authentication feature is well-architected and implements the approved ADR, Security Review, and Integration Review with high fidelity. The codebase demonstrates strong separation of concerns, proper use of Spring Security and JWT, and appropriate SSR handling. All critical security controls are in place (BCrypt, stateless JWT, generic errors, server-side authorization, dev-only bootstrap).

**Blocking Issues:** None.

**Non-Blocking Issues:**  
- 1 MEDIUM: Axios 401 error handler lacks concurrency guards (risk of multiple redirects).
- 1 MEDIUM: JWT service tests incomplete; missing tampered, wrong-issuer, wrong-audience tests.
- 1 MEDIUM: CORS allowCredentials(true) is unnecessary for bearer auth (anti-pattern, not a vulnerability).
- 1 MEDIUM: No test for bootstrap disabled in production; guard is correct but untested.

**Recommendation:** Resolve the four MEDIUM issues before deploying to production. The four LOW issues can be addressed in a follow-up maintenance sprint or as part of E2E test implementation.

---

## Reviewer Notes

1. **Security Posture**: The implementation correctly embodies the stateless JWT design with server-side authorization as the source of truth. The frontend guard is appropriately non-authoritative. Token storage in localStorage is an accepted MVP trade-off documented in the ADR.

2. **SSR Readiness**: Admin routes are correctly excluded from prerendering and all localStorage access is guarded by isPlatformBrowser. This prevents Node.js runtime errors and ensures client-side-only token handling.

3. **Bootstrap Safety**: The dev-only bootstrap configuration is properly guarded by profile and property conditions. Credentials are never committed. Ensure environment variables are never logged or exposed in CI/CD logs.

4. **Testing Gaps**: While core functionality is tested, edge cases (concurrent 401s, malformed JWTs, production bootstrap disabled) require additional coverage before moving to E2E validation.

5. **Future Work**: Rate limiting, brute-force protection, and token revocation (denylist or per-admin token version) remain out of scope per the ADR and are assigned to infrastructure ownership. A follow-up ticket should track these gaps.

6. **HTTPS Requirement**: Deployment must enforce HTTPS to protect localStorage tokens from network interception. A CSP and XSS review is recommended before release, as noted in the Security Review.

---

**Next Checkpoint:** E2E Testing and Documentation (per the roadmap).

