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

Returns only the current authenticated admin's non-sensitive identifying fields: `adminId` and `username`. The response never includes `passwordHash`, credentials, tokens, or bootstrap data.

### Success response
```json
{
  "success": true,
  "message": "Authenticated admin",
  "data": {
    "adminId": 1,
    "username": "admin"
  },
  "timestamp": "2026-08-01T11:00:00"
}
```

## POST /api/v1/auth/logout

Clears the client-side token and returns a success message; it does not invalidate the token server-side under the stateless JWT design.