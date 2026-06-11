import json
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from src.modules.audit_log.service import write_audit_event
from src.modules.audience_profiles.schemas import CreateAudienceProfileRequest
from src.modules.audience_profiles.service import (
    create_profile as create_audience_profile,
    get_profile as get_audience_profile,
    list_profiles as list_audience_profiles,
)
from src.modules.brand_profiles.schemas import CreateBrandProfileRequest
from src.modules.brand_profiles.service import (
    create_profile as create_brand_profile,
    get_profile as get_brand_profile,
    list_profiles as list_brand_profiles,
)
from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.creative_assets.service import (
    create_asset,
    create_asset_from_file,
    get_asset,
    list_assets,
)
from src.modules.creative_assets.upload import process_upload
from src.modules.report_generator.comparison import compare_test_runs
from src.modules.report_generator.service import generate_report
from src.modules.test_rubrics.service import list_rubrics
from src.modules.test_runs.schemas import CreateTestRunRequest
from src.modules.test_runs.service import (
    create_test_run,
    get_test_run,
    run_test_run,
)
from src.modules.test_runs.service import list_test_runs as _list_test_runs
from src.shared.config.settings import get_settings
from src.shared.errors import AppError

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _ctx(request: Request, **extra) -> dict:
    settings = get_settings()
    base = {
        "local_only": settings.local_only_mode,
        "cloud_blocked": not settings.allow_cloud_llm,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
    }
    base.update(extra)
    return base


def _render(request: Request, name: str, **context):
    return templates.TemplateResponse(request, name, _ctx(request, **context))


def _error(request: Request, message: str):
    return templates.TemplateResponse(request, "error.html", _ctx(request, message=message))


@router.get("/static/styles.css", include_in_schema=False)
def serve_css():
    return FileResponse(str(STATIC_DIR / "styles.css"), media_type="text/css")


@router.get("/", include_in_schema=False)
@router.get("/ui", include_in_schema=False)
def dashboard(request: Request):
    settings = get_settings()
    assets = list_assets()
    brands = list_brand_profiles()
    audiences = list_audience_profiles()
    runs = _list_test_runs()
    recent = sorted(runs, key=lambda r: r.created_at, reverse=True)[:5]
    return _render(
        request, "dashboard.html",
        asset_count=len(assets),
        brand_count=len(brands),
        audience_count=len(audiences),
        run_count=len(runs),
        recent_runs=recent,
    )


# ── Creative Assets ──────────────────────────────────────────────

@router.get("/ui/creative-assets", include_in_schema=False)
def ui_creative_assets_list(request: Request):
    return _render(request, "creative_assets/list.html", assets=list_assets())


@router.get("/ui/creative-assets/new", include_in_schema=False)
def ui_creative_assets_new(request: Request):
    return _render(request, "creative_assets/new.html")


@router.post("/ui/creative-assets", include_in_schema=False)
async def ui_creative_assets_create(
    request: Request,
    title: str = Form(...),
    asset_type: str = Form("text"),
    text_content: str | None = Form(None),
    file: UploadFile | None = File(None),
    metadata: str | None = Form(None),
):
    try:
        meta = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        return _render(request, "creative_assets/new.html", error="Invalid JSON in metadata field.")

    try:
        if asset_type == "file" and file and file.filename:
            content = await file.read()
            try:
                result = process_upload(
                    filename=file.filename,
                    content=content,
                    content_type=file.content_type or "application/octet-stream",
                )
            except AppError as e:
                return _render(request, "creative_assets/new.html", error=e.message)

            display_title = title or result["original_filename"]
            asset = create_asset_from_file(
                title=display_title,
                asset_type=result["asset_type"],
                file_path=result["file_path"],
                original_filename=result["original_filename"],
                mime_type=result["mime_type"],
                file_size_bytes=result["file_size_bytes"],
                extracted_text=result["extracted_text"],
                metadata={**meta, **result.get("parser_metadata", {}), "warnings": result.get("warnings", [])},
            )
            write_audit_event("creative_file_uploaded", "creative_asset", asset.id, {
                "title": asset.title,
                "original_filename": result["original_filename"],
            })
        else:
            if not text_content:
                return _render(request, "creative_assets/new.html", error="Text content is required for text assets.")
            asset = create_asset(
                CreateCreativeAssetRequest(
                    title=title,
                    asset_type="text",
                    text_content=text_content,
                    metadata=meta,
                )
            )
            write_audit_event("creative_asset_created", "creative_asset", asset.id, {"title": asset.title})
    except AppError as e:
        return _render(request, "creative_assets/new.html", error=e.message)

    return RedirectResponse(url=f"/ui/creative-assets/{asset.id}", status_code=303)


