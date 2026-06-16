import json
from pathlib import Path

from fastapi import APIRouter, File, Form, Query, Request, UploadFile
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
from src.modules.clients.schemas import CreateClientRequest
from src.modules.projects.schemas import CreateProjectRequest
from src.modules.brand_profiles.service import (
    create_profile as create_brand_profile,
    get_profile as get_brand_profile,
    list_profiles as list_brand_profiles,
)
from src.modules.clients.service import (
    create_client,
    get_client,
    list_clients,
)
from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.creative_assets.service import (
    create_asset,
    create_asset_from_file,
    get_asset,
    list_assets,
)
from src.modules.creative_assets.upload import process_upload
from src.modules.projects.service import (
    create_project,
    get_project,
    list_projects,
)
from src.modules.projects.history import get_project_history
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
from src.shared.db.session import check_db_connection, get_database_url
from src.shared.errors import AppError
from src.shared.i18n import get_translator
from src.shared.version import get_version_info
from src.shared.security.auth import get_current_user_from_request
from src.modules.reviews.schemas import CreateReviewRequest
from src.modules.reviews.service import create_review, get_review, list_reviews
from src.modules.batches.service import create_batch, get_batch, list_batches
from src.modules.batches.schemas import CreateBatchRequest

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _detect_lang(request: Request) -> str:
    lang = request.query_params.get("lang", "")
    if lang in ("ru", "en"):
        return lang
    lang = request.cookies.get("lang", "")
    if lang in ("ru", "en"):
        return lang
    return "ru"


def _ctx(request: Request, **extra) -> dict:
    settings = get_settings()
    current_user = {"user_id": "system", "role": "admin", "display_name": "System", "is_active": True}
    try:
        current_user = get_current_user_from_request(request)
    except Exception:
        if settings.enable_auth:
            current_user = None
    version_info = get_version_info()
    lang = _detect_lang(request)
    tr = get_translator(lang)
    base = {
        "local_only": settings.local_only_mode,
        "cloud_blocked": not settings.allow_cloud_llm,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "db_connected": check_db_connection(),
        "db_type": "SQLite",
        "auth_enabled": settings.enable_auth,
        "current_user": current_user,
        "app_version": version_info["version"],
        "app_stage": version_info["stage"],
        "lang": lang,
        "t": tr.t,
    }
    base.update(extra)
    return base


def _render(request: Request, name: str, **context):
    return templates.TemplateResponse(request, name, _ctx(request, **context))


def _error(request: Request, message: str):
    return templates.TemplateResponse(request, "error.html", _ctx(request, message=message))


@router.get("/lang/{lang}", include_in_schema=False)
def switch_lang(request: Request, lang: str, ref: str | None = None):
    if lang not in ("ru", "en"):
        lang = "ru"
    redirect_to = ref or request.headers.get("referer", "/")
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=365*24*3600, samesite="lax")
    return response


@router.get("/static/styles.css", include_in_schema=False)
def serve_css():
    return FileResponse(str(STATIC_DIR / "styles.css"), media_type="text/css")


@router.get("/static/logo.svg", include_in_schema=False)
def serve_logo():
    return FileResponse(str(STATIC_DIR / "logo.svg"), media_type="image/svg+xml")


@router.get("/", include_in_schema=False)
@router.get("/ui", include_in_schema=False)
def dashboard(request: Request):
    settings = get_settings()
    assets = list_assets()
    brands = list_brand_profiles()
    audiences = list_audience_profiles()
    runs = _list_test_runs()
    recent = sorted(runs, key=lambda r: r.created_at, reverse=True)[:5]

    from src.modules.brandbooks.service import list_brandbooks
    from src.modules.knowledge_base.service import list_knowledge_items
    brandbooks = list_brandbooks()
    knowledge = list_knowledge_items()
    clients = list_clients()
    projects = list_projects()

    return _render(
        request, "dashboard.html",
        client_count=len(clients),
        project_count=len(projects),
        asset_count=len(assets),
        brand_count=len(brands),
        audience_count=len(audiences),
        run_count=len(runs),
        recent_runs=recent,
        brandbook_count=len(brandbooks),
        knowledge_count=len(knowledge),
    )


# ── Clients UI ────────────────────────────────────────────────────

