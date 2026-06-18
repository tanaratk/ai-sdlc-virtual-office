import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import PipelineRunStatus, PipelineStepStatus


class PipelineRunResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: PipelineRunStatus
    current_step: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineStepResponse(BaseModel):
    id: uuid.UUID
    pipeline_run_id: uuid.UUID
    step_name: str
    agent_id: Optional[uuid.UUID]
    status: PipelineStepStatus
    output_document_id: Optional[uuid.UUID]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int

    model_config = {"from_attributes": True}
