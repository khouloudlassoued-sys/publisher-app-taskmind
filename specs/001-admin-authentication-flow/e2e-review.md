# E2E Review: Admin Authentication Flow

## Scope and evidence

This re-review verifies the current branch and the supplied run logs. No tests were run during this review. The verified fixes are in commits `fc0cd54`, `66770d5`, and `2becb4c`; the latest full E2E result is `e2e-admin-log6.txt`, and the focused security test result is `securityconfigtest-b2.txt`.

## Fix verification

| Prior finding | Current evidence | Status |
|---|---|---|
| HIGH — JWT signing secret and admin bootstrap hash were tracked in the development environment file. | Commit `fc0cd54` removes both assignments from `spring-publisher-service/config/.env.dev`. Compose optionally loads `spring-publisher-service/config/.env.dev.local` (`docker-compose.yml:16-19`, local path at line 18), and the local-file pattern is ignored (`.gitignore:43`). The ignored local file is present. Its configured JWT value and admin hash differ from the values in `c9237fa`; the hash difference alone does not prove that the underlying admin password was changed. The old values remain in Git history at `c9237fa`. The project owner reports that, in a manual terminal check, the old admin password received HTTP 401 from `/api/v1/auth/login` while the new password was accepted (**constaté manuellement, non reproductible depuis un fichier**; owner observation, 2026-10-18). | The current JWT/admin values are no longer in the tracked dev file; historic exposure remains in history. Admin-password rotation is supported by the owner's manual observation, but cannot be independently confirmed from the hash difference alone. |
| MEDIUM — API authorization and JWT validity had insufficient test coverage. | `SecurityConfigTest` now tests public catalogue GETs (`catalogueGetEndpointsReturnOkWithoutAuthentication`, line 51), valid admin JWT access (`validAdminJwtCanAccessCurrentAdminEndpoint`, line 59), altered-signature rejection (`jwtWithAlteredSignatureIsRejectedOnCurrentAdminEndpoint`, line 69), and expired-token rejection (`expiredJwtIsRejectedOnCurrentAdminEndpoint`, line 78). The focused run reports 5 tests, 0 failures, and `BUILD SUCCESS` (`securityconfigtest-b2.txt:262,266,273`). | Addressed for the listed cases. |
| LOW — valid-login E2E credentials did not require both system properties. | `AdminSteps` reads both properties without a fallback and rejects either missing/blank value (`AdminSteps.java:15-16,26-31`); commit `66770d5`. | Addressed. |

### Remaining tracked credential finding

The tracked database-password settings are classified **PRE-EXISTING / ACCEPTED-RISK**:

- All three tracked environment files, `.env.dev`, `.env.staging`, and `.env.prod`, contain `POSTGRES_PASSWORD` on line 4 and `SPRING_DATASOURCE_PASSWORD` on line 21; values are intentionally omitted (`spring-publisher-service/config/.env.dev:4,21`; `spring-publisher-service/config/.env.staging:4,21`; `spring-publisher-service/config/.env.prod:4,21`). Compose loads the selected environment file for the database container (`docker-compose.yml:107-115`).
- The history for `.env.staging` shows changes only by the original project author, Amira-Dgham, in commits `5815ee5`, `c2c792a`, and `c971cc4`; the history for `.env.prod` shows the same author and commits (`git log --format="%h %an %ad %s" -- spring-publisher-service/config/.env.staging`; `git log --format="%h %an %ad %s" -- spring-publisher-service/config/.env.prod`; commits dated 2025-07-18 through 2025-09-10). The dev password variable names are also present before the SCRUM-5 commit in `c9237fa~1:spring-publisher-service/config/.env.dev` (lines 4 and 21; variable names only). Current `.env.dev` has subsequent SCRUM-5-related history, but these database settings predate that work.
- **Owner decision, not technical repository evidence:** on 2026-10-18, the project owner (the student) accepted and documented this pre-existing deviation as outside SCRUM-5 scope because the project and its deployment belong to her supervisor; she will open a separate “database secrets management” ticket and flag this deviation in the pull request description. This is the owner's instruction for this review, not a claim verified from a repository artifact.

The tracked Spring README also contains a static database-password example (`spring-publisher-service/README.md:97`); it is documentation and should be addressed by the separate secrets-management follow-up. The prior HIGH finding's JWT and admin-bootstrap values were removed from the tracked dev file by `fc0cd54`; their historic exposure remains in `c9237fa`.

## Requirement traceability

