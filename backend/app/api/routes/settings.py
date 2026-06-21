import uuid
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.config import settings as app_settings
from app.db.models import LlmSetting
from app.db.session import get_session
from app.schemas.llm import (
    LlmSettingCreate,
    LlmSettingResponse,
    LlmSettingUpdate,
    OllamaModel,
    OllamaModelsResponse,
)

router = APIRouter()


def _to_response(row: LlmSetting) -> LlmSettingResponse:
    r = LlmSettingResponse.model_validate(row)
    r.has_api_key = bool(row.api_key_encrypted)
    return r


@router.get("/llm", response_model=list[LlmSettingResponse])
def list_llm_settings(session: Session = Depends(get_session)):
    rows = session.exec(select(LlmSetting).order_by(LlmSetting.created_at.desc())).all()
    return [_to_response(r) for r in rows]


@router.post("/llm", response_model=LlmSettingResponse, status_code=201)
def create_llm_setting(body: LlmSettingCreate, session: Session = Depends(get_session)):
    data = body.model_dump(exclude={"api_key"})
    row = LlmSetting(**data)
    if body.api_key:
        row.api_key_encrypted = body.api_key
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_response(row)


@router.patch("/llm/{setting_id}", response_model=LlmSettingResponse)
def update_llm_setting(
    setting_id: uuid.UUID,
    body: LlmSettingUpdate,
    session: Session = Depends(get_session),
):
    row = session.get(LlmSetting, setting_id)
    if not row:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "LLM setting not found"})

    if body.is_active is not None:
        row.is_active = body.is_active
    if body.api_key is not None:
        row.api_key_encrypted = body.api_key if body.api_key else None
    if body.temperature is not None:
        row.temperature = body.temperature
    if body.max_tokens is not None:
        row.max_tokens = body.max_tokens

    row.updated_at = datetime.now(UTC)
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_response(row)


@router.post("/llm/{setting_id}/activate", response_model=LlmSettingResponse)
def activate_llm_setting(setting_id: uuid.UUID, session: Session = Depends(get_session)):
    target = session.get(LlmSetting, setting_id)
    if not target:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "LLM setting not found"})

    all_rows = session.exec(select(LlmSetting)).all()
    for row in all_rows:
        row.is_active = row.id == setting_id
        row.updated_at = datetime.now(UTC)
        session.add(row)
    session.commit()
    session.refresh(target)
    return _to_response(target)


@router.get("/llm/models", response_model=OllamaModelsResponse)
def list_ollama_models():
    base_url = app_settings.ollama_base_url
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail={"error_code": "OLLAMA_UNAVAILABLE", "message": f"Cannot reach Ollama at {base_url}: {exc}"},
        ) from exc

    models = [
        OllamaModel(
            name=m.get("name", ""),
            size=m.get("size"),
            modified_at=m.get("modified_at"),
        )
        for m in data.get("models", [])
    ]
    return OllamaModelsResponse(models=models, base_url=base_url)
