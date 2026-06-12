"""Tests for brandbook compliance pipeline stage."""

from src.modules.test_runs.pipeline import (
    _detect_forbidden_claims,
    _detect_tone_violations,
    brandbook_compliance_review,
)
from src.shared.llm.stub import StubProvider


def _stub():
    return StubProvider()


def test_forbidden_claims_detection():
    violations = _detect_forbidden_claims("This product is a miracle cure for everything.")
    assert len(violations) >= 1
    assert any("miracle" in v["rule"] or "cure" in v["rule"] for v in violations)
    for v in violations:
        assert v["severity"] == "high"


def test_no_forbidden_claims_clean():
    violations = _detect_forbidden_claims("This is a standard product description.")
    assert violations == []


def test_tone_violations_aggressive():
    violations = _detect_tone_violations("You must act now. You need to buy this. Don't miss this urgent offer.")
    assert any(v["rule"] == "tone_aggressive" for v in violations)


def test_tone_violations_casual():
    violations = _detect_tone_violations("Hey guys, this is gonna be awesome and cool. Wanna check it out?")
    assert any(v["rule"] == "tone_too_casual" for v in violations)


def test_no_tone_violations_clean():
    violations = _detect_tone_violations("This is a balanced and professional message.")
    assert violations == []


def test_compliance_stub_clean():
    result = brandbook_compliance_review(
        asset_id="nonexistent",
        brand_profile_id=None,
        provider=_stub(),
    )
    assert result["overall_verdict"] == "compliant"
    assert result["compliance_score"] >= 7


def test_compliance_stub_with_violations():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="Test Asset",
        asset_type="text",
        text_content="This miracle cure will change everything. Act now! Don't miss this urgent limited time offer.",
    ))
    result = brandbook_compliance_review(
        asset_id=asset.id,
        brand_profile_id=None,
        provider=_stub(),
    )
    assert result["overall_verdict"] != "compliant"
    assert len(result["violations"]) >= 1
    assert len(result["recommendations"]) >= 1
    assert result["compliance_score"] < 10


def test_compliance_stub_verdict_non_compliant():
    from src.modules.creative_assets.service import create_asset as create_creative_asset
    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest

    asset = create_creative_asset(CreateCreativeAssetRequest(
        title="Bad Asset",
        asset_type="text",
        text_content="This miracle cure is a guaranteed result. Secret formula. Hidden from you.",
    ))
    result = brandbook_compliance_review(
        asset_id=asset.id,
        brand_profile_id=None,
        provider=_stub(),
    )
    assert result["overall_verdict"] == "non_compliant"
