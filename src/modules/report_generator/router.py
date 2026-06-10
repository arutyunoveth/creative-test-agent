from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event
from src.modules.report_generator.schemas import ReportResponse
from src.modules.report_generator.service import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{test_run_id}", response_model=ReportResponse)
def get_report(test_run_id: str):
    report = generate_report(test_run_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not available")
    write_audit_event("report_generated", "report", test_run_id, {"final_recommendation": report.final_recommendation})
    return report
