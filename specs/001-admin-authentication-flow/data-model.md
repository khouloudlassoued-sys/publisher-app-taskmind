# Data Model: Admin Authentication Flow

## Entities

### Admin
- id: Long
- username: String
- passwordHash: String
- createdAt: Instant
- updatedAt: Instant

**Validation rules**:
- username must be present and unique.
- passwordHash must be present.

### AuthenticationRequest
- username: String
- password: String

### AuthToken
- accessToken: String
- tokenType: String
- expiresAt: Instant
- adminId: Long

## Relationships
- An admin can authenticate and obtain a token.
- The token is validated per request and mapped to a principal with admin authority.
