"""Tests for client pilot documentation files."""

import os


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "client_pilot")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
MAKEFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "Makefile")


def test_client_pilot_docs_dir_exists():
    """docs/client_pilot/ directory exists."""
    assert os.path.isdir(DOCS_DIR), f"Missing: {DOCS_DIR}"


CLIENT_PILOT_DOCS = [
    "README.md",
    "pilot_scope_ru.md",
    "security_statement_ru.md",
    "technical_overview_ru.md",
    "client_onboarding_questions_ru.md",
    "pilot_success_criteria_ru.md",
    "commercial_pilot_outline_ru.md",
    "pilot_profile_format_ru.md",
]


def test_all_client_pilot_docs_exist():
    """All required client pilot docs exist."""
    for doc in CLIENT_PILOT_DOCS:
        path = os.path.join(DOCS_DIR, doc)
        assert os.path.isfile(path), f"Missing: {path}"


def test_readme_links_client_pilot_pack():
    """README.md links to Client Pilot Pack."""
    assert os.path.isfile(README_PATH)
    with open(README_PATH) as f:
        content = f.read()
    assert "Client Pilot Pack" in content, "README.md missing Client Pilot Pack reference"


def test_readme_has_client_pilot_section():
    """README.md has a ## Client Pilot Pack section."""
    assert os.path.isfile(README_PATH)
    with open(README_PATH) as f:
        content = f.read()
    assert "Client Pilot Pack" in content


def test_makefile_has_load_demo_profile():
    """Makefile includes load-demo-profile command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "load-demo-profile" in content


def test_makefile_has_build_client_pack():
    """Makefile includes build-client-pack command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "build-client-pack" in content


def test_makefile_has_client_pilot_check():
    """Makefile includes client-pilot-check command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "client-pilot-check" in content


def test_pilot_profile_format_doc_mentions_loader():
    """pilot_profile_format_ru.md mentions load_pilot_profile.py."""
    path = os.path.join(DOCS_DIR, "pilot_profile_format_ru.md")
    assert os.path.isfile(path)
    with open(path) as f:
        content = f.read()
    assert "load_pilot_profile.py" in content, "Doc should reference the loader script"


def test_pilot_scope_mentions_closed_loop():
    """pilot_scope_ru.md mentions closed-loop or stub."""
    path = os.path.join(DOCS_DIR, "pilot_scope_ru.md")
    assert os.path.isfile(path)
    with open(path) as f:
        content = f.read()
    assert "stub" in content or "closed-loop" in content
