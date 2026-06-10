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

    scorecard = [
        ScorecardItem(criterion=f.criterion, score=f.score)
        for f in run.findings
    ]

    risks = []
    for f in run.findings:
        if f.criterion == "negativity_risk" and f.score > 5:
            risks.append(RiskItem(risk="Negative perception risk detected", severity="medium"))
        if f.score < 5:
            risks.append(RiskItem(risk=f"Low score on '{f.criterion}'", severity="low"))

    recommendations = []
    for f in run.findings:
        if f.score < 6:
            recommendations.append(
                RecommendationItem(
                    recommendation=f"Improve '{f.criterion}': {f.explanation}",
                    priority="high" if f.score < 4 else "medium",
                )
            )

    avg_score = sum(f.score for f in run.findings) / max(len(run.findings), 1)

    if avg_score >= 7.5:
        final_rec = "show_to_client"
    elif avg_score >= 5.0:
        final_rec = "revise"
    else:
        final_rec = "reject"

    summary = (
        f"Test run {test_run_id} completed with average score {avg_score:.1f}/10. "
        f"Recommendation: {final_rec.replace('_', ' ')}."
    )

    report_markdown_lines = [
        f"# Creative Pre-Test Report",
        f"**Test Run ID:** {test_run_id}",
        f"**Average Score:** {avg_score:.1f}/10",
        f"**Final Recommendation:** {final_rec.replace('_', ' ')}",
        "",
        "## Scorecard",
    ]
    for f in run.findings:
        report_markdown_lines.append(f"- {f.criterion}: {f.score}/10")
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