@router.get("/ui/creative-assets/{asset_id}", include_in_schema=False)
def ui_creative_assets_detail(request: Request, asset_id: str):
    asset = get_asset(asset_id)
    if asset is None:
        return _error(request, f"Creative asset not found: {asset_id}")
    return _render(request, "creative_assets/detail.html", asset=asset)


# ── Brand Profiles ────────────────────────────────────────────────

@router.get("/ui/brand-profiles", include_in_schema=False)
def ui_brand_profiles_list(request: Request):
    return _render(request, "brand_profiles/list.html", profiles=list_brand_profiles())


@router.get("/ui/brand-profiles/new", include_in_schema=False)
def ui_brand_profiles_new(request: Request):
    return _render(request, "brand_profiles/new.html")


@router.post("/ui/brand-profiles", include_in_schema=False)
def ui_brand_profiles_create(
    request: Request,
    name: str = Form(...),
    tone_of_voice: str | None = Form(None),
    target_audience: str | None = Form(None),
    restrictions: str | None = Form(None),
    claims_policy: str | None = Form(None),
):
    try:
        profile = create_brand_profile(
            CreateBrandProfileRequest(
                name=name,
                tone_of_voice=tone_of_voice,
                target_audience=target_audience,
                restrictions=restrictions,
                claims_policy=claims_policy,
            )
        )
    except AppError as e:
        return _render(request, "brand_profiles/new.html", error=e.message)
    return RedirectResponse(url=f"/ui/brand-profiles/{profile.id}", status_code=303)


@router.get("/ui/brand-profiles/{profile_id}", include_in_schema=False)
def ui_brand_profiles_detail(request: Request, profile_id: str):
    profile = get_brand_profile(profile_id)
    if profile is None:
        return _error(request, f"Brand profile not found: {profile_id}")
    return _render(request, "brand_profiles/detail.html", profile=profile)


# ── Audience Profiles ──────────────────────────────────────────────

@router.get("/ui/audience-profiles", include_in_schema=False)
def ui_audience_profiles_list(request: Request):
    return _render(request, "audience_profiles/list.html", profiles=list_audience_profiles())


@router.get("/ui/audience-profiles/new", include_in_schema=False)
def ui_audience_profiles_new(request: Request):
    return _render(request, "audience_profiles/new.html")


@router.post("/ui/audience-profiles", include_in_schema=False)
def ui_audience_profiles_create(
    request: Request,
    name: str = Form(...),
    segment_description: str = Form(...),
    pains: str | None = Form(None),
    motivations: str | None = Form(None),
    objections: str | None = Form(None),
):
    try:
        profile = create_audience_profile(
            CreateAudienceProfileRequest(
                name=name,
                segment_description=segment_description,
                pains=pains,
                motivations=motivations,
                objections=objections,
            )
        )
    except AppError as e:
        return _render(request, "audience_profiles/new.html", error=e.message)
    return RedirectResponse(url=f"/ui/audience-profiles/{profile.id}", status_code=303)


@router.get("/ui/audience-profiles/{profile_id}", include_in_schema=False)
def ui_audience_profiles_detail(request: Request, profile_id: str):
    profile = get_audience_profile(profile_id)
    if profile is None:
        return _error(request, f"Audience profile not found: {profile_id}")
    return _render(request, "audience_profiles/detail.html", profile=profile)


