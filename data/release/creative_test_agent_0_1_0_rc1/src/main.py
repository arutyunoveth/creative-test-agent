import logging
import sys

from fastapi import FastAPI

from src.modules.agent_registry.router import router as agent_registry_router
from src.modules.audit_log.router import router as audit_log_router
from src.modules.audience_profiles.router import router as audience_profiles_router
from src.modules.brand_profiles.router import router as brand_profiles_router
from src.modules.creative_assets.router import router as creative_assets_router
from src.modules.report_generator.router import router as report_generator_router
from src.modules.test_rubrics.router import router as test_rubrics_router
from src.modules.ui.router import router as ui_router
from src.modules.test_runs.router import router as test_runs_router
from src.modules.clients.router import router as clients_router
from src.modules.projects.router import router as projects_router
from src.modules.users.router import router as users_router
from src.modules.brandbooks.router import router as brandbooks_router
from src.modules.knowledge_base.router import router as knowledge_base_router
from src.modules.export_jobs.router import router as export_jobs_router
from src.modules.admin.router import router as admin_router
from src.modules.auth.router import router as auth_router
from src.modules.model_profiles.router import router as model_profiles_router
from src.modules.prompt_registry.router import router as prompt_registry_router
from src.modules.evaluations.router import router as evaluations_router
from src.modules.prompt_traces.router import router as prompt_traces_router
from src.modules.reviews.router import router as reviews_router
from src.modules.job_queue.router import router as job_queue_router
from src.modules.batches.router import router as batches_router
from src.modules.demo.router import router as demo_router
from src.shared.api.errors import register_exception_handlers
from src.shared.config.settings import get_settings
from src.shared.db.session import check_db_connection, get_database_url, init_db
from src.shared.llm.router import router as llm_router
from src.shared.vision.router import router as vision_router

from src.modules.projects.history import get_project_history
from src.shared.version import get_version_info

settings = get_settings()

app = FastAPI(title=settings.app_name)

register_exception_handlers(app)


@app.on_event("startup")
def on_startup():
    _setup_logging()
    init_db()


def _setup_logging():
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if settings.log_file:
        handlers.append(logging.FileHandler(settings.log_file))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )
    if settings.log_format == "plain":
        logging.getLogger().handlers[0].setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )


app.include_router(agent_registry_router)
app.include_router(creative_assets_router)
app.include_router(brand_profiles_router)
app.include_router(audience_profiles_router)
app.include_router(test_rubrics_router)
app.include_router(test_runs_router)
app.include_router(report_generator_router)
app.include_router(audit_log_router)
app.include_router(ui_router)
app.include_router(llm_router)
app.include_router(vision_router, prefix="/vision")
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(users_router)
app.include_router(brandbooks_router)
app.include_router(knowledge_base_router)
app.include_router(export_jobs_router, prefix="/exports")
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(model_profiles_router)
app.include_router(prompt_registry_router)
app.include_router(evaluations_router)
app.include_router(prompt_traces_router)
app.include_router(reviews_router)
app.include_router(job_queue_router)
app.include_router(batches_router)
app.include_router(demo_router)


# ── Auth middleware for write protection ──────────────────────────


@app.middleware("http")
async def auth_write_middleware(request, call_next):
    settings = get_settings()
    if settings.enable_auth and request.method in ("POST", "PUT", "PATCH", "DELETE"):
        path = request.url.path
        if path == "/":
            pass
        elif path.startswith(("/auth/login", "/auth/logout", "/ui/login")):
            pass
        else:
            from src.shared.security.auth import get_current_user_from_request
            try:
                user = get_current_user_from_request(request)
                role = user.get("role", "")
                if role not in ("admin", "manager", "analyst"):
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=403,
                        content={"detail": f"Role '{role}' does not have write permission"},
                    )
            except Exception as e:
                from fastapi.responses import JSONResponse
                status = getattr(e, "status_code", 401)
                detail = getattr(e, "detail", str(e)) if hasattr(e, "detail") else str(e)
                return JSONResponse(status_code=status, content={"detail": detail})
    response = await call_next(request)
    return response


@app.get("/health/db")
def health_db():
    connected = check_db_connection()
    return {
        "status": "ok" if connected else "error",
        "database": "connected" if connected else "disconnected",
        "database_url": get_database_url(masked=True),
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "local_only_mode": settings.local_only_mode,
    }


@app.get("/version")
def version():
    return get_version_info()


@app.get("/clients/{client_id}/projects")
def get_client_projects(client_id: str):
    return list_projects_by_client(client_id)


@app.get("/projects/{project_id}/history")
def project_history(project_id: str):
    return get_project_history(project_id)


def list_projects_by_client(client_id: str):
    from src.modules.projects.service import list_projects
    return list_projects(client_id=client_id)
