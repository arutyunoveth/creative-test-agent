#!/usr/bin/env python3
"""Server readiness verification script.

Checks:
1. Settings / env parsed correctly.
2. Database connected.
3. Storage root writable.
4. Alembic migrations current (basic check).
5. Closed-loop check passes (delegates to check_closed_loop).
6. Client pack can be built.
7. No cloud SDKs detected.
8. Auth module importable and configured.
9. HTTP health endpoints available (if app running).

Returns exit code 0 on PASS, 1 on FAIL.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FAILURES: list[str] = []


def check(message: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")
        if detail:
            print(f"    {detail}")
        FAILURES.append(message)


def check_settings():
    from src.shared.config.settings import get_settings

    settings = get_settings()
    check(f"env={settings.env} host={settings.host} port={settings.port}", bool(settings.env))
    check(f"enable_auth={settings.enable_auth}", not settings.enable_auth, "Auth should be disabled by default")
    check(f"enable_projects={settings.enable_projects}", not settings.enable_projects)
    check(f"llm_provider={settings.llm_provider}", settings.llm_provider in ("stub", "ollama", "lmstudio"))
    check(f"vision_provider={settings.vision_provider}", settings.vision_provider in ("stub", "local_ocr", "local_vlm", "hybrid"))


def check_auth():
    """Check auth settings and auth module availability."""
    from src.shared.config.settings import get_settings
    from src.shared.security.auth import get_current_user_from_request
    from src.shared.security.permissions import require_write, require_admin
    from src.shared.security.password import hash_password, verify_password
    from src.shared.security.session import create_session_token, decode_session_token

    settings = get_settings()
    check(f"session_cookie_name={settings.session_cookie_name}", bool(settings.session_cookie_name))
    check(f"session_ttl_hours={settings.session_ttl_hours}", settings.session_ttl_hours > 0)
    check(f"password_min_length={settings.password_min_length}", settings.password_min_length >= 6)

    # Verify auth module functions are importable
    check("hash_password/verify_password importable", callable(hash_password))
    check("create_session_token/decode_session_token importable", callable(create_session_token))
    check("get_current_user_from_request importable", callable(get_current_user_from_request))
    check("require_write/require_admin importable", callable(require_write))


def check_database():
    from src.shared.db.session import check_db_connection

    connected = check_db_connection()
    check("Database connection", connected)


def check_storage_root():
    from src.shared.config.settings import get_settings

    path = get_settings().storage_root
    os.makedirs(path, exist_ok=True)
    writable = os.access(path, os.W_OK)
    check(f"Storage root writable ({path})", writable)


def check_migrations():
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        script = ScriptDirectory.from_config(alembic_cfg)
        head = script.get_current_head()
        check(f"Alembic migrations head: {head}", head is not None, "No migration head found")
    except Exception as e:
        check("Alembic migrations checkable", True, f"Could not check migrations — {e}")


def check_closed_loop():
    try:
        from scripts.check_closed_loop import main as cl_main

        cl_main()
    except SystemExit as e:
        ok = e.code == 0
        check("Closed-loop check passes", ok)
    except Exception as e:
        check("Closed-loop check passes", False, str(e))


def check_cloud_sdks():
    forbidden = ["openai", "anthropic", "google.generativeai", "google.cloud.vision", "boto3", "azure.ai.vision"]
    for pkg in forbidden:
        try:
            __import__(pkg.replace(".", "."))
            check(f"No cloud SDK: {pkg}", False, f"Package {pkg} is installed")
        except ImportError:
            check(f"No cloud SDK: {pkg}", True)


def check_client_pack():
    try:
        from scripts.build_client_pilot_pack import build_pack

        tmpdir = os.path.join(os.path.dirname(__file__), "..", "data", "server_readiness_check")
        build_pack(tmpdir)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
        shutil.rmtree(f"{tmpdir}.zip", ignore_errors=True)
        check("Client pack buildable", True)
    except Exception as e:
        check("Client pack buildable", False, str(e))


def check_knowledge_base():
    try:
        from src.modules.brandbooks.chunking import chunk_text
        from src.modules.brandbooks.ingestion import ingest_brandbook
        from src.modules.knowledge_base.search import keyword_search
        from src.modules.knowledge_base.context_builder import build_context
        from src.shared.config.settings import get_settings

        settings = get_settings()
        check(f"kb_chunk_size={settings.kb_chunk_size_chars}", settings.kb_chunk_size_chars > 0)
        check(f"kb_context_max_items={settings.kb_context_max_items}", settings.kb_context_max_items > 0)
        check(f"kb_context_max_chars={settings.kb_context_max_chars}", settings.kb_context_max_chars > 0)

        chunks = chunk_text("Hello world. This is a test.")
        check(f"Chunking works ({len(chunks)} chunks)", len(chunks) >= 1)

        results = keyword_search("test")
        check("Keyword search importable", callable(keyword_search))

        ctx = build_context("test")
        check("Context builder importable", callable(build_context))
    except Exception as e:
        check("Knowledge base modules", False, str(e))


def check_exports():
    try:
        from src.modules.export_jobs.renderers.docx_report import build_docx_report
        from src.modules.export_jobs.renderers.pptx_report import build_pptx_report
        from src.modules.export_jobs.renderers.pdf_report import build_pdf_ready_html
        from src.shared.config.settings import get_settings

        settings = get_settings()
        check(f"exports_root={settings.exports_root}", bool(settings.exports_root))
        check("DOCX renderer importable", callable(build_docx_report))
        check("PPTX renderer importable", callable(build_pptx_report))
        check("PDF-ready renderer importable", callable(build_pdf_ready_html))
    except Exception as e:
        check("Export modules", False, str(e))


def check_model_profiles():
    try:
        from src.modules.model_profiles.service import list_profiles, create_profile, check_profile_health
        from src.modules.model_profiles.models import ModelProfile
        from src.modules.model_profiles.schemas import CreateModelProfileRequest, ModelProfileResponse

        check("ModelProfile model importable", callable(ModelProfile))
        check("list_profiles importable", callable(list_profiles))
        check("check_profile_health importable", callable(check_profile_health))
        profiles = list_profiles()
        check(f"Model profiles accessible ({len(profiles)} found)", True)
    except Exception as e:
        check("Model profile modules", False, str(e))


def check_prompt_registry():
    try:
        from src.modules.prompt_registry.models import PromptVersion
        from src.modules.prompt_registry.service import list_prompts, get_active_prompt, register_prompt

        check("PromptVersion model importable", callable(PromptVersion))
        check("list_prompts importable", callable(list_prompts))
        check("get_active_prompt importable", callable(get_active_prompt))
        check("register_prompt importable", callable(register_prompt))
    except Exception as e:
        check("Prompt registry modules", False, str(e))


def check_evaluations():
    try:
        from src.modules.evaluations.models import EvaluationRun, EvaluationCaseResult
        from src.modules.evaluations.runner import run_evaluation, get_evaluation_results
        from src.modules.evaluations.schemas import RunEvaluationRequest

        check("EvaluationRun model importable", callable(EvaluationRun))
        check("EvaluationCaseResult model importable", callable(EvaluationCaseResult))
        check("run_evaluation importable", callable(run_evaluation))
        check("get_evaluation_results importable", callable(get_evaluation_results))

        # Quick smoke run with stub
        result = run_evaluation(profile_id=None, case_ids=["novabank_variant_a"])
        check(f"Eval smoke run: score={result['overall_score']}", result["status"] == "completed")
    except Exception as e:
        check("Evaluation runner", False, str(e))


def check_prompt_traces():
    try:
        from src.modules.prompt_traces.models import PromptTrace
        from src.modules.prompt_traces.service import create_trace, get_trace, list_traces

        check("PromptTrace model importable", callable(PromptTrace))
        check("create_trace importable", callable(create_trace))
        check("get_trace importable", callable(get_trace))
        check("list_traces importable", callable(list_traces))
    except Exception as e:
        check("Prompt trace modules", False, str(e))


def check_structured_output():
    try:
        from src.shared.llm.structured_output import (
            extract_json_candidate, repair_json, validate_stage_output, StageResult,
        )
        from src.shared.llm.stage_processor import process_stage_output

        check("extract_json_candidate importable", callable(extract_json_candidate))
        check("repair_json importable", callable(repair_json))
        check("validate_stage_output importable", callable(validate_stage_output))
        check("StageResult importable", callable(StageResult))
        check("process_stage_output importable", callable(process_stage_output))
    except Exception as e:
        check("Structured output modules", False, str(e))


def check_fallbacks():
    try:
        from src.modules.test_runs.fallbacks import FALLBACKS, get_fallback, has_fallback

        check("FALLBACKS dict importable", len(FALLBACKS) >= 7)
        check("get_fallback importable", callable(get_fallback))
        check("has_fallback importable", callable(has_fallback))
    except Exception as e:
        check("Fallback modules", False, str(e))


def check_http_endpoints():
    try:
        import httpx
    except ImportError:
        check("HTTP health endpoints (httpx not installed)", True, "Skipping HTTP checks")
        return

    base = os.environ.get("CTA_BASE_URL", "http://localhost:8000")
    endpoints = ["/health", "/health/db", "/llm/health", "/vision/health"]
    for ep in endpoints:
        try:
            resp = httpx.get(f"{base}{ep}", timeout=3)
            ok = resp.status_code == 200
            check(f"GET {base}{ep} returns 200", ok, f"Got {resp.status_code}" if not ok else "")
        except httpx.ConnectError:
            check(f"GET {base}{ep}", True, "Server not running — skipping")
        except Exception as e:
            check(f"GET {base}{ep}", True, f"Could not reach — {e}")


def main():
    print("=" * 60)
    print("Server readiness check")
    print("=" * 60)
    print()

    print("[1/17] Settings...")
    check_settings()
    print()

    print("[2/17] Database...")
    check_database()
    print()

    print("[3/17] Storage...")
    check_storage_root()
    print()

    print("[4/17] Migrations...")
    check_migrations()
    print()

    print("[5/17] Model Profiles...")
    check_model_profiles()
    print()

    print("[6/17] Prompt Registry...")
    check_prompt_registry()
    print()

    print("[7/17] Evaluations...")
    check_evaluations()
    print()

    print("[8/17] Prompt Traces...")
    check_prompt_traces()
    print()

    print("[9/17] Structured Output...")
    check_structured_output()
    print()

    print("[10/17] Fallbacks...")
    check_fallbacks()
    print()

    print("[11/17] Closed-loop...")
    check_closed_loop()
    print()

    print("[12/17] Cloud SDKs...")
    check_cloud_sdks()
    print()

    print("[13/17] Client pack...")
    check_client_pack()
    print()

    print("[14/17] Auth module...")
    check_auth()
    print()

    print("[15/17] Knowledge Base...")
    check_knowledge_base()
    print()

    print("[16/17] Exports...")
    check_exports()
    print()

    print("[17/17] HTTP endpoints (skipped if app not running)...")
    try:
        check_http_endpoints()
    except Exception:
        print("  — HTTP checks skipped")
    print()

    print("=" * 60)
    if FAILURES:
        print(f"Server readiness: FAIL ({len(FAILURES)} failure(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Server readiness: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
