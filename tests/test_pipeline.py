from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.creative_assets.service import create_asset
from src.modules.test_runs.pipeline import (
    brand_safety_review,
    creative_summary,
    final_recommendation,
    rubric_scoring,
    run_pipeline,
)
from src.shared.llm.stub import StubProvider


def _stub():
    return StubProvider()


def test_pipeline_returns_structured_result():
    asset = create_asset(CreateCreativeAssetRequest(title="Test", asset_type="text", text_content="Hello world"))

    result = run_pipeline(
        creative_asset_id=asset.id,
        brand_profile_id=None,
        audience_profile_ids=[],
        rubric_id=None,
        provider=_stub(),
    )

    assert "summary" in result
    assert result["summary"] != ""
    assert "scorecard" in result
    assert len(result["scorecard"]) > 0
    assert "risks" in result
    assert "audience_reactions" in result
    assert "final_recommendation" in result
    assert result["final_recommendation"] in ("show_to_client", "revise", "reject")
    assert "findings" in result
    assert len(result["findings"]) > 0


def test_pipeline_scorecard_has_expected_criteria():
    asset = create_asset(CreateCreativeAssetRequest(title="Score Test", asset_type="text", text_content="Buy now!"))

    result = run_pipeline(
        creative_asset_id=asset.id,
        brand_profile_id=None,
        audience_profile_ids=[],
        rubric_id=None,
        provider=_stub(),
    )

    criteria = {s["criterion"] for s in result["scorecard"]}
    assert "message_clarity" in criteria
    assert "memorability" in criteria
    assert "audience_fit" in criteria
    assert "call_to_action" in criteria
    assert "trust" in criteria
    assert "brand_fit" in criteria
    assert "negativity_risk" in criteria
    assert "distinctiveness" in criteria


def test_creative_summary_stub():
    asset = create_asset(CreateCreativeAssetRequest(title="Summary Test", asset_type="text", text_content="Amazing offer!"))
    result = creative_summary(asset.id, _stub())
    assert "summary" in result
    assert result["key_message"] == "Amazing offer!"


def test_brand_safety_stub():
    asset = create_asset(CreateCreativeAssetRequest(title="Safety Test", asset_type="text", text_content="Safe content"))
    result = brand_safety_review(asset.id, None, _stub())
    assert len(result) > 0
    assert result[0]["risk_type"] == "brand_fit"


def test_rubric_scoring_stub():
    asset = create_asset(CreateCreativeAssetRequest(title="Rubric Test", asset_type="text", text_content="Score me"))
    scores, avg = rubric_scoring(asset.id, None, _stub())
    assert len(scores) > 0
    assert avg > 0


def test_final_recommendation_stub():
    asset = create_asset(CreateCreativeAssetRequest(title="Rec Test", asset_type="text", text_content="Decide"))
    rec = final_recommendation(
        asset_id=asset.id,
        summary={"summary": "Good ad"},
        scorecard=[{"criterion": "test", "score": 8.0}],
        risks=[],
        audience_reactions=[],
        provider=_stub(),
    )
    assert rec in ("show_to_client", "revise", "reject")


def test_pipeline_with_audience_profiles():
    from src.modules.audience_profiles.schemas import CreateAudienceProfileRequest
    from src.modules.audience_profiles.service import create_profile as create_audience

    asset = create_asset(CreateCreativeAssetRequest(title="Audience Test", asset_type="text", text_content="Hello"))
    profile = create_audience(CreateAudienceProfileRequest(name="TestSegment", segment_description="Test desc"))

    result = run_pipeline(
        creative_asset_id=asset.id,
        brand_profile_id=None,
        audience_profile_ids=[profile.id],
        rubric_id=None,
        provider=_stub(),
    )

    assert len(result["audience_reactions"]) > 0
    assert result["audience_reactions"][0]["segment_name"] == "TestSegment"


def test_pipeline_with_brand_profile():
    from src.modules.brand_profiles.schemas import CreateBrandProfileRequest
    from src.modules.brand_profiles.service import create_profile as create_brand

    asset = create_asset(CreateCreativeAssetRequest(title="Brand Pipe Test", asset_type="text", text_content="Brand content"))
    brand = create_brand(CreateBrandProfileRequest(name="TestBrand"))

    result = run_pipeline(
        creative_asset_id=asset.id,
        brand_profile_id=brand.id,
        audience_profile_ids=[],
        rubric_id=None,
        provider=_stub(),
    )

    assert len(result["risks"]) > 0
