## Admin authentication

The admin API uses a stateless one-hour JWT and BCrypt password hashes. No credentials or JWT secrets belong in source control.

For local development only, set `ADMIN_BOOTSTRAP_ENABLED=true`, `ADMIN_BOOTSTRAP_USERNAME`, and `ADMIN_BOOTSTRAP_PASSWORD_HASH` in the environment before starting the Spring service. The bootstrap is active only with the `dev` profile; it is disabled by default and unavailable when the `prod` profile is active. Generate the hash with a trusted BCrypt tool, then remove the bootstrap variables after the first account is created.

Sign in through `/admin/login`. Logout removes the browser token; it does not revoke a copied JWT server-side.
# Quickstart: Admin Authentication Flow

## Prerequisites
- Backend service running with a configured database.
- Frontend dev server available.
- An initial dedicated `Admin` entity has been created through the development-only bootstrap script or endpoint, using a pre-hashed password or one-time setup secret.

## Validation steps
1. Start the backend and frontend services.
2. Open the admin login route in the Angular app.
3. Submit valid admin credentials and verify the app redirects to the protected admin area.
4. Attempt to access an admin-only route or API with invalid or non-admin credentials and verify access is denied.
5. Log out and verify the session is cleared and the user is redirected away from protected routes.