@router.get("/ui/clients", include_in_schema=False)
def ui_clients_list(request: Request):
    clients = list_clients()
    projects = list_projects()
    project_counts = {}
    for p in projects:
        project_counts[p.client_id] = project_counts.get(p.client_id, 0) + 1
    return _render(request, "clients/list.html", clients=clients, project_counts=project_counts)


@router.get("/ui/clients/new", include_in_schema=False)
def ui_clients_new(request: Request):
    return _render(request, "clients/new.html")


@router.post("/ui/clients", include_in_schema=False)
def ui_clients_create(
    request: Request,
    name: str = Form(...),
    industry: str | None = Form(None),
    description: str | None = Form(None),
    contact_name: str | None = Form(None),
    contact_email: str | None = Form(None),
):
    try:
        client = create_client(CreateClientRequest(
            name=name, industry=industry, description=description,
            contact_name=contact_name, contact_email=contact_email,
        ))
    except AppError as e:
        return _render(request, "clients/new.html", error=e.message)
    write_audit_event("client_created", "client", client.id, {"name": client.name})
    return RedirectResponse(url=f"/ui/clients/{client.id}", status_code=303)


@router.get("/ui/clients/{client_id}", include_in_schema=False)
def ui_clients_detail(request: Request, client_id: str):
    client = get_client(client_id)
    if client is None:
        return _error(request, f"Client not found: {client_id}")
    projects = list_projects(client_id=client_id)
    return _render(request, "clients/detail.html", client=client, projects=projects)


# ── Projects UI ───────────────────────────────────────────────────

@router.get("/ui/projects", include_in_schema=False)
def ui_projects_list(request: Request):
    projects = list_projects()
    clients_map = {}
    for c in list_clients():
        clients_map[c.id] = c.name
    return _render(request, "projects/list.html", projects=projects, client_names=clients_map)


@router.get("/ui/projects/new", include_in_schema=False)
def ui_projects_new(request: Request, client_id: str | None = None):
    return _render(request, "projects/new.html", clients=list_clients(), client_id=client_id)


@router.post("/ui/projects", include_in_schema=False)
def ui_projects_create(
    request: Request,
    client_id: str = Form(...),
    name: str = Form(...),
    description: str | None = Form(None),
):
    try:
        project = create_project(CreateProjectRequest(
            client_id=client_id, name=name, description=description,
        ))
    except AppError as e:
        return _render(request, "projects/new.html", error=e.message, clients=list_clients())
    write_audit_event("project_created", "project", project.id, {"name": project.name, "client_id": client_id})
    return RedirectResponse(url=f"/ui/projects/{project.id}", status_code=303)


def _project_counts(project_id: str) -> dict:
    from src.modules.creative_assets.models import CreativeAsset
    from src.modules.brand_profiles.models import BrandProfile
    from src.modules.audience_profiles.models import AudienceProfile
    from src.modules.brandbooks.models import BrandbookDocument
    from src.modules.knowledge_base.models import KnowledgeItem
    from src.modules.test_runs.models import TestRun
    from src.modules.report_generator.models import Report
    from src.modules.batches.models import BatchRun
    from src.shared.db.repository import db_session

    counts = {"creative_assets": 0, "brand_profiles": 0, "audience_profiles": 0,
              "brandbooks": 0, "knowledge_items": 0, "test_runs": 0,
              "completed_runs": 0, "reports": 0, "exports": 0, "batches": 0}
    with db_session() as db:
        counts["creative_assets"] = db.query(CreativeAsset).filter(CreativeAsset.project_id == project_id).count()
        counts["brand_profiles"] = db.query(BrandProfile).filter(BrandProfile.project_id == project_id).count()
        counts["audience_profiles"] = db.query(AudienceProfile).filter(AudienceProfile.project_id == project_id).count()
        counts["brandbooks"] = db.query(BrandbookDocument).filter(BrandbookDocument.project_id == project_id).count()
        counts["knowledge_items"] = db.query(KnowledgeItem).filter(KnowledgeItem.project_id == project_id).count()
        runs = db.query(TestRun).filter(TestRun.project_id == project_id).all()
        counts["test_runs"] = len(runs)
        counts["completed_runs"] = sum(1 for r in runs if r.status == "completed")
        counts["reports"] = db.query(Report).filter(Report.project_id == project_id).count()
        counts["exports"] = 0
        counts["batches"] = db.query(BatchRun).filter(BatchRun.project_id == project_id).count()
    return counts


