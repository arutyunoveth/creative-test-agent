"""Structured creative pre-test pipeline.

Orchestrates 5 agent stages:
1. creative_summary   — summarize the creative asset
2. audience_simulation — simulate audience reactions
3. brand_safety_review — check brand safety against brand profile
4. rubric_scoring     — score creative against rubric criteria
5. final_recommendation — generate final recommendation from all data

Each stage supports two modes:
- stub: returns deterministic structured defaults (for tests / default config)
- live: loads prompt template → calls LLM → parses JSON → returns data
"""

import json

from src.modules.audience_profiles.service import get_profile as get_audience
from src.modules.brand_profiles.service import get_profile as get_brand
from src.modules.creative_assets.service import get_asset_model
from src.modules.test_rubrics.service import get_rubric
from src.shared.llm.base import LLMProvider

from .prompts import load_prompt

STUB_SCORECARD = [
    {"criterion": "message_clarity", "score": 7.5, "rationale": "The core message is reasonably clear.", "recommendation": "Consider sharpening the headline."},
    {"criterion": "memorability", "score": 6.0, "rationale": "Moderate memorability; could use a stronger hook.", "recommendation": "Add a memorable visual or slogan."},
    {"criterion": "audience_fit", "score": 8.0, "rationale": "Good alignment with target audience.", "recommendation": "Maintain current targeting."},
    {"criterion": "call_to_action", "score": 7.0, "rationale": "CTA is present but could be more compelling.", "recommendation": "Make the CTA more urgent."},
    {"criterion": "trust", "score": 8.5, "rationale": "High trust signals.", "recommendation": "Keep trust elements."},
    {"criterion": "brand_fit", "score": 9.0, "rationale": "Strong brand alignment.", "recommendation": "No changes needed."},
    {"criterion": "negativity_risk", "score": 3.0, "rationale": "Low risk of negative perception.", "recommendation": "No changes needed."},
    {"criterion": "distinctiveness", "score": 6.5, "rationale": "Moderately distinct from competitors.", "recommendation": "Add a unique differentiator."},
]


def _is_stub(provider: LLMProvider) -> bool:
    return provider.__class__.__name__ == "StubProvider"


def _call_llm_json(provider: LLMProvider, prompt: str) -> dict | None:
    result = provider.generate(prompt)
    content = result.get("content", "")
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None


def _parse_stage_result(raw: dict | None, default: dict) -> dict:
    if raw is None:
        return default
    return raw


def _asset_text(asset) -> str:
    return (asset.text_content or asset.extracted_text or "") if asset else ""


def creative_summary(asset_id: str, provider: LLMProvider) -> dict:
    asset = get_asset_model(asset_id)
    if asset is None:
        return {"summary": "Creative asset not found.", "key_message": "", "tone": "", "target_audience_vibe": ""}
    text = _asset_text(asset)

    if _is_stub(provider):
        return {
            "summary": f"A {asset.asset_type} creative titled '{asset.title}' that communicates a promotional message.",
            "key_message": text,
            "tone": "persuasive",
            "target_audience_vibe": "general consumers",
        }

    prompt = load_prompt(
        "creative_summary",
        title=asset.title,
        asset_type=asset.asset_type,
        text_content=text,
    )
    raw = _call_llm_json(provider, prompt)
    return _parse_stage_result(raw, {
        "summary": f"Creative titled '{asset.title}'.",
        "key_message": text,
        "tone": "neutral",
        "target_audience_vibe": "general",
    })


def audience_simulation(asset_id: str, audience_ids: list[str], provider: LLMProvider) -> list[dict]:
    asset = get_asset_model(asset_id)
    asset_text = _asset_text(asset)
    asset_title = asset.title if asset else ""
    asset_type = asset.asset_type if asset else "text"

    if not audience_ids:
        if _is_stub(provider):
            return [{
                "audience_profile_id": "default",
                "segment_name": "General Audience",
                "reaction": "The creative would likely be well-received.",
                "positive_triggers": ["Clear messaging", "Relevant offer"],
                "objections": ["Needs more social proof"],
                "engagement_probability": 7.0,
            }]
        return []

    reactions = []
    for aid in audience_ids:
        profile = get_audience(aid)
        if profile is None:
            continue

        if _is_stub(provider):
            reactions.append({
                "audience_profile_id": aid,
                "segment_name": profile.name,
                "reaction": f"This segment would respond positively to the creative.",
                "positive_triggers": ["Relevant messaging"],
                "objections": [],
                "engagement_probability": 7.0,
            })
            continue

        prompt = load_prompt(
            "audience_simulation",
            title=asset_title,
            text_content=asset_text,
            asset_type=asset_type,
            segment_name=profile.name,
            segment_description=profile.segment_description,
            pains=profile.pains or "",
            motivations=profile.motivations or "",
            objections=profile.objections or "",
        )
        raw = _call_llm_json(provider, prompt)
        result = _parse_stage_result(raw, {
            "reaction": "Neutral reaction expected.",
            "positive_triggers": [],
            "objections": [],
            "engagement_probability": 5.0,
        })
        result["audience_profile_id"] = aid
        result["segment_name"] = profile.name
        reactions.append(result)

    return reactions


