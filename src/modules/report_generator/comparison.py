from uuid import uuid4

from src.modules.report_generator.schemas import (
    CompareResponse,
    ScoreDelta,
    VariantSummary,
)
from src.modules.test_runs.service import get_test_run


def compare_test_runs(
    test_run_ids: list[str],
    report_mode: str = "internal",
) -> CompareResponse:
    if len(test_run_ids) < 2:
        raise ValueError("comparison_requires_two_runs")

    runs = []
    for tid in test_run_ids:
        run = get_test_run(tid)
        if run is None:
            raise ValueError(f"test_run_not_found: {tid}")
        if run.status != "completed":
            raise ValueError(f"test_run_not_completed: {tid}")
        if not run.findings and not run.scorecard:
            raise ValueError(f"structured_findings_missing: {tid}")
        runs.append(run)

    score_deltas: list[ScoreDelta] = []

    all_criteria: set[str] = set()
    for run in runs:
        for f in run.findings or []:
            all_criteria.add(f.criterion)

    for criterion in sorted(all_criteria):
        scores: dict[str, float] = {}
        for run in runs:
            found = [f for f in (run.findings or []) if f.criterion == criterion]
            scores[run.id] = found[0].score if found else 0.0

        score_values = list(scores.values())
        diff = max(score_values) - min(score_values)
        if diff < 0.5:
            diff_summary = f"Scores are close (difference {diff:.1f})"
        else:
            best_id = max(scores, key=scores.get)
            diff_summary = f"{best_id[:8]}... leads by {diff:.1f} points"

        score_deltas.append(
            ScoreDelta(
                criterion=criterion,
                scores=scores,
                difference_summary=diff_summary,
            )
        )

    variant_summaries: list[VariantSummary] = []
    for run in runs:
        strengths = []
        weaknesses = []
        for f in run.findings or []:
            if f.score >= 7:
                strengths.append(f"{f.criterion} ({f.score}/10): {f.explanation}")
            elif f.score < 6:
                weaknesses.append(f"{f.criterion} ({f.score}/10): {f.explanation}")
        variant_summaries.append(
            VariantSummary(
                test_run_id=run.id,
                summary=run.summary or "No summary available.",
                strengths=strengths or ["No notable strengths detected."],
                weaknesses=weaknesses or ["No notable weaknesses detected."],
            )
        )

    run_scores: list[tuple[str, float]] = []
    for run in runs:
        avg = run.overall_score or (
            sum(f.score for f in (run.findings or [])) / max(len(run.findings or []), 1)
            if run.findings
            else 0.0
        )
        high_risk_count = sum(1 for r in (run.risks or []) if r.level == "high")
        penalty = high_risk_count * 0.5
        effective_score = avg - penalty
        run_scores.append((run.id, effective_score, avg, high_risk_count))

    run_scores.sort(key=lambda x: x[1], reverse=True)

    if len(run_scores) >= 2:
        score_diff = abs(run_scores[0][1] - run_scores[1][1])
        if score_diff < 0.5:
            winner = "no_clear_winner"
            rationale = (
                f"Average scores are very close (difference {score_diff:.1f}). "
                f"Consider revising both variants or running additional tests."
            )
            recommendation = "revise_both"
        else:
            best = run_scores[0]
            winner = best[0]
            rationale = (
                f"Variant {best[0][:8]}... scores highest with effective score {best[1]:.1f}/10 "
                f"(average {best[2]:.1f}/10, {best[3]} high-risk penalties)."
            )
            recommendation = f"select_variant_{best[0][:8]}..."
    else:
        winner = "insufficient_data"
        rationale = "Only one valid test run available."
        recommendation = "insufficient_data"

    return CompareResponse(
        comparison_id=str(uuid4()),
        test_run_ids=test_run_ids,
        report_mode=report_mode,
        winner=winner,
        rationale=rationale,
        score_deltas=score_deltas,
        variant_summaries=variant_summaries,
        recommendation=recommendation,
    )
