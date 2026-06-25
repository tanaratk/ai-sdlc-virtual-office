import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import ProjectStatus


class TechStackConfig(BaseModel):
    # Core
    preset: Optional[str] = None
    frontend: Optional[str] = None
    backend: Optional[str] = None
    database: Optional[str] = None
    app_type: Optional[str] = None
    # Language & versions (FR-06, FR-07)
    language: Optional[str] = None
    frontend_version: Optional[str] = None
    backend_version: Optional[str] = None
    database_version: Optional[str] = None
    # Infrastructure (FR-09)
    cloud: Optional[str] = None
    auth: Optional[str] = None
    orm: Optional[str] = None
    container: Optional[str] = None
    testing: Optional[str] = None
    logging: Optional[str] = None
    monitoring: Optional[str] = None
    api_docs: Optional[str] = None
    cache: Optional[str] = None
    queue: Optional[str] = None
    deployment_target: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: str
    workspace_path: Optional[str] = r"D:\workspace"
    tech_stack: Optional[TechStackConfig] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    workspace_path: Optional[str] = None
    tech_stack: Optional[TechStackConfig] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_by: str
    workspace_path: Optional[str]
    tech_stack: Optional[TechStackConfig] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
