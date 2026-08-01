# Research: Admin Authentication Flow

## Decision: Use Spring Security with JWT and an admin role flag on existing user records

**Rationale**:
- The repository already follows a layered Spring Boot architecture and uses DTO-based REST APIs with a global exception handler.
- The constitution requires stateless JWT authentication, BCrypt password hashing, and authorization via Spring Security.
- The feature scope explicitly calls for using existing user records rather than hardcoded credentials, so the cleanest fit is to extend the existing user domain with an explicit admin flag and enforce authorization server-side.

## Alternatives considered

- Hardcoded admin credentials: rejected because it does not align with the security guidance or maintainable identity handling.
- Separate admin user store: rejected because it introduces unnecessary duplication and adds complexity for a first release.
- Frontend-only guard: rejected because the constitution requires backend authorization enforcement and the acceptance criteria require API protection.

## Notes

- The backend should expose an authentication endpoint under /api/v1/auth/login or equivalent.
- The frontend should route unauthenticated users to a login screen and preserve the current Angular routing structure.
- The initial implementation should keep the scope focused on admin-only access and not introduce multi-role support beyond the single admin flag.