@router.get("/ui/projects/{project_id}", include_in_schema=False)
def ui_projects_detail(request: Request, project_id: str):
    project = get_project(project_id)
    if project is None:
        return _error(request, f"Project not found: {project_id}")
    client = get_client(project.client_id)
    client_name = client.name if client else project.client_id
    counts = _project_counts(project_id)
    history = get_project_history(project_id)
    return _render(request, "projects/detail.html",
                   project=project, client_name=client_name,
                   counts=counts, history=history)


@router.get("/ui/projects/{project_id}/test-runs/new", include_in_schema=False)
def ui_projects_test_runs_new(request: Request, project_id: str):
    assets = list_assets()
    brand_profiles = list_brand_profiles()
    audience_profiles = list_audience_profiles()
    rubrics = list_rubrics()
    return _render(request, "test_runs/new.html",
                   assets=assets, brand_profiles=brand_profiles,
                   audience_profiles=audience_profiles, rubrics=rubrics,
                   project_id=project_id)


@router.get("/ui/projects/{project_id}/compare", include_in_schema=False)
def ui_projects_compare(request: Request, project_id: str):
    all_runs = _list_test_runs()
    completed = [r for r in all_runs if r.status == "completed" and getattr(r, "project_id", None) == project_id]
    return _render(request, "reports/compare.html", completed_runs=completed, project_id=project_id)


@router.get("/ui/projects/{project_id}/reports", include_in_schema=False)
def ui_projects_reports(request: Request, project_id: str):
    from src.modules.report_generator.models import Report
    from src.shared.db.repository import db_session
    with db_session() as db:
        reports = db.query(Report).filter(Report.project_id == project_id).order_by(Report.created_at.desc()).all()
    report_list = []
    for r in reports:
        report_list.append({
            "id": r.id,
            "test_run_id": r.test_run_id,
            "report_type": r.report_type,
            "created_at": r.created_at,
        })
    return _render(request, "reports/project_list.html", reports=report_list, project_id=project_id)


@router.get("/ui/projects/{project_id}/exports", include_in_schema=False)
def ui_projects_exports(request: Request, project_id: str):
    return _render(request, "exports/project_list.html", jobs=[], project_id=project_id)


@router.get("/ui/projects/{project_id}/batches", include_in_schema=False)
def ui_projects_batches(request: Request, project_id: str):
    return _render(request, "batches/list.html", batches=list_batches(project_id=project_id))


@router.get("/ui/projects/{project_id}/batches/new", include_in_schema=False)
def ui_projects_batches_new(request: Request, project_id: str):
    return _render(request, "batches/new.html", project_id=project_id)


@router.post("/ui/projects/{project_id}/batches", include_in_schema=False)
async def ui_projects_batches_create(
    request: Request,
    project_id: str,
    name: str = Form(...),
    description: str | None = Form(None),
    creative_asset_ids: str | None = Form(None),
    audience_profile_ids: str | None = Form(None),
    brand_profile_id: str | None = Form(None),
    test_rubric_id: str | None = Form(None),
    input_context: str | None = Form(None),
):
    asset_list = [a.strip() for a in creative_asset_ids.split("\n") if a.strip()] if creative_asset_ids else []
    audience_list = [a.strip() for a in audience_profile_ids.split("\n") if a.strip()] if audience_profile_ids else []
    ctx = {}
    if input_context:
        try:
            ctx = json.loads(input_context)
        except json.JSONDecodeError:
            pass

    try:
        batch = create_batch(CreateBatchRequest(
            project_id=project_id,
            name=name,
            description=description or None,
            creative_asset_ids=asset_list,
            audience_profile_ids=audience_list,
            brand_profile_id=brand_profile_id or None,
            test_rubric_id=test_rubric_id or None,
            input_context=ctx,
        ))
        write_audit_event("batch_created", "batch_run", batch.id, {"name": name})
        return RedirectResponse(url=f"/ui/batches/{batch.id}", status_code=303)
    except Exception as e:
        return _render(request, "batches/new.html", error=str(e), project_id=project_id)


@router.get("/ui/clients/{client_id}/projects/new", include_in_schema=False)
def ui_client_projects_new(request: Request, client_id: str):
    return _render(request, "projects/new.html", clients=[], client_id=client_id)


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
    project_id: str | None = Form(None),
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
                project_id=project_id or None,
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
                    project_id=project_id or None,
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


# ── Brandbooks ─────────────────────────────────────────────────────