# ── Test Runs ──────────────────────────────────────────────────────

@router.get("/ui/test-runs", include_in_schema=False)
def ui_test_runs_list(request: Request):
    return _render(request, "test_runs/list.html", runs=_list_test_runs())


@router.get("/ui/test-runs/new", include_in_schema=False)
def ui_test_runs_new(request: Request):
    return _render(
        request, "test_runs/new.html",
        assets=list_assets(),
        brand_profiles=list_brand_profiles(),
        audience_profiles=list_audience_profiles(),
        rubrics=list_rubrics(),
    )


@router.post("/ui/test-runs", include_in_schema=False)
def ui_test_runs_create(
    request: Request,
    creative_asset_id: str = Form(...),
    brand_profile_id: str | None = Form(None),
    audience_profile_ids: list[str] = Form([]),
    rubric_id: str | None = Form(None),
    input_context: str | None = Form(None),
):
    ctx = {}
    if input_context:
        try:
            ctx = json.loads(input_context)
        except json.JSONDecodeError:
            return _render(
                request, "test_runs/new.html",
                error="Invalid JSON in input context.",
                assets=list_assets(),
                brand_profiles=list_brand_profiles(),
                audience_profiles=list_audience_profiles(),
                rubrics=list_rubrics(),
            )

    if not audience_profile_ids:
        audience_profile_ids = []

    try:
        run = create_test_run(
            CreateTestRunRequest(
                creative_asset_id=creative_asset_id,
                brand_profile_id=brand_profile_id or None,
                audience_profile_ids=audience_profile_ids,
                rubric_id=rubric_id or None,
                input_context=ctx,
            )
        )
    except AppError as e:
        return _render(
            request, "test_runs/new.html",
            error=e.message,
            assets=list_assets(),
            brand_profiles=list_brand_profiles(),
            audience_profiles=list_audience_profiles(),
            rubrics=list_rubrics(),
        )

    return RedirectResponse(url=f"/ui/test-runs/{run.id}", status_code=303)


@router.get("/ui/test-runs/{run_id}", include_in_schema=False)
def ui_test_runs_detail(request: Request, run_id: str):
    run = get_test_run(run_id)
    if run is None:
        return _error(request, f"Test run not found: {run_id}")
    return _render(request, "test_runs/detail.html", run=run)


@router.post("/ui/test-runs/{run_id}/run", include_in_schema=False)
def ui_test_runs_run(request: Request, run_id: str):
    run = get_test_run(run_id)
    if run is None:
        return _error(request, f"Test run not found: {run_id}")

    try:
        run_test_run(run_id)
    except (AppError, ValueError, Exception) as e:
        return _render(request, "test_runs/detail.html", run=get_test_run(run_id), error=str(e))

    return RedirectResponse(url=f"/ui/test-runs/{run_id}", status_code=303)


# ── Reports ────────────────────────────────────────────────────────

@router.get("/ui/reports/{run_id}", include_in_schema=False)
def ui_reports_detail(request: Request, run_id: str):
    report = generate_report(run_id, report_mode="internal", report_format="json")
    if report is None:
        return _error(request, f"Report not available for test run: {run_id}")
    return _render(request, "reports/detail.html", report=report)


# ── A/B Comparison ─────────────────────────────────────────────────

@router.get("/ui/compare", include_in_schema=False)
def ui_compare_form(request: Request):
    all_runs = _list_test_runs()
    completed = [r for r in all_runs if r.status == "completed"]
    return _render(request, "reports/compare.html", completed_runs=completed)


@router.post("/ui/compare", include_in_schema=False)
def ui_compare_result(
    request: Request,
    test_run_ids: list[str] = Form(...),
    report_mode: str = Form("internal"),
):
    try:
        result = compare_test_runs(test_run_ids, report_mode)
    except ValueError as e:
        all_runs = _list_test_runs()
        completed = [r for r in all_runs if r.status == "completed"]
        return _render(request, "reports/compare.html", error=str(e), completed_runs=completed)

    return _render(request, "reports/comparison_result.html", result=result)
