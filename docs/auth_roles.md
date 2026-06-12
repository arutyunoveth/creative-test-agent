# Auth and Roles

## Default: auth disabled

When `CTA_ENABLE_AUTH=false` (default):
- All API and UI work without login.
- `GET /auth/me` and `GET /users/me` return a system user stub.
- All write endpoints are accessible.
- No authentication checks are performed.

## Enabling auth

Set environment variables:

```bash
CTA_ENABLE_AUTH=true
CTA_SECRET_KEY=<your-secret-key>
```

If `CTA_SECRET_KEY` is empty when auth is enabled, the system will still work but will use an insecure default key. For server/production mode, always set a strong secret key.

## Bootstrap admin

Before using auth, create an admin user:

```bash
CTA_ENABLE_AUTH=true \
CTA_SECRET_KEY=your-secret-key \
CTA_BOOTSTRAP_ADMIN_EMAIL=admin@example.com \
CTA_BOOTSTRAP_ADMIN_PASSWORD=your-strong-password \
python scripts/bootstrap_admin.py
```

The script is idempotent — running it multiple times won't create duplicates.

## Roles

| Role | Permissions |
|------|-------------|
| admin | Full access — manage users, all operations |
| manager | Create/update clients, projects, profiles, creatives, test runs |
| analyst | Create creatives, run tests, view reports, upload brandbooks |
| viewer | Read-only access to all entities |

## Permission matrix

| Operation | admin | manager | analyst | viewer |
|-----------|-------|---------|---------|--------|
| Create users | ✓ | ✗ | ✗ | ✗ |
| Read entities | ✓ | ✓ | ✓ | ✓ |
| Create clients/projects | ✓ | ✓ | ✗ | ✗ |
| Create brand/audience profiles | ✓ | ✓ | ✓ | ✗ |
| Upload creatives | ✓ | ✓ | ✓ | ✗ |
| Run tests | ✓ | ✓ | ✓ | ✗ |
| View reports | ✓ | ✓ | ✓ | ✓ |
| Upload brandbooks | ✓ | ✓ | ✓ | ✗ |

## API endpoints

```
POST /auth/login      — login (returns session cookie)
POST /auth/logout     — logout (clears session cookie)
GET  /auth/me         — current user info

GET  /users           — list users (admin only)
POST /users           — create user (admin only)
GET  /users/{id}      — get user (admin only)
PATCH /users/{id}     — update user (admin only)
POST /users/{id}/deactivate — deactivate user (admin only)
```

## UI login flow

1. Open `http://localhost:8000/ui/login`
2. Login with email and password
3. Dashboard shows user info and role
4. Users link visible to admins
5. Logout button in navigation

## Limitations

- No OAuth, SSO, or external auth providers.
- No password reset flow.
- No rate limiting on login.
- No MFA.
- Sessions use signed cookies (no server-side session store).
- Session TTL is configurable via `CTA_SESSION_TTL_HOURS`.
- Passwords are hashed with bcrypt.
- User management UI is minimal.
