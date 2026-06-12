# Local server setup

## System requirements

- Python 3.14+
- pip

## Quickstart

```bash
git clone <repo>
cd creative-test-agent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

Open http://localhost:8000/

## Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default settings work out of the box with stub providers.

## Production-like local run

```bash
CTA_ENV=production CTA_HOST=0.0.0.0 CTA_PORT=8000 uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Verification

```bash
make pilot-check
make build-client-pack
```

## Known limitations

- Default database is SQLite (single file).
- Auth is disabled by default.
- No multi-tenant support.
- PDF stub mode only — real PDF generation requires additional setup.
