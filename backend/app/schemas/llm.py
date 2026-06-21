import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import ModelProvider


class LlmSettingResponse(BaseModel):
    id: uuid.UUID
    provider: ModelProvider
    base_url: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    is_active: bool
    has_api_key: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj: object) -> "LlmSettingResponse":
        data = cls.model_validate(obj)
        # api_key_encrypted is not exposed — just signal presence
        raw = getattr(obj, "api_key_encrypted", None)
        data.has_api_key = bool(raw)
        return data


class LlmSettingCreate(BaseModel):
    provider: ModelProvider
    base_url: Optional[str] = None
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    is_active: bool = False


class LlmSettingUpdate(BaseModel):
    is_active: Optional[bool] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class LlmKeyTestRequest(BaseModel):
    provider: ModelProvider
    api_key: str


class LlmKeyTestResponse(BaseModel):
    valid: bool
    message: str


class OllamaModel(BaseModel):
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None


class OllamaModelsResponse(BaseModel):
    models: list[OllamaModel]
    base_url: str
