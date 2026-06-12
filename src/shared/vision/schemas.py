from pydantic import BaseModel


class VisionRisk(BaseModel):
    risk_type: str
    level: str  # low | medium | high
    description: str
    mitigation: str = ""


class VisionResult(BaseModel):
    provider: str = "stub"
    visual_summary: str = ""
    detected_text: str = ""
    layout_notes: list[str] = []
    visual_risks: list[VisionRisk] = []
    warnings: list[str] = []
    metadata: dict = {}


class VisionProviderHealth(BaseModel):
    provider: str = "stub"
    local_ocr_enabled: bool = False
    local_vlm_enabled: bool = False
    available: bool = True
    warnings: list[str] = []
