"""Tests for server operations documentation."""
from pathlib import Path


def test_server_deployment_guide_exists():
    assert Path("docs/deployment/server_deployment_guide_ru.md").is_file()


def test_backup_restore_doc_exists():
    assert Path("docs/deployment/backup_restore_ru.md").is_file()


def test_maintenance_doc_exists():
    assert Path("docs/deployment/maintenance_ru.md").is_file()


def test_docker_server_profile_doc_exists():
    assert Path("docs/deployment/docker_server_profile.md").is_file()


def test_readme_has_server_deployment_section():
    content = Path("README.md").read_text()
    assert "Server Deployment" in content


def test_readme_links_server_docs():
    content = Path("README.md").read_text()
    assert "docs/deployment/server_deployment_guide_ru.md" in content
    assert "docs/deployment/docker_server_profile.md" in content
    assert "docs/deployment/backup_restore_ru.md" in content
    assert "docs/deployment/maintenance_ru.md" in content


def test_deployment_readme_exists():
    assert Path("docs/deployment/README.md").is_file()
