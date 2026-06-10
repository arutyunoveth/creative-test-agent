from pydantic import BaseModel


class LLMRequest(BaseModel):
    prompt: str
    metadata: dict | None = None


class LLMResponse(BaseModel):
    provider: str
    content: str
    metadata: dict


class LLMProviderHealth(BaseModel):
    provider: str
    model: str | None = None
    base_url: str | None = None
    available: bool
    local_only_mode: bool
