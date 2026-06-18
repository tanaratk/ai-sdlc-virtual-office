import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import ArtifactType, DocumentStatus, DocumentType, InputType, LinkType


class TraceabilityLinkCreate(BaseModel):
    source_type: ArtifactType
    source_id: uuid.UUID
    target_type: ArtifactType
    target_id: uuid.UUID
    link_type: LinkType


class TraceabilityLinkResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    source_type: ArtifactType
    source_id: uuid.UUID
    target_type: ArtifactType
    target_id: uuid.UUID
    link_type: LinkType
    created_at: datetime

    model_config = {"from_attributes": True}


class RequirementInputSummary(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    input_type: InputType
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCoverage(BaseModel):
    id: uuid.UUID
    document_type: DocumentType
    title: str
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class CoverageStats(BaseModel):
    total_requirement_inputs: int
    total_documents: int
    linked_requirement_inputs: int
    document_types_present: list[DocumentType]
    document_types_missing: list[DocumentType]
    coverage_pct: float


class TraceabilityMatrix(BaseModel):
    project_id: uuid.UUID
    requirement_inputs: list[RequirementInputSummary]
    documents: list[DocumentCoverage]
    links: list[TraceabilityLinkResponse]
    coverage: CoverageStats


class AutoLinkResult(BaseModel):
    links_created: int
    links_skipped: int
    message: str
