"""Tests for pilot QA documentation files."""

import os
import re


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
MAKEFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "Makefile")


def test_pilot_qa_doc_exists():
    """docs/pilot_qa.md exists."""
    path = os.path.join(DOCS_DIR, "pilot_qa.md")
    assert os.path.isfile(path), f"Missing: {path}"


def test_readme_links_pilot_qa():
    """README.md links to docs/pilot_qa.md."""
    assert os.path.isfile(README_PATH), "README.md not found"
    with open(README_PATH) as f:
        content = f.read()
    assert "pilot_qa.md" in content, "README.md does not link to pilot_qa.md"


def test_readme_has_pilot_qa_section():
    """README.md has a ## Pilot QA section."""
    assert os.path.isfile(README_PATH)
    with open(README_PATH) as f:
        content = f.read()
    assert re.search(r"##+\s+Pilot QA", content), "README.md missing Pilot QA section"


def test_makefile_exists():
    """Makefile exists in project root."""
    assert os.path.isfile(MAKEFILE_PATH), "Makefile not found"


def test_makefile_has_pilot_check():
    """Makefile includes pilot-check command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "pilot-check" in content, "Makefile missing pilot-check command"


def test_makefile_has_check_closed_loop():
    """Makefile includes check-closed-loop command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "check-closed-loop" in content


def test_makefile_has_check_demo():
    """Makefile includes check-demo command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "check-demo" in content
