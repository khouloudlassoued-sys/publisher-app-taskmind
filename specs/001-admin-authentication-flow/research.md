# Research: Admin Authentication Flow

## Decision: Use Spring Security with JWT and a dedicated Admin entity

**Rationale**:
- The repository already follows a layered Spring Boot architecture and uses DTO-based REST APIs with a global exception handler.
- The constitution requires stateless JWT authentication, BCrypt password hashing, and authorization via Spring Security.
- The feature scope requires an admin identity without hardcoded credentials, so the cleanest fit is to create a dedicated `Admin` entity from scratch and enforce its authorization server-side.
- The frontend architecture was confirmed by inspecting `angular-publisher-service/src/app/core/services/api.service.ts`: the application uses Axios through this centralized service, which already contains loader interceptors. Authentication must therefore extend that service with Axios request and response interceptors.

## Alternatives considered

- Hardcoded admin credentials: rejected because it does not align with the security guidance or maintainable identity handling.
- Reusing an existing user domain with an explicit admin flag: rejected because the final feature decision is to create a dedicated `Admin` entity from scratch and keep the authentication boundary explicit.
- Frontend-only guard: rejected because the constitution requires backend authorization enforcement and the acceptance criteria require API protection.

## Notes

- Confirmed research finding: the frontend uses Axios through the centralized `angular-publisher-service/src/app/core/services/api.service.ts`, whose existing loader interceptors must be extended for authentication rather than replaced by a separate interceptor file.
- The backend should expose an authentication endpoint under /api/v1/auth/login or equivalent.
- The frontend should route unauthenticated users to a login screen and preserve the current Angular routing structure.
- The initial implementation should keep the scope focused on admin-only access and not introduce multi-role support beyond the dedicated admin authority.