| Requirement | Covered by E2E | Covered by backend test | Gap / assessment |
|---|---|---|---|
| **FR-001** Dedicated admin login experience | Yes — successful login scenario (`Admin.feature:7-10`); it is present in the latest run (`e2e-admin-log6.txt:14439`). | No dedicated login-screen UI test. | E2E covers the login-to-dashboard path. |
| **FR-002** Validate credentials against the dedicated Admin entity | Partially — valid and invalid login flows invoke authentication (`Admin.feature:7-16`; latest run `e2e-admin-log6.txt:14439,14445`). | Yes — `AdminAuthenticationServiceTest.authenticatesNormalizedUsername` and `rejectsUnknownOrInvalidCredentials` (`AdminAuthenticationServiceTest.java:29-45`). | E2E does not itself assert which identity store/entity was used. |
| **FR-003** Deny invalid credentials with a clear error | Yes — invalid-login scenario asserts an error and staying on the login page (`Admin.feature:13-16`; latest run `e2e-admin-log6.txt:14445`). | Yes — invalid/unknown credentials are rejected by `AdminAuthenticationServiceTest.rejectsUnknownOrInvalidCredentials` (`AdminAuthenticationServiceTest.java:39-45`). | Covered for the tested invalid-login path. |
| **FR-004** Authorized admins can use protected admin pages/features | Yes — successful login redirects to the dashboard (`Admin.feature:7-10`; latest run `e2e-admin-log6.txt:14439`). | Partially — a valid admin JWT is accepted on `/api/v1/auth/me` (`SecurityConfigTest.validAdminJwtCanAccessCurrentAdminEndpoint`, line 59). | No backend test for an admin-only page or other protected admin feature is evidenced here. |
| **FR-005** Prevent non-admins from accessing admin pages and APIs | Partially — unauthenticated dashboard navigation redirects to login (`Admin.feature:19-21`; latest run `e2e-admin-log6.txt:14451`). | Yes for unauthenticated/invalid credentials — `protectedEndpointRejectsUnauthenticatedRequest` (`SecurityConfigTest.java:46`) and altered/expired JWT rejection (lines 69, 78). | No test supplies a valid JWT for a non-admin identity; the E2E route case is unauthenticated, not an authenticated non-admin. |
| **FR-006** Apply the same authorization rules to routes and APIs | Partially — E2E exercises the admin route guard (`Admin.feature:19-21`). | Partially — MockMvc tests the protected `/api/v1/auth/me` endpoint and the public catalogue routes (`SecurityConfigTest.java:46,51,59,69,78`). | Both layers have relevant coverage, but no test asserts parity for the same unauthorized identity across a route and API. |
| **FR-007** Logout clears the client token/session | Partially — logout followed by another dashboard visit is exercised (`Admin.feature:24-30`; latest run `e2e-admin-log6.txt:14456`). The client removes its stored token (`auth.service.ts:27-30`). | No server-side revocation test; the JWT design is stateless. | The E2E checks the redirect/route guard, not token absence directly. Server-side token invalidation is not expected. |
| **FR-008** Redirect signed-out or expired sessions away from protected routes | Partially — signed-out dashboard access and post-logout access are covered (`Admin.feature:19-21,24-30`; latest run `e2e-admin-log6.txt:14451,14456`). | Expired JWTs receive 401 on `/api/v1/auth/me` (`SecurityConfigTest.expiredJwtIsRejectedOnCurrentAdminEndpoint`, line 78). | Expired-session redirection in the browser is not covered. |
| **FR-009** Stateless JWT, one-hour validity, no refresh flow | No E2E assertion for token claims, duration, or refresh behavior. | Yes for expired-token rejection only (`SecurityConfigTest.expiredJwtIsRejectedOnCurrentAdminEndpoint`, line 78; `JwtServiceTest.expiredTokenIsRejected`, `JwtServiceTest.java:9-13`). | **Known limitation:** the configured default is one hour (`application.properties:36`), but the one-hour duration is not asserted by a test; only rejection of an expired token is tested. |
| **FR-010** Automate successful and failed authentication scenarios | Yes — successful and invalid-login scenarios (`Admin.feature:7-16`; latest run `e2e-admin-log6.txt:14439,14445`). | Yes — `AdminAuthenticationServiceTest.authenticatesNormalizedUsername` and `rejectsUnknownOrInvalidCredentials` (`AdminAuthenticationServiceTest.java:29-45`). | Covered for the exercised success/failure cases. |
| **FR-011** Include the full admin-auth MVP: login, backend auth, route/API protection, logout, expiry | Partially — login, route guard, and logout scenarios are present and ran in log6 (`Admin.feature:7-30`; `e2e-admin-log6.txt:14439-14461`). | Partially — auth-service tests and `SecurityConfigTest` cover authentication, authorization, catalogue access, and expired-token rejection (`AdminAuthenticationServiceTest.java:29-45`; `SecurityConfigTest.java:46-82`). | Browser expiry handling and the one-hour JWT duration remain unasserted; see FR-008/009. |

