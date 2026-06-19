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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LlmSettingCreate(BaseModel):
    provider: ModelProvider
    base_url: Optional[str] = None
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 4096


class OllamaModel(BaseModel):
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None


class OllamaModelsResponse(BaseModel):
    models: list[OllamaModel]
    base_url: str
