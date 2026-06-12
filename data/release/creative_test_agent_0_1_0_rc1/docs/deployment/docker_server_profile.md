# Docker Server Profile

## Overview

The server Docker profile provides a production-ready container setup for pilot deployment. It includes:

- Non-root user for security
- Health check endpoint monitoring
- Persistent volumes for database, uploads, exports, and backups
- `restart: unless-stopped` policy for reliability

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container build: slim Python 3.14 image, non-root user, healthcheck |
| `.dockerignore` | Excludes venv, git, data, secrets from build context |
| `docker-compose.server.yml` | Production compose file with volumes and env file |

## Build & Run

```bash
# Build the image
make server-build

# Start the container
make server-up

# Check server readiness
make server-check

# View logs
make server-logs

# Stop
make server-down
```

## Volumes

| Host path | Container path | Purpose |
|-----------|---------------|---------|
| `./data/db` | `/app/data/db` | SQLite database |
| `./data/storage` | `/app/data/storage` | Uploaded files |
| `./data/exports` | `/app/data/exports` | Generated exports |
| `./data/backups` | `/app/data/backups` | Backup archives |

## Environment

Configure via `.env.server` (copy from `.env.server.example`).

## Limitations

- SQLite is used for storage — not suitable for high-concurrency production
- No load balancing or horizontal scaling
- No external logging service integration

## Health Check

The container includes a Docker health check that pings `GET /health` every 30 seconds.
Container status is visible via `docker ps`.
