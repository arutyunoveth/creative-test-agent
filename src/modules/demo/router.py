"""Guided demo UI routes."""

import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.modules.demo.status import get_demo_status
from src.modules.ui.router import _ctx, templates
from src.modules.audit_log.service import write_audit_event

router = APIRouter()

DEMO_STEPS = [
    {"id": "load_profile", "title": "demo.load_profile.title", "description": "demo.load_profile.description", "link": None},
    {"id": "open_client", "title": "demo.open_client.title", "description": "demo.open_client.description", "link": "/ui/clients"},
    {"id": "open_project", "title": "demo.open_project.title", "description": "demo.open_project.description", "link": "/ui/projects"},
    {"id": "upload_brandbook", "title": "demo.upload_brandbook.title", "description": "demo.upload_brandbook.description", "link": "/ui/brandbooks"},
    {"id": "review_creatives", "title": "demo.review_creatives.title", "description": "demo.review_creatives.description", "link": "/ui/creative-assets"},
    {"id": "run_batch", "title": "demo.run_batch.title", "description": "demo.run_batch.description", "link": "/ui/batches"},
    {"id": "campaign_summary", "title": "demo.campaign_summary.title", "description": "demo.campaign_summary.description", "link": None},
    {"id": "export_report", "title": "demo.export_report.title", "description": "demo.export_report.description", "link": "/ui/exports"},
    {"id": "create_review", "title": "demo.create_review.title", "description": "demo.create_review.description", "link": "/ui/reviews"},
    {"id": "save_knowledge", "title": "demo.save_knowledge.title", "description": "demo.save_knowledge.description", "link": "/ui/knowledge-base"},
]


def _step_status(step_id: str, status: dict) -> str:
    if step_id == "load_profile":
        return "completed" if status.get("profile_loaded") else "not_started"
    if step_id == "open_client":
        return "completed" if status.get("client_exists") else "missing"
    if step_id == "open_project":
        return "completed" if status.get("project_exists") else "missing"
    if step_id == "upload_brandbook":
        return "completed" if status.get("brandbooks_count", 0) > 0 else "available" if status.get("client_exists") else "missing"
    if step_id == "review_creatives":
        return "completed" if status.get("creatives_count", 0) > 0 else "available" if status.get("project_exists") else "missing"
    if step_id == "run_batch":
        return "completed" if status.get("batch_completed") else "available" if status.get("creatives_count", 0) > 0 else "missing"
    if step_id == "campaign_summary":
        return "completed" if status.get("reports_count", 0) > 0 else "available" if status.get("batch_completed") else "missing"
    if step_id == "export_report":
        return "completed" if status.get("exports_count", 0) > 0 else "available" if status.get("reports_count", 0) > 0 else "missing"
    if step_id == "create_review":
        return "completed" if status.get("reviews_count", 0) > 0 else "available" if status.get("reports_count", 0) > 0 else "missing"
    if step_id == "save_knowledge":
        return "completed" if status.get("knowledge_items_count", 0) > 0 else "available"
    return "not_started"


def _render(request: Request, name: str, **context):
    return templates.TemplateResponse(request, name, _ctx(request, **context))


@router.get("/ui/demo", include_in_schema=False)
def guided_demo(request: Request):
    status = get_demo_status()
    steps = []
    for step in DEMO_STEPS:
        steps.append({**step, "status": _step_status(step["id"], status)})
    completed = sum(1 for s in steps if s["status"] == "completed")
    total = len(steps)
    return _render(request, "demo/index.html", status=status, steps=steps, completed=completed, total=total)


@router.get("/ui/demo/start", include_in_schema=False)
def demo_start(request: Request):
    try:
        cfg = Path(__file__).parent.parent.parent.parent / "config" / "pilot_profiles" / "novabank_demo.json"
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent.parent.parent / "scripts" / "load_pilot_profile.py"), str(cfg)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=result.stderr)
        write_audit_event("demo_profile_loaded", "demo", "novabank", {})
        return RedirectResponse(url="/ui/demo", status_code=303)
    except Exception as e:
        return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=str(e))


@router.get("/ui/demo/steps", include_in_schema=False)
def demo_steps(request: Request):
    status = get_demo_status()
    steps = []
    for step in DEMO_STEPS:
        steps.append({**step, "status": _step_status(step["id"], status)})
    return steps


@router.get("/ui/demo/status", include_in_schema=False)
def demo_status(request: Request):
    return get_demo_status()


@router.post("/ui/demo/load-profile", include_in_schema=False)
def demo_load_profile(request: Request):
    cfg = Path(__file__).parent.parent.parent.parent / "config" / "pilot_profiles" / "novabank_demo.json"
    if not cfg.exists():
        return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error="Demo profile not found")
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent.parent.parent / "scripts" / "load_pilot_profile.py"), str(cfg)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=result.stderr)
        write_audit_event("demo_profile_loaded", "demo", "novabank", {})
        return RedirectResponse(url="/ui/demo", status_code=303)
    except Exception as e:
        return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=str(e))


@router.post("/ui/demo/create-batch", include_in_schema=False)
def demo_create_batch(request: Request):
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent.parent.parent / "scripts" / "run_demo_batch.py")],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=result.stderr)
        return RedirectResponse(url="/ui/demo", status_code=303)
    except Exception as e:
        return _render(request, "demo/index.html", status=get_demo_status(), steps=[], completed=0, total=10, error=str(e))
