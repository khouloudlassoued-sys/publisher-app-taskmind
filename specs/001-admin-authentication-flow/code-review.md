# Code Review: Admin Authentication Flow

## Files Reviewed

- Backend authentication, JWT security, bootstrap configuration, Flyway migration, application configuration, and related tests.
- Angular authentication service, Axios API service, admin guard, admin routes, SSR route configuration, components, and related tests.
- Approved `adr.md`, `security-review.md`, `integration-review.md`, and `.specify/memory/constitution.md`.

## Findings

- No blocking findings remain after the confirmed corrections described below.
- The `JwtAuthenticationFilter` behavior is consistent with the approved single-role ADMIN design. It grants the fixed `ROLE_ADMIN` authority after successful JWT validation; separate authority-claim validation is not required by this role model.
- Remaining test coverage gaps for negative JWT cases and bootstrap behavior are recommended follow-up work, but do not block approval of the implemented feature.

## Verdict

Approved

## Reviewer Notes

The implementation conforms to the approved architecture and integration contract: dedicated `Admin` entity, layered backend flow, BCrypt password verification, stateless one-hour JWTs, generic authentication errors, server-side admin protection, Flyway schema ownership, SSR-safe browser storage, and matching frontend/backend DTOs.

Two corrections were applied during review:

1. In `angular-publisher-service/src/app/core/services/api.service.ts`, 401 token cleanup and redirection were moved from the Axios request-error handler to the response-error handler, where real server-side 401 responses are processed.
2. In `spring-publisher-service/src/main/resources/application.properties`, the known JWT secret fallback was removed. `JWT_SECRET` is now mandatory via `app.jwt.secret=${JWT_SECRET}`, preventing startup when the signing secret is not supplied.

The absence of separate JWT `authorities` claim validation is accepted because the approved ADR defines a single ADMIN role and the filter assigns the fixed `ROLE_ADMIN` authority only after validating the signed token, issuer, audience, subject, and expiry.
