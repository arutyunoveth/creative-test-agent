import json
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.report_generator.models import Report
from src.modules.report_generator.renderers import build_html_report, build_markdown_report
from src.modules.report_generator.schemas import (
    RecommendationItem,
    ReportAudienceReaction,
    ReportMetadata,
    ReportResponse,
    ReportVersionInfo,
    RiskItem,
    ScorecardItem,
)
from src.modules.test_runs.schemas import TestRunResponse
from src.shared.db.repository import db_session, json_dumps, json_loads


def _version_key(test_run_id: str, mode: str, fmt: str) -> str:
    return f"{test_run_id}||{mode}||{fmt}"


def _get_next_version(test_run_id: str, mode: str, fmt: str) -> int:
    with db_session() as db:
        existing = db.query(Report).filter(
            Report.test_run_id == test_run_id,
            Report.report_mode == mode,
            Report.report_format == fmt,
        ).count()
        return existing + 1


_VALID_MODES = {"internal", "client_facing"}
_VALID_FORMATS = {"json", "markdown", "html", "pdf_stub"}


def _build_visual_notes(run) -> str:
    """Collect visual analysis notes from the test run's creative asset."""
    try:
        from src.modules.creative_assets.service import get_asset
        asset = get_asset(run.creative_asset_id)
        if not asset:
            return ""
        meta = asset.metadata or {}
        va = meta.get("visual_analysis", {})
        if not va:
            return ""

        parts = []
        provider = va.get("provider", "")
        summary = va.get("visual_summary", "")
        detected = va.get("detected_text", "")
        layout = va.get("layout_notes", [])
        risks = va.get("visual_risks", [])
        warnings = va.get("warnings", [])

        if provider:
            parts.append(f"Analysis provider: {provider}")
        if summary:
            parts.append(f"Visual summary: {summary}")
        if detected:
            parts.append(f"Detected text: {detected}")
        if layout:
            parts.append("Layout observations:")
            for note in layout:
                parts.append(f"- {note}")
        if warnings:
            parts.append("Warnings: " + ", ".join(warnings))
        if risks:
            parts.append("Visual risks:")
            for r in risks:
                parts.append(f"- [{r.get('level', 'unknown').upper()}] {r.get('description', '')}")

        return "\n".join(parts) if parts else ""
    except Exception:
        return ""


def _build_mode_report(
    run: TestRunResponse,
    mode: str,
    fmt: str,
) -> dict:
    if mode not in _VALID_MODES:
        raise ValueError(f"unsupported_report_mode: {mode}")
    if fmt not in _VALID_FORMATS:
        raise ValueError(f"unsupported_report_format: {fmt}")

    scorecard = []
    if run.scorecard:
        for s in run.scorecard:
            scorecard.append(ScorecardItem(criterion=s.criterion, score=s.score))
    else:
        scorecard = [
            ScorecardItem(criterion=f.criterion, score=f.score)
            for f in (run.findings or [])
        ]

    risks = []
    for r in run.risks or []:
        risks.append(RiskItem(risk=r.description or r.risk_type or "Unknown risk", severity=r.level or "medium"))

    recommendations = []
    for s in run.scorecard or []:
        if s.score < 6 and s.recommendation:
            recommendations.append(
                RecommendationItem(
                    recommendation=s.recommendation,
                    priority="high" if s.score < 4 else "medium",
                )
            )
    if not recommendations:
        for f in run.findings or []:
            if f.score < 6:
                recommendations.append(
                    RecommendationItem(
                        recommendation=f"Improve '{f.criterion}': {f.explanation}",
                        priority="high" if f.score < 4 else "medium",
                    )
                )

    final_rec = (run.final_recommendation or "revise").replace("_", " ")

    avg_score = run.overall_score or (
        sum(f.score for f in (run.findings or [])) / max(len(run.findings or []), 1)
        if run.findings
        else 0.0
    )

    main_message = ""
    if run.findings:
        best = max(run.findings, key=lambda f: f.score)
        main_message = best.explanation

    audience_reactions = [
        ReportAudienceReaction(
            audience_profile_id=a.audience_profile_id,
            segment_name=a.segment_name,
            reaction=a.reaction,
            positive_triggers=a.positive_triggers,
            objections=a.objections,
            engagement_probability=a.engagement_probability,
        )
        for a in (run.audience_reactions or [])
    ]

    top_strengths = sorted(
        [f for f in (run.findings or []) if f.score >= 7],
        key=lambda x: x.score,
        reverse=True,
    )
    top_improvements = sorted(
        [f for f in (run.findings or []) if f.score < 6],
        key=lambda x: x.score,
    )

    strengths_str = [f"{f.criterion} ({f.score}/10): {f.explanation}" for f in top_strengths]
    improvements_str = [f"{f.criterion} ({f.score}/10): {f.explanation}" for f in top_improvements]

    title = f"Creative Pre-Test Report — {run.id[:8]}..."

    summary_parts = [run.summary or f"Test run {run.id} completed."]
    if mode == "internal":
        summary_parts.append(f"Average score: {avg_score:.1f}/10.")
        summary_parts.append(f"Final recommendation: {final_rec}.")
    else:
        summary_parts.append(f"The creative has been evaluated and is ready for review.")
    summary = " ".join(summary_parts)

    markdown_content = build_markdown_report(
        title=title,
        run=run,
        mode=mode,
        summary=summary,
        avg_score=avg_score,
        scorecard=scorecard,
        risks=risks,
        recommendations=recommendations,
        final_rec=final_rec,
        main_message=main_message,
        audience_reactions=audience_reactions,
        strengths=strengths_str,
        improvements=improvements_str,
    )

    # Build visual notes from asset metadata
    visual_notes = _build_visual_notes(run)

    markdown_content = build_markdown_report(
        title=title,
        run=run,
        mode=mode,
        summary=summary,
        avg_score=avg_score,
        scorecard=scorecard,
        risks=risks,
        recommendations=recommendations,
        final_rec=final_rec,
        main_message=main_message,
        audience_reactions=audience_reactions,
        strengths=strengths_str,
        improvements=improvements_str,
        visual_notes=visual_notes,
    )

    html_content = build_html_report(
        title=title,
        run=run,
        mode=mode,
        summary=summary,
        avg_score=avg_score,
        scorecard=scorecard,
        risks=risks,
        recommendations=recommendations,
        final_rec=final_rec,
        main_message=main_message,
        audience_reactions=audience_reactions,
        strengths=strengths_str,
        improvements=improvements_str,
        visual_notes=visual_notes,
    )

    return {
        "title": title,
        "summary": summary,
        "main_message": main_message,
        "audience_reactions": audience_reactions,
        "scorecard": scorecard,
        "risks": risks,
        "recommendations": recommendations,
        "final_recommendation": final_rec,
        "report_markdown": markdown_content,
        "report_html": html_content if fmt in ("html", "pdf_stub") else None,
        "file_path": None,
        "visual_notes": visual_notes,
    }