@router.get("/ui/brandbooks", include_in_schema=False)
def ui_brandbooks_list(request: Request):
    from src.modules.brandbooks.service import list_brandbooks
    return _render(request, "brandbooks/list.html", docs=list_brandbooks())


@router.get("/ui/brandbooks/new", include_in_schema=False)
def ui_brandbooks_new(request: Request):
    return _render(request, "brandbooks/new.html")


@router.post("/ui/brandbooks", include_in_schema=False)
async def ui_brandbooks_create(
    request: Request,
    title: str | None = Form(None),
    document_type: str = Form("brandbook"),
    brand_profile_id: str | None = Form(None),
    client_id: str | None = Form(None),
    project_id: str | None = Form(None),
    file: UploadFile = File(...),
):
    from src.modules.brandbooks.router import post_upload_brandbook

    try:
        doc = await post_upload_brandbook(
            file=file,
            title=title,
            document_type=document_type,
            client_id=client_id,
            project_id=project_id,
            brand_profile_id=brand_profile_id,
        )
    except Exception as e:
        return _render(request, "brandbooks/new.html", error=str(e))

    return RedirectResponse(url=f"/ui/brandbooks/{doc.id}", status_code=303)


@router.get("/ui/brandbooks/{doc_id}", include_in_schema=False)
def ui_brandbooks_detail(request: Request, doc_id: str):
    from src.modules.brandbooks.service import get_brandbook

    doc = get_brandbook(doc_id)
    if doc is None:
        return _error(request, f"Brandbook not found: {doc_id}")
    return _render(request, "brandbooks/detail.html", doc=doc)


@router.post("/ui/brandbooks/{doc_id}/ingest", include_in_schema=False)
def ui_brandbooks_ingest(request: Request, doc_id: str):
    from src.modules.brandbooks.service import get_brandbook
    from src.modules.brandbooks.ingestion import ingest_brandbook

    doc = get_brandbook(doc_id)
    if doc is None:
        return _error(request, f"Brandbook not found: {doc_id}")

    try:
        result = ingest_brandbook(doc_id)
    except ValueError as e:
        return _render(request, "brandbooks/detail.html", doc=doc, error=str(e))

    return _render(request, "brandbooks/detail.html", doc=doc, ingest_result={"chunks_created": result})


# ── Reviews ─────────────────────────────────────────────────────────

@router.get("/ui/reviews", include_in_schema=False)
def ui_reviews_list(request: Request, creative_asset_id: str | None = Query(None), project_id: str | None = Query(None), status: str | None = Query(None)):
    return _render(request, "reviews/list.html", reviews=list_reviews(
        creative_asset_id=creative_asset_id,
        project_id=project_id,
        status=status,
    ))


@router.get("/ui/reviews/new", include_in_schema=False)
def ui_reviews_new(request: Request, asset_id: str | None = Query(None), report_id: str | None = Query(None)):
    return _render(request, "reviews/new.html", asset_id=asset_id, report_id=report_id)


@router.post("/ui/reviews", include_in_schema=False)
async def ui_reviews_create(
    request: Request,
    creative_asset_id: str = Form(...),
    report_id: str | None = Form(None),
    reviewer: str = Form("system"),
    decision: str | None = Form(None),
    rating: int | None = Form(None),
    summary: str | None = Form(None),
    strengths: str | None = Form(None),
    concerns: str | None = Form(None),
    revision_requests: str | None = Form(None),
):
    try:
        review = create_review(CreateReviewRequest(
            creative_asset_id=creative_asset_id,
            report_id=report_id,
            reviewer=reviewer,
            decision=decision or None,
            rating=rating,
            summary=summary or None,
            strengths=strengths or None,
            concerns=concerns or None,
            revision_requests=revision_requests or None,
        ))
        write_audit_event("review_created", "creative_review", review.id, {
            "creative_asset_id": creative_asset_id,
            "reviewer": reviewer,
        })
        return RedirectResponse(url=f"/ui/reviews/{review.id}", status_code=303)
    except Exception as e:
        return _render(request, "reviews/new.html", error=str(e),
                       asset_id=creative_asset_id, report_id=report_id)


@router.get("/ui/reviews/{review_id}", include_in_schema=False)
def ui_reviews_detail(request: Request, review_id: str):
    review = get_review(review_id)
    if review is None:
        return _error(request, f"Review not found: {review_id}")
    return _render(request, "reviews/detail.html", review=review)


