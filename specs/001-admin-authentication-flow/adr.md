# ADR-001: Admin Authentication Flow Architecture

## Status
Proposed

## Context

The feature requires a dedicated admin login experience, server-enforced protection of admin pages and APIs, BCrypt password verification, and a stateless JWT with a one-hour lifetime and no refresh token. The intended backend convention is Controller -> Service -> Repository -> Entity with `ApiResponseDto` envelopes and `/api/v1/` endpoints.

The repository supports the proposed layering, but it does not currently contain Spring Security/JWT dependencies or security classes. Its Angular application uses Axios through `ApiService`, not Angular `HttpClient` interceptors, and its SSR configuration prerenders every route. The backend currently relies on `spring.jpa.hibernate.ddl-auto=update` and has no migration dependency or migration directory. `CONSTITUTION.md` is empty, so the checks asserted in `plan.md` are not independently established constraints.

The feature artifacts also conflict: `spec.md` and `data-model.md` require a new `Admin` entity, while `research.md` and `quickstart.md` describe an existing user record with `admin=true`. The contract calls logout an invalidation operation, but a stateless JWT cannot be revoked by a client-only logout endpoint unless a server-side denylist or token-version state is added.

## Decision

Use a dedicated `Admin` aggregate for this MVP. It owns a generated `id`, unique normalized `username`, BCrypt `passwordHash`, and audit timestamps. Do not add a role hierarchy, general user table, or speculative account fields. The single admin authority is derived from successful authentication against this aggregate; an additional `admin` flag is unnecessary and must be removed from the quickstart/research wording.

Implement the backend boundary as:

`AuthController` -> `AdminAuthenticationService` -> `AdminRepository` -> `Admin`.

The service verifies the password with a Spring `PasswordEncoder`, rejects unknown or unauthorized credentials with the same externally visible failure response, and issues a signed JWT containing only the minimum subject and authority claims. A dedicated JWT authentication filter validates signature, issuer/audience (if configured), subject, authority, and expiry before placing an authenticated principal in the Spring Security context. `SecurityConfig` permits only the login endpoint (and health/docs endpoints according to the existing deployment policy); it requires `ROLE_ADMIN` for admin APIs. Authentication entry-point and access-denied handlers return the repository's `ApiResponseDto` shape with HTTP 401 and 403 respectively.

Expose:

- `POST /api/v1/auth/login`: validates `AuthenticationRequest`, returns `AuthToken` with `Bearer`, token expiry, and admin identifier.
- `GET /api/v1/auth/me`: requires `ROLE_ADMIN`; returns a minimal admin projection and never the password hash.
- `POST /api/v1/auth/logout`: clears the browser token only. It is not a server revocation operation under the stateless MVP decision.

Protect Angular admin routes with a functional guard that checks local session state and redirects to `/admin/login` with a return URL. Extend the existing Axios `ApiService` with request/response interception (or introduce one narrowly scoped adapter) to attach `Authorization: Bearer <token>`, clear the token on 401, and navigate to login. The guard is a user-experience control only; the backend remains authoritative for every admin API. Because the application prerenders all routes, admin routes must be excluded from prerendering or rendered only client-side, and browser-only token access must be guarded during SSR.

For the MVP, store the access token in `sessionStorage` after login and clear it on logout or a 401/expiry event. This limits persistence to the browser tab but does not defend against XSS. Serve the application over HTTPS, do not log tokens or passwords, use generic login errors, and apply reasonable login throttling/rate limiting at the deployment boundary. A later migration to an HttpOnly, Secure, SameSite cookie requires an explicit CSRF design and is not silently mixed with bearer-token behavior.

Own the `Admin` schema through a versioned migration and seed an initial admin through an operational bootstrap mechanism that accepts a pre-hashed password or one-time setup secret; never commit credentials. Disable `ddl-auto=update` for deployed environments once migration ownership is introduced. JWT signing secret, issuer/audience, CORS origins, and token lifetime must come from environment-backed configuration, with startup failure for missing or weak production secrets. Configure CORS narrowly; bearer authorization does not require `allowCredentials=true` when no cookie is used.

## Authentication and Session Flow

1. The browser submits credentials to the public login endpoint over HTTPS.
2. The service loads the normalized username, compares the supplied password with BCrypt, and rejects all failures without revealing whether the username exists.
3. On success, the service signs a one-hour JWT whose subject identifies the admin and whose authority is `ROLE_ADMIN`; the browser stores it in `sessionStorage`.
4. The Axios layer attaches the bearer token to API requests. The backend filter validates it on every request, and endpoint/method authorization checks `ROLE_ADMIN`.
5. The frontend guard prevents ordinary navigation without a token, but a missing, malformed, expired, or rejected token always results in backend denial and client cleanup.
6. Logout removes the token locally. Since no refresh tokens or server session exist, a copied token remains usable until its expiry. If immediate revocation is a hard requirement, this ADR must be revisited to add a denylist or per-admin token version, accepting state and operational complexity.

## Security Considerations

- Keep password hashes, JWT secrets, and raw credentials out of DTO responses, logs, source control, and browser-visible diagnostics.
- Use a strong, rotated signing secret and a fixed accepted algorithm; reject algorithm substitution and invalid claims.
- Use generic credential failure messages and consistent 401/403 behavior to reduce account and authorization disclosure.
- Validate request fields server-side with `@Valid`; client validation is only convenience.
- Cover expired, tampered, wrong-audience, missing-authority, non-admin, and malformed bearer tokens, not only successful login.
- Treat the Angular guard as non-security code and test direct API access independently.
- Review SSR and XSS posture before release because browser token storage is readable by injected script.

## Alternatives Considered

- **Extend existing users with `admin=true`:** rejected for this feature because it contradicts the clarified dedicated `Admin` entity and couples authentication to a domain model that does not exist in the repository.
- **Hardcoded credentials:** rejected because it is unsafe, unmaintainable, and cannot support secure rotation.
- **HttpOnly cookie session:** deferred. It improves token exposure in JavaScript but needs CSRF protection and changes the contract from bearer-token handling.
- **JWT denylist or token-version revocation:** deferred. It would make logout immediately effective, but introduces server-side session state and conflicts with the stated simple stateless MVP.
- **Frontend-only protection:** rejected because it cannot protect direct API calls.

## Consequences

- Positive: one authoritative admin identity source, clear Spring Security boundary, consistent API envelopes, and shared server-side authorization for every protected API.
- Positive: short-lived bearer tokens and tab-scoped storage reduce persistence and avoid refresh-token complexity.
- Negative / trade-off: adding Spring Security/JWT and migration support is real foundational work absent from the current build; the plan must include it explicitly.
- Negative / trade-off: client-only logout does not revoke a stolen token before its one-hour expiry.
- Negative / trade-off: SSR route configuration and Axios interception require deliberate integration and additional browser/SSR tests.

## Verdict

Changes Requested

## Open Follow-ups

- Update `research.md` and `quickstart.md` to consistently use the dedicated `Admin` entity and define the admin bootstrap/seed process.
- Decide whether the product accepts logout's one-hour residual token validity; otherwise approve a revocation mechanism and revise the stateless constraint.
- Add the exact Spring Security/JWT and Flyway/Liquibase dependencies, migration strategy, and production `ddl-auto` policy to `plan.md`.
- Specify which existing CRUD routes are admin-protected and how SSR should handle `/admin/**` before implementation.
- Populate the constitution or explicitly mark the plan's constitution checks as repository assumptions rather than passed governance gates.