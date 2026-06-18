"""RAG API — /projects/{project_id}/rag/..."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, func, select

from app.db.models import Project, RagChunk
from app.db.session import get_session
from app.rag import store

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    project_id: str
    chunks_created: int
    message: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class ChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_type: str
    chunk_index: int
    chunk_text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]


class ChunkStats(BaseModel):
    project_id: str
    total_chunks: int
    document_types: list[str]


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post(
    "/{project_id}/rag/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest project documents into RAG store",
    description=(
        "Chunk and embed all documents for a project. "
        "Existing chunks are replaced so this operation is idempotent. "
        "Requires Ollama embed model (nomic-embed-text) to be running."
    ),
)
def ingest(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> IngestResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        count = store.ingest_project(session, project_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ingestion failed: {exc}",
        )

    return IngestResponse(
        project_id=str(project_id),
        chunks_created=count,
        message=f"Ingested {count} chunks from project documents.",
    )


@router.post(
    "/{project_id}/rag/search",
    response_model=SearchResponse,
    summary="Semantic search over project documents",
)
def search(
    project_id: uuid.UUID,
    body: SearchRequest,
    session: Annotated[Session, Depends(get_session)],
) -> SearchResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        hits = store.search(session, project_id, body.query, body.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Search failed: {exc}",
        )

    return SearchResponse(
        query=body.query,
        results=[ChunkResult(**h) for h in hits],
    )


@router.get(
    "/{project_id}/rag/chunks",
    response_model=ChunkStats,
    summary="RAG chunk statistics for a project",
)
def chunk_stats(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> ChunkStats:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total = session.exec(
        select(func.count(RagChunk.id)).where(RagChunk.project_id == project_id)
    ).one()

    types_rows = session.exec(
        select(RagChunk.document_type)
        .where(RagChunk.project_id == project_id)
        .distinct()
    ).all()

    return ChunkStats(
        project_id=str(project_id),
        total_chunks=total,
        document_types=list(types_rows),
    )
