"""Structured creative pre-test pipeline.

Orchestrates 6 agent stages:
1. creative_summary             — summarize the creative asset
2. audience_simulation          — simulate audience reactions
3. brand_safety_review          — check brand safety against brand profile
4. brandbook_compliance_review  — check creative against brandbook guidelines
5. rubric_scoring               — score creative against rubric criteria
6. final_recommendation         — generate final recommendation from all data

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


def _call_llm_json(provider: LLMProvider, prompt: str, stage_name: str = "") -> dict | None:
    result = provider.generate(prompt)
    content = result.get("content", "")
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        pass

    # If direct parse fails and stage_name is provided, use structured output recovery
    if stage_name:
        import time
        from src.shared.llm.stage_processor import process_stage_output
        start = time.time()
        stage_result = process_stage_output(
            stage_name=stage_name,
            raw_response=content,
            prompt_text=prompt,
            provider=provider,
            latency_ms=(time.time() - start) * 1000,
        )
        if stage_result.success and stage_result.parsed_data is not None:
            return stage_result.parsed_data
    return None


def _parse_stage_result(raw: dict | None, default: dict) -> dict:
    if raw is None:
        return default
    return raw


def _asset_text(asset) -> str:
    return (asset.text_content or asset.extracted_text or "") if asset else ""


def _asset_visual_context(asset) -> dict:
    """Extract visual analysis context from asset metadata, if available."""
    if not asset or not asset.metadata_json:
        return {}
    from src.shared.db.repository import json_loads
    meta = json_loads(asset.metadata_json) or {}
    va = meta.get("visual_analysis", {})
    return {
        "visual_summary": va.get("visual_summary", ""),
        "detected_text": va.get("detected_text", ""),
        "layout_notes": va.get("layout_notes", []),
        "visual_risks": va.get("visual_risks", []),
        "visual_warnings": va.get("warnings", []),
        "visual_provider": va.get("provider", ""),
    }


def creative_summary(asset_id: str, provider: LLMProvider) -> dict:
    asset = get_asset_model(asset_id)
    if asset is None:
        return {"summary": "Creative asset not found.", "key_message": "", "tone": "", "target_audience_vibe": ""}
    text = _asset_text(asset)
    visual = _asset_visual_context(asset)

    # Include visual summary and detected text in the creative context
    visual_desc = ""
    if visual.get("visual_summary"):
        visual_desc += f"Visual description: {visual['visual_summary']}\n"
    if visual.get("detected_text"):
        visual_desc += f"Text detected in image: {visual['detected_text']}\n"
    if visual.get("layout_notes"):
        visual_desc += "Layout observations:\n" + "\n".join(f"- {n}" for n in visual["layout_notes"])

    combined_text = text
    if visual_desc:
        combined_text = (text + "\n\n" + visual_desc) if text else visual_desc

    if _is_stub(provider):
        summary = f"A {asset.asset_type} creative titled '{asset.title}' that communicates a promotional message."
        if visual.get("visual_summary"):
            summary += f" {visual['visual_summary']}"
        return {
            "summary": summary,
            "key_message": combined_text,
            "tone": "persuasive",
            "target_audience_vibe": "general consumers",
        }

    prompt = load_prompt(
        "creative_summary",
        title=asset.title,
        asset_type=asset.asset_type,
        text_content=combined_text,
        visual_description=visual_desc,
    )
    raw = _call_llm_json(provider, prompt, stage_name="creative_summary")
    return _parse_stage_result(raw, {
        "summary": f"Creative titled '{asset.title}'.",
        "key_message": combined_text,
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
        raw = _call_llm_json(provider, prompt, stage_name="audience_simulation")
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


def _scan_risky_claims(text: str) -> list[dict]:
    """Detect common risky claim patterns in creative text (stub mode only)."""
    if not text:
        return []
    lower = text.lower()
    found = []
    risky_patterns = [
        ("overclaim_absolute", "high", ["only ", " ever need", "the best ", "number one ", "top-rated "],
         "Contains absolute or superlative claims that may exaggerate the product's uniqueness.",
         "Replace absolute claims with specific, verifiable benefits."),
        ("overclaim_guarantee", "high", ["guarantee", "guaranteed", "promise", "assure "],
         "Contains guaranteed outcome language that may overstate what the product delivers.",
         "Frame benefits as product features, not guaranteed outcomes."),
        ("overclaim_zero_risk", "high", ["zero risk", "no risk", "risk-free", "no hassle", "zero hassle"],
         "Contains zero-risk or no-hassle language that may be misleading.",
         "Acknowledge reasonable risks or limitations honestly."),
        ("overclaim_pressure", "medium", ["forget ", "ever again", "stop worrying", "never look back"],
         "Contains pressure language that may create unrealistic expectations.",
         "Use measured, reassuring language instead."),
        ("overclaim_income", "high", ["guaranteed income", "guaranteed return", "make money", "get rich"],
         "Contains income or financial outcome guarantees that violate typical claims policies.",
         "Remove financial guarantees; frame as features."),
        ("overclaim_absolute_pct", "medium", ["100%", "100 percent"],
         "Contains absolute percentage claims that may be hard to substantiate.",
         "Qualify percentage claims with specific conditions or sources."),
    ]
    for risk_type, level, patterns, description, mitigation in risky_patterns:
        for pat in patterns:
            if pat in lower:
                found.append({
                    "risk_type": risk_type,
                    "level": level,
                    "description": description,
                    "mitigation": mitigation,
                })
                break
    return found


def _detect_claim_violations(text: str) -> list[dict]:
    """Check creative text against brand restrictions and claims policy."""
    risks = []
    overclaims = _scan_risky_claims(text)
    risks.extend(overclaims)
    return risks


def brand_safety_review(asset_id: str, brand_profile_id: str | None, provider: LLMProvider) -> list[dict]:
    asset = get_asset_model(asset_id)
    asset_text = _asset_text(asset)
    asset_title = asset.title if asset else ""
    asset_type = asset.asset_type if asset else "text"
    visual = _asset_visual_context(asset)

    if _is_stub(provider):
        risks = [
            {"risk_type": "brand_fit", "level": "low", "description": "Creative aligns well with brand identity.", "mitigation": "No action needed."},
            {"risk_type": "negativity_risk", "level": "low", "description": "Low risk of negative perception.", "mitigation": "Monitor comments."},
        ]
        # Include content-aware risk detection
        claim_violations = _detect_claim_violations(asset_text)
        risks.extend(claim_violations)
        # Include visual risks if available
        for vr in visual.get("visual_risks", []):
            risks.append({
                "risk_type": vr.get("risk_type", "visual_risk"),
                "level": vr.get("level", "low"),
                "description": vr.get("description", ""),
                "mitigation": vr.get("mitigation", ""),
            })
        return risks

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
    raw = _call_llm_json(provider, prompt, stage_name="brand_safety_review")
    result = _parse_stage_result(raw, {
        "overall_risk_level": "low",
        "risks": [],
        "brand_fit_score": 7.0,
        "claims_compliance": "compliant",
    })
    return result.get("risks", [])


def _detect_tone_violations(text: str) -> list[dict]:
    """Detect potential tone mismatches in creative text (stub mode)."""
    if not text:
        return []
    lower = text.lower()
    violations = []
    aggressive_words = ["must", "have to", "you need", "urgent", "immediately", "act now", "don't miss"]
    casual_markers = ["gonna", "wanna", "hey", "yo", "sup", "cool", "awesome", "guys"]
    formal_markers = ["hereby", "henceforth", "hereinafter", "thereto", "whereas"]

    aggr_count = sum(1 for w in aggressive_words if w in lower)
    casual_count = sum(1 for w in casual_markers if w in lower)
    formal_count = sum(1 for w in formal_markers if w in lower)

    if aggr_count >= 2:
        violations.append({
            "rule": "tone_aggressive",
            "severity": "medium",
            "details": f"Contains {aggr_count} aggressive/pressure words that may conflict with a friendly tone of voice.",
        })
    if casual_count >= 3:
        violations.append({
            "rule": "tone_too_casual",
            "severity": "low",
            "details": f"Contains {casual_count} casual language markers that may undercut brand authority.",
        })
    if formal_count >= 3:
        violations.append({
            "rule": "tone_too_formal",
            "severity": "low",
            "details": f"Contains {formal_count} formal/legalistic terms that may feel distant to the audience.",
        })
    return violations


_STUB_FORBIDDEN_CLAIMS = [
    "cure", "instant", "overnight", "miracle", "guaranteed results",
    "secret", "hidden", "exclusive access", "limited time",
    "act fast", "supplies running out",
]


def _detect_forbidden_claims(text: str) -> list[dict]:
    if not text:
        return []
    lower = text.lower()
    violations = []
    for claim in _STUB_FORBIDDEN_CLAIMS:
        if claim in lower:
            violations.append({
                "rule": f"forbidden_claim_{claim.replace(' ', '_')}",
                "severity": "high",
                "details": f"Contains forbidden claim: '{claim}'. This violates standard brandbook guidelines.",
            })
    return violations


def brandbook_compliance_review(
    asset_id: str,
    brand_profile_id: str | None,
    provider: LLMProvider,
    context_text: str = "",
) -> dict:
    asset = get_asset_model(asset_id)
    asset_text = _asset_text(asset)
    asset_title = asset.title if asset else ""
    asset_type = asset.asset_type if asset else "text"

    if _is_stub(provider):
        violations = []
        violations.extend(_detect_forbidden_claims(asset_text))
        violations.extend(_detect_tone_violations(asset_text))

        if not violations:
            compliance_score = 9.0
            overall_verdict = "compliant"
            recommendations = ["Creative aligns well with brandbook guidelines."]
        else:
            high_count = sum(1 for v in violations if v["severity"] == "high")
            medium_count = sum(1 for v in violations if v["severity"] == "medium")
            compliance_score = max(1.0, 9.0 - high_count * 3.0 - medium_count * 1.5)
            overall_verdict = "non_compliant" if high_count > 0 else "needs_revision"
            recommendations = [
                f"Fix {v['rule']}: {v['details']}" for v in violations
            ]

        return {
            "overall_verdict": overall_verdict,
            "violations": violations,
            "recommendations": recommendations[:5],
            "compliance_score": compliance_score,
        }

    if brand_profile_id is None:
        return {
            "overall_verdict": "compliant",
            "violations": [],
            "recommendations": [],
            "compliance_score": 10.0,
        }

    brand = get_brand(brand_profile_id)
    if brand is None:
        return {
            "overall_verdict": "compliant",
            "violations": [],
            "recommendations": [],
            "compliance_score": 10.0,
        }

    compliance_rules = (
        f"Tone of voice: {brand.tone_of_voice or 'Not specified'}\n"
        f"Restrictions: {brand.restrictions or 'None'}\n"
        f"Claims policy: {brand.claims_policy or 'None'}\n"
    )

    prompt = load_prompt(
        "brandbook_compliance",
        title=asset_title,
        text_content=asset_text,
        asset_type=asset_type,
        brand_context=context_text or f"Brand: {brand.name}",
        compliance_rules=compliance_rules,
    )
    raw = _call_llm_json(provider, prompt, stage_name="brandbook_compliance_review")
    result = _parse_stage_result(raw, {
        "overall_verdict": "compliant",
        "violations": [],
        "recommendations": [],
        "compliance_score": 7.0,
    })
    return result


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
    raw = _call_llm_json(provider, prompt, stage_name="rubric_scoring")
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
    raw = _call_llm_json(provider, prompt, stage_name="final_recommendation")
    result = _parse_stage_result(raw, {"final_recommendation": "revise"})
    rec = result.get("final_recommendation", "revise")
    if rec not in ("show_to_client", "revise", "reject"):
        rec = "revise"
    return rec


def _build_brandbook_context(brand_profile_id: str | None) -> str:
    if brand_profile_id is None:
        return ""
    try:
        from src.modules.brandbooks.service import get_brandbook_context
        ctx = get_brandbook_context(brand_profile_id=brand_profile_id)
        if ctx.snippets:
            return "\n\n".join(ctx.snippets[:3])
    except Exception:
        pass
    return ""


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

    brandbook_ctx = _build_brandbook_context(brand_profile_id)
    compliance = brandbook_compliance_review(
        creative_asset_id, brand_profile_id, provider,
        context_text=brandbook_ctx,
    )

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
        "brandbook_compliance": compliance,
    }
