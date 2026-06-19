import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import AgentStatus, ModelProvider, SpriteDirection


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: str
    description: Optional[str]
    goal: Optional[str]
    status: AgentStatus
    home_zone: Optional[str]
    current_zone: Optional[str]
    location_x: int
    location_y: int
    sprite_direction: SpriteDirection
    model_provider: ModelProvider
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentUpdate(BaseModel):
    model_provider: Optional[ModelProvider] = None
    model_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
