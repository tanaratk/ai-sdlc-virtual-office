"""Figma Integration API — /projects/{project_id}/figma/..."""
import uuid
from datetime import UTC, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.models import ConnectorSetting, ConnectorType, Document, DocumentType, FigmaSetting, Project
from app.db.session import get_session
from app.services.figma_service import (
    FigmaServiceError,
    ParsedScreen,
    build_comment_for_screen,
    extract_file_key,
    get_file_info,
    parse_screens_from_spec,
    push_comment,
)

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_project_or_404(session: Session, project_id: uuid.UUID) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_figma_token(session: Session) -> str:
    """Retrieve Figma PAT from the global ConnectorSetting (Sprint 47)."""
    row = session.exec(
        select(ConnectorSetting).where(ConnectorSetting.connector_type == ConnectorType.figma)
    ).first()
    if not row or not row.access_token:
        raise HTTPException(
            status_code=400,
            detail="Figma token not configured. Go to Settings → Connectors and save a Figma PAT first.",
        )
    return row.access_token


def _get_setting_or_none(session: Session, project_id: uuid.UUID) -> Optional[FigmaSetting]:
    return session.exec(
        select(FigmaSetting).where(FigmaSetting.project_id == project_id)
    ).first()


# ── Request / Response schemas ────────────────────────────────────────────────

class FigmaSettingUpsert(BaseModel):
    file_url: str     # full Figma URL or raw file key


class FigmaSettingResponse(BaseModel):
    id:         uuid.UUID
    project_id: uuid.UUID
    file_key:   str
    file_url:   str
    file_name:  Optional[str]
    embed_url:  str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FigmaScreenResponse(BaseModel):
    screen_id:   str
    name:        str
    description: str
    components:  list[str]


class PushScreensResponse(BaseModel):
    pushed:  int
    skipped: int
    errors:  list[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

def _to_response(s: FigmaSetting) -> FigmaSettingResponse:
    embed_url = f"https://www.figma.com/embed?embed_host=astra&url={s.file_url}"
    return FigmaSettingResponse(
        id=s.id,
        project_id=s.project_id,
        file_key=s.file_key,
        file_url=s.file_url,
        file_name=s.file_name,
        embed_url=embed_url,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.get(
    "/{project_id}/figma",
    response_model=Optional[FigmaSettingResponse],
    summary="Get Figma file linked to this project",
)
def get_figma_setting(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
):
    _get_project_or_404(session, project_id)
    s = _get_setting_or_none(session, project_id)
    return _to_response(s) if s else None


@router.put(
    "/{project_id}/figma",
    response_model=FigmaSettingResponse,
    summary="Link a Figma file to this project (verifies connection)",
)
def upsert_figma_setting(
    project_id: uuid.UUID,
    body: FigmaSettingUpsert,
    session: Annotated[Session, Depends(get_session)],
) -> FigmaSettingResponse:
    _get_project_or_404(session, project_id)
    token = _get_figma_token(session)

    try:
        file_key = extract_file_key(body.file_url)
        info = get_file_info(file_key, token)
    except FigmaServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    existing = _get_setting_or_none(session, project_id)
    now = datetime.now(UTC)

    if existing:
        existing.file_key  = file_key
        existing.file_url  = body.file_url
        existing.file_name = info["name"]
        existing.updated_at = now
        session.commit()
        session.refresh(existing)
        return _to_response(existing)

    s = FigmaSetting(
        project_id=project_id,
        file_key=file_key,
        file_url=body.file_url,
        file_name=info["name"],
    )
    session.add(s)
    session.commit()
    session.refresh(s)
    return _to_response(s)


@router.delete("/{project_id}/figma", status_code=204, summary="Unlink Figma file from project")
def delete_figma_setting(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
):
    s = _get_setting_or_none(session, project_id)
    if s:
        session.delete(s)
        session.commit()


@router.get(
    "/{project_id}/figma/screens",
    response_model=list[FigmaScreenResponse],
    summary="Parse UX Agent screen spec into a list of screens",
)
def list_figma_screens(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> list[FigmaScreenResponse]:
    _get_project_or_404(session, project_id)

    doc = session.exec(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.screen_spec,
        )
        .order_by(Document.created_at.desc())
    ).first()

    if not doc:
        return []

    screens = parse_screens_from_spec(doc.content_markdown or "")
    return [
        FigmaScreenResponse(
            screen_id=s.screen_id,
            name=s.name,
            description=s.description,
            components=s.components,
        )
        for s in screens
    ]


@router.post(
    "/{project_id}/figma/push-screens",
    response_model=PushScreensResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Push UX Agent screen specs as annotations (comments) on the linked Figma file",
)
def push_screens_to_figma(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> PushScreensResponse:
    project = _get_project_or_404(session, project_id)
    token = _get_figma_token(session)

    s = _get_setting_or_none(session, project_id)
    if not s:
        raise HTTPException(
            status_code=400,
            detail="No Figma file linked to this project. Link a file first.",
        )

    doc = session.exec(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.document_type == DocumentType.screen_spec,
        )
        .order_by(Document.created_at.desc())
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="No screen spec document found. Run the UX Agent pipeline step first.",
        )

    screens: list[ParsedScreen] = parse_screens_from_spec(doc.content_markdown or "")
    if not screens:
        raise HTTPException(
            status_code=404,
            detail="Could not parse any screens from the screen spec document.",
        )

    pushed = 0
    skipped = 0
    errors: list[str] = []

    for screen in screens:
        try:
            message = build_comment_for_screen(screen, project.name or "Project")
            push_comment(s.file_key, token, message)
            pushed += 1
        except FigmaServiceError as exc:
            errors.append(f"{screen.screen_id} ({screen.name}): {exc}")
            skipped += 1

    return PushScreensResponse(pushed=pushed, skipped=skipped, errors=errors)
