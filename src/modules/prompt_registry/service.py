import hashlib
import json

from src.modules.prompt_registry.models import PromptVersion
from src.modules.prompt_registry.schemas import PromptVersionResponse
from src.shared.db.repository import db_session, json_dumps, json_loads

STAGE_NAMES = [
    "creative_summary",
    "audience_simulation",
    "brand_safety_review",
    "brandbook_compliance_review",
    "rubric_scoring",
    "final_recommendation",
    "report_input_normalization",
]


def _compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _to_response(pv: PromptVersion) -> PromptVersionResponse:
    return PromptVersionResponse(
        id=pv.id,
        stage_name=pv.stage_name,
        version=pv.version,
        template_path=pv.template_path,
        template_hash=pv.template_hash,
        is_active=pv.is_active,
        metadata=json_loads(pv.metadata_json) or {},
        created_at=pv.created_at,
    )


def register_prompt(stage_name: str, template_path: str, version: str | None = None) -> PromptVersionResponse:
    from pathlib import Path
    path = Path(template_path)
    if not path.is_file():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    content = path.read_text()
    template_hash = _compute_hash(content)
    ver = version or path.stem

    with db_session() as db:
        existing = db.query(PromptVersion).filter(
            PromptVersion.stage_name == stage_name,
            PromptVersion.template_hash == template_hash,
        ).first()
        if existing:
            return _to_response(existing)
        pv = PromptVersion(
            stage_name=stage_name,
            version=ver,
            template_path=str(template_path),
            template_hash=template_hash,
            is_active=True,
            metadata_json=json_dumps({"registered_by": "register_prompts", "file_size": len(content)}),
        )
        db.add(pv)
        db.flush()
        db.refresh(pv)
        return _to_response(pv)


def list_prompts() -> list[PromptVersionResponse]:
    with db_session() as db:
        prompts = db.query(PromptVersion).order_by(PromptVersion.stage_name, PromptVersion.created_at.desc()).all()
        return [_to_response(p) for p in prompts]


def get_active_prompt(stage_name: str) -> PromptVersionResponse | None:
    with db_session() as db:
        pv = db.query(PromptVersion).filter(
            PromptVersion.stage_name == stage_name,
            PromptVersion.is_active == True,
        ).order_by(PromptVersion.created_at.desc()).first()
        if pv is None:
            return None
        return _to_response(pv)


def get_prompt_hash(stage_name: str, template_content: str) -> str:
    return _compute_hash(template_content)
