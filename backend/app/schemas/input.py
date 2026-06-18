import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.db.models import InputType


class RequirementInputCreate(BaseModel):
    input_type: InputType
    title: Optional[str] = None
    content: str
    file_url: Optional[str] = None
    source_owner: Optional[str] = None
    source_date: Optional[datetime] = None
    metadata_json: Optional[dict[str, Any]] = None


class RequirementInputResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    input_type: InputType
    title: Optional[str]
    content: str
    file_url: Optional[str]
    source_owner: Optional[str]
    source_date: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