# ── Batches ──────────────────────────────────────────────────────────

@router.get("/ui/batches", include_in_schema=False)
def ui_batches_list(request: Request, project_id: str | None = Query(None)):
    return _render(request, "batches/list.html", batches=list_batches(project_id=project_id))


@router.get("/ui/batches/new", include_in_schema=False)
def ui_batches_new(request: Request, project_id: str | None = Query(None), asset_ids: str | None = Query(None)):
    ids = asset_ids.split(",") if asset_ids else []
    return _render(request, "batches/new.html", project_id=project_id, asset_ids=ids)


@router.post("/ui/batches", include_in_schema=False)
async def ui_batches_create(
    request: Request,
    name: str = Form(...),
    description: str | None = Form(None),
    project_id: str | None = Form(None),
    creative_asset_ids: str | None = Form(None),
    audience_profile_ids: str | None = Form(None),
    brand_profile_id: str | None = Form(None),
    test_rubric_id: str | None = Form(None),
    input_context: str | None = Form(None),
):
    asset_list = [a.strip() for a in creative_asset_ids.split("\n") if a.strip()] if creative_asset_ids else []
    audience_list = [a.strip() for a in audience_profile_ids.split("\n") if a.strip()] if audience_profile_ids else []
    ctx = {}
    if input_context:
        try:
            ctx = json.loads(input_context)
        except json.JSONDecodeError:
            pass

    try:
        batch = create_batch(CreateBatchRequest(
            project_id=project_id or None,
            name=name,
            description=description or None,
            creative_asset_ids=asset_list,
            audience_profile_ids=audience_list,
            brand_profile_id=brand_profile_id or None,
            test_rubric_id=test_rubric_id or None,
            input_context=ctx,
        ))
        write_audit_event("batch_created", "batch_run", batch.id, {"name": name})
        return RedirectResponse(url=f"/ui/batches/{batch.id}", status_code=303)
    except Exception as e:
        return _render(request, "batches/new.html", error=str(e), project_id=project_id)


@router.get("/ui/batches/{batch_id}", include_in_schema=False)
def ui_batches_detail(request: Request, batch_id: str):
    batch = get_batch(batch_id)
    if batch is None:
        return _error(request, f"Batch not found: {batch_id}")
    return _render(request, "batches/detail.html", batch=batch)


# ── Knowledge Base ─────────────────────────────────────────────────

@router.get("/ui/knowledge-base", include_in_schema=False)
def ui_knowledge_base(request: Request, q: str | None = Query(None)):
    from src.modules.knowledge_base.service import list_knowledge_items
    from src.modules.knowledge_base.search import keyword_search

    items_list = []
    total = 0
    if q:
        results = keyword_search(query=q, max_results=20)
        items_list = [r.item for r in results]
        total = len(results)
    else:
        all_items = list_knowledge_items()
        items_list = all_items[:50]
        total = len(all_items)

    return _render(request, "knowledge_base/list.html", items=items_list, total=total, query=q or "")


@router.post("/ui/knowledge-base", include_in_schema=False)
def ui_knowledge_base_create(
    request: Request,
    title: str = Form(...),
    content: str | None = Form(None),
    tags: str | None = Form(None),
):
    from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
    from src.modules.knowledge_base.service import create_knowledge_item

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    try:
        item = create_knowledge_item(CreateKnowledgeItemRequest(
            source_type="manual_note",
            title=title,
            content=content,
            tags=tag_list,
        ))
    except Exception as e:
        return _render(request, "knowledge_base/list.html", error=str(e), items=[], total=0, query="", show_form=True)

    return RedirectResponse(url=f"/ui/knowledge-base?created={item.id[:8]}", status_code=303)


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
    project_id: str | None = Form(None),
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
                project_id=project_id or None,
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
def ui_reports_detail(request: Request, run_id: str, export_job: str | None = None):
    report = generate_report(run_id, report_mode="internal", report_format="json")
    if report is None:
        return _error(request, f"Report not available for test run: {run_id}")
    extra = {}
    if export_job:
        from src.modules.export_jobs.service import get_export_job
        job = get_export_job(export_job)
        if job:
            extra["export_job"] = job
    return _render(request, "reports/detail.html", report=report, **extra)


# ── UI Export helpers ───────────────────────────────────────────────────

