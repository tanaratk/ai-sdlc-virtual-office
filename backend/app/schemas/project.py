import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: str
    workspace_path: Optional[str] = r"D:\workspace"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    workspace_path: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_by: str
    workspace_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
