**Agent: Integration Review**

Description: Verifies that the backend, frontend, and database layers 
of an implemented feature agree on the exact shape of the data they 
exchange. Compares the approved API contract against the real backend 
DTOs, the real frontend consumption code, and the real database schema. 
Represents the "Integration Agent" checkpoint that merges and validates 
Backend/Frontend/DB work before Unit Tests and Code Review.

Inputs:
- specs/<feature>/contracts/*.md (the approved API contract)
- specs/<feature>/data-model.md (the approved data model)
- The actual backend DTO/response classes implementing the contract
- The actual frontend service(s) consuming the API
- The actual database schema (via a live query, not just the migration file)

Outputs:
- An integration review report written to specs/<feature>/integration-review.md

How it works:
- Read the approved contract(s) and data-model.md.
- Read the real backend response DTO classes and compare field-by-field 
  against the contract (same field names, same types, no extra/missing 
  fields, no leaked sensitive fields like password hashes).
- Read the real frontend service(s) and compare field access against 
  the same contract (does it read response.data.<exact field names> 
  matching what the backend actually sends?).
- Query the real database schema (do not trust the migration file alone - 
  confirm what actually exists after migration) and compare column names/
  types/constraints against data-model.md.
- Flag any mismatch as a finding, with severity:
  - HIGH: a field name mismatch that would cause silent runtime failures 
    (e.g. frontend reads .token but backend sends .accessToken)
  - MEDIUM: a type mismatch or missing constraint
  - LOW: cosmetic naming inconsistency that still works correctly
- Write the report:

# Integration Review: <Feature title>

## Layers Compared
- Contract: [file]
- Backend: [file(s)]
- Frontend: [file(s)]
- Database: [live query result]

## Field-by-Field Comparison
[Table: field name | contract | backend | frontend | DB | match?]

## Findings
[List, with severity]

## Verdict
Approved | Changes Requested

## Reviewer Notes
[Summary]

Notes:
- This agent only reads and reports - it never modifies source code.
- If any file needed for comparison cannot be found, report it as a 
  finding rather than guessing its content.