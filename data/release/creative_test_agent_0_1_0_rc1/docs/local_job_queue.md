# Local Job Queue

The local job queue provides a simple, deterministic, DB-backed queue for processing tasks without external dependencies.

## Architecture

- **Storage**: SQLite `job` table
- **No broker**: no Celery, Redis, RabbitMQ, or external services
- **No daemon**: no background worker process — jobs are processed explicitly via API calls
- **No secrets**: job payloads and results are JSON stored in the database (no raw secrets)

## Job Statuses

```
queued → running → completed
                → failed → (retry) → queued
                → cancelled
```

## Job Types

| Type | Description |
|---|---|
| `run_test` | Execute a test run |
| `generate_report` | Generate a report for a test run |
| `analyze_visual` | Run visual analysis on an asset |
| `batch_run` | Run all items in a batch |
| `batch_report` | Generate a batch summary report |
| `export_report` | Export a report to DOCX/PPTX/PDF |

## Maximum Attempts

Jobs have a configurable `max_attempts` (default: 3). Once a job has failed and been retried `max_attempts` times, it cannot be retried again.

## API

See [batch_testing.md](batch_testing.md) for the full job queue API reference.

## Future Async Worker

In a future sprint, a lightweight async worker could be added that polls for queued jobs in a background thread. This would process jobs without explicit `run-next` / `run-all` calls. The queue model and service layer are designed to support this without changes.
