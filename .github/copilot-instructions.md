# Copilot instructions for publisher-app

Purpose: provide concise, actionable repository-specific guidance so future Copilot sessions (agents, /plan, /tasks) can find build/test/lint commands, understand the high-level architecture, and follow conventions used across modules.

---

## Quick commands (root)
- Start entire stack (dev):
  - ./scripts/run-all.sh dev start
- Build all images:
  - docker compose build
- Start with Docker Compose:
  - docker compose up -d

## Per-module build & test
- Spring service (spring-publisher-service)
  - Build: ./mvnw -f spring-publisher-service clean package
  - Run (dev via scripts): ./scripts/run-spring.sh dev start
  - Run tests (module): cd spring-publisher-service && ./mvnw test
  - Run a single unit/testng test (example):
    - cd spring-publisher-service && ./mvnw -Dtest=ClassName#method test
    - or: ./mvnw -Dtest=FullyQualifiedClassName test
  - Notes: environment files are under spring-publisher-service/config/.env.{dev,staging,prod}

- Angular frontend (angular-publisher-service)
  - Dev server: cd angular-publisher-service && npm start  # runs ng serve
  - Build: cd angular-publisher-service && npm run build
  - Unit tests: cd angular-publisher-service && npm test
  - Run single unit/spec: focus a spec with `fdescribe`/`fit` in the spec or edit the spec to run only that test during development (Karma/Jasmine).
  - Container: scripts/run-angular.sh and Dockerfile available; service name in docker-compose is `angular-publisher-service`.
  - SSR server: npm run serve:ssr:angular-publisher-service (runs built SSR server)

- Automation / tests (ui-automation-testing, api-automation-testing)
  - Build & run (module): cd ui-automation-testing && mvn test  (uses TestNG + Cucumber + Playwright)
  - API tests: cd api-automation-testing && mvn test
  - Run a single TestNG test/class: cd <module> && mvn -Dtest=ClassName test
  - TestNG suite used: test-suite/testng.xml in each automation module (pom.xml references this file)
  - Allure reports: target/site/allure-maven-plugin/index.html (module-specific)

- Helpful wrapper scripts (root/scripts)
  - ./scripts/run-spring.sh <env> <start|stop|test|build|logs>
  - ./scripts/run-angular.sh <env> <start|stop|test|build|logs>
  - ./scripts/run-ui-tests.sh <env> <test|start|stop|logs>
  - ./scripts/run-api-tests.sh <env> <test|start|stop|logs>
  - These scripts accept env = dev|staging|prod and pass env files where required.

## High-level architecture (big picture)
- Microservice layout:
  - Frontend: angular-publisher-service (Angular app, port 4200 in compose)
  - Backend: spring-publisher-service (Spring Boot REST API, port 8080)
  - DB: Postgres container (configured in docker-compose)
  - Testing: Separate modules for UI and API automation using Playwright + TestNG/Cucumber. Docker Compose optionally runs automation containers.
- Orchestration & env:
  - docker-compose.yml coordinates services. Environment-specific variables for the Spring service live in spring-publisher-service/config/.env.* and are passed to docker compose in scripts.
- Observability:
  - Spring Actuator exposed at /actuator
  - Allure reports produced by automation modules

## Key repository conventions (specific patterns)
- Scripts are canonical entry points. Prefer using scripts/run-*.sh for environment-aware runs rather than calling docker/mvn/npm directly.
- Environment selection: most scripts require the first arg to be the environment token (dev|staging|prod); this toggles build targets and environment files.
- Docker service names: docker compose services use module folder names (e.g., angular-publisher-service, spring-publisher-service). Scripts validate these names before acting.
- Tests
  - TestNG suite XML located at test-suite/testng.xml in automation modules; CI and pom.xml reference that suite.
  - To run a focused Java test via Maven use -Dtest=ClassName or -Dtest=ClassName#method
  - Cucumber feature files for UI live in ui-automation-testing/src/test/resources/features/ (run via TestNG runner)
- Frontend
  - Angular uses environment files in src/environments/environment.{dev,staging,prod}. The run-angular script will validate the corresponding file before starting.
  - Use fdescribe/fit to focus Karma/Jasmine tests locally if needed.
- Logs & reports
  - All modules write logs under their module-level logs/ directories; Allure output is under target/site/allure-maven-plugin.

## Files and docs to consult (used to compose this file)
- README.md (root)
- spring-publisher-service/README.md
- angular-publisher-service/README.md
- scripts/*.sh
- api-automation-testing/pom.xml and ui-automation-testing/pom.xml (TestNG + Playwright configs)

---

If this file already exists, merge these notes into the existing file and keep any repository-specific pointers already present.

Short checklist for Copilot sessions
- Look at scripts/* first for env-aware entry points
- Use docker compose for full-stack runs and the module scripts for focused work
- For single Java tests use Maven -Dtest; for single Angular specs use fdescribe/fit
- For Jira work, use the workspace agent at .github/agents/jira-ticket-data-extraction.agent.md for ticket lookup and normalization

---

Generated by repository scan on: 2026-07-14
