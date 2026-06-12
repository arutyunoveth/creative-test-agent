"""Tests for deployment documentation existence and Makefile commands."""

import os

MAKEFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "Makefile")


def test_makefile_has_check_server():
    """Makefile includes check-server command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "check-server" in content


def test_makefile_has_docker_build():
    """Makefile includes docker-build command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "docker-build" in content


def test_makefile_has_docker_up():
    """Makefile includes docker-up command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "docker-up" in content


def test_makefile_has_docker_down():
    """Makefile includes docker-down command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "docker-down" in content


def test_makefile_has_docker_logs():
    """Makefile includes docker-logs command."""
    assert os.path.isfile(MAKEFILE_PATH)
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "docker-logs" in content


def test_readme_has_new_sections():
    """README.md has new Sprint 11 sections."""
    readme = os.path.join(os.path.dirname(__file__), "..", "README.md")
    assert os.path.isfile(readme)
    with open(readme) as f:
        content = f.read()
    assert "Server Deployment Foundation" in content
    assert "Authentication and Roles" in content
    assert "Clients and Projects" in content
    assert "Brandbooks and Knowledge Base" in content
    assert "Advanced Exports" in content


def test_users_doc_exists():
    """docs/users_roles.md exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "users_roles.md")
    assert os.path.isfile(path)


def test_clients_projects_doc_exists():
    """docs/clients_projects_history.md exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "clients_projects_history.md")
    assert os.path.isfile(path)


def test_brandbooks_doc_exists():
    """docs/brandbooks_knowledge_base.md exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "brandbooks_knowledge_base.md")
    assert os.path.isfile(path)


def test_advanced_exports_doc_exists():
    """docs/advanced_exports.md exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "advanced_exports.md")
    assert os.path.isfile(path)


def test_pilot_check_still_present():
    """Makefile still has pilot-check command."""
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "pilot-check" in content


def test_client_pilot_check_still_present():
    """Makefile still has client-pilot-check command."""
    with open(MAKEFILE_PATH) as f:
        content = f.read()
    assert "client-pilot-check" in content
