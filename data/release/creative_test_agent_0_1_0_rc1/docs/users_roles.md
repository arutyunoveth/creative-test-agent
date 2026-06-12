# Users and Roles

## Current status

User module skeleton is created with:

- **User model** with email, display_name, role, is_active, password_hash (optional)
- **User roles**: admin, manager, analyst, viewer
- **`GET /users/me`** endpoint returning system user context
- **Auth disabled by default** (`CTA_ENABLE_AUTH=false`)

## Auth disabled by default

When auth is disabled:
- All API/UI work as before without authentication
- `GET /users/me` returns a system user stub
- No login required
- No password validation

When auth is enabled (`CTA_ENABLE_AUTH=true`):
- `POST /users` and login endpoints return 501 Not Implemented
- Full auth will be implemented in a future sprint

## Roles

| Role | Description |
|------|-------------|
| admin | Full system access |
| manager | Can manage projects and clients |
| analyst | Can run tests and view reports |
| viewer | Read-only access |

## Limitations

- No complex RBAC implementation yet
- No JWT/session auth
- No password hashing (field exists but unused)
- Auth is purely a data model foundation
- No user management UI