def brand_safety_review(asset_id: str, brand_profile_id: str | None, provider: LLMProvider) -> list[dict]:
    asset = get_asset_model(asset_id)
    asset_text = _asset_text(asset)
    asset_title = asset.title if asset else ""
    asset_type = asset.asset_type if asset else "text"

    if _is_stub(provider):
        return [
            {"risk_type": "brand_fit", "level": "low", "description": "Creative aligns well with brand identity.", "mitigation": "No action needed."},
            {"risk_type": "negativity_risk", "level": "low", "description": "Low risk of negative perception.", "mitigation": "Monitor comments."},
        ]

    if brand_profile_id is None:
        return []

    brand = get_brand(brand_profile_id)
    if brand is None:
        return []

    prompt = load_prompt(
        "brand_safety",
        title=asset_title,
        text_content=asset_text,
        asset_type=asset_type,
        brand_name=brand.name,
        tone_of_voice=brand.tone_of_voice or "",
        brand_target_audience=brand.target_audience or "",
        restrictions=brand.restrictions or "",
        claims_policy=brand.claims_policy or "",
    )
    raw = _call_llm_json(provider, prompt)
    result = _parse_stage_result(raw, {
        "overall_risk_level": "low",
        "risks": [],
        "brand_fit_score": 7.0,
        "claims_compliance": "compliant",
    })
    return result.get("risks", [])


def rubric_scoring(asset_id: str, rubric_id: str | None, provider: LLMProvider) -> tuple[list[dict], float]:
    asset = get_asset_model(asset_id)
    asset_text = _asset_text(asset)
    asset_title = asset.title if asset else ""
    asset_type = asset.asset_type if asset else "text"

    if _is_stub(provider):
        scores = STUB_SCORECARD
        avg = sum(s["score"] for s in scores) / len(scores)
        return scores, avg

    rubric = get_rubric(rubric_id) if rubric_id else None
    if rubric is None:
        scores = STUB_SCORECARD
        avg = sum(s["score"] for s in scores) / len(scores)
        return scores, avg

    criteria_lines = "\n".join(
        f"- {c.name}: {c.description}" for c in rubric.criteria
    )
    prompt = load_prompt(
        "rubric_scoring",
        title=asset_title,
        text_content=asset_text,
        asset_type=asset_type,
        rubric_name=rubric.name,
        scale_min=str(rubric.scale_min),
        scale_max=str(rubric.scale_max),
        criteria_list=criteria_lines,
    )
    raw = _call_llm_json(provider, prompt)
    result = _parse_stage_result(raw, {"scorecard": [], "overall_score": 5.0})
    scores = result.get("scorecard", [])
    avg = result.get("overall_score", 5.0)
    if not scores:
        scores = STUB_SCORECARD
        avg = sum(s["score"] for s in scores) / len(scores)
    return scores, avg


def final_recommendation(
    asset_id: str,
    summary: dict,
    scorecard: list[dict],
    risks: list[dict],
    audience_reactions: list[dict],
    provider: LLMProvider,
) -> str:
    asset = get_asset_model(asset_id)
    asset_title = asset.title if asset else ""

    if _is_stub(provider):
        avg = sum(s["score"] for s in scorecard) / max(len(scorecard), 1)
        if avg >= 7.5:
            return "show_to_client"
        elif avg >= 5.0:
            return "revise"
        return "reject"

    prompt = load_prompt(
        "final_recommendation",
        title=asset_title,
        summary=json.dumps(summary),
        scorecard=json.dumps(scorecard),
        risks=json.dumps(risks),
        audience_reactions=json.dumps(audience_reactions),
    )
    raw = _call_llm_json(provider, prompt)
    result = _parse_stage_result(raw, {"final_recommendation": "revise"})
    rec = result.get("final_recommendation", "revise")
    if rec not in ("show_to_client", "revise", "reject"):
        rec = "revise"
    return rec


def run_pipeline(
    creative_asset_id: str,
    brand_profile_id: str | None,
    audience_profile_ids: list[str],
    rubric_id: str | None,
    provider: LLMProvider,
) -> dict:
    summary = creative_summary(creative_asset_id, provider)
    audience = audience_simulation(creative_asset_id, audience_profile_ids, provider)
    risks = brand_safety_review(creative_asset_id, brand_profile_id, provider)
    scorecard, overall = rubric_scoring(creative_asset_id, rubric_id, provider)
    recommendation = final_recommendation(
        creative_asset_id, summary, scorecard, risks, audience, provider,
    )

    findings = [
        {"criterion": s["criterion"], "score": s["score"], "explanation": s.get("rationale", "")}
        for s in scorecard
    ]

    return {
        "summary": summary.get("summary", ""),
        "scorecard": scorecard,
        "risks": risks,
        "audience_reactions": audience,
        "final_recommendation": recommendation,
        "findings": findings,
        "overall_score": overall,
    }
