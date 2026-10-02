# E2E Test Agent

## Description
Writes and wires the end-to-end (E2E) UI test scenario for the Admin Authentication Flow feature (spec `001-admin-authentication-flow`), inside the existing `ui-automation-testing` module (Playwright + TestNG + Cucumber, Page Object Model). This agent corresponds to the "E2E Test Agent" step in the project's delivery flowchart, which runs after implementation and code review, and before the E2E Review Agent validates the result.

## Inputs
- `specs/001-admin-authentication-flow/spec.md`, `data-model.md`, `contracts/auth-api.md` — functional requirements to cover (login success, invalid credentials, protected-route access without auth, logout).
- Real route paths, confirmed in `angular-publisher-service/src/app/app.routes.ts`:
  - `admin/login` → `LoginComponent`
  - `admin` → `DashboardComponent`, guarded by `adminGuard`
- Real components (read them before writing anything, do not assume their markup changed):
  - `angular-publisher-service/src/app/features/admin/login.component.html` / `.ts`
  - `angular-publisher-service/src/app/features/admin/dashboard.component.html` / `.ts`
- Existing conventions to mirror exactly (read all of these before writing the Admin equivalents):
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/pages/AuthorPage.java`
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/steps/AuthorSteps.java`
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/constants/AuthorTestIds.java`
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/constants/PagesNavigate.java`
  - `ui-automation-testing/src/test/resources/features/Author.feature`
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/hooks/Hooks.java`
  - `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/runners/TestRunner.java` (features path/glue — should not need changes)

## Outputs
1. `login.component.html` and `dashboard.component.html` updated with `data-testid` attributes on: username input, password input, submit button, error message, dashboard root/page marker, logout button — following the exact naming style already used in `AuthorTestIds` (kebab-case, prefixed by feature: `admin-username-input`, `admin-password-input`, `admin-login-button`, `admin-login-error`, `admin-dashboard-page`, `admin-logout-button`). No other change to these components — no logic, no styling.
2. New `AdminTestIds.java` in `constants/`, same style as `AuthorTestIds.java`.
3. Two new constants added to `PagesNavigate.java`: `ADMIN_LOGIN_NAVIGATE = "/admin/login"`, `ADMIN_DASHBOARD_NAVIGATE = "/admin"`.
4. New `AdminPage.java` in `pages/`, following the same structure as `AuthorPage.java` (private locators built from `AdminTestIds`, a constructor taking `Page`, navigation/action/query methods, no assertions inside the page object).
5. New `AdminSteps.java` in `steps/`, following the same structure as `AuthorSteps.java` (Cucumber `@Given/@When/@Then`, TestNG `Assert`, no direct Playwright calls outside the page object).
6. New `Admin.feature` in `src/test/resources/features/`, same Gherkin style/tag convention as `Author.feature` (`@smoke`, `@regression`), covering at minimum:
   - Successful login redirects to the dashboard.
   - Invalid credentials show the login error message and stay on the login page.
   - Visiting `/admin` directly without being authenticated redirects to `/admin/login`.
   - Logout from the dashboard returns to the login page, and a subsequent direct visit to `/admin` redirects to login again.

## How it works
1. Read every file listed under Inputs before writing anything — do not assume unread file contents.
2. Confirm how valid admin credentials are obtained in the local/test environment (bootstrap env vars `ADMIN_BOOTSTRAP_ENABLED`/`ADMIN_BOOTSTRAP_USERNAME`/`ADMIN_BOOTSTRAP_PASSWORD_HASH`, and how the test environment is meant to know the plaintext password matching that hash — check `ui-automation-testing/src/test/resources/environments/dev.properties` and any `.env`/docker-compose used to start the stack for E2E). If this plaintext credential is not discoverable anywhere in the repo, stop and report this as a blocking gap instead of inventing a value — the human must decide where the E2E admin test credential is defined.
3. Apply the `data-testid` additions to the two Angular components.
4. Create `AdminTestIds.java` and extend `PagesNavigate.java`.
5. Create `AdminPage.java`, `AdminSteps.java`, `Admin.feature`.
6. Do not touch `Hooks.java` or `TestRunner.java` unless something you found in step 1 requires it (e.g. a per-scenario admin bootstrap call) — if so, explain why before changing it.
7. Report back a summary of every file created or modified, and the blocking gap from step 2 if unresolved.

## Notes
- This agent only writes E2E test code and the minimal `data-testid` markup needed to make it deterministic — it must not modify backend code, security logic, or any file outside the paths listed above.
- A human (Koukou) reviews and runs the resulting tests before they are considered validated; this agent does not mark the E2E step as "Approved" — that is the E2E Review Agent's job, done afterward.
- Follow the naming/style conventions found in the existing Author/Magazine files exactly; do not introduce a different pattern.