@router.post("/ui/exports/report/{report_id}/docx", include_in_schema=False)
def ui_export_report_docx(request: Request, report_id: str):
    from src.modules.export_jobs.router import post_docx_export
    try:
        job = post_docx_export(report_id)
        return RedirectResponse(url=f"/ui/reports/{job.entity_id}?export_job={job.id}", status_code=303)
    except Exception as e:
        from src.modules.report_generator.service import get_report_by_id
        report = get_report_by_id(report_id)
        if report:
            return _render(request, "reports/detail.html", report=report, error=str(e))
        return _error(request, str(e))


@router.post("/ui/exports/report/{report_id}/pptx", include_in_schema=False)
def ui_export_report_pptx(request: Request, report_id: str):
    from src.modules.export_jobs.router import post_pptx_export
    try:
        job = post_pptx_export(report_id)
        return RedirectResponse(url=f"/ui/reports/{job.entity_id}?export_job={job.id}", status_code=303)
    except Exception as e:
        from src.modules.report_generator.service import get_report_by_id
        report = get_report_by_id(report_id)
        if report:
            return _render(request, "reports/detail.html", report=report, error=str(e))
        return _error(request, str(e))


@router.post("/ui/exports/report/{report_id}/pdf", include_in_schema=False)
def ui_export_report_pdf(request: Request, report_id: str):
    from src.modules.export_jobs.router import post_pdf_export
    try:
        job = post_pdf_export(report_id)
        return RedirectResponse(url=f"/ui/reports/{job.entity_id}?export_job={job.id}", status_code=303)
    except Exception as e:
        from src.modules.report_generator.service import get_report_by_id
        report = get_report_by_id(report_id)
        if report:
            return _render(request, "reports/detail.html", report=report, error=str(e))
        return _error(request, str(e))


@router.get("/ui/exports", include_in_schema=False)
def ui_exports_list(request: Request):
    from src.modules.export_jobs.service import list_export_jobs
    return _render(request, "exports/list.html", jobs=list_export_jobs())


@router.get("/ui/exports/{job_id}", include_in_schema=False)
def ui_exports_detail(request: Request, job_id: str):
    from src.modules.export_jobs.service import get_export_job
    job = get_export_job(job_id)
    if job is None:
        return _error(request, f"Export job not found: {job_id}")
    return _render(request, "exports/list.html", jobs=[job])


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


# ── Model Profiles UI ──────────────────────────────────────────────────

@router.get("/ui/model-profiles", include_in_schema=False)
def ui_model_profiles_list(request: Request):
    from src.modules.model_profiles.service import list_profiles
    return _render(request, "model_profiles/list.html", profiles=list_profiles())


@router.get("/ui/model-profiles/new", include_in_schema=False)
def ui_model_profiles_new(request: Request):
    return _render(request, "model_profiles/new.html")


@router.post("/ui/model-profiles", include_in_schema=False)
def ui_model_profiles_create(
    request: Request,
    profile_name: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    base_url: str | None = Form(None),
    timeout_seconds: int = Form(120),
    notes: str | None = Form(None),
):
    from src.modules.model_profiles.schemas import CreateModelProfileRequest
    from src.modules.model_profiles.service import create_profile
    try:
        profile = create_profile(CreateModelProfileRequest(
            profile_name=profile_name, provider=provider, model=model,
            base_url=base_url or None, timeout_seconds=timeout_seconds, notes=notes or None,
        ))
    except ValueError as e:
        return _render(request, "model_profiles/new.html", error=str(e))
    return RedirectResponse(url=f"/ui/model-profiles/{profile.id}", status_code=303)


@router.get("/ui/model-profiles/{profile_id}", include_in_schema=False)
def ui_model_profiles_detail(request: Request, profile_id: str):
    from src.modules.model_profiles.service import get_profile
    profile = get_profile(profile_id)
    if profile is None:
        return _error(request, f"Model profile not found: {profile_id}")
    return _render(request, "model_profiles/detail.html", profile=profile, health=None)


@router.post("/ui/model-profiles/{profile_id}/health", include_in_schema=False)
def ui_model_profiles_health(request: Request, profile_id: str):
    from src.modules.model_profiles.service import check_profile_health, get_profile
    from src.modules.model_profiles.schemas import ModelProfileHealth
    profile = get_profile(profile_id)
    if profile is None:
        return _error(request, f"Model profile not found: {profile_id}")
    try:
        health = check_profile_health(profile_id)
    except ValueError as e:
        return _render(request, "model_profiles/detail.html", profile=profile, health=None, error=str(e))
    return _render(request, "model_profiles/detail.html", profile=profile, health=health)


