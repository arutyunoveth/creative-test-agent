from datetime import datetime, timezone
from uuid import uuid4

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

_store: dict[str, ReportResponse] = {}
_versions: dict[str, list[ReportVersionInfo]] = {}


def _version_key(test_run_id: str, mode: str, fmt: str) -> str:
    return f"{test_run_id}||{mode}||{fmt}"


def _get_next_version(test_run_id: str, mode: str, fmt: str) -> int:
    key = _version_key(test_run_id, mode, fmt)
    existing = _versions.get(key, [])
    return len(existing) + 1


def _record_version(test_run_id: str, mode: str, fmt: str, version: int) -> None:
    key = _version_key(test_run_id, mode, fmt)
    if key not in _versions:
        _versions[key] = []
    _versions[key].append(
        ReportVersionInfo(
            test_run_id=test_run_id,
            report_mode=mode,
            report_format=fmt,
            version=version,
            created_at=datetime.now(timezone.utc),
        )
    )


_VALID_MODES = {"internal", "client_facing"}
_VALID_FORMATS = {"json", "markdown", "html", "pdf_stub"}


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
    }


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

    now = datetime.now(timezone.utc)

    report = ReportResponse(
        id=str(uuid4()),
        test_run_id=test_run_id,
        report_mode=report_mode,
        report_format=report_format,
        version=version,
        title=data["title"],
        summary=data["summary"],
        main_message=data["main_message"],
        audience_reactions=data["audience_reactions"],
        scorecard=data["scorecard"],
        risks=data["risks"],
        recommendations=data["recommendations"],
        final_recommendation=data["final_recommendation"],
        report_markdown=data["report_markdown"],
        report_html=data["report_html"],
        file_path=data["file_path"],
        created_at=now,
        metadata=ReportMetadata(
            generated_at=now.isoformat(),
            version_info=f"v{version} ({report_mode}, {report_format})",
            note="",
        ),
    )

    _store[report.id] = report
    _record_version(test_run_id, report_mode, report_format, version)

    return report


def get_report_by_id(report_id: str) -> ReportResponse | None:
    return _store.get(report_id)


def list_versions_for_run(
    test_run_id: str,
    report_mode: str | None = None,
    report_format: str | None = None,
) -> list[ReportVersionInfo]:
    results: list[ReportVersionInfo] = []
    for key, versions in _versions.items():
        tid, mode, fmt = key.split("||", 2)
        if tid != test_run_id:
            continue
        if report_mode and mode != report_mode:
            continue
        if report_format and fmt != report_format:
            continue
        results.extend(versions)
    results.sort(key=lambda v: v.created_at)
    return results
