import base64
import uuid
from datetime import UTC, datetime
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.config import settings as app_settings
from app.db.models import ConnectorSetting, ConnectorType, LlmSetting
from app.db.session import get_session
from app.schemas.llm import (
    LlmKeyTestRequest,
    LlmKeyTestResponse,
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


@router.post("/llm/test-key", response_model=LlmKeyTestResponse)
def test_llm_api_key(body: LlmKeyTestRequest) -> LlmKeyTestResponse:
    """Test whether the given API key can reach the provider."""
    try:
        with httpx.Client(timeout=10.0) as client:
            if body.provider == "anthropic":
                resp = client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": body.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                if resp.status_code == 200:
                    return LlmKeyTestResponse(valid=True, message="API key is valid")
                if resp.status_code == 401:
                    return LlmKeyTestResponse(valid=False, message="Invalid API key — authentication failed")
                return LlmKeyTestResponse(valid=False, message=f"Anthropic returned {resp.status_code}")

            elif body.provider == "openai":
                resp = client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {body.api_key}"},
                )
                if resp.status_code == 200:
                    return LlmKeyTestResponse(valid=True, message="API key is valid")
                if resp.status_code == 401:
                    return LlmKeyTestResponse(valid=False, message="Invalid API key — authentication failed")
                return LlmKeyTestResponse(valid=False, message=f"OpenAI returned {resp.status_code}")

            else:
                return LlmKeyTestResponse(valid=False, message=f"Provider '{body.provider}' does not require an API key test")

    except httpx.TimeoutException:
        return LlmKeyTestResponse(valid=False, message="Request timed out — check your network connection")
    except httpx.HTTPError as exc:
        return LlmKeyTestResponse(valid=False, message=f"Network error: {exc}")


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


# ── Connector Settings ────────────────────────────────────────────────────────

# Metadata catalogue — defines what's shown even before a row exists in DB
_CONNECTOR_META: dict[str, dict[str, Any]] = {
    "github": {
        "display_name": "GitHub",
        "description":  "Connect to GitHub for branch, commit and pull-request automation.",
        "icon":         "github",
        "token_label":  "Personal Access Token",
        "token_hint":   "ghp_xxxxxxxxxxxxxxxxxxxx",
        "requires_token": True,
    },
    "figma": {
        "display_name": "Figma",
        "description":  "Allow UX Agent to push wireframes and read design context.",
        "icon":         "figma",
        "token_label":  "Personal Access Token",
        "token_hint":   "figd_xxxxxxxxxxxxxxxxxxxx",
        "requires_token": True,
    },
    "drawio": {
        "display_name": "Draw.io",
        "description":  "Generate architecture and ERD diagrams via local Draw.io desktop.",
        "icon":         "drawio",
        "token_label":  None,
        "token_hint":   None,
        "requires_token": False,
    },
    "jira": {
        "display_name": "Jira",
        "description":  "Sync requirements and user stories with Jira issues.",
        "icon":         "jira",
        "token_label":  "API Token",
        "token_hint":   "ATATT3xFfGF0...",
        "requires_token": True,
    },
}


class ConnectorResponse(BaseModel):
    connector_type: str
    display_name:   str
    description:    str
    icon:           str
    token_label:    Optional[str]
    token_hint:     Optional[str]
    requires_token: bool
    has_token:      bool
    last_tested_at: Optional[datetime]
    last_test_ok:   Optional[bool]
    last_error:     Optional[str]
    extra_config:   Optional[dict[str, Any]]


class ConnectorUpsert(BaseModel):
    access_token: Optional[str] = None
    extra_config: Optional[dict[str, Any]] = None


class ConnectorTestResponse(BaseModel):
    ok:      bool
    message: str


def _build_response(ctype: str, row: Optional[ConnectorSetting]) -> ConnectorResponse:
    meta = _CONNECTOR_META[ctype]
    return ConnectorResponse(
        connector_type=ctype,
        display_name=meta["display_name"],
        description=meta["description"],
        icon=meta["icon"],
        token_label=meta["token_label"],
        token_hint=meta["token_hint"],
        requires_token=meta["requires_token"],
        has_token=bool(row and row.access_token),
        last_tested_at=row.last_tested_at if row else None,
        last_test_ok=row.last_test_ok if row else None,
        last_error=row.last_error if row else None,
        extra_config=row.extra_config if row else None,
    )


