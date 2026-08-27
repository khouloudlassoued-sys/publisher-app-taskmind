# Security Review: Admin Authentication Flow

## Threat Model Summary
- An attacker may brute-force the public login endpoint, enumerate the administrator account, or exploit weak input handling.
- An attacker with database access may target the Admin credential record; plaintext or weakly protected passwords would enable account takeover.
- An attacker may forge, tamper with, replay, or algorithm-substitute JWTs to access admin APIs.
- An injected script may read the access token from `localStorage` and use it until the one-hour expiry.
- SSR may access browser-only session state incorrectly, causing authentication state leakage, runtime failures, or unsafe prerendering of admin routes.
- A copied bearer token remains usable after client logout under the stateless MVP design.
- A misconfigured dev-only bootstrap, migration, CORS policy, logging configuration, or Axios interceptor could expose credentials or bypass intended controls.

## Security Checklist
- [x] Passwords hashed (algorithm: BCrypt; password hashes are not returned in DTOs)
- [x] Secrets via environment variables only (JWT secret, database credentials, issuer/audience, and CORS configuration)
- [x] Generic error messages (no account enumeration for unknown, invalid, or unauthorized credentials)
- [x] Server-side authorization enforcement (Spring Security JWT validation and `ROLE_ADMIN` checks; frontend guard is not authoritative)
- [x] Input validation on auth endpoints (server-side `@Valid` validation is required for authentication requests)
- [x] Token expiration enforced (one-hour JWT lifetime and validation of expiry and other required claims)
- [x] No sensitive data in logs (passwords, password hashes, JWTs, and raw credentials must be excluded)
- [x] SSR/localStorage protection specified (`isPlatformBrowser(platformId)` for every browser-only access; admin routes excluded from prerendering or rendered client-side)
- [x] Axios interceptor boundary specified (attach bearer tokens and handle 401 cleanup/redirect while preserving existing loader interceptors)
- [x] Dev-only Admin bootstrap constrained (pre-hashed password or one-time secret; disabled in production; no committed credentials)
- [x] Versioned schema ownership specified (Flyway migration with normalized username uniqueness; disable deployed `ddl-auto=update` once migration ownership is introduced)
- [x] Rate limiting and brute-force protection explicitly accepted as an MVP risk and assigned as a potential future reverse-proxy/WAF responsibility
- [x] Logout semantics are consistent across the contract, specification, and approved stateless architecture

## Findings
- **MEDIUM: Accepted MVP risk: no application-level rate limiting.** Login rate limiting and brute-force protection are explicitly out of scope for this MVP. A future ticket may assign this control to infrastructure such as a reverse proxy or WAF if operational evidence requires it.
- **LOW: Token storage in `localStorage` accepts XSS exposure by design.** The ADR documents this trade-off, but there is no explicit CSP/XSS hardening requirement or residual-token response plan beyond one-hour expiry. The implementation must avoid token logging and browser diagnostics and should add a documented CSP and XSS review before release.
- **LOW: Axios 401 handling needs loop and request-boundary safeguards.** The interceptor must avoid attaching tokens to login or other public requests, avoid recursive redirect/interceptor behavior, and preserve loader cleanup on failures. Concurrent 401 responses should produce deterministic token cleanup and navigation rather than repeated or inconsistent redirects.

## Verdict
Approved

## Reviewer Notes
- The core architecture is security-appropriate and consistent with the constitution: dedicated Admin identity, BCrypt, environment-backed secrets, one-hour stateless JWTs, fixed algorithm and claim validation, server-side authorization, generic authentication failures, and SSR-aware browser storage.
- The ADR is marked `Approved` and governs this review. Logout is explicitly client-side token clearing only; no denylist or token-versioning is added.
- Rate limiting and brute-force protection remain out of scope for the MVP as an accepted risk; infrastructure ownership through a reverse proxy or WAF can be addressed in a future ticket.
- The first Admin is created through a dev-only bootstrap using a pre-hashed password or one-time secret, guarded by `ADMIN_BOOTSTRAP_ENABLED=false` by default and unavailable in production; credentials are never committed.
- Flyway is the definitive migration tool, with normalized unique `Admin.username` enforcement and no deployed reliance on `ddl-auto=update`.
- The API uses a dedicated Admin entity, BCrypt, environment-backed secrets, one-hour stateless JWTs, fixed claim and algorithm validation, generic authentication errors, server-side `ROLE_ADMIN` authorization, and minimal `/auth/me` fields (`adminId`, `username`) only.
- The frontend stores tokens in `localStorage` for MVP simplicity and tab persistence, while every browser-only access is protected by `isPlatformBrowser(platformId)` under Angular SSR.
- Axios request/response interceptors remain centralized in `api.service.ts`, preserve loader behavior, attach bearer tokens, and clean up on 401 with loop and public-request safeguards.
- Required tests should cover malformed, expired, tampered, wrong-audience, wrong-issuer, wrong-algorithm, missing-authority, and replayed JWTs; credential-error equivalence; direct API access; SSR without browser storage; Axios 401 cleanup; and bootstrap-disabled-in-production behavior.