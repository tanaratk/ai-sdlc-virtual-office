import uuid
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.config import settings as app_settings
from app.db.models import LlmSetting
from app.db.session import get_session
from app.schemas.llm import LlmSettingCreate, LlmSettingResponse, OllamaModel, OllamaModelsResponse

router = APIRouter()


@router.get("/llm", response_model=list[LlmSettingResponse])
def list_llm_settings(session: Session = Depends(get_session)):
    rows = session.exec(select(LlmSetting).order_by(LlmSetting.created_at.desc())).all()
    return [LlmSettingResponse.model_validate(r) for r in rows]


@router.post("/llm", response_model=LlmSettingResponse, status_code=201)
def create_llm_setting(body: LlmSettingCreate, session: Session = Depends(get_session)):
    row = LlmSetting(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return LlmSettingResponse.model_validate(row)


@router.post("/llm/{setting_id}/activate", response_model=LlmSettingResponse)
def activate_llm_setting(setting_id: uuid.UUID, session: Session = Depends(get_session)):
    target = session.get(LlmSetting, setting_id)
    if not target:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "LLM setting not found"})

    # Deactivate all, then activate target
    all_rows = session.exec(select(LlmSetting)).all()
    for row in all_rows:
        row.is_active = row.id == setting_id
        row.updated_at = datetime.now(UTC)
        session.add(row)
    session.commit()
    session.refresh(target)
    return LlmSettingResponse.model_validate(target)


@router.get("/llm/models", response_model=OllamaModelsResponse)
def list_ollama_models():
    """Proxy Ollama /api/tags to list available models."""
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
