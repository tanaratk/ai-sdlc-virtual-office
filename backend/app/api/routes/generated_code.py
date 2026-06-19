"""Generated Code API -- file tree, file content, ZIP download."""
import io
import os
import re
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.db.models import Project
from app.db.session import get_session

router = APIRouter()

# Extension → language name (for frontend highlighting hint)
_EXT_LANG: dict[str, str] = {
    ".py":         "python",
    ".ts":         "typescript",
    ".tsx":        "tsx",
    ".js":         "javascript",
    ".jsx":        "jsx",
    ".sql":        "sql",
    ".yml":        "yaml",
    ".yaml":       "yaml",
    ".json":       "json",
    ".md":         "markdown",
    ".toml":       "toml",
    ".sh":         "bash",
    ".bash":       "bash",
    ".env":        "bash",
    ".txt":        "text",
    ".dockerfile": "dockerfile",
    "":            "text",
}


def _lang(path: str) -> str:
    ext = Path(path).suffix.lower()
    # Handle Dockerfile (no extension)
    if Path(path).name.lower().startswith("dockerfile"):
        return "dockerfile"
    return _EXT_LANG.get(ext, "text")


def _resolve_generated_dir(project: Project) -> Optional[str]:
    """Return the absolute path to generated_app/ for this project, or None."""
    raw = (project.workspace_path or "/workspace")

    # Translate Windows host path → container mount point
    container_path = re.sub(
        r"^[A-Za-z]:[/\\]workspace", "/workspace", raw, flags=re.IGNORECASE
    )
    if not container_path.startswith("/workspace"):
        container_path = "/workspace"

    safe_name = re.sub(r"[^\w\-]", "_", project.name or "project")
    return os.path.join(container_path, safe_name, "generated_app")


def _safe_path(base_dir: str, rel_path: str) -> str:
    """Resolve rel_path under base_dir and raise 400 on path traversal."""
    # Strip leading slashes and collapse traversal sequences
    clean = re.sub(r"\.\.+[/\\]", "", rel_path).lstrip("/\\")
    full = os.path.realpath(os.path.join(base_dir, clean))
    real_base = os.path.realpath(base_dir)
    if not full.startswith(real_base):
        raise HTTPException(status_code=400, detail="Invalid file path.")
    return full


# -- Schemas ------------------------------------------------------------------

class FileEntry(BaseModel):
    path: str       # relative to generated_app/
    size: int
    lang: str


class FileTreeResponse(BaseModel):
    base_dir: str
    files: list[FileEntry]
    exists: bool


class FileContentResponse(BaseModel):
    path: str
    lang: str
    content: str
    size: int


# -- Endpoints ----------------------------------------------------------------

@router.get("/{project_id}/generated-code/tree", response_model=FileTreeResponse)
def get_file_tree(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> FileTreeResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    gen_dir = _resolve_generated_dir(project)

    if not gen_dir or not os.path.isdir(gen_dir):
        return FileTreeResponse(base_dir=gen_dir or "", files=[], exists=False)

    entries: list[FileEntry] = []
    for root, _dirs, files in os.walk(gen_dir):
        for fname in sorted(files):
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, gen_dir).replace("\\", "/")
            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0
            entries.append(FileEntry(path=rel, size=size, lang=_lang(rel)))

    entries.sort(key=lambda e: e.path)
    return FileTreeResponse(base_dir=gen_dir, files=entries, exists=True)


@router.get("/{project_id}/generated-code/file", response_model=FileContentResponse)
def get_file_content(
    project_id: uuid.UUID,
    path: str = Query(..., description="Relative file path inside generated_app/"),
    session: Session = Depends(get_session),
) -> FileContentResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    gen_dir = _resolve_generated_dir(project)
    if not gen_dir or not os.path.isdir(gen_dir):
        raise HTTPException(status_code=404, detail="No generated code found for this project.")

    full_path = _safe_path(gen_dir, path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        with open(full_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {exc}") from exc

    rel = path.replace("\\", "/").lstrip("/")
    return FileContentResponse(
        path=rel,
        lang=_lang(rel),
        content=content,
        size=len(content.encode("utf-8")),
    )


@router.get("/{project_id}/generated-code/download")
def download_zip(
    project_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    gen_dir = _resolve_generated_dir(project)
    if not gen_dir or not os.path.isdir(gen_dir):
        raise HTTPException(status_code=404, detail="No generated code found for this project.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(gen_dir):
            for fname in files:
                full = os.path.join(root, fname)
                arcname = os.path.relpath(full, os.path.dirname(gen_dir)).replace("\\", "/")
                zf.write(full, arcname)

    buf.seek(0)
    safe_name = re.sub(r"[^\w\-]", "_", project.name or "project")
    filename = f"{safe_name}_generated_app.zip"

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
