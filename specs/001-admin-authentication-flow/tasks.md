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

- [ ] T001 Create backend auth/security package structure in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/
- [ ] T002 Create frontend admin auth feature structure in angular-publisher-service/src/app/features/admin/
- [ ] T003 [P] Add shared auth models and DTOs in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the admin domain and core security infrastructure required before any story can be implemented.

- [ ] T004 Create Admin entity and repository in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/entity/Admin.java and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/repository/AdminRepository.java
- [ ] T005 Implement BCrypt password hashing and JWT utility/configuration in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/security/
- [ ] T006 Implement Spring Security filter chain and authorization rules for /api/v1/auth/** and admin-protected endpoints in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/config/SecurityConfig.java
- [ ] T007 Add admin authentication DTOs and exception handling for auth failures in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/dto/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/exception/
- [ ] T008 Add auth configuration properties for JWT secret and expiration in spring-publisher-service/src/main/resources/application.properties

**Checkpoint**: Foundation ready - admin authentication implementation can now begin.

---

## Phase 3: User Story 1 - Secure Admin Sign-In (Priority: P1) 🎯 MVP

**Goal**: Allow an admin to sign in securely and receive an authenticated session.

**Independent Test**: An administrator can open the login screen, submit valid credentials, and reach the protected admin area.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add backend authentication controller/service unit tests in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/service/ and spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/controller/
- [ ] T010 [P] [US1] Add frontend login component tests in angular-publisher-service/src/app/features/admin/**/*.spec.ts

### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement admin authentication service and login endpoint in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/service/ and spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java
- [ ] T012 [US1] Implement login form UI and admin route entry in angular-publisher-service/src/app/features/admin/login.component.ts and angular-publisher-service/src/app/features/admin/login.component.html
- [ ] T013 [US1] Add frontend auth service and token storage in angular-publisher-service/src/app/core/services/auth.service.ts and angular-publisher-service/src/app/core/models/auth.model.ts
- [ ] T014 [US1] Add error handling for invalid credentials and show clear login errors in angular-publisher-service/src/app/features/admin/login.component.ts

**Checkpoint**: User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Controlled Access for Admin-Only Areas (Priority: P2)

**Goal**: Protect admin-only pages and API endpoints so only authenticated admins can access them.

**Independent Test**: A non-admin or unauthenticated user cannot access protected admin content.

### Tests for User Story 2

- [ ] T015 [P] [US2] Add backend authorization integration tests for protected routes in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [ ] T016 [P] [US2] Add frontend route guard tests in angular-publisher-service/src/app/core/**/*.spec.ts

### Implementation for User Story 2

- [ ] T017 [P] [US2] Add Angular route guard and protected admin route configuration in angular-publisher-service/src/app/app.routes.ts and angular-publisher-service/src/app/core/guards/admin.guard.ts
- [ ] T018 [US2] Add backend method security and endpoint protection for admin APIs in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/
- [ ] T019 [US2] Add admin dashboard placeholder page and navigation wiring in angular-publisher-service/src/app/features/admin/dashboard.component.ts and angular-publisher-service/src/app/features/admin/dashboard.component.html

**Checkpoint**: User Story 2 should be independently functional and protected.

---

## Phase 5: User Story 3 - Session Lifecycle Management (Priority: P2)

**Goal**: Support logout and session expiration handling for the admin authentication flow.

**Independent Test**: A signed-out or expired admin session is redirected away from protected areas and cannot continue using them.

### Tests for User Story 3

- [ ] T020 [P] [US3] Add logout and expired-token backend tests in spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [ ] T021 [P] [US3] Add frontend logout/session-expiration tests in angular-publisher-service/src/app/features/admin/**/*.spec.ts

### Implementation for User Story 3

- [ ] T022 [US3] Implement logout flow and token clearing in angular-publisher-service/src/app/core/services/auth.service.ts and angular-publisher-service/src/app/features/admin/login.component.ts
- [ ] T023 [US3] Add JWT expiration handling and redirect logic in angular-publisher-service/src/app/core/interceptors/auth.interceptor.ts and angular-publisher-service/src/app/core/guards/admin.guard.ts
- [ ] T024 [US3] Add backend auth/me and logout endpoints in spring-publisher-service/src/main/java/com/mobelite/publisherManagementSystem/controller/AuthController.java

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and hardening for the new authentication flow.

- [ ] T025 [P] Update documentation and quickstart steps in specs/001-admin-authentication-flow/quickstart.md
- [ ] T026 [P] Add end-to-end validation for login, logout, and protected route access in angular-publisher-service/src/app/features/admin/ and spring-publisher-service/src/test/java/com/mobelite/publisherManagementSystem/
- [ ] T027 Run backend tests and frontend build verification for the new admin auth flow
