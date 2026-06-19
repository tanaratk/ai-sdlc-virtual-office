"""Workspace file-system utilities shared across all document agents.

Each agent calls write_workspace_docs() after committing to DB.
Files land in: {workspace}/{project_name}/docs/<filename>
Dev-agent code goes to:  {workspace}/{project_name}/generated_app/
"""
import logging
import os
import re
import uuid

logger = logging.getLogger(__name__)

_WIN_WORKSPACE_RE = re.compile(r"^[A-Za-z]:[/\\]workspace", re.IGNORECASE)


def _docs_dir(session, project_id: uuid.UUID) -> str:
    from app.db.models import Project

    project = session.get(Project, project_id)
    raw = (project.workspace_path if project else None) or "/workspace"

    container_path = _WIN_WORKSPACE_RE.sub("/workspace", raw)
    if not container_path.startswith("/workspace"):
        container_path = "/workspace"

    safe_name = re.sub(r"[^\w\-]", "_", project.name if project else "project")
    return os.path.join(container_path, safe_name, "docs")


def write_workspace_docs(
    session,
    project_id: uuid.UUID,
    files: dict[str, str],
) -> None:
    """Write {filename: markdown_content} to workspace docs dir.

    Failures are logged as warnings — never raise so the pipeline is not blocked.
    """
    try:
        docs_dir = _docs_dir(session, project_id)
        os.makedirs(docs_dir, exist_ok=True)
        for filename, content in files.items():
            path = os.path.join(docs_dir, filename)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            logger.info("workspace doc written: %s", path)
    except Exception as exc:
        logger.warning("write_workspace_docs failed project=%s: %s", project_id, exc)
