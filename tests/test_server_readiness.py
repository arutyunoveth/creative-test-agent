"""Tests for server readiness and deployment foundation."""

import os


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "deployment")
DOCKERFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
DOCKERIGNORE_PATH = os.path.join(os.path.dirname(__file__), "..", ".dockerignore")
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")


def test_deployment_docs_exist():
    """All deployment docs exist."""
    required = [
        "README.md", "local_server_setup.md", "docker_setup.md",
        "env_reference.md", "server_checklist_ru.md",
    ]
    for doc in required:
        path = os.path.join(DOCS_DIR, doc)
        assert os.path.isfile(path), f"Missing: {path}"


def test_dockerfile_exists():
    """Dockerfile exists."""
    assert os.path.isfile(DOCKERFILE_PATH), "Dockerfile not found"


def test_dockerignore_exists():
    """.dockerignore exists."""
    assert os.path.isfile(DOCKERIGNORE_PATH), ".dockerignore not found"


def test_compose_exists():
    """docker-compose.yml exists."""
    assert os.path.isfile(COMPOSE_PATH), "docker-compose.yml not found"


def test_check_server_readiness_imports():
    """check_server_readiness.py imports without errors."""
    import scripts.check_server_readiness  # noqa: F401


def test_check_server_readiness_has_main():
    """check_server_readiness.py exposes main()."""
    from scripts.check_server_readiness import main
    assert callable(main)


def test_settings_has_new_fields():
    """Settings has new deployment and feature flag fields."""
    from src.shared.config.settings import get_settings
    s = get_settings()
    assert hasattr(s, "env")
    assert hasattr(s, "host")
    assert hasattr(s, "port")
    assert hasattr(s, "public_base_url")
    assert hasattr(s, "enable_auth")
    assert hasattr(s, "enable_admin")
    assert hasattr(s, "enable_projects")
    assert hasattr(s, "enable_brandbooks")
    assert hasattr(s, "enable_advanced_exports")
    assert hasattr(s, "trusted_hosts")
    assert hasattr(s, "cors_allowed_origins")


def test_settings_defaults_are_safe():
    """Default settings keep demo-friendly defaults."""
    from src.shared.config.settings import get_settings
    s = get_settings()
    assert s.enable_auth is False
    assert s.enable_admin is False
    assert s.enable_projects is False
    assert s.enable_brandbooks is False
    assert s.enable_advanced_exports is False


def test_env_example_has_new_vars():
    """.env.example includes new deployment and feature flag vars."""
    example = os.path.join(os.path.dirname(__file__), "..", ".env.example")
    assert os.path.isfile(example)
    with open(example) as f:
        content = f.read()
    assert "CTA_ENV=" in content
    assert "CTA_HOST=" in content
    assert "CTA_PORT=" in content
    assert "CTA_PUBLIC_BASE_URL=" in content
    assert "CTA_SECRET_KEY=" in content
    assert "CTA_ENABLE_AUTH=" in content
    assert "CTA_ENABLE_ADMIN=" in content
    assert "CTA_ENABLE_PROJECTS=" in content
    assert "CTA_ENABLE_BRANDBOOKS=" in content
    assert "CTA_ENABLE_ADVANCED_EXPORTS=" in content
    assert "CTA_CORS_ALLOWED_ORIGINS=" in content
    assert "CTA_TRUSTED_HOSTS=" in content
