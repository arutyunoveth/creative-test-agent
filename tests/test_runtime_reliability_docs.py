"""Runtime reliability documentation tests."""

from pathlib import Path


DOCS_DIR = Path(__file__).parent.parent / "docs"


def test_local_runtime_reliability_doc_exists():
    assert (DOCS_DIR / "local_runtime_reliability.md").is_file()


def test_prompt_tracing_doc_exists():
    assert (DOCS_DIR / "prompt_tracing.md").is_file()


def test_json_recovery_doc_exists():
    assert (DOCS_DIR / "json_recovery.md").is_file()


def test_local_runtime_doc_has_content():
    content = (DOCS_DIR / "local_runtime_reliability.md").read_text()
    assert len(content) > 100


def test_prompt_tracing_doc_has_content():
    content = (DOCS_DIR / "prompt_tracing.md").read_text()
    assert len(content) > 100


def test_json_recovery_doc_has_content():
    content = (DOCS_DIR / "json_recovery.md").read_text()
    assert len(content) > 100


def test_evaluation_harness_doc_updated():
    content = (DOCS_DIR / "evaluation_harness.md").read_text()
    assert "trace" in content.lower() or "repair" in content.lower() or "metrics" in content.lower()


def test_local_model_pilot_readiness_doc_updated():
    content = (DOCS_DIR / "local_model_pilot_readiness.md").read_text()
    assert "diagnostic" in content.lower() or "check_local_model" in content.lower() or "trace" in content.lower()
