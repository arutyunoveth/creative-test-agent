from fastapi import APIRouter

from src.shared.config.settings import get_settings
from src.shared.vision.schemas import VisionProviderHealth

router = APIRouter()


@router.get("/health", response_model=VisionProviderHealth)
def vision_health():
    settings = get_settings()
    provider = settings.vision_provider
    warnings = []

    if provider == "local_ocr":
        try:
            from src.shared.vision.ocr import _TESSERACT_AVAILABLE
            if not _TESSERACT_AVAILABLE:
                warnings.append("local_ocr_unavailable")
        except Exception:
            warnings.append("local_ocr_unavailable")

    if provider == "local_vlm":
        if not settings.vision_base_url or not settings.vision_model:
            warnings.append("local_vlm_unavailable")

    if provider == "hybrid":
        ocr_ok = True
        vlm_ok = True
        try:
            from src.shared.vision.ocr import _TESSERACT_AVAILABLE
            if not _TESSERACT_AVAILABLE:
                ocr_ok = False
        except Exception:
            ocr_ok = False
        if not settings.vision_base_url or not settings.vision_model:
            vlm_ok = False
        if not ocr_ok and not vlm_ok:
            warnings.append("hybrid_unavailable")
        elif not ocr_ok:
            warnings.append("local_ocr_unavailable")
        elif not vlm_ok:
            warnings.append("local_vlm_unavailable")

    return VisionProviderHealth(
        provider=provider,
        local_ocr_enabled=settings.enable_local_ocr,
        local_vlm_enabled=settings.enable_local_vlm,
        available=provider == "stub" or not warnings,
        warnings=warnings,
    )
