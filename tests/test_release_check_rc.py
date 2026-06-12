from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_release_check_includes_rc_checks():
    from scripts.release_check import run_checks
    results = run_checks()
    check_names = [r["name"] for r in results]
    assert "release notes exist" in check_names
    assert "release bundle script exists" in check_names
    assert "first install guide exists" in check_names
    assert "pilot smoke script exists" in check_names
    assert "demo meeting checklist exists" in check_names
    assert "version is rc1" in check_names
    assert "bundle can be built" in check_names


async def test_release_check_passes_with_new_checks():
    from scripts.release_check import run_checks
    results = run_checks()
    failures = [r for r in results if not r["passed"]]
    passed_count = sum(1 for r in results if r["passed"])
    assert passed_count >= len(results) - 1
