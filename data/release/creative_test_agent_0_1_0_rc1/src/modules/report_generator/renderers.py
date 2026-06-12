from src.modules.report_generator.schemas import RecommendationItem, ReportAudienceReaction, RiskItem, ScorecardItem
from src.modules.test_runs.schemas import BrandbookCompliance, TestRunResponse


def _build_compliance_md(compliance: BrandbookCompliance | None, mode: str) -> list[str]:
    if not compliance or compliance.compliance_score >= 10.0 and not compliance.violations:
        return []
    lines = ["## Brandbook Compliance", ""]
    if mode == "internal":
        lines.append(f"- **Verdict:** {compliance.overall_verdict.replace('_', ' ').title()}")
        lines.append(f"- **Compliance Score:** {compliance.compliance_score:.1f}/10")
        lines.append("")
        if compliance.violations:
            lines.append("### Violations")
            for v in compliance.violations:
                sev = v.severity.upper() if v.severity else "INFO"
                lines.append(f"- **[{sev}]** {v.rule}: {v.details}")
            lines.append("")
        if compliance.recommendations:
            lines.append("### Recommendations")
            for r in compliance.recommendations:
                lines.append(f"- {r}")
            lines.append("")
    else:
        label = "Passed" if compliance.overall_verdict == "compliant" else "Needs Attention"
        lines.append(f"**Brand alignment: {label}**")
        if compliance.overall_verdict != "compliant":
            lines.append("")
            lines.append("The creative may require adjustments to better align with brand guidelines.")
        lines.append("")
    return lines


def _build_compliance_html(compliance: BrandbookCompliance | None, mode: str) -> str:
    if not compliance or compliance.compliance_score >= 10.0 and not compliance.violations:
        return ""
    if mode == "internal":
        violations_html = ""
        if compliance.violations:
            v_rows = "".join(
                f'<tr><td>{_html_escape(v.rule)}</td>'
                f'<td><span class="severity-{v.severity}">{_html_escape(v.severity.upper())}</span></td>'
                f'<td>{_html_escape(v.details)}</td></tr>'
                for v in compliance.violations
            )
            violations_html = f"""
            <h3>Violations</h3>
            <table>
              <tr><th>Rule</th><th>Severity</th><th>Details</th></tr>
              {v_rows}
            </table>
            """
        recs_html = ""
        if compliance.recommendations:
            recs_html = '<h3>Recommendations</h3><ul>'
            for r in compliance.recommendations:
                recs_html += f"<li>{_html_escape(r)}</li>"
            recs_html += "</ul>"
        score_color = "green" if compliance.compliance_score >= 7 else "orange" if compliance.compliance_score >= 4 else "red"
        return f"""
        <h2>Brandbook Compliance</h2>
        <p><strong>Verdict:</strong> {compliance.overall_verdict.replace('_', ' ').title()}</p>
        <p><strong>Compliance Score:</strong> <span style="color:{score_color}">{compliance.compliance_score:.1f}/10</span></p>
        {violations_html}
        {recs_html}
        """
    else:
        label = "Passed" if compliance.overall_verdict == "compliant" else "Needs Attention"
        extra = ""
        if compliance.overall_verdict != "compliant":
            extra = "<p>The creative may require adjustments to better align with brand guidelines.</p>"
        return f"""
        <h2>Brand Alignment</h2>
        <p><strong>Brand alignment: {label}</strong></p>
        {extra}
        """


def _mode_label(mode: str) -> str:
    return "Internal Report" if mode == "internal" else "Client-Facing Report"


def _build_visual_notes_md(notes: str, mode: str) -> list[str]:
    if not notes:
        return []
    if mode == "client_facing":
        notes = notes.replace("stub", "limited").replace("Stub", "Limited")
    return ["## Visual Analysis Notes", notes, ""]


