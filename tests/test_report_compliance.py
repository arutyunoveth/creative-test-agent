"""Tests for brandbook compliance section in reports."""

from src.modules.report_generator.renderers import _build_compliance_html, _build_compliance_md
from src.modules.report_generator.service import generate_report
from src.modules.test_runs.schemas import BrandbookCompliance, ComplianceViolation


def test_compliance_md_empty():
    lines = _build_compliance_md(None, "internal")
    assert lines == []


def test_compliance_md_clean():
    compliance = BrandbookCompliance(overall_verdict="compliant", compliance_score=10.0, violations=[], recommendations=[])
    lines = _build_compliance_md(compliance, "internal")
    assert lines == []


def test_compliance_md_with_violations():
    compliance = BrandbookCompliance(
        overall_verdict="non_compliant",
        compliance_score=4.5,
        violations=[ComplianceViolation(rule="test_rule", severity="high", details="Test details")],
        recommendations=["Fix the issue"],
    )
    lines = _build_compliance_md(compliance, "internal")
    assert len(lines) > 0
    combined = "\n".join(lines)
    assert "Brandbook Compliance" in combined
    assert "non_compliant" in combined or "Non Compliant" in combined
    assert "4.5" in combined
    assert "test_rule" in combined
    assert "Fix the issue" in combined


def test_compliance_md_client_facing():
    compliance = BrandbookCompliance(
        overall_verdict="non_compliant",
        compliance_score=5.0,
        violations=[ComplianceViolation(rule="test", severity="high", details="Details")],
    )
    lines = _build_compliance_md(compliance, "client_facing")
    combined = "\n".join(lines)
    assert "Needs Attention" in combined or "Brand alignment" in combined


def test_compliance_html_empty():
    html = _build_compliance_html(None, "internal")
    assert html == ""


def test_compliance_html_with_violations():
    compliance = BrandbookCompliance(
        overall_verdict="needs_revision",
        compliance_score=6.0,
        violations=[ComplianceViolation(rule="tone_rule", severity="medium", details="Tone mismatch detected")],
        recommendations=["Adjust tone to be more formal"],
    )
    html = _build_compliance_html(compliance, "internal")
    assert "Brandbook Compliance" in html
    assert "needs_revision" in html or "Needs Revision" in html
    assert "6.0" in html
    assert "tone_rule" in html
    assert "Adjust tone" in html


def test_compliance_verdict_labels():
    c1 = BrandbookCompliance(overall_verdict="compliant", compliance_score=10.0)
    assert c1.overall_verdict == "compliant"
    c2 = BrandbookCompliance(overall_verdict="non_compliant", compliance_score=3.0)
    assert c2.overall_verdict == "non_compliant"
    c3 = BrandbookCompliance(overall_verdict="needs_revision", compliance_score=6.0)
    assert c3.overall_verdict == "needs_revision"
