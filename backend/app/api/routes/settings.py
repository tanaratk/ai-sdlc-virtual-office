from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "LLM settings routes — Sprint 8"})


@router.get("/llm")
def list_llm_settings():
    raise _NOT_IMPL


@router.post("/llm", status_code=201)
def create_llm_setting():
    raise _NOT_IMPL


@router.patch("/llm/{setting_id}")
def update_llm_setting(setting_id: str):
    raise _NOT_IMPL


@router.post("/llm/{setting_id}/activate")
def activate_llm_setting(setting_id: str):
    raise _NOT_IMPL
