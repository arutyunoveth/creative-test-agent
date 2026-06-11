import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")


def test_demo_pilot_doc_exists():
    path = os.path.join(DOCS_DIR, "demo_pilot.md")
    assert os.path.isfile(path), "docs/demo_pilot.md not found"
    with open(path) as fh:
        content = fh.read()
    assert len(content) > 500
    assert "NovaBank" in content
    assert "seed_demo_data" in content


def test_client_pitch_summary_exists():
    path = os.path.join(DOCS_DIR, "client_pitch_summary.md")
    assert os.path.isfile(path), "docs/client_pitch_summary.md not found"
    with open(path) as fh:
        content = fh.read()
    assert len(content) > 500
    # Should be in Russian
    assert "креатив" in content.lower() or "тестирован" in content.lower()


def test_client_pitch_summary_in_russian():
    path = os.path.join(DOCS_DIR, "client_pitch_summary.md")
    with open(path) as fh:
        content = fh.read()
    # Check for Russian-specific characters
    assert "закрытый контур" in content or "Closed-loop" in content
    assert "бренд" in content


def test_pilot_checklist_exists():
    path = os.path.join(DOCS_DIR, "pilot_checklist.md")
    assert os.path.isfile(path), "docs/pilot_checklist.md not found"
    with open(path) as fh:
        content = fh.read()
    assert len(content) > 500
    assert "Technical Readiness" in content
    assert "Demo Data Readiness" in content
    assert "Client Conversation Checklist" in content


def test_screenshots_readme_exists():
    path = os.path.join(DOCS_DIR, "screenshots", "README.md")
    assert os.path.isfile(path), "docs/screenshots/README.md not found"
    with open(path) as fh:
        content = fh.read()
    assert len(content) > 500
    assert "Dashboard" in content
    assert "screenshot" in content.lower()
