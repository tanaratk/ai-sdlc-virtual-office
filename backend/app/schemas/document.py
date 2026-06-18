import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    document_type: DocumentType
    title: str
    content_markdown: str
    version: int
    status: DocumentStatus
    created_by_agent_id: Optional[uuid.UUID]
    approved_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    """Lightweight list item — omits content_markdown."""
    id: uuid.UUID
    project_id: uuid.UUID
    document_type: DocumentType
    title: str
    version: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