@router.post("/ui/model-profiles/load-from-config", include_in_schema=False)
def ui_model_profiles_load_config(request: Request):
    from src.modules.model_profiles.router import post_load_from_config
    try:
        result = post_load_from_config()
    except Exception as e:
        return _render(request, "model_profiles/list.html", profiles=[], error=str(e))
    return RedirectResponse(url="/ui/model-profiles", status_code=303)


# ── Evaluations UI ──────────────────────────────────────────────────

@router.get("/ui/evaluations", include_in_schema=False)
def ui_evaluations_list(request: Request):
    from src.modules.evaluations.runner import get_evaluation_results
    from src.modules.evaluations.models import EvaluationRun
    from src.shared.db.repository import db_session, json_loads
    with db_session() as db:
        runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
        run_list = [
            {
                "id": r.id,
                "profile_id": r.profile_id,
                "provider": r.provider,
                "model": r.model,
                "status": r.status,
                "summary": json_loads(r.summary_json) or {},
                "created_at": r.created_at,
            }
            for r in runs
        ]
    return _render(request, "evaluations/list.html", runs=run_list)


@router.get("/ui/evaluations/run", include_in_schema=False)
def ui_evaluations_run_form(request: Request):
    from src.modules.model_profiles.service import list_profiles
    cases = [
        {"case_id": "novabank_variant_a", "title": "NovaBank Variant A (clean)"},
        {"case_id": "novabank_variant_b", "title": "NovaBank Variant B (clean)"},
        {"case_id": "novabank_variant_c_risky", "title": "NovaBank Variant C (risky)"},
        {"case_id": "brandbook_claim_policy_violation", "title": "Brandbook Claim Policy Violation"},
        {"case_id": "tone_of_voice_mismatch", "title": "Tone of Voice Mismatch"},
    ]
    return _render(request, "evaluations/run.html", profiles=list_profiles(), cases=cases)


@router.post("/ui/evaluations/run", include_in_schema=False)
def ui_evaluations_run(
    request: Request,
    profile_id: str | None = Form(None),
    case_ids: list[str] = Form([]),
):
    from src.modules.evaluations.runner import run_evaluation, get_evaluation_results
    try:
        result = run_evaluation(profile_id=profile_id or None, case_ids=case_ids or None)
    except Exception as e:
        from src.modules.model_profiles.service import list_profiles
        cases = [
            {"case_id": "novabank_variant_a", "title": "NovaBank Variant A (clean)"},
            {"case_id": "novabank_variant_b", "title": "NovaBank Variant B (clean)"},
            {"case_id": "novabank_variant_c_risky", "title": "NovaBank Variant C (risky)"},
            {"case_id": "brandbook_claim_policy_violation", "title": "Brandbook Claim Policy Violation"},
            {"case_id": "tone_of_voice_mismatch", "title": "Tone of Voice Mismatch"},
        ]
        return _render(request, "evaluations/run.html", error=str(e), profiles=list_profiles(), cases=cases)
    return RedirectResponse(url=f"/ui/evaluations/{result['evaluation_run_id']}", status_code=303)


@router.get("/ui/evaluations/{eval_id}", include_in_schema=False)
def ui_evaluations_detail(request: Request, eval_id: str):
    from src.modules.evaluations.runner import get_evaluation_results
    result = get_evaluation_results(eval_id)
    if result is None:
        return _error(request, f"Evaluation not found: {eval_id}")
    return _render(request, "evaluations/detail.html", eval_id=eval_id, result=result)


# ── Prompt Traces UI ──────────────────────────────────────────────────

@router.get("/ui/prompt-traces", include_in_schema=False)
def ui_prompt_traces_list(
    request: Request,
    test_run_id: str | None = None,
    evaluation_run_id: str | None = None,
):
    from src.modules.prompt_traces.service import list_traces
    traces = list_traces(test_run_id=test_run_id, evaluation_run_id=evaluation_run_id)
    return _render(request, "prompt_traces/list.html", traces=traces,
                   test_run_id=test_run_id, evaluation_run_id=evaluation_run_id)


