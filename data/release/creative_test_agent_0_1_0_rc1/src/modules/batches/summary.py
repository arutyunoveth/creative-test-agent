from src.modules.batches.service import get_batch, list_batch_items
from src.modules.test_runs.service import get_test_run


def build_batch_summary(batch_id: str) -> dict:
    batch = get_batch(batch_id)
    if batch is None:
        return {"batch_id": batch_id, "status": "not_found", "error": "Batch not found"}

    items = list_batch_items(batch_id)
    completed_items = [i for i in items if i.status == "completed"]
    failed_items = [i for i in items if i.status == "failed"]
    skipped_items = [i for i in items if i.status == "skipped"]
    pending_items = [i for i in items if i.status in ("pending", "queued", "running")]

    scores = []
    test_runs = []
    recommendations = []
    all_risks = []
    compliance_summary = {"compliant": 0, "non_compliant": 0, "unknown": 0}
    best_score = -1
    best_item = None

    for item in completed_items:
        score_summary = item.score_summary or {}
        score = score_summary.get("overall_score")
        if score is not None:
            scores.append(score)
            if score > best_score:
                best_score = score
                best_item = item

        if item.test_run_id:
            test_run = get_test_run(item.test_run_id)
            if test_run:
                test_runs.append(test_run)
                if hasattr(test_run, "findings") and test_run.findings:
                    for f in test_run.findings:
                        rec = getattr(f, "recommendation", None) or getattr(f, "explanation", "")
                        if rec:
                            recommendations.append(rec)
                if hasattr(test_run, "risks") and test_run.risks:
                    for r in test_run.risks:
                        all_risks.append({
                            "risk_type": getattr(r, "risk_type", "") or getattr(r, "risk", ""),
                            "level": getattr(r, "level", "") or getattr(r, "severity", ""),
                            "description": getattr(r, "description", "") or getattr(r, "risk", ""),
                        })
                if hasattr(test_run, "brandbook_compliance") and test_run.brandbook_compliance:
                    verdict = test_run.brandbook_compliance.overall_verdict if hasattr(test_run.brandbook_compliance, "overall_verdict") else "unknown"
                    if verdict == "compliant":
                        compliance_summary["compliant"] += 1
                    else:
                        compliance_summary["non_compliant"] += 1
                else:
                    compliance_summary["unknown"] += 1

    avg_score = sum(scores) / len(scores) if scores else None

    risk_counts = {}
    for r in all_risks:
        key = r.get("risk_type", "unknown")
        risk_counts[key] = risk_counts.get(key, 0) + 1
    top_risks = sorted(risk_counts.items(), key=lambda x: -x[1])[:5]

    rec_counts = {}
    for rec in recommendations:
        rec_counts[rec] = rec_counts.get(rec, 0) + 1
    top_recs = sorted(rec_counts.items(), key=lambda x: -x[1])[:5]

    result = {
        "batch_id": batch_id,
        "batch_name": batch.name,
        "status": batch.status,
        "total_items": len(items),
        "completed_items": len(completed_items),
        "failed_items": len(failed_items),
        "skipped_items": len(skipped_items),
        "pending_items": len(pending_items),
        "average_score": round(avg_score, 2) if avg_score is not None else None,
        "best_creative_asset_id": best_item.creative_asset_id if best_item else None,
        "best_test_run_id": best_item.test_run_id if best_item else None,
        "score_summary": {
            "min": round(min(scores), 2) if scores else None,
            "max": round(max(scores), 2) if scores else None,
            "avg": round(avg_score, 2) if avg_score is not None else None,
            "count": len(scores),
        },
        "risk_summary": {
            "total_risks": len(all_risks),
            "top_risks": [{"risk_type": k, "count": v} for k, v in top_risks],
        },
        "brandbook_compliance_summary": compliance_summary,
        "top_recommendations": [{"text": rec, "count": count} for rec, count in top_recs],
        "warnings": [],
    }

    if not completed_items:
        result["warnings"].append("No completed items in batch")
    if failed_items:
        result["warnings"].append(f"{len(failed_items)} item(s) failed")
    if pending_items:
        result["warnings"].append(f"{len(pending_items)} item(s) still pending")

    return result
