import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import EventType


class ActivityLogResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    agent_id: Optional[uuid.UUID]
    event_type: EventType
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityLogList(BaseModel):
    total: int
    items: list[ActivityLogResponse]