## Failure classification

### E2E — Author/Magazine scenarios

The latest complete E2E run reports 14 tests and 5 failures (`e2e-admin-log6.txt:15010`). Its five reported failures are the same Author/Magazine scenarios found in log4 and log5 (`e2e-admin-log4.txt:634,642,686,776,784,828,836`; `e2e-admin-log5.txt:367,411,419,463,471`; `e2e-admin-log6.txt:14747,14791,14799,14843,14851`). The failure list in log6 contains no Admin scenario, and its four Admin scenarios are present at `e2e-admin-log6.txt:14439,14445,14451,14456`.

| Failing scenario | Classification | Evidence |
|---|---|---|
| Navigate through author pages | **UNCONFIRMED : non causés par les scénarios Admin, mêmes 5 échecs dans log4, log5 et log6, pas de run sur main** | log4:686; log5:367; log6:14747 |
| Add a new magazine | **UNCONFIRMED : non causés par les scénarios Admin, mêmes 5 échecs dans log4, log5 et log6, pas de run sur main** | log4:776; log5:411; log6:14791 |
| Delete a dynamically created magazine | **UNCONFIRMED : non causés par les scénarios Admin, mêmes 5 échecs dans log4, log5 et log6, pas de run sur main** | log4:784; log5:419; log6:14799 |
| Validate form errors (Magazine) | **UNCONFIRMED : non causés par les scénarios Admin, mêmes 5 échecs dans log4, log5 et log6, pas de run sur main** | log4:828; log5:463; log6:14843 |
| Navigate through magazine pages | **UNCONFIRMED : non causés par les scénarios Admin, mêmes 5 échecs dans log4, log5 et log6, pas de run sur main** | log4:836; log5:471; log6:14851 |

There is no E2E-on-main log among the reviewed evidence. The repeated failures therefore cannot be classified as pre-existing; run the same E2E suite on `main` to establish a baseline.

### Backend — BookServiceImplTest

`backend-full-tests.txt` reports 77 tests, with one failure and one error, both in `BookServiceImplTest$GetAllBooksTests` (`backend-full-tests.txt:647-660,709`). The same two test methods fail in both branch and main evidence (`book-tests-branch.txt:49-62,83`; `book-tests-main.txt:58-71,92`):

| Failing test | Classification | Evidence |
|---|---|---|
| `BookServiceImplTest$GetAllBooksTests.shouldGetAllBooksWithPagination` | **PRE-EXISTING** | backend-full-tests.txt:647; book-tests-branch.txt:49; book-tests-main.txt:58 |
| `BookServiceImplTest$GetAllBooksTests.shouldHandleMultipleBooksWithDifferentAuthors` | **PRE-EXISTING** | backend-full-tests.txt:658; book-tests-branch.txt:60; book-tests-main.txt:69 |

## Verdict

**Approved with notes**

The SCRUM-5 API-coverage and E2E credential-validation findings are addressed (`2becb4c`, `66770d5`; `securityconfigtest-b2.txt:262-273`). No Admin scenario fails in the latest full E2E run (`e2e-admin-log6.txt:14439-14461,14747-14851`). The two backend failures are confirmed pre-existing by the corresponding `main` run (`book-tests-main.txt:58-92`). The three tracked environment files contain pre-existing database-password settings (`spring-publisher-service/config/.env.dev:4,21`; `spring-publisher-service/config/.env.staging:4,21`; `spring-publisher-service/config/.env.prod:4,21`); the owner has accepted this risk for SCRUM-5 and committed to track remediation in a separate ticket and to flag it in the pull request description (owner decision communicated for this review on 2026-10-18, not repository-verifiable). The five E2E Author/Magazine failures remain **UNCONFIRMED** as pre-existing, and an E2E run on `main` remains the recommended follow-up (`e2e-admin-log4.txt:686,776,784,828,836`; `e2e-admin-log5.txt:367,411,419,463,471`; `e2e-admin-log6.txt:14747,14791,14799,14843,14851`). The one-hour JWT duration remains unasserted; only expired-token rejection is tested (`application.properties:36`; `SecurityConfigTest.java:78`).
