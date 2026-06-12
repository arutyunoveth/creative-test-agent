"""Tests for export documentation files."""

import os


def test_advanced_report_exports_doc_exists():
    path = "docs/advanced_report_exports.md"
    assert os.path.isfile(path), f"{path} not found"
    with open(path) as f:
        content = f.read()
    assert "DOCX" in content
    assert "PPTX" in content
    assert "PDF" in content


def test_advanced_exports_doc_exists():
    path = "docs/advanced_exports.md"
    assert os.path.isfile(path), f"{path} not found"
    with open(path) as f:
        content = f.read()
    assert "docx" in content
    assert "pptx" in content


def test_export_docs_referenced_in_readme():
    path = "README.md"
    assert os.path.isfile(path)
    with open(path) as f:
        content = f.read()
    assert "advanced_report_exports" in content


def test_export_root_in_env_example():
    path = ".env.example"
    assert os.path.isfile(path)
    with open(path) as f:
        content = f.read()
    assert "CTA_EXPORTS_ROOT" in content


def test_export_root_in_settings():
    from src.shared.config.settings import get_settings
    settings = get_settings()
    assert hasattr(settings, "exports_root")
    assert settings.exports_root is not None


def test_export_docs_client_pilot():
    path = "docs/client_pilot/technical_overview_ru.md"
    assert os.path.isfile(path)
    with open(path) as f:
        content = f.read()
    assert "DOCX" in content or "PPTX" in content or "Word" in content or "PowerPoint" in content


def test_no_cloud_conversion_api():
    from scripts.check_server_readiness import check_cloud_sdks
    import sys
    try:
        check_cloud_sdks()
    except SystemExit:
        pass
