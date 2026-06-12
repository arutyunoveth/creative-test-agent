import pytest

from src.shared.errors import AppError
from src.shared.vision.policy import validate_vision_provider


def test_stub_vision_provider_is_allowed():
    validate_vision_provider("stub")


def test_local_ocr_provider_with_default_disabled():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("local_ocr")
    assert exc.value.code == "local_ocr_disabled"


def test_local_vlm_provider_with_default_disabled():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("local_vlm")
    assert exc.value.code == "local_vlm_disabled"


def test_hybrid_provider_with_both_disabled():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("hybrid")
    assert exc.value.code == "hybrid_disabled"


def test_google_vision_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("google_vision")
    assert exc.value.code == "cloud_vision_forbidden"


def test_aws_textract_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("aws_textract")
    assert exc.value.code == "cloud_vision_forbidden"


def test_azure_ocr_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("azure_ocr")
    assert exc.value.code == "cloud_vision_forbidden"


def test_openai_vision_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("openai_vision")
    assert exc.value.code == "cloud_vision_forbidden"


def test_gemini_vision_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("gemini_vision")
    assert exc.value.code == "cloud_vision_forbidden"


def test_claude_vision_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("claude_vision")
    assert exc.value.code == "cloud_vision_forbidden"


def test_unsupported_vision_provider():
    with pytest.raises(AppError) as exc:
        validate_vision_provider("nonexistent_provider")
    assert exc.value.code == "unsupported_vision_provider"