@router.get("/ui/prompt-traces/{trace_id}", include_in_schema=False)
def ui_prompt_traces_detail(request: Request, trace_id: str):
    from src.modules.prompt_traces.service import get_trace
    trace = get_trace(trace_id)
    if trace is None:
        return _error(request, f"Prompt trace not found: {trace_id}")
    return _render(request, "prompt_traces/detail.html", trace=trace)


@router.get("/ui/test-runs/{run_id}/prompt-traces", include_in_schema=False)
def ui_test_run_prompt_traces(request: Request, run_id: str):
    from src.modules.prompt_traces.service import list_traces
    traces = list_traces(test_run_id=run_id)
    return _render(request, "prompt_traces/list.html", traces=traces, test_run_id=run_id)


# ── Login / Logout ────────────────────────────────────────────────────


@router.get("/ui/login", include_in_schema=False)
def ui_login_page(request: Request):
    settings = get_settings()
    return _render(request, "login.html", auth_disabled=not settings.enable_auth)


@router.post("/ui/login", include_in_schema=False)
async def ui_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    settings = get_settings()
    if not settings.enable_auth:
        return _render(request, "login.html", auth_disabled=True, message="Auth is disabled in local/demo mode")

    from src.modules.auth.service import login as auth_login
    try:
        result = auth_login(email, password)
    except ValueError as e:
        return _render(request, "login.html", error=str(e), auth_disabled=False)

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=result["token"],
        httponly=True,
        max_age=settings.session_ttl_hours * 3600,
        samesite="lax",
    )
    return response


@router.post("/ui/logout", include_in_schema=False)
def ui_logout(request: Request):
    settings = get_settings()
    response = RedirectResponse(url="/ui/login", status_code=303)
    response.delete_cookie(key=settings.session_cookie_name)
    return response


# ── Users admin pages ──────────────────────────────────────────────────


@router.get("/ui/users", include_in_schema=False)
def ui_users_list(request: Request):
    from src.modules.users.service import list_users
    return _render(request, "users/list.html", users=list_users())


@router.get("/ui/users/new", include_in_schema=False)
def ui_users_new(request: Request):
    from src.modules.users.models import UserRole
    return _render(request, "users/new.html", roles=list(UserRole))


@router.post("/ui/users", include_in_schema=False)
def ui_users_create(
    request: Request,
    email: str = Form(...),
    display_name: str = Form(...),
    role: str = Form("viewer"),
    password: str = Form(...),
):
    from src.modules.users.models import UserRole
    from src.modules.users.schemas import CreateUserRequest
    from src.modules.users.service import create_user

    try:
        user = create_user(CreateUserRequest(
            email=email,
            display_name=display_name,
            role=UserRole(role),
            is_active=True,
            password=password,
        ))
    except (ValueError, Exception) as e:
        return _render(request, "users/new.html",
                       error=str(e), roles=list(UserRole))

    return RedirectResponse(url=f"/ui/users?created={user.id}", status_code=303)


@router.get("/ui/users/{user_id}", include_in_schema=False)
def ui_users_detail(request: Request, user_id: str):
    from src.modules.users.service import get_user
    user = get_user(user_id)
    if user is None:
        return _error(request, f"User not found: {user_id}")
    return _render(request, "users/detail.html", u=user)


@router.post("/ui/users/{user_id}/deactivate", include_in_schema=False)
def ui_users_deactivate(request: Request, user_id: str):
    from src.modules.users.service import deactivate_user
    try:
        deactivate_user(user_id)
    except ValueError as e:
        return _error(request, str(e))
    return RedirectResponse(url="/ui/users", status_code=303)


# ── Maintenance UI ──────────────────────────────────────────────────


@router.get("/ui/admin/maintenance", include_in_schema=False)
def ui_maintenance(request: Request):
    from src.modules.admin.router import (
        get_maintenance_status,
        get_storage_status,
        get_database_status,
    )
    from src.shared.security.auth import get_current_user_from_request

    settings = get_settings()
    try:
        current_user = get_current_user_from_request(request)
    except Exception:
        current_user = None

    if settings.enable_auth and (not current_user or current_user.get("role") not in ("admin", "manager")):
        return _error(request, "Maintenance page requires admin or manager role.")

    try:
        status = get_maintenance_status()
        storage = get_storage_status()
        db_status = get_database_status()
    except Exception as e:
        return _error(request, f"Could not load maintenance data: {e}")

    return _render(request, "admin/maintenance.html",
                   status=status, storage=storage, db_status=db_status)
