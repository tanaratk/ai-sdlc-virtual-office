import uuid

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app.db.models import Document, DocumentStatus
from app.schemas.common import PaginatedResponse
from app.schemas.document import DocumentResponse, DocumentSummary


class DocumentService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        project_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[DocumentSummary]:
        query = select(Document).where(Document.project_id == project_id)
        total = self.session.exec(
            select(func.count()).select_from(query.subquery())
        ).one()
        items = self.session.exec(
            query.order_by(Document.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return PaginatedResponse(
            total=total, page=page, page_size=page_size,
            items=[DocumentSummary.model_validate(d) for d in items],
        )

    def get(self, project_id: uuid.UUID, document_id: uuid.UUID) -> DocumentResponse:
        doc = self.session.exec(
            select(Document).where(
                Document.id == document_id,
                Document.project_id == project_id,
            )
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Document {document_id} not found"})
        return DocumentResponse.model_validate(doc)

    def approve(self, project_id: uuid.UUID, document_id: uuid.UUID, approved_by: str = "user") -> DocumentResponse:
        doc = self.session.exec(
            select(Document).where(Document.id == document_id, Document.project_id == project_id)
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Document {document_id} not found"})
        doc.status = DocumentStatus.approved
        doc.approved_by = approved_by
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return DocumentResponse.model_validate(doc)

    def reject(self, project_id: uuid.UUID, document_id: uuid.UUID) -> DocumentResponse:
        doc = self.session.exec(
            select(Document).where(Document.id == document_id, Document.project_id == project_id)
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": f"Document {document_id} not found"})
        doc.status = DocumentStatus.rejected
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return DocumentResponse.model_validate(doc)
