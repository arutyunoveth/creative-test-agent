# Environment variable reference

All variables are prefixed with `CTA_`.

## Core

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_ENV` | `local` | Environment name (`local`, `production`) |
| `CTA_DEBUG` | `false` | Enable debug logging |
| `CTA_HOST` | `127.0.0.1` | Bind address |
| `CTA_PORT` | `8000` | Bind port |
| `CTA_PUBLIC_BASE_URL` | `http://localhost:8000` | Public-facing base URL |
| `CTA_CORS_ALLOWED_ORIGINS` | `` | Comma-separated allowed CORS origins |
| `CTA_TRUSTED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |

## Auth & Session

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_ENABLE_AUTH` | `false` | Enable user authentication and write protection |
| `CTA_SECRET_KEY` | `` | Secret key for signing session cookies (required if auth enabled) |
| `CTA_SESSION_COOKIE_NAME` | `cta_session` | Session cookie name |
| `CTA_SESSION_TTL_HOURS` | `12` | Session TTL in hours |
| `CTA_PASSWORD_MIN_LENGTH` | `10` | Minimum password length |
| `CTA_BOOTSTRAP_ADMIN_EMAIL` | `` | Bootstrap admin email (run `bootstrap_admin.py`) |
| `CTA_BOOTSTRAP_ADMIN_PASSWORD` | `` | Bootstrap admin password |
| `CTA_BOOTSTRAP_ADMIN_NAME` | `Admin` | Bootstrap admin display name |

## Feature flags

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_ENABLE_AUTH` | `false` | Enable user authentication |
| `CTA_ENABLE_ADMIN` | `false` | Enable admin panel |
| `CTA_ENABLE_PROJECTS` | `false` | Enable clients and projects |
| `CTA_ENABLE_BRANDBOOKS` | `false` | Enable brandbook upload |
| `CTA_ENABLE_ADVANCED_EXPORTS` | `false` | Enable advanced export jobs |

## Database

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_DATABASE_URL` | `sqlite:///./creative_test_agent.db` | Database connection string |

## Closed-loop

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_LOCAL_ONLY_MODE` | `true` | Enforce local-only processing |
| `CTA_ALLOW_CLOUD_LLM` | `false` | Allow cloud LLM providers |

## LLM

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_LLM_PROVIDER` | `stub` | LLM provider (`stub`, `ollama`, `lmstudio`) |
| `CTA_LLM_MODEL` | — | Model name |
| `CTA_LLM_BASE_URL` | — | Provider base URL |
| `CTA_LLM_TIMEOUT_SECONDS` | `60` | Request timeout |

## Vision

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_VISION_PROVIDER` | `stub` | Vision provider (`stub`, `local_ocr`, `local_vlm`, `hybrid`) |
| `CTA_ENABLE_LOCAL_OCR` | `false` | Enable local OCR |
| `CTA_ENABLE_LOCAL_VLM` | `false` | Enable local VLM |
| `CTA_VISION_MODEL` | — | Vision model name |
| `CTA_VISION_BASE_URL` | — | Vision provider base URL |
| `CTA_VISION_TIMEOUT_SECONDS` | `60` | Vision request timeout |

## Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `CTA_STORAGE_ROOT` | `./data/storage` | Local file storage root |
| `CTA_MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload file size |
| `CTA_ALLOWED_UPLOAD_TYPES` | `txt,md,pdf,png,jpg,jpeg,webp` | Allowed upload extensions |
