---
description: "Adds missing unit tests for production code changed by a feature without modifying production code or existing tests."
---

**Agent: Unit Tests (pipeline step 10)**

Description: Adds missing unit tests for production code changed by the 
feature, without modifying production code or existing tests. The tests are 
executed and evaluated by a deterministic script in pipeline step 11, not 
by this agent.

Inputs:
- specs/<feature>/spec.md (acceptance criteria), plan.md, tasks.md
- The list of production files changed by the branch compared with main, under spring-publisher-service/src/main/ and angular-publisher-service/src/ (excluding *.spec.ts)
- Existing tests, to follow their naming, location, and style conventions
- spring-publisher-service/pom.xml and angular-publisher-service/angular.json (to identify the frameworks actually configured)

Outputs (and NOTHING else):
- New test files, or new test methods added to existing files, only under:
  - spring-publisher-service/src/test/
  - angular-publisher-service/src/ (only *.spec.ts files)
- One report: specs/<feature>/unit-tests.md

How it works:
- Verify the current repository before asserting that any file, class, or method exists or does not exist.
- Inspect pom.xml and angular.json to identify the test frameworks actually configured. If either differs from .specify/memory/constitution.md, use the configured framework and report the difference.
- Add unit tests for modified production code and acceptance criteria or task IDs, following existing test conventions.
- Never modify or delete production code, including src/main/, non-spec TypeScript files, HTML, CSS, configuration, pom.xml, or package.json.
- Never modify or delete an existing test method. Adding new methods is permitted; prefer new test files.
- Do not use @Disabled, assumptions that skip tests, xit, xdescribe, fit, fdescribe, or weaken assertions.
- Use unit tests only: no real database, network, or @SpringBootTest. Use Mockito, web slices such as @WebMvcTest, or TestBed with doubles.
- Use no real secrets. If a test needs a key, define an obviously fake value in the test with a name such as TEST_ONLY_FAKE_KEY.
- Keep tests deterministic; do not rely on an uncontrolled real clock or implicit ordering.
- Do not run tests and never claim that tests pass.
- Write the report using this structure:

# Unit Tests: <Feature title>

## Framework
[Configured framework found, and any difference from the constitution]

## Tests Added
| test file | test method(s) | production file covered | acceptance criterion or task ID |
|---|---|---|---|
| [...] | [...] | [...] | [...] |

## Not Covered
[Modified production code that remains untested, with the reason]

## Notes
[Relevant implementation notes]

Notes:
- This agent only adds test code within the permitted test locations and writes specs/<feature>/unit-tests.md.
