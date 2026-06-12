def extract_recommendations_from_report(report) -> list[dict]:
    recommendations = []
    if not report:
        return recommendations

    if hasattr(report, "recommendations") and report.recommendations:
        for rec in report.recommendations:
            rec_dict = rec if isinstance(rec, dict) else rec.model_dump() if hasattr(rec, "model_dump") else {}
            recommendations.append({
                "type": "recommendation",
                "category": "general",
                "description": rec_dict.get("recommendation", str(rec)),
                "priority": rec_dict.get("priority", "medium"),
                "rationale": "",
            })

    if hasattr(report, "risks") and report.risks:
        for risk in report.risks:
            risk_dict = risk if isinstance(risk, dict) else risk.model_dump() if hasattr(risk, "model_dump") else {}
            recommendations.append({
                "type": "risk",
                "category": "risk",
                "description": risk_dict.get("risk", str(risk)),
                "priority": risk_dict.get("severity", "medium"),
                "rationale": "",
            })

    if hasattr(report, "summary") and report.summary:
        recommendations.append({
            "type": "summary_note",
            "category": "summary",
            "description": report.summary[:500] if len(report.summary) > 500 else report.summary,
            "priority": "medium",
            "rationale": "Extracted from report summary",
        })

    return recommendations


def extract_changes_from_report(report) -> list[dict]:
    changes = []
    recommendations = extract_recommendations_from_report(report)
    for rec in recommendations:
        changes.append({
            "action": "address_risk" if rec["type"] == "risk" else "implement_recommendation",
            "target": rec["category"],
            "description": rec["description"],
            "priority": rec["priority"],
            "rationale": rec["rationale"],
        })
    return changes


def extract_concerns_from_report(report) -> str:
    parts = []
    if hasattr(report, "risks") and report.risks:
        for r in report.risks:
            r_dict = r if isinstance(r, dict) else r.model_dump() if hasattr(r, "model_dump") else {}
            desc = r_dict.get("risk", "")
            severity = r_dict.get("severity", "medium")
            if desc:
                parts.append(f"[{severity.upper()}] {desc}")
    return "\n".join(parts) if parts else ""
