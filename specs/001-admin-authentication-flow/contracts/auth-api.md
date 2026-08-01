# Authentication API Contract

## POST /api/v1/auth/login

### Request
```json
{
  "username": "admin",
  "password": "secret"
}
```

### Success response
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "jwt-token",
    "tokenType": "Bearer",
    "expiresAt": "2026-08-01T12:00:00Z",
    "adminId": 1
  },
  "timestamp": "2026-08-01T11:00:00"
}
```

### Failure response
```json
{
  "success": false,
  "message": "Invalid username or password",
  "data": null,
  "timestamp": "2026-08-01T11:00:00"
}
```

## GET /api/v1/auth/me

Returns the current authenticated user details and admin status.

## POST /api/v1/auth/logout

Invalidates the client-side session state and returns a success message.
