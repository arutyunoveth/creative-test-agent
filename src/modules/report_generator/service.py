from src.modules.report_generator.schemas import (
    RecommendationItem,
    ReportResponse,
    RiskItem,
    ScorecardItem,
)
from src.modules.test_runs.service import get_test_run


def generate_report(test_run_id: str) -> ReportResponse | None:
    run = get_test_run(test_run_id)
    if run is None:
        return None

    if run.status != "completed":
        return None

    scorecard = []
    if run.scorecard:
        for s in run.scorecard:
            scorecard.append(ScorecardItem(criterion=s.criterion, score=s.score))
    else:
        scorecard = [
            ScorecardItem(criterion=f.criterion, score=f.score)
            for f in run.findings
        ]

    risks = []
    for r in run.risks:
        risks.append(RiskItem(risk=r.description or r.risk_type, severity=r.level))

    recommendations = []
    for s in run.scorecard:
        if s.score < 6 and s.recommendation:
            recommendations.append(
                RecommendationItem(
                    recommendation=s.recommendation,
                    priority="high" if s.score < 4 else "medium",
                )
            )

    if not recommendations:
        for f in run.findings:
            if f.score < 6:
                recommendations.append(
                    RecommendationItem(
                        recommendation=f"Improve '{f.criterion}': {f.explanation}",
                        priority="high" if f.score < 4 else "medium",
                    )
                )

    final_rec = run.final_recommendation or "revise"
    avg_score = run.overall_score or (
        sum(f.score for f in run.findings) / max(len(run.findings), 1) if run.findings else 0
    )

    base_summary = run.summary or f"Test run {test_run_id} completed."
    summary = (
        f"{base_summary} "
        f"Average score: {avg_score:.1f}/10. "
        f"Recommendation: {final_rec.replace('_', ' ')}."
    )

    report_markdown_lines = [
        f"# Creative Pre-Test Report",
        f"**Test Run ID:** {test_run_id}",
        f"**Average Score:** {avg_score:.1f}/10",
        f"**Final Recommendation:** {final_rec.replace('_', ' ')}",
        "",
        "## Summary",
        run.summary or "No summary available.",
        "",
        "## Scorecard",
    ]
    for s in scorecard:
        report_markdown_lines.append(f"- {s.criterion}: {s.score}/10")
    report_markdown_lines.append("")
    if risks:
        report_markdown_lines.append("## Risks")
        for r in risks:
            report_markdown_lines.append(f"- [{r.severity}] {r.risk}")
        report_markdown_lines.append("")
    if recommendations:
        report_markdown_lines.append("## Recommendations")
        for r in recommendations:
            report_markdown_lines.append(f"- [{r.priority}] {r.recommendation}")

    return ReportResponse(
        test_run_id=test_run_id,
        summary=summary,
        scorecard=scorecard,
        risks=risks,
        recommendations=recommendations,
        final_recommendation=final_rec,
        report_markdown="\n".join(report_markdown_lines),
    )
