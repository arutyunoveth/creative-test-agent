# Docker setup

## Build and run

```bash
make docker-build
make docker-up
```

App will be available at http://localhost:8000/

## Stop

```bash
make docker-down
```

## Logs

```bash
make docker-logs
```

## Configuration

Create `.env` file in the project root. Docker Compose passes env vars to the container.

## Volumes

- SQLite database is stored on a local volume for persistence.
- Uploaded files are stored on a local volume.

## Notes

- The Docker setup is designed for pilot deployment, not production hardening.
- No cloud services are included.
- No external APIs are configured.
- Default stub providers are used.