def build_markdown_report(
    title: str,
    run: TestRunResponse,
    mode: str,
    summary: str,
    avg_score: float,
    scorecard: list[ScorecardItem],
    risks: list[RiskItem],
    recommendations: list[RecommendationItem],
    final_rec: str,
    main_message: str,
    audience_reactions: list[ReportAudienceReaction],
    strengths: list[str],
    improvements: list[str],
    visual_notes: str = "",
) -> str:
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append(f"*{_mode_label(mode)}*")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append(summary)
    lines.append("")

    lines.append("## Creative Overview")
    lines.append(f"- **Test Run ID:** {run.id}")
    lines.append(f"- **Asset ID:** {run.creative_asset_id}")
    lines.append(f"- **Status:** {run.status}")
    if run.completed_at:
        lines.append(f"- **Completed:** {run.completed_at.isoformat()}")
    lines.append("")

    lines.append("## Main Message")
    if main_message:
        lines.append(main_message)
    else:
        lines.append("No main message extracted.")
    lines.append("")

    lines.extend(_build_visual_notes_md(visual_notes, mode))

    lines.append("## Audience Reactions")
    if audience_reactions:
        for a in audience_reactions:
            lines.append(f"### {a.segment_name or a.audience_profile_id}")
            lines.append(f"- **Reaction:** {a.reaction}")
            lines.append(f"- **Engagement probability:** {a.engagement_probability:.0%}")
            if a.positive_triggers:
                lines.append(f"- **Positive triggers:** {', '.join(a.positive_triggers)}")
            if a.objections:
                lines.append(f"- **Objections:** {', '.join(a.objections)}")
            lines.append("")
    else:
        lines.append("No audience reaction data available.")
        lines.append("")

    lines.extend(_build_compliance_md(run.brandbook_compliance, mode))

    lines.append("## Scorecard")
    lines.append(f"| Criterion | Score |")
    lines.append(f"|---|---|")
    for s in scorecard:
        lines.append(f"| {s.criterion} | {s.score:.0f}/10 |")
    lines.append("")
    lines.append(f"**Average score: {avg_score:.1f}/10**")
    lines.append("")

    lines.append("## Brand Safety and Risks")
    if risks:
        for r in risks:
            lines.append(f"- **[{r.severity.upper()}]** {r.risk}")
    else:
        lines.append("No significant risks identified.")
    lines.append("")

    lines.append("## Recommendations")
    if recommendations:
        for r in recommendations:
            lines.append(f"- **[{r.priority.upper()}]** {r.recommendation}")
    else:
        lines.append("No specific recommendations at this time.")
    lines.append("")

    lines.append("## Final Recommendation")
    lines.append(f"**{final_rec.upper()}**")
    lines.append("")

    if mode == "internal":
        if strengths:
            lines.append("### Top Strengths")
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")
        if improvements:
            lines.append("### Key Improvement Areas")
            for imp in improvements:
                lines.append(f"- {imp}")
            lines.append("")

    lines.append("## Appendix: Test Context")
    lines.append(f"- **Rubric ID:** {run.rubric_id or 'default'}")
    lines.append(f"- **Audience profiles:** {', '.join(run.audience_profile_ids) or 'none'}")
    lines.append(f"- **Brand profile:** {run.brand_profile_id or 'none'}")
    if mode == "internal":
        lines.append(f"- **Input context keys:** {', '.join(run.input_context.keys()) if run.input_context else 'none'}")
    lines.append("")

    return "\n".join(lines)


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_html_report(
    title: str,
    run: TestRunResponse,
    mode: str,
    summary: str,
    avg_score: float,
    scorecard: list[ScorecardItem],
    risks: list[RiskItem],
    recommendations: list[RecommendationItem],
    final_rec: str,
    main_message: str,
    audience_reactions: list[ReportAudienceReaction],
    strengths: list[str],
    improvements: list[str],
    visual_notes: str = "",
) -> str:
    compliance_html = _build_compliance_html(run.brandbook_compliance, mode)
    sc_rows = "".join(
        f"<tr><td>{_html_escape(s.criterion)}</td><td>{s.score:.0f}/10</td></tr>"
        for s in scorecard
    )

    risk_blocks = ""
    if risks:
        for r in risks:
            severity_class = "risk-high" if r.severity.lower() == "high" else "risk-medium" if r.severity.lower() == "medium" else "risk-low"
            risk_blocks += f'<div class="risk-item {severity_class}"><strong>[{_html_escape(r.severity.upper())}]</strong> {_html_escape(r.risk)}</div>\n'
    else:
        risk_blocks = "<p>No significant risks identified.</p>"

    rec_blocks = ""
    if recommendations:
        for r in recommendations:
            priority_class = "rec-high" if r.priority.lower() == "high" else "rec-medium"
            rec_blocks += f'<div class="rec-item {priority_class}"><strong>[{_html_escape(r.priority.upper())}]</strong> {_html_escape(r.recommendation)}</div>\n'
    else:
        rec_blocks = "<p>No specific recommendations at this time.</p>"

    audience_blocks = ""
    if audience_reactions:
        for a in audience_reactions:
            triggers = ", ".join(_html_escape(t) for t in a.positive_triggers) if a.positive_triggers else "None"
            objections = ", ".join(_html_escape(o) for o in a.objections) if a.objections else "None"
            audience_blocks += f"""
            <div class="audience-section">
              <h3>{_html_escape(a.segment_name or a.audience_profile_id)}</h3>
              <p><strong>Reaction:</strong> {_html_escape(a.reaction)}</p>
              <p><strong>Engagement probability:</strong> {a.engagement_probability:.0%}</p>
              <p><strong>Positive triggers:</strong> {triggers}</p>
              <p><strong>Objections:</strong> {objections}</p>
            </div>
            """
    else:
        audience_blocks = "<p>No audience reaction data available.</p>"

    internal_section = ""
    if mode == "internal" and strengths:
        internal_section += '<h2>Top Strengths</h2><ul>'
        for s in strengths:
            internal_section += f"<li>{_html_escape(s)}</li>"
        internal_section += "</ul>"
    if mode == "internal" and improvements:
        internal_section += '<h2>Key Improvement Areas</h2><ul>'
        for imp in improvements:
            internal_section += f"<li>{_html_escape(imp)}</li>"
        internal_section += "</ul>"

    main_msg_html = _html_escape(main_message) if main_message else "<p>No main message extracted.</p>"

    visual_html = ""
    if visual_notes:
        display_notes = visual_notes
        if mode == "client_facing":
            display_notes = display_notes.replace("stub", "limited").replace("Stub", "Limited")
        visual_html = f'<h2>Visual Analysis Notes</h2><div class="visual-notes">{_html_escape(display_notes)}</div>\n'

    mode_tag = "Internal Report" if mode == "internal" else "Client-Facing Report"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html_escape(title)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; color: #1a1a1a; line-height: 1.6; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
  h2 {{ margin-top: 2rem; color: #2c3e50; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; }}
  h3 {{ margin-top: 1.5rem; color: #34495e; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
  th {{ background-color: #f5f5f5; }}
  .risk-item {{ padding: 0.5rem; margin: 0.3rem 0; border-radius: 4px; }}
  .risk-high {{ background-color: #ffeaea; border-left: 4px solid #e74c3c; }}
  .risk-medium {{ background-color: #fff8e1; border-left: 4px solid #f39c12; }}
  .risk-low {{ background-color: #e8f5e9; border-left: 4px solid #27ae60; }}
  .rec-item {{ padding: 0.5rem; margin: 0.3rem 0; border-radius: 4px; }}
  .rec-high {{ background-color: #ffeaea; border-left: 4px solid #e74c3c; }}
  .rec-medium {{ background-color: #fff8e1; border-left: 4px solid #f39c12; }}
  .final-rec {{ background-color: #eaf7ea; border: 2px solid #27ae60; border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center; font-weight: bold; font-size: 1.2rem; }}
  .mode-badge {{ display: inline-block; background-color: #3498db; color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem; }}
  .audience-section {{ background-color: #f9f9f9; border-radius: 6px; padding: 0.8rem; margin: 0.5rem 0; }}
  .audience-section h3 {{ margin-top: 0; }}
</style>
</head>
<body>
<span class="mode-badge">{mode_tag}</span>
<h1>{_html_escape(title)}</h1>

<h2>Executive Summary</h2>
<p>{_html_escape(summary)}</p>

<h2>Creative Overview</h2>
<table>
  <tr><th>Field</th><th>Value</th></tr>
  <tr><td>Test Run ID</td><td>{_html_escape(run.id)}</td></tr>
  <tr><td>Asset ID</td><td>{_html_escape(run.creative_asset_id)}</td></tr>
  <tr><td>Status</td><td>{_html_escape(run.status)}</td></tr>
  <tr><td>Completed</td><td>{run.completed_at.isoformat() if run.completed_at else 'N/A'}</td></tr>
</table>

<h2>Main Message</h2>
{main_msg_html}

{visual_html}
<h2>Audience Reactions</h2>
{audience_blocks}

{compliance_html}

<h2>Scorecard</h2>
<table>
  <tr><th>Criterion</th><th>Score</th></tr>
  {sc_rows}
</table>
<p><strong>Average score: {avg_score:.1f}/10</strong></p>

<h2>Brand Safety and Risks</h2>
{risk_blocks}

<h2>Recommendations</h2>
{rec_blocks}

<h2>Final Recommendation</h2>
<div class="final-rec">{_html_escape(final_rec.upper())}</div>

{internal_section}

<h2>Appendix: Test Context</h2>
<table>
  <tr><td>Rubric ID</td><td>{_html_escape(run.rubric_id or 'default')}</td></tr>
  <tr><td>Audience profiles</td><td>{_html_escape(', '.join(run.audience_profile_ids) or 'none')}</td></tr>
  <tr><td>Brand profile</td><td>{_html_escape(run.brand_profile_id or 'none')}</td></tr>
  {'<tr><td>Input context keys</td><td>' + _html_escape(', '.join(run.input_context.keys()) if run.input_context else 'none') + '</td></tr>' if mode == 'internal' else ''}
</table>
</body>
</html>"""
