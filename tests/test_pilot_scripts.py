"""Tests for pilot QA scripts."""

import os
import sys


SOURCES_DIR = os.path.join(os.path.dirname(__file__), "..")


def test_check_closed_loop_imports():
    """scripts/check_closed_loop.py imports without error."""
    sys.path.insert(0, SOURCES_DIR)
    import scripts.check_closed_loop  # noqa: F401


def test_check_demo_readiness_imports():
    """scripts/check_demo_readiness.py imports without error."""
    sys.path.insert(0, SOURCES_DIR)
    import scripts.check_demo_readiness  # noqa: F401


def test_check_closed_loop_has_main():
    """scripts/check_closed_loop.py exposes a main() function."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.check_closed_loop import main  # noqa: F401
    assert callable(main)


def test_check_demo_readiness_has_main():
    """scripts/check_demo_readiness.py exposes a main() function."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.check_demo_readiness import main  # noqa: F401
    assert callable(main)
