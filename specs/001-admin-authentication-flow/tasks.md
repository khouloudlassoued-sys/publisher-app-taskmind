# Tasks: Admin Authentication Flow

**Input**: Design documents from `/specs/001-admin-authentication-flow/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the backend and frontend structure for the new admin authentication feature.

- [X] T001 Create backend auth/security package structure in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/
- [X] T002 Create frontend admin auth feature structure in angular-publisher-service/src/app/features/admin/
- [X] T003 [P] Add shared auth models and DTOs in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the admin domain and core security infrastructure required before any story can be implemented.

- [X] T004 Create Admin entity and repository in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/entity/Admin.java and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/repository/AdminRepository.java
- [X] T005 Implement BCrypt password hashing and JWT utility/configuration in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/
- [X] T006 Implement Spring Security filter chain and authorization rules for /api/v1/auth/** and admin-protected endpoints in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/SecurityConfig.java
- [X] T007 Add admin authentication DTOs and exception handling for auth failures in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/exception/
- [X] T008 Add auth configuration properties for JWT secret and expiration in spring-publisher-service/src/main/resources/application.properties
- [X] T009 Add a Flyway migration for the new Admin entity, including a normalized unique constraint on Admin.username, in spring-publisher-service/src/main/resources/db/migration/
- [X] T010 Add a dev-only Admin bootstrap script or endpoint that creates the first dedicated Admin using a pre-hashed password or one-time setup secret; keep it disabled in production and never commit credentials, in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/ or spring-publisher-service/src/main/resources/
- [X] T011 Enforce the Admin bootstrap production guard with an environment-backed ADMIN_BOOTSTRAP_ENABLED configuration set to false by default, fail closed when absent in production, and cover the disabled-production behavior with a test in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/ and spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/

**Checkpoint**: Foundation ready - admin authentication implementation can now begin.

---

## Phase 3: User Story 1 - Secure Admin Sign-In (Priority: P1) 🎯 MVP

**Goal**: Allow an admin to sign in securely and receive an authenticated session.

**Independent Test**: An administrator can open the login screen, submit valid credentials, and reach the protected admin area.

### Tests for User Story 1

- [X] T012 [P] [US1] Add backend authentication controller/service unit tests in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/ and spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/controller/
- [X] T013 [P] [US1] Add explicit backend test for empty or incomplete login form handling in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/controller/
- [X] T014 [P] [US1] Add frontend login component tests in angular-publisher-service/src/app/features/admin/**/*.spec.ts

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement admin authentication service and login endpoint in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java
- [X] T016 [US1] Implement login form UI and admin route entry in angular-publisher-service/src/app/features/admin/login.component.ts and angular-publisher-service/src/app/features/admin/login.component.html
- [X] T017 [US1] Add frontend auth service and token storage in angular-publisher-service/src/app/core/services/auth.service.ts and angular-publisher-service/src/app/core/models/auth.model.ts
- [X] T018 [US1] Add error handling for invalid credentials and show clear login errors in angular-publisher-service/src/app/features/admin/login.component.ts

**Checkpoint**: User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Controlled Access for Admin-Only Areas (Priority: P2)

**Goal**: Protect admin-only pages and API endpoints so only authenticated admins can access them.

**Independent Test**: A non-admin or unauthenticated user cannot access protected admin content.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add backend authorization integration tests for protected routes in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [ ] T020 [P] [US2] Add explicit backend integration test for non-admin access denial in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [X] T021 [P] [US2] Add frontend route guard tests in angular-publisher-service/src/app/core/**/*.spec.ts

### Implementation for User Story 2

- [X] T022 [P] [US2] Add Angular route guard and protected admin route configuration in angular-publisher-service/src/app/app.routes.ts and angular-publisher-service/src/app/core/guards/admin.guard.ts
- [X] T023 [US2] Add backend method security and endpoint protection for admin APIs in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/
- [X] T024 [US2] Add admin dashboard placeholder page and navigation wiring in angular-publisher-service/src/app/features/admin/dashboard.component.ts and angular-publisher-service/src/app/features/admin/dashboard.component.html

**Checkpoint**: User Story 2 should be independently functional and protected.

---

## Phase 5: User Story 3 - Session Lifecycle Management (Priority: P2)

**Goal**: Support logout and session expiration handling for the admin authentication flow.

**Independent Test**: A signed-out or expired admin session is redirected away from protected areas and cannot continue using them.

### Tests for User Story 3

- [X] T025 [P] [US3] Add logout and expired-token backend tests in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [X] T026 [P] [US3] Add frontend logout/session-expiration tests in angular-publisher-service/src/app/features/admin/**/*.spec.ts

### Implementation for User Story 3

- [X] T027 [US3] Implement logout flow and token clearing in angular-publisher-service/src/app/core/services/auth.service.ts and angular-publisher-service/src/app/features/admin/login.component.ts; guard every localStorage access with isPlatformBrowser(platformId) for SSR compatibility
- [X] T028 [US3] Modify the existing angular-publisher-service/src/app/core/services/api.service.ts to add Axios request interception that injects the JWT and response interception that handles 401 cleanup/redirect, while preserving the existing loader interceptors; guard every localStorage access with isPlatformBrowser(platformId) because SSR runs on Node.js; update angular-publisher-service/src/app/core/guards/admin.guard.ts for expiration handling and redirect logic
- [X] T029 [US3] Add backend auth/me and logout endpoints in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and hardening for the new authentication flow.

- [X] T030 [P] Update documentation and quickstart steps in specs/001-admin-authentication-flow/quickstart.md
- [X] T031 [P] Add end-to-end validation for login, logout, and protected route access in angular-publisher-service/src/app/features/admin/ and spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [X] T032 Run backend tests and frontend build verification for the new admin auth flow
