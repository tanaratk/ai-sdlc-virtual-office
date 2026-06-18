"""RAG ingestion and retrieval backed by the rag_chunks table."""
import logging
import uuid

from sqlmodel import Session, delete, select

from app.db.models import Document, RagChunk
from app.rag import chunker, embedder

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 500
_OVERLAP = 50


def ingest_project(session: Session, project_id: uuid.UUID) -> int:
    """Chunk and embed all documents for a project. Returns total chunks created."""
    # Delete existing chunks so re-ingest is idempotent
    session.exec(delete(RagChunk).where(RagChunk.project_id == project_id))  # type: ignore[arg-type]
    session.commit()

    documents = session.exec(
        select(Document).where(Document.project_id == project_id)
    ).all()

    total = 0
    for doc in documents:
        chunks = chunker.chunk_text(doc.content_markdown, _CHUNK_SIZE, _OVERLAP)
        logger.info(
            "Ingesting doc %s (%s) → %d chunks", doc.id, doc.document_type, len(chunks)
        )
        for idx, text in enumerate(chunks):
            try:
                vector = embedder.embed(text)
                embedding_json = embedder.serialize(vector)
            except Exception as exc:
                logger.warning("Embed failed for chunk %d of doc %s: %s", idx, doc.id, exc)
                embedding_json = None

            chunk = RagChunk(
                project_id=project_id,
                document_id=doc.id,
                document_type=doc.document_type.value,
                chunk_index=idx,
                chunk_text=text,
                embedding_json=embedding_json,
            )
            session.add(chunk)
        total += len(chunks)

    session.commit()
    return total


def search(
    session: Session,
    project_id: uuid.UUID,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Return the top-k most similar chunks for a query within a project."""
    try:
        query_vec = embedder.embed(query)
    except Exception as exc:
        logger.warning("Embed query failed: %s", exc)
        return []

    chunks = session.exec(
        select(RagChunk).where(
            RagChunk.project_id == project_id,
            RagChunk.embedding_json.is_not(None),  # type: ignore[union-attr]
        )
    ).all()

    scored: list[tuple[float, RagChunk]] = []
    for chunk in chunks:
        try:
            vec = embedder.deserialize(chunk.embedding_json)  # type: ignore[arg-type]
            score = embedder.cosine_similarity(query_vec, vec)
            scored.append((score, chunk))
        except Exception:
            continue

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "chunk_id": str(c.id),
            "document_id": str(c.document_id),
            "document_type": c.document_type,
            "chunk_index": c.chunk_index,
            "chunk_text": c.chunk_text,
            "score": round(score, 4),
        }
        for score, c in scored[:top_k]
    ]
