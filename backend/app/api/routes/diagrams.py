"""Diagram generation API — /projects/{project_id}/diagrams/..."""
import uuid
from datetime import UTC, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.models import Agent, Document, DocumentStatus, DocumentType, Project
from app.db.session import get_session
from app.services.diagram_service import (
    generate_diagrams,
    mermaid_to_drawio_url,
    wrap_in_markdown,
)

router = APIRouter()


# ── Response schemas ──────────────────────────────────────────────────────────

class DiagramResponse(BaseModel):
    id:            uuid.UUID
    title:         str
    document_type: str
    content_markdown: str
    mermaid_code:  str          # extracted from the fenced code block
    drawio_url:    str          # Mermaid Live Editor pre-loaded URL
    created_at:    datetime
    updated_at:    datetime

    model_config = {"from_attributes": True}


class GenerateDiagramsResponse(BaseModel):
    generated: int
    diagrams:  list[DiagramResponse]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_project_or_404(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _latest_doc(session: Session, project_id: uuid.UUID, doc_type: DocumentType) -> Optional[Document]:
    return session.exec(
        select(Document)
        .where(Document.project_id == project_id, Document.document_type == doc_type)
        .order_by(Document.created_at.desc())
    ).first()


def _extract_mermaid(content: str) -> str:
    """Extract the raw Mermaid code from a fenced markdown block."""
    import re
    m = re.search(r"```(?:mermaid)?\s*\n?([\s\S]+?)\n?```", content)
    return m.group(1).strip() if m else content.strip()


def _to_response(doc: Document) -> DiagramResponse:
    code = _extract_mermaid(doc.content_markdown)
    return DiagramResponse(
        id=doc.id,
        title=doc.title,
        document_type=doc.document_type if isinstance(doc.document_type, str) else doc.document_type.value,
        content_markdown=doc.content_markdown,
        mermaid_code=code,
        drawio_url=mermaid_to_drawio_url(code),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


def _get_diagram_agent_id(session: Session) -> Optional[uuid.UUID]:
    agent = session.exec(
        select(Agent).where(Agent.role == "diagram-agent")
    ).first()
    return agent.id if agent else None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/{project_id}/diagrams",
    response_model=list[DiagramResponse],
    summary="List all generated diagrams for a project",
)
def list_diagrams(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> list[DiagramResponse]:
    _get_project_or_404(session, project_id)
    docs = session.exec(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.diagram_spec,
        )
        .order_by(Document.created_at.desc())
    ).all()
    return [_to_response(d) for d in docs]


@router.post(
    "/{project_id}/diagrams/generate",
    response_model=GenerateDiagramsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Mermaid diagrams (architecture + ERD) from existing project documents",
)
def generate_project_diagrams(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> GenerateDiagramsResponse:
    _get_project_or_404(session, project_id)

    arch_doc = _latest_doc(session, project_id, DocumentType.architecture_design)
    db_doc   = _latest_doc(session, project_id, DocumentType.database_design)

    if not arch_doc and not db_doc:
        raise HTTPException(
            status_code=404,
            detail="No architecture or database design documents found. "
                   "Run the Solution Architect Agent pipeline step first.",
        )

    arch_content = arch_doc.content_markdown if arch_doc else "No architecture design available."
    db_content   = db_doc.content_markdown   if db_doc   else "No database design available."

    # Pick a model — reuse the same model as the architect agent if available
    model = "qwen3:8b"
    if arch_doc and arch_doc.created_by_agent_id:
        agent = session.get(Agent, arch_doc.created_by_agent_id)
        if agent and agent.model_name:
            model = agent.model_name

    diagrams = generate_diagrams(
        architecture_doc=arch_content,
        database_doc=db_content,
        model=model,
    )

    agent_id = _get_diagram_agent_id(session)
    now = datetime.now(UTC)
    created_docs: list[Document] = []

    for title, key in [
        ("Architecture Diagram", "architecture_mermaid"),
        ("Entity Relationship Diagram (ERD)", "erd_mermaid"),
    ]:
        mermaid_code = diagrams[key]
        doc = Document(
            project_id=project_id,
            document_type=DocumentType.diagram_spec,
            title=title,
            content_markdown=wrap_in_markdown(mermaid_code),
            status=DocumentStatus.draft,
            created_by_agent_id=agent_id,
            created_at=now,
            updated_at=now,
        )
        session.add(doc)
        created_docs.append(doc)

    session.commit()
    for doc in created_docs:
        session.refresh(doc)

    return GenerateDiagramsResponse(
        generated=len(created_docs),
        diagrams=[_to_response(d) for d in created_docs],
    )


@router.get(
    "/{project_id}/diagrams/{diagram_id}",
    response_model=DiagramResponse,
    summary="Get a single diagram document",
)
def get_diagram(
    project_id: uuid.UUID,
    diagram_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> DiagramResponse:
    _get_project_or_404(session, project_id)
    doc = session.get(Document, diagram_id)
    if not doc or doc.project_id != project_id or doc.document_type != DocumentType.diagram_spec:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return _to_response(doc)
