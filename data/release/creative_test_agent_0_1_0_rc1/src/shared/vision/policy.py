"""Vision closed-loop policy.

Mirrors the LLM closed-loop policy from src/shared/llm/policy.py.
"""

from src.shared.errors import AppError

LOCAL_VISION_PROVIDERS = {"stub", "local_ocr", "local_vlm", "hybrid"}
CLOUD_VISION_PROVIDERS = {
    "google_vision",
    "aws_textract",
    "azure_ocr",
    "openai_vision",
    "gemini_vision",
    "claude_vision",
}


def validate_vision_provider(provider: str | None = None) -> None:
    """Validate that the requested vision provider is allowed.

    Raises AppError if the provider is forbidden.
    """
    from src.shared.config.settings import get_settings

    settings = get_settings()
    provider = provider or settings.vision_provider

    if provider in CLOUD_VISION_PROVIDERS:
        raise AppError(
            code="cloud_vision_forbidden",
            message=f"Cloud vision provider '{provider}' is not allowed in local-only mode.",
            status_code=403,
        )

    if provider not in LOCAL_VISION_PROVIDERS:
        raise AppError(
            code="unsupported_vision_provider",
            message=f"Unsupported vision provider '{provider}'. Must be one of: {', '.join(sorted(LOCAL_VISION_PROVIDERS))}.",
            status_code=400,
        )

    if provider == "local_ocr" and not settings.enable_local_ocr:
        raise AppError(
            code="local_ocr_disabled",
            message="Local OCR is disabled. Set CTA_ENABLE_LOCAL_OCR=true to enable.",
            status_code=400,
        )

    if provider == "local_vlm" and not settings.enable_local_vlm:
        raise AppError(
            code="local_vlm_disabled",
            message="Local VLM is disabled. Set CTA_ENABLE_LOCAL_VLM=true to enable.",
            status_code=400,
        )

    if provider == "hybrid" and not (settings.enable_local_ocr or settings.enable_local_vlm):
        raise AppError(
            code="hybrid_disabled",
            message="Hybrid vision requires at least one local component enabled (OCR or VLM).",
            status_code=400,
        )
