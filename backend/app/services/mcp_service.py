"""MCP tool executor -- runs approved tool calls.

Each tool either executes real logic (github.* / figma.* tools)
or returns a stub result for tools not yet implemented.
"""
import logging
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from app.db.models import (
    ConnectorSetting,
    ConnectorType,
    FigmaSetting,
    GitHubSetting,
    McpCallStatus,
    McpToolCall,
)
from app.db.models import Document, DocumentType
from app.services.diagram_service import extract_mermaid, mermaid_to_drawio_xml
from app.services.figma_service import (
    FigmaServiceError,
    extract_file_key,
    get_design_detail,
    get_node,
    push_comment,
)
from app.services.github_service import (
    GitHubRepo,
    GitHubServiceError,
    create_branch,
    create_issue,
    list_issues,
)

logger = logging.getLogger(__name__)


class McpExecutionError(Exception):
    pass


IMPLEMENTED_TOOLS: frozenset[str] = frozenset({
    "github.create_issue",
    "github.create_branch",
    "github.list_issues",
    "figma.get_design",
    "figma.get_node",
    "figma.push_comment",
    "drawio.export_diagram",
    "drawio.list_diagrams",
})


def execute_call(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Execute a single approved MCP tool call. Returns output dict."""
    handlers = {
        "github.create_issue":  _exec_github_create_issue,
        "github.create_branch": _exec_github_create_branch,
        "github.list_issues":   _exec_github_list_issues,
        "figma.get_design":     _exec_figma_get_design,
        "figma.get_node":       _exec_figma_get_node,
        "figma.push_comment":   _exec_figma_push_comment,
        "drawio.export_diagram": _exec_drawio_export_diagram,
        "drawio.list_diagrams":  _exec_drawio_list_diagrams,
    }
    handler = handlers.get(call.tool_name)
    if handler:
        return handler(call, session)
    return _stub_result(call.tool_name)


# -- GitHub executors ---------------------------------------------------------

def _get_github_repo(call: McpToolCall, session: Session) -> GitHubRepo:
    setting = session.exec(
        select(GitHubSetting).where(GitHubSetting.project_id == call.project_id)
    ).first()
    if not setting:
        raise McpExecutionError(
            "GitHub not configured for this project. "
            "Go to GitHub settings first."
        )
    return GitHubRepo(
        owner=setting.repo_owner,
        name=setting.repo_name,
        token=setting.access_token,
        default_branch=setting.default_branch,
    )


def _exec_github_create_issue(call: McpToolCall, session: Session) -> dict[str, Any]:
    repo = _get_github_repo(call, session)
    params = call.input_json or {}
    title = params.get("title", "AI-SDLC Generated Issue")
    body = params.get("body", "")
    labels = params.get("labels", ["ai-sdlc"])
    try:
        result = create_issue(repo, title=title, body=body, labels=labels)
        return {"status": "created", **result}
    except GitHubServiceError as e:
        raise McpExecutionError(str(e))


def _exec_github_create_branch(call: McpToolCall, session: Session) -> dict[str, Any]:
    repo = _get_github_repo(call, session)
    params = call.input_json or {}
    branch_name = params.get("branch_name", "")
    if not branch_name:
        raise McpExecutionError("branch_name is required in input_json")
    try:
        result = create_branch(
            repo, branch_name=branch_name,
            from_branch=params.get("from_branch")
        )
        return {"status": "created", **result}
    except GitHubServiceError as e:
        raise McpExecutionError(str(e))


def _exec_github_list_issues(call: McpToolCall, session: Session) -> dict[str, Any]:
    repo = _get_github_repo(call, session)
    params = call.input_json or {}
    try:
        issues = list_issues(repo, state=params.get("state", "open"))
        return {"status": "ok", "count": len(issues), "issues": issues}
    except GitHubServiceError as e:
        raise McpExecutionError(str(e))


# -- Figma helpers ------------------------------------------------------------

def _get_figma_token(session: Session) -> str:
    """Retrieve Figma PAT from global connector_settings."""
    row = session.exec(
        select(ConnectorSetting).where(ConnectorSetting.connector_type == ConnectorType.figma)
    ).first()
    if not row or not row.access_token:
        raise McpExecutionError(
            "Figma token not configured. "
            "Go to Settings -> Connectors -> Figma and save a Personal Access Token first."
        )
    return row.access_token


def _resolve_figma_file_key(params: dict, call: McpToolCall, session: Session) -> str:
    """
    Resolve Figma file key from:
    1. input_json.file_url or input_json.file_key  (explicit override)
    2. Project-linked figma_settings               (default)
    """
    if file_url := params.get("file_url"):
        try:
            return extract_file_key(file_url)
        except FigmaServiceError as e:
            raise McpExecutionError(str(e))
    if file_key := params.get("file_key"):
        return file_key

    # Fall back to project-linked file
    setting = session.exec(
        select(FigmaSetting).where(FigmaSetting.project_id == call.project_id)
    ).first()
    if not setting:
        raise McpExecutionError(
            "No Figma file linked to this project and no file_url in input. "
            "Either link a file in the project Figma tab, "
            "or pass {\"file_url\": \"https://www.figma.com/file/...\"} in the input."
        )
    return setting.file_key


# -- Figma executors ----------------------------------------------------------

def _exec_figma_get_design(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Fetch design info: file name, pages, optional node details."""
    token = _get_figma_token(session)
    params = call.input_json or {}
    file_key = _resolve_figma_file_key(params, call, session)
    node_id = params.get("node_id")
    try:
        result = get_design_detail(file_key, token, node_id=node_id)
        return {"status": "ok", **result}
    except FigmaServiceError as e:
        raise McpExecutionError(str(e))


def _exec_figma_get_node(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Fetch a specific Figma node by node_id."""
    token = _get_figma_token(session)
    params = call.input_json or {}
    file_key = _resolve_figma_file_key(params, call, session)
    node_id = params.get("node_id", "")
    if not node_id:
        raise McpExecutionError("node_id is required in input_json for figma.get_node")
    try:
        node = get_node(file_key, node_id, token)
        return {"status": "ok", "file_key": file_key, "node": node}
    except FigmaServiceError as e:
        raise McpExecutionError(str(e))


def _exec_figma_push_comment(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Post a comment on a Figma file."""
    token = _get_figma_token(session)
    params = call.input_json or {}
    file_key = _resolve_figma_file_key(params, call, session)
    message = params.get("message", "")
    if not message:
        raise McpExecutionError("message is required in input_json for figma.push_comment")
    try:
        result = push_comment(file_key, token, message)
        return {"status": "posted", "file_key": file_key, **result}
    except FigmaServiceError as e:
        raise McpExecutionError(str(e))


# -- Draw.io executors --------------------------------------------------------

def _exec_drawio_list_diagrams(call: McpToolCall, session: Session) -> dict[str, Any]:
    """List generated diagram documents for the project."""
    docs = session.exec(
        select(Document).where(
            Document.project_id == call.project_id,
            Document.document_type == DocumentType.diagram_spec,
        ).order_by(Document.created_at.desc())
    ).all()
    return {
        "status": "ok",
        "count": len(docs),
        "diagrams": [
            {"id": str(d.id), "title": d.title, "created_at": d.created_at.isoformat()}
            for d in docs
        ],
    }


def _exec_drawio_export_diagram(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Export a project's Mermaid diagram as Draw.io XML."""
    params = call.input_json or {}
    diagram_title = params.get("title", "")

    query = select(Document).where(
        Document.project_id == call.project_id,
        Document.document_type == DocumentType.diagram_spec,
    ).order_by(Document.created_at.desc())
    docs = session.exec(query).all()

    if not docs:
        raise McpExecutionError(
            "No diagrams found for this project. "
            "Generate diagrams first from the Diagrams tab in the project workspace."
        )

    # Filter by title keyword if given
    doc = next(
        (d for d in docs if diagram_title.lower() in d.title.lower()),
        docs[0],
    )

    mermaid_code = extract_mermaid(doc.content_markdown)
    xml = mermaid_to_drawio_xml(mermaid_code)
    filename = doc.title.lower().replace(" ", "_").replace("(", "").replace(")", "") + ".drawio"

    return {
        "status": "ok",
        "diagram_id": str(doc.id),
        "title": doc.title,
        "filename": filename,
        "drawio_xml": xml,
        "instructions": (
            "Save the 'drawio_xml' content as a .drawio file, "
            "then open it in https://app.diagrams.net or the Draw.io desktop app."
        ),
    }


# -- Stub ---------------------------------------------------------------------

def _stub_result(tool_name: str) -> dict[str, Any]:
    return {
        "status": "not_implemented",
        "message": (
            f"Tool '{tool_name}' is registered but execution is not yet wired. "
            "Will be implemented in a future sprint."
        ),
    }


# -- Call lifecycle helper ----------------------------------------------------

def run_call(call: McpToolCall, session: Session) -> McpToolCall:
    """Execute a call and update its status in the DB. Returns updated call."""
    call.status = McpCallStatus.running
    session.commit()

    try:
        output = execute_call(call, session)
        call.status = McpCallStatus.completed
        call.output_json = output
        logger.info("MCP call %s completed: %s", call.id, call.tool_name)
    except McpExecutionError as exc:
        call.status = McpCallStatus.failed
        call.error_message = str(exc)
        logger.warning("MCP call %s failed: %s", call.id, exc)
    except Exception as exc:
        call.status = McpCallStatus.failed
        call.error_message = f"Unexpected error: {exc}"
        logger.exception("MCP call %s unexpected error", call.id)
    finally:
        call.resolved_at = datetime.now(UTC)
        session.commit()
        session.refresh(call)

    return call
