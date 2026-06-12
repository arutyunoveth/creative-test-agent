from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_release_check_script_imports():
    from scripts.release_check import run_checks
    assert callable(run_checks)


async def test_release_check_returns_pass_in_default_context():
    from scripts.release_check import run_checks, CHECKS
    results = run_checks()
    assert len(results) >= 5
    passed_count = sum(1 for r in results if r["passed"])
    assert passed_count >= len(results) - 1


async def test_release_check_detects_pytest():
    from scripts.release_check import _pytest_available
    assert _pytest_available() is True
