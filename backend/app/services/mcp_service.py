"""MCP tool executor โ€” runs approved tool calls.

Each tool either executes real logic (github.* tools via github_service)
or returns a stub result for tools not yet implemented.
Agents will be wired to this service when LangGraph is added.
"""
import logging
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from app.db.models import (
    GitHubSetting,
    McpCallStatus,
    McpToolCall,
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


def execute_call(call: McpToolCall, session: Session) -> dict[str, Any]:
    """Execute a single approved MCP tool call. Returns output dict."""
    handlers = {
        "github.create_issue": _exec_github_create_issue,
        "github.create_branch": _exec_github_create_branch,
        "github.list_issues":   _exec_github_list_issues,
    }
    handler = handlers.get(call.tool_name)
    if handler:
        return handler(call, session)
    return _stub_result(call.tool_name)


# โ”€โ”€ GitHub executors โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

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


# โ”€โ”€ Stub โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _stub_result(tool_name: str) -> dict[str, Any]:
    return {
        "status": "not_implemented",
        "message": (
            f"Tool '{tool_name}' is registered but execution is not yet wired. "
            "Will be implemented in a future sprint."
        ),
    }


# โ”€โ”€ Call lifecycle helper โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

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
