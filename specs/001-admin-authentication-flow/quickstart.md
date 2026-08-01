# Quickstart: Admin Authentication Flow

## Prerequisites
- Backend service running with a configured database.
- Frontend dev server available.
- At least one user record exists with admin=true.

## Validation steps
1. Start the backend and frontend services.
2. Open the admin login route in the Angular app.
3. Submit valid admin credentials and verify the app redirects to the protected admin area.
4. Attempt to access an admin-only route or API with invalid or non-admin credentials and verify access is denied.
5. Log out and verify the session is cleared and the user is redirected away from protected routes.
