import os


def test_makefile_has_release_targets():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Makefile")
    with open(path) as f:
        content = f.read()
    assert "release-bundle:" in content
    assert "verify-release-install:" in content
    assert "pilot-smoke:" in content
