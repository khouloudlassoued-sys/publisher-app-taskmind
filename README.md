
> **Note** : Ce repository est une copie de travail du projet original
> de [Amira Dgham](https://github.com/Amira-Dgham/publisher-app), utilisée
> dans le cadre d'un stage (projet TaskMind). Voir [NOTICE.md](./NOTICE.md)
> pour plus de détails.

---

# Publisher Application

## Overview
A comprehensive publishing management system built with a microservices architecture, consisting of:
- Spring Boot backend service
- Angular frontend application
- End-to-end testing with Playwright
- Containerized deployment using Docker

## Project Architecture

```
├── Frontend Layer (Angular)
│   └── Angular Publisher Service
├── Backend Layer (Spring Boot)
│   └── Spring Publisher Service
├── Testing Layer
│   └── Playwright E2E Testing
└── Infrastructure Layer
    └── Docker Containers
```

![Architecture Diagram](docs/images/architecture.png)

## Project Structure

```
publisher-app/
├── angular-publisher-service/    # Frontend Angular application
├── spring-publisher-service/     # Backend Spring Boot service
├── ui-automation-testing/       # UI automation (Cucumber + Playwright + TestNG)
├── api-automation-testing/      # API automation (Playwright + TestNG)
├── scripts/                     # Deployment and run scripts
│   ├── run-all.sh              # Run entire stack
│   ├── run-angular.sh          # Run frontend only
│   ├── run-spring.sh           # Run backend only
│   ├── run-ui-tests.sh         # Run UI automation tests
│   ├── run-api-tests.sh        # Run API automation tests
├── docker-compose.yml          # Docker composition
└── README.md                   # This file
```

## Technologies Used

### Frontend (Angular)
- Angular 17+
- TypeScript
- Docker container

### Backend (Spring Boot)
- Java 17
- Spring Boot 3.5.3
- PostgreSQL
- Docker container


### Testing & Automation
#### UI Automation
- Playwright (UI automation)
- Cucumber (Gherkin BDD)
- TestNG (runner)
- Allure Reporting
- Java 17

#### API Automation
- Playwright (API automation)
- TestNG
- Allure Reporting
- Java 17

### Infrastructure
- Docker
- Docker Compose
- Shell Scripts

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Java 17
- Node.js 18+
- Maven 3.6+

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Amira-Dgham/publisher-app.git
cd publisher-app
```

2. Start the entire stack:
```bash
./scripts/run-all.sh
```

This will:
- Build and start all Docker containers
- Initialize the database
- Start the Spring Boot backend
- Launch the Angular frontend
- Prepare the UI and API automation environments

### Individual Component Setup

#### Backend Service
```bash
./scripts/run-spring.sh dev start
```

#### Frontend Service
```bash
./scripts/run-angular.sh dev start
```


#### UI Automation (Cucumber + Playwright)
```bash
./scripts/run-ui-tests.sh test dev
```

#### API Automation
```bash
./scripts/run-api-tests.sh test dev
```

## Docker Configuration

### Docker Compose Overview
The application uses Docker Compose to manage multiple containers:

```yaml
services:
  frontend:
    build: ./angular-publisher-service
    ports:
      - "4200:80"
    depends_on:
      - backend

  backend:
    build: ./spring-publisher-service
    ports:
      - "8080:8080"
    depends_on:
      - db

  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: publisher
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret

  # Automation containers (if needed)
  ui-automation-testing:
    build: ./ui-automation-testing
    depends_on:
      - frontend
      - backend

  api-automation-testing:
    build: ./api-automation-testing
    depends_on:
      - backend
```

### Running with Docker

1. Build all containers:
```bash
docker-compose build
```

2. Start the stack:
```bash
docker-compose up -d
```

3. Check status:
```bash
docker-compose ps
```

4. View logs:
```bash
docker-compose logs -f
```

## Available Endpoints

### Frontend
- Main Application: http://localhost:4200

### Backend
- API Base URL: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html
- API Docs: http://localhost:8080/v3/api-docs


## Testing & Automation

### UI Automation (Cucumber + Playwright)
- Gherkin feature files in `ui-automation-testing/src/test/resources/features/`
- Step definitions in `ui-automation-testing/src/test/java/com/mobelite/publisher/ui/steps/`
- Test runner: Cucumber + TestNG (`TestRunner.java`)
- Allure reports generated after each run

Run all UI tests:
```bash
./scripts/run-ui-tests.sh test dev
```
Allure report: `ui-automation-testing/target/site/allure-maven-plugin/index.html`

### API Automation
- Test classes in `api-automation-testing/src/test/java/com/mobelite/publisher/api/tests/`
- TestNG-based, Playwright-powered API tests
- Allure reports generated after each run

Run all API tests:
```bash
./scripts/run-api-tests.sh test dev
```
Allure report: `api-automation-testing/target/site/allure-maven-plugin/index.html`

### Run All Tests (UI + API)
```bash
./scripts/run-all.sh test e2e
```
This will run both UI and API automation suites and generate Allure reports for each.

## Monitoring & Logging

### Application Monitoring
- Spring Actuator: http://localhost:8080/actuator
- Angular Performance: http://localhost:4200/metrics


### Logs
- Backend Logs: `spring-publisher-service/logs/`
- Frontend Logs: `angular-publisher-service/logs/`
- UI Automation Logs: `ui-automation-testing/logs/`
- API Automation Logs: `api-automation-testing/logs/`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Additional Documentation
- [Spring Service Documentation](spring-publisher-service/README.md)
- [Angular Service Documentation](angular-publisher-service/README.md)
- [UI Automation Documentation](ui-automation-testing/README.md)
- [API Automation Documentation](api-automation-testing/README.md)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
