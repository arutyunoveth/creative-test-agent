from fastapi import APIRouter, HTTPException

from src.modules.prompt_registry.schemas import PromptVersionResponse
from src.modules.prompt_registry.service import get_active_prompt, list_prompts

router = APIRouter(prefix="/prompt-registry", tags=["prompt_registry"])


@router.get("", response_model=list[PromptVersionResponse])
def get_prompt_registry():
    return list_prompts()


@router.get("/active/{stage_name}", response_model=PromptVersionResponse)
def get_active_prompt_by_stage(stage_name: str):
    pv = get_active_prompt(stage_name)
    if pv is None:
        raise HTTPException(status_code=404, detail=f"No active prompt for stage: {stage_name}")
    return pv
