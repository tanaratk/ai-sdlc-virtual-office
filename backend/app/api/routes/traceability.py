from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPL = HTTPException(status_code=501, detail={"error_code": "NOT_IMPLEMENTED", "message": "Traceability routes — Sprint 15"})


@router.get("/{project_id}/traceability")
def get_traceability_matrix(project_id: str):
    raise _NOT_IMPL


@router.post("/{project_id}/traceability/links", status_code=201)
def create_traceability_link(project_id: str):
    raise _NOT_IMPL


@router.delete("/{project_id}/traceability/links/{link_id}", status_code=204)
def delete_traceability_link(project_id: str, link_id: str):
    raise _NOT_IMPL
