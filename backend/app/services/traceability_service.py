import uuid
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.db.models import (
    ArtifactType,
    Document,
    DocumentType,
    LinkType,
    RequirementInput,
    TraceabilityLink,
)
from app.schemas.traceability import (
    AutoLinkResult,
    CoverageStats,
    DocumentCoverage,
    RequirementInputSummary,
    TraceabilityLinkCreate,
    TraceabilityLinkResponse,
    TraceabilityMatrix,
)

# Document types that the 10-step pipeline is expected to produce
_PIPELINE_DOC_TYPES: list[DocumentType] = [
    DocumentType.requirement_summary,
    DocumentType.gap_analysis_report,
    DocumentType.brd,
    DocumentType.fsd,
    DocumentType.user_story,
    DocumentType.architecture_design,
    DocumentType.database_design,
    DocumentType.api_spec,
    DocumentType.screen_spec,
    DocumentType.code_task_list,
    DocumentType.test_cases,
    DocumentType.uat_script,
]


class TraceabilityService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_matrix(self, project_id: uuid.UUID) -> TraceabilityMatrix:
        req_inputs = self.session.exec(
            select(RequirementInput)
            .where(RequirementInput.project_id == project_id)
            .order_by(RequirementInput.created_at)
        ).all()

        documents = self.session.exec(
            select(Document)
            .where(Document.project_id == project_id)
            .order_by(Document.document_type, Document.created_at.desc())
        ).all()

        # Deduplicate: keep only the latest document per type
        seen: set[DocumentType] = set()
        unique_docs: list[Document] = []
        for doc in documents:
            if doc.document_type not in seen:
                seen.add(doc.document_type)
                unique_docs.append(doc)

        links = self.session.exec(
            select(TraceabilityLink)
            .where(TraceabilityLink.project_id == project_id)
            .order_by(TraceabilityLink.created_at)
        ).all()

        linked_req_ids = {
            lnk.source_id
            for lnk in links
            if lnk.source_type == ArtifactType.requirement_input
        }

        types_present = [d.document_type for d in unique_docs]
        types_missing = [t for t in _PIPELINE_DOC_TYPES if t not in types_present]
        coverage_pct = (
            round(len(types_present) / len(_PIPELINE_DOC_TYPES) * 100, 1)
            if _PIPELINE_DOC_TYPES else 0.0
        )

        return TraceabilityMatrix(
            project_id=project_id,
            requirement_inputs=[RequirementInputSummary.model_validate(r) for r in req_inputs],
            documents=[DocumentCoverage.model_validate(d) for d in unique_docs],
            links=[TraceabilityLinkResponse.model_validate(lnk) for lnk in links],
            coverage=CoverageStats(
                total_requirement_inputs=len(req_inputs),
                total_documents=len(unique_docs),
                linked_requirement_inputs=len(linked_req_ids),
                document_types_present=types_present,
                document_types_missing=types_missing,
                coverage_pct=coverage_pct,
            ),
        )

    def create_link(
        self, project_id: uuid.UUID, body: TraceabilityLinkCreate
    ) -> TraceabilityLinkResponse:
        # Prevent duplicate links
        existing = self.session.exec(
            select(TraceabilityLink).where(
                TraceabilityLink.project_id == project_id,
                TraceabilityLink.source_type == body.source_type,
                TraceabilityLink.source_id == body.source_id,
                TraceabilityLink.target_type == body.target_type,
                TraceabilityLink.target_id == body.target_id,
                TraceabilityLink.link_type == body.link_type,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail={"error_code": "DUPLICATE_LINK", "message": "Traceability link already exists"},
            )

        link = TraceabilityLink(
            project_id=project_id,
            source_type=body.source_type,
            source_id=body.source_id,
            target_type=body.target_type,
            target_id=body.target_id,
            link_type=body.link_type,
        )
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return TraceabilityLinkResponse.model_validate(link)

    def delete_link(self, project_id: uuid.UUID, link_id: uuid.UUID) -> None:
        link = self.session.get(TraceabilityLink, link_id)
        if not link or link.project_id != project_id:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "NOT_FOUND", "message": "Traceability link not found"},
            )
        self.session.delete(link)
        self.session.commit()

    def auto_link(self, project_id: uuid.UUID) -> AutoLinkResult:
        """Create derived_from links from every requirement_input to every document."""
        req_inputs = self.session.exec(
            select(RequirementInput).where(RequirementInput.project_id == project_id)
        ).all()

        documents = self.session.exec(
            select(Document).where(Document.project_id == project_id)
        ).all()

        existing_keys: set[tuple] = {
            (lnk.source_id, lnk.target_id, lnk.link_type)
            for lnk in self.session.exec(
                select(TraceabilityLink).where(TraceabilityLink.project_id == project_id)
            ).all()
        }

        created = 0
        skipped = 0
        for req in req_inputs:
            for doc in documents:
                key = (req.id, doc.id, LinkType.derived_from)
                if key in existing_keys:
                    skipped += 1
                    continue
                link = TraceabilityLink(
                    project_id=project_id,
                    source_type=ArtifactType.requirement_input,
                    source_id=req.id,
                    target_type=ArtifactType.document,
                    target_id=doc.id,
                    link_type=LinkType.derived_from,
                )
                self.session.add(link)
                existing_keys.add(key)
                created += 1

        self.session.commit()
        return AutoLinkResult(
            links_created=created,
            links_skipped=skipped,
            message=f"Auto-link complete: {created} links created, {skipped} already existed.",
        )

    def list_links(self, project_id: uuid.UUID) -> list[TraceabilityLinkResponse]:
        links = self.session.exec(
            select(TraceabilityLink)
            .where(TraceabilityLink.project_id == project_id)
            .order_by(TraceabilityLink.created_at)
        ).all()
        return [TraceabilityLinkResponse.model_validate(lnk) for lnk in links]

    def get_link(self, project_id: uuid.UUID, link_id: uuid.UUID) -> Optional[TraceabilityLinkResponse]:
        link = self.session.get(TraceabilityLink, link_id)
        if not link or link.project_id != project_id:
            return None
        return TraceabilityLinkResponse.model_validate(link)
