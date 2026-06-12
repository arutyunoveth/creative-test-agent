"""Evaluation documentation page tests."""

import pytest
from pathlib import Path


DOCS_DIR = Path(__file__).parent.parent / "docs"


def test_model_profiles_doc_exists():
    assert (DOCS_DIR / "model_profiles.md").is_file()


def test_evaluation_harness_doc_exists():
    assert (DOCS_DIR / "evaluation_harness.md").is_file()


def test_local_model_pilot_readiness_doc_exists():
    assert (DOCS_DIR / "local_model_pilot_readiness.md").is_file()


def test_model_profiles_doc_has_content():
    content = (DOCS_DIR / "model_profiles.md").read_text()
    assert len(content) > 100
    assert "stub" in content
    assert "ollama" in content


def test_evaluation_harness_doc_has_content():
    content = (DOCS_DIR / "evaluation_harness.md").read_text()
    assert len(content) > 100
    assert "eval case" in content.lower() or "case" in content


def test_local_model_pilot_doc_has_content():
    content = (DOCS_DIR / "local_model_pilot_readiness.md").read_text()
    assert len(content) > 100
    assert "pilot" in content.lower()


def test_eval_scripts_exist():
    scripts_dir = Path(__file__).parent.parent / "scripts"
    assert (scripts_dir / "run_evaluation.py").is_file()
    assert (scripts_dir / "register_prompts.py").is_file()


def test_eval_cases_dir_exists():
    cases_dir = Path(__file__).parent.parent / "data" / "eval_cases"
    assert cases_dir.is_dir()
    files = list(cases_dir.glob("*.json"))
    assert len(files) >= 5


def test_config_profiles_exist():
    config_dir = Path(__file__).parent.parent / "config" / "model_profiles"
    assert config_dir.is_dir()
    json_files = list(config_dir.glob("*.json"))
    assert len(json_files) >= 1
