PYTHON = .venv/bin/python
UVICORN = .venv/bin/uvicorn

.PHONY: test run seed-demo reset-demo export-pilot check-closed-loop check-demo pilot-check load-demo-profile build-client-pack client-pilot-check check-server docker-build docker-up docker-down docker-logs bootstrap-admin server-build server-up server-down server-logs server-shell server-check server-bootstrap-admin server-backup server-restore migrations-check migrations-upgrade register-prompts eval-stub eval-local check-local-model release-manifest release-check release-bundle verify-release-install pilot-smoke

test:
	$(PYTHON) -m pytest tests/ -v

run:
	$(UVICORN) src.main:app --reload

seed-demo:
	$(PYTHON) scripts/seed_demo_data.py

reset-demo:
	$(PYTHON) scripts/reset_demo_data.py

export-pilot:
	$(PYTHON) scripts/export_pilot_data.py

check-closed-loop:
	$(PYTHON) scripts/check_closed_loop.py

check-demo:
	$(PYTHON) scripts/check_demo_readiness.py

load-demo-profile:
	$(PYTHON) scripts/load_pilot_profile.py config/pilot_profiles/novabank_demo.json

run-demo-batch:
	$(PYTHON) scripts/run_demo_batch.py

build-client-pack:
	$(PYTHON) scripts/build_client_pilot_pack.py

client-pilot-check:
	$(PYTHON) scripts/build_client_pilot_pack.py /tmp/cta_client_pilot_check && rm -rf /tmp/cta_client_pilot_check /tmp/cta_client_pilot_check.zip

check-server:
	$(PYTHON) scripts/check_server_readiness.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

bootstrap-admin:
	$(PYTHON) scripts/bootstrap_admin.py

pilot-check:
	$(PYTHON) -m pytest tests/ -v && $(PYTHON) scripts/check_closed_loop.py && $(PYTHON) scripts/check_demo_readiness.py

release-manifest:
	$(PYTHON) scripts/build_release_manifest.py

release-check:
	$(PYTHON) scripts/release_check.py

release-bundle:
	$(PYTHON) scripts/build_release_bundle.py

verify-release-install:
	$(PYTHON) scripts/verify_release_install.py

pilot-smoke:
	$(PYTHON) scripts/run_pilot_smoke.py

# ── Prompt Registry ─────────────────────────────────────────────

register-prompts:
	$(PYTHON) scripts/register_prompts.py

# ── Evaluation ──────────────────────────────────────────────────

eval-stub:
	$(PYTHON) scripts/run_evaluation.py --profile stub

eval-local:
	$(PYTHON) scripts/run_evaluation.py --profile ollama-local --smoke

check-local-model:
	$(PYTHON) scripts/check_local_model.py --profile ollama-local

# ── Server Deployment ─────────────────────────────────────────────

server-build:
	docker compose -f docker-compose.server.yml build

server-up:
	docker compose -f docker-compose.server.yml up -d

server-down:
	docker compose -f docker-compose.server.yml down

server-logs:
	docker compose -f docker-compose.server.yml logs -f

server-shell:
	docker compose -f docker-compose.server.yml exec creative-test-agent bash

server-check:
	docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/check_server_readiness.py

server-bootstrap-admin:
	docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/bootstrap_admin.py

server-backup:
	docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/backup_data.py

server-restore:
	@echo "Usage: make server-restore BACKUP=path/to/backup.zip"
	docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/restore_data.py $(BACKUP)

# ── Migrations ────────────────────────────────────────────────────

migrations-check:
	$(PYTHON) scripts/check_migrations.py

migrations-upgrade:
	$(PYTHON) scripts/run_migrations.py
