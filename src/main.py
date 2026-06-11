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
from src.shared.api.errors import register_exception_handlers
from src.shared.config.settings import get_settings
from src.shared.llm.router import router as llm_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

register_exception_handlers(app)

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


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "local_only_mode": settings.local_only_mode,
    }
