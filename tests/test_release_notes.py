import os


def test_release_notes_file_exists():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "releases", "0.1.0-rc1.md")
    assert os.path.isfile(path), "Release notes not found"


def test_release_notes_mentions_controlled_local_pilot():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "releases", "0.1.0-rc1.md")
    with open(path) as f:
        content = f.read()
    assert "controlled local pilot" in content.lower() or "release candidate" in content.lower()