def _report_to_response(r: Report) -> ReportResponse:
    return ReportResponse(
        id=r.id,
        test_run_id=r.test_run_id,
        report_mode=r.report_mode,
        report_format=r.report_format,
        version=r.version,
        title=r.title or "",
        summary=r.summary or "",
        main_message=r.main_message or "",
        audience_reactions=[ReportAudienceReaction(**a) for a in (json.loads(r.audience_reactions_json) if r.audience_reactions_json else [])] if r.audience_reactions_json else [],
        scorecard=[ScorecardItem(**s) for s in (json.loads(r.scorecard_json) if r.scorecard_json else [])] if r.scorecard_json else [],
        risks=[RiskItem(**risk) for risk in (json.loads(r.risks_json) if r.risks_json else [])] if r.risks_json else [],
        recommendations=[RecommendationItem(**rec) for rec in (json.loads(r.recommendations_json) if r.recommendations_json else [])] if r.recommendations_json else [],
        final_recommendation=r.final_recommendation or "",
        report_markdown=r.report_markdown or "",
        report_html=r.report_html,
        visual_notes=r.visual_notes or "",
        file_path=r.file_path,
        created_at=r.created_at,
        metadata=ReportMetadata(
            generated_at=r.created_at.isoformat() if r.created_at else "",
            version_info=f"v{r.version} ({r.report_mode}, {r.report_format})",
            note="",
        ),
    )


def generate_report(
    test_run_id: str,
    report_mode: str = "internal",
    report_format: str = "json",
) -> ReportResponse | None:
    from src.modules.test_runs.service import get_test_run

    run = get_test_run(test_run_id)
    if run is None:
        return None
    if run.status != "completed":
        return None

    try:
        data = _build_mode_report(run, report_mode, report_format)
    except ValueError:
        return None

    version = _get_next_version(test_run_id, report_mode, report_format)

    with db_session() as db:
        report = Report(
            test_run_id=test_run_id,
            report_mode=report_mode,
            report_format=report_format,
            version=version,
            title=data["title"],
            summary=data["summary"],
            main_message=data["main_message"],
            audience_reactions_json=json.dumps([a.model_dump() for a in data["audience_reactions"]], default=str),
            scorecard_json=json.dumps([s.model_dump() for s in data["scorecard"]], default=str),
            risks_json=json.dumps([r.model_dump() for r in data["risks"]], default=str),
            recommendations_json=json.dumps([r.model_dump() for r in data["recommendations"]], default=str),
            final_recommendation=data["final_recommendation"],
            report_markdown=data["report_markdown"],
            report_html=data["report_html"],
            visual_notes=data.get("visual_notes", ""),
            file_path=data["file_path"],
            metadata_json=json.dumps({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version_info": f"v{version} ({report_mode}, {report_format})",
            }),
        )
        db.add(report)
        db.flush()
        db.refresh(report)
        return _report_to_response(report)


def get_report_by_id(report_id: str) -> ReportResponse | None:
    with db_session() as db:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report is None:
            return None
        return _report_to_response(report)


def list_versions_for_run(
    test_run_id: str,
    report_mode: str | None = None,
    report_format: str | None = None,
) -> list[ReportVersionInfo]:
    with db_session() as db:
        query = db.query(Report).filter(Report.test_run_id == test_run_id)
        if report_mode:
            query = query.filter(Report.report_mode == report_mode)
        if report_format:
            query = query.filter(Report.report_format == report_format)
        reports = query.order_by(Report.created_at.asc()).all()
        return [
            ReportVersionInfo(
                test_run_id=r.test_run_id,
                report_mode=r.report_mode,
                report_format=r.report_format,
                version=r.version,
                created_at=r.created_at,
            )
            for r in reports
        ]


get_report = get_report_by_id