def _test_connector(ctype: str, token: Optional[str], extra: Optional[dict]) -> ConnectorTestResponse:
    """Synchronously test a connector and return result."""
    if ctype == "drawio":
        return ConnectorTestResponse(ok=True, message="Draw.io does not require authentication.")

    if not token:
        return ConnectorTestResponse(ok=False, message="No access token configured.")

    try:
        with httpx.Client(timeout=10.0) as client:
            if ctype == "github":
                resp = client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                )
                if resp.status_code == 200:
                    login = resp.json().get("login", "unknown")
                    return ConnectorTestResponse(ok=True, message=f"Connected as @{login}")
                if resp.status_code == 401:
                    return ConnectorTestResponse(ok=False, message="Invalid token — authentication failed.")
                return ConnectorTestResponse(ok=False, message=f"GitHub returned {resp.status_code}")

            elif ctype == "figma":
                resp = client.get(
                    "https://api.figma.com/v1/me",
                    headers={"X-Figma-Token": token},
                )
                if resp.status_code == 200:
                    name = resp.json().get("name", "unknown")
                    return ConnectorTestResponse(ok=True, message=f"Connected as {name}")
                if resp.status_code == 403:
                    return ConnectorTestResponse(ok=False, message="Invalid token — authentication failed.")
                return ConnectorTestResponse(ok=False, message=f"Figma returned {resp.status_code}")

            elif ctype == "jira":
                domain = (extra or {}).get("domain", "")
                email  = (extra or {}).get("email", "")
                if not domain or not email:
                    return ConnectorTestResponse(ok=False, message="Jira requires domain and email in extra_config.")
                creds = base64.b64encode(f"{email}:{token}".encode()).decode()
                resp = client.get(
                    f"https://{domain}.atlassian.net/rest/api/3/myself",
                    headers={"Authorization": f"Basic {creds}", "Accept": "application/json"},
                )
                if resp.status_code == 200:
                    display = resp.json().get("displayName", "unknown")
                    return ConnectorTestResponse(ok=True, message=f"Connected as {display}")
                if resp.status_code == 401:
                    return ConnectorTestResponse(ok=False, message="Invalid credentials.")
                return ConnectorTestResponse(ok=False, message=f"Jira returned {resp.status_code}")

    except httpx.TimeoutException:
        return ConnectorTestResponse(ok=False, message="Request timed out.")
    except httpx.HTTPError as exc:
        return ConnectorTestResponse(ok=False, message=f"Network error: {exc}")

    return ConnectorTestResponse(ok=False, message="Unknown connector type.")


@router.get("/connectors", response_model=list[ConnectorResponse])
def list_connectors(session: Session = Depends(get_session)):
    rows = {
        r.connector_type: r
        for r in session.exec(select(ConnectorSetting)).all()
    }
    return [_build_response(ctype, rows.get(ctype)) for ctype in _CONNECTOR_META]


@router.put("/connectors/{connector_type}", response_model=ConnectorResponse)
def upsert_connector(
    connector_type: str,
    body: ConnectorUpsert,
    session: Session = Depends(get_session),
):
    if connector_type not in _CONNECTOR_META:
        raise HTTPException(status_code=404, detail={"error_code": "UNKNOWN_CONNECTOR", "message": f"Unknown connector: {connector_type}"})

    row = session.exec(
        select(ConnectorSetting).where(ConnectorSetting.connector_type == connector_type)
    ).first()

    if row is None:
        row = ConnectorSetting(connector_type=ConnectorType(connector_type))
        session.add(row)

    if body.access_token is not None:
        row.access_token = body.access_token or None
    if body.extra_config is not None:
        row.extra_config = body.extra_config
    row.updated_at = datetime.now(UTC)

    session.commit()
    session.refresh(row)
    return _build_response(connector_type, row)


@router.post("/connectors/{connector_type}/test", response_model=ConnectorTestResponse)
def test_connector(connector_type: str, session: Session = Depends(get_session)):
    if connector_type not in _CONNECTOR_META:
        raise HTTPException(status_code=404, detail={"error_code": "UNKNOWN_CONNECTOR", "message": f"Unknown connector: {connector_type}"})

    row = session.exec(
        select(ConnectorSetting).where(ConnectorSetting.connector_type == connector_type)
    ).first()

    result = _test_connector(connector_type, row.access_token if row else None, row.extra_config if row else None)

    # Persist test result
    if row is None:
        row = ConnectorSetting(connector_type=ConnectorType(connector_type))
        session.add(row)
    row.last_tested_at = datetime.now(UTC)
    row.last_test_ok   = result.ok
    row.last_error     = None if result.ok else result.message
    row.updated_at     = datetime.now(UTC)
    session.commit()

    return result


@router.delete("/connectors/{connector_type}", status_code=204)
def delete_connector(connector_type: str, session: Session = Depends(get_session)):
    row = session.exec(
        select(ConnectorSetting).where(ConnectorSetting.connector_type == connector_type)
    ).first()
    if row:
        session.delete(row)
        session.commit()
