# Unit Tests: Admin Authentication Flow

## Framework
Angular tests use Karma/Jasmine via the configured `@angular/build:karma` builder. Spring tests use JUnit Jupiter, Mockito, and AssertJ as configured in `spring-publisher-service/pom.xml`. The Spring configuration differs from `.specify/memory/constitution.md`, which specifies TestNG; the configured JUnit Jupiter framework was used.

## Tests Added
| test file | test method(s) | production file covered | acceptance criterion or task ID |
|---|---|---|---|
| `angular-publisher-service/src/app/core/services/auth.service.login.spec.ts` | `stores the access token returned by the login API`; `does not access browser storage when running on the server` | `angular-publisher-service/src/app/core/services/auth.service.ts` | US1 / FR-002, FR-004; US3 / FR-007; T017, T027 |
| `angular-publisher-service/src/app/core/services/api.service.auth.spec.ts` | `adds the stored bearer token to non-login requests`; `clears the token and redirects to login after an unauthorized response` | `angular-publisher-service/src/app/core/services/api.service.ts` | US2 / FR-005, FR-006; US3 / FR-007, FR-008; T028 |
| `angular-publisher-service/src/app/core/guards/admin.guard.authenticated.spec.ts` | `allows navigation for an authenticated administrator` | `angular-publisher-service/src/app/core/guards/admin.guard.ts` | US2 / FR-004, FR-005; T021, T022 |
| `angular-publisher-service/src/app/features/admin/login.success.spec.ts` | `redirects to the requested protected URL and clears the submitting state` | `angular-publisher-service/src/app/features/admin/login.component.ts` | US1 / FR-001, FR-004; T014, T016 |
| `spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/security/JwtAuthenticationFilterTest.java` | `validBearerTokenSetsAdminAuthenticationAndContinuesChain`; `malformedBearerTokenClearsAuthenticationAndContinuesChain` | `spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/JwtAuthenticationFilter.java` | US2 / FR-005, FR-006; US3 / FR-009; T023 |
| `spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/config/AdminBootstrapConfigurationTest.java` | `bootstrapIsRestrictedToDevAndExplicitlyEnabled`; `createsAdminUsingNormalizedUsernameWhenMissing`; `doesNotCreateDuplicateAdmin`; `rejectsMissingBootstrapCredentialsBeforeRepositoryAccess` | `spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/AdminBootstrapConfiguration.java` | FR-002; T010, T011 |
| `spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationServiceInvalidPasswordTest.java` | `rejectsIncorrectPasswordWithoutIssuingToken` | `spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/AdminAuthenticationService.java` | US1 / FR-002, FR-003; T012 |

## Not Covered
No new unit tests were added for `app.routes.ts`, `app.routes.server.ts`, `dashboard.component.ts`/`.html`, `login.component.html`/`.css`, `environment.dev.ts`, the authentication request/response DTOs, `Admin`, `AdminRepository`, `GlobalExceptionHandler`, `AuthController`, `SecurityConfig`, or `JwtService`. Existing specs/tests already cover parts of authentication, login-form validation, route denial, controller request validation, JWT parsing/expiration, and security-chain access. The protected-route integration-test tasks T019/T020 were not added because this task is limited to unit tests. Database migration behavior was not tested because it requires database-level validation.

## Notes
The newly added tests were not run, per the unit-test task constraints.
