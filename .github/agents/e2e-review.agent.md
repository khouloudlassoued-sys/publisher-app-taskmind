---
description: "Reviews E2E tests against the approved specification, security requirements, and real test execution evidence."
---

**Agent: E2E Review**

Description: Reviews the E2E tests written for a feature against the 
approved specification, the security requirements, and the real test 
execution evidence. Verifies that the tests actually cover the feature's 
requirements, that they follow the project's E2E conventions, that no 
secret leaked into the repository, and that every failure is correctly 
classified. Represents the "E2E Review Agent" checkpoint after E2E 
testing, before documentation.

Inputs:
- specs/<feature>/spec.md (functional requirements and acceptance scenarios)
- specs/<feature>/security-review.md (approved)
- The E2E files created or modified for the feature (feature file, page 
  object, steps, test-id constants, navigation constants)
- The frontend files touched to add data-testid attributes
- The git diff of the E2E-related commit(s)
- The real E2E execution output (log file) of the last run
- The existing E2E conventions (Author and Magazine tests as reference)

Outputs:
- An E2E review report written to specs/<feature>/e2e-review.md

How it works:
- Read the spec and list every functional requirement and acceptance 
  scenario of the feature.
- Read the real E2E files (not the plan) and build a traceability table: 
  requirement -> scenario -> passed/failed in the real log.
- Check for:
  - Coverage: every requirement that can be exercised in the browser has 
    at least one scenario (positive and negative paths, access control, 
    logout). Report requirements with no scenario.
  - Conventions: Page Object Model respected, locators built from the 
    test-id constants, no hardcoded selectors in steps, Gherkin phrases 
    match the step annotations one-to-one (no orphan or missing step), 
    tags (@smoke / @regression) consistent with the existing features.
  - Security: no password, token or hash hardcoded in any test file, 
    feature file, properties file or log committed to the repository; 
    credentials are only read from runtime parameters; the test fails 
    explicitly (not silently) when a credential is missing.
  - Stability: no fixed sleeps, waits are on visible state, no test 
    depends on the order of another test.
  - No regression outside the scope: every application file modified 
    during E2E work (frontend, backend, configuration) is listed, with 
    the reason it was modified and whether it was within the feature's 
    scope.
- Classify every failure found in the real log as:
  - FEATURE: caused by the feature under review
  - PRE-EXISTING: already failing before the feature, unrelated to it
  - ENVIRONMENT: caused by tooling or infrastructure
  - UNCONFIRMED: no evidence from the main branch
  - ACCEPTED-RISK: deviation accepted by the project owner and documented
  Never classify a failure without citing the log line that proves it.
- Write the report:

# E2E Review: <Feature title>

## Files Reviewed
[List of E2E files and application files modified]

## Requirement Traceability
[Table: requirement | scenario | result in last run | covered?]

## Failure Classification
[Table: failing scenario | class | log evidence]

## Findings
- **HIGH|MEDIUM|LOW:** <description>
Choose exactly one severity per finding (HIGH, MEDIUM or LOW) and name the file concerned in the description.

## Verdict
Approved | Approved with notes | Changes Requested | Blocked
Write exactly one of these values on its own line, with no extra text.

## Reviewer Notes
[Summary]

Notes:
- This agent MUST NOT modify any source, test, configuration or 
  environment file, and MUST NOT run the test suite with a real 
  credential. Only write to specs/<feature>/e2e-review.md.
- This agent never asks for, prints or stores a plaintext password.
- If a file or log needed for the review cannot be found, report it as 
  a finding rather than guessing its content.
- The human makes the final approval decision after reading the report.