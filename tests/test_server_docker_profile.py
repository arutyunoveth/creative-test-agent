"""Tests for Docker server profile and Makefile commands."""
import os
from pathlib import Path


def test_dockerfile_exists():
    assert Path("Dockerfile").is_file()


def test_dockerfile_has_healthcheck():
    content = Path("Dockerfile").read_text()
    assert "HEALTHCHECK" in content


def test_dockerfile_has_non_root_user():
    content = Path("Dockerfile").read_text()
    assert "cta" in content
    assert "USER cta" in content


def test_dockerfile_has_uvicorn_cmd():
    content = Path("Dockerfile").read_text()
    assert "uvicorn" in content


def test_docker_compose_server_exists():
    assert Path("docker-compose.server.yml").is_file()


def test_docker_compose_server_has_required_volumes():
    import yaml
    with open("docker-compose.server.yml") as f:
        compose = yaml.safe_load(f)
    service = compose.get("services", {}).get("creative-test-agent", {})
    volumes = [v.split(":")[0] for v in service.get("volumes", [])]
    assert any("./data/db" in v for v in volumes)
    assert any("./data/storage" in v for v in volumes)
    assert any("./data/exports" in v for v in volumes)
    assert any("./data/backups" in v for v in volumes)


def test_docker_compose_server_has_restart_policy():
    import yaml
    with open("docker-compose.server.yml") as f:
        compose = yaml.safe_load(f)
    service = compose.get("services", {}).get("creative-test-agent", {})
    assert service.get("restart") == "unless-stopped"


def test_docker_compose_server_env_file():
    import yaml
    with open("docker-compose.server.yml") as f:
        compose = yaml.safe_load(f)
    service = compose.get("services", {}).get("creative-test-agent", {})
    env_files = service.get("env_file", [])
    assert ".env.server" in env_files


def test_docker_compose_server_no_cloud_services():
    import yaml
    with open("docker-compose.server.yml") as f:
        compose = yaml.safe_load(f)
    services = compose.get("services", {})
    assert "creative-test-agent" in services
    assert len(services) == 1


def test_dockerignore_exists():
    assert Path(".dockerignore").is_file()


def test_dockerignore_excludes_env():
    content = Path(".dockerignore").read_text()
    assert ".env" in content


def test_dockerignore_excludes_data():
    content = Path(".dockerignore").read_text()
    assert "data/" in content


def test_dockerignore_excludes_git():
    content = Path(".dockerignore").read_text()
    assert ".git" in content


def test_makefile_has_server_commands():
    content = Path("Makefile").read_text()
    server_cmds = [
        "server-build",
        "server-up",
        "server-down",
        "server-logs",
        "server-check",
        "server-bootstrap-admin",
        "server-backup",
    ]
    for cmd in server_cmds:
        assert cmd in content, f"Missing Makefile command: {cmd}"


def test_makefile_has_migration_commands():
    content = Path("Makefile").read_text()
    assert "migrations-check" in content
    assert "migrations-upgrade" in content
