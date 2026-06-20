"""MCP API โ€” tool registry and call management."""
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import (
    McpCallStatus,
    McpTool,
    McpToolCall,
    Project,
)
from app.services.mcp_service import run_call

# Global tool registry (prefix: none  โ’ /mcp/tools/...)
tool_router = APIRouter()

# Per-project call management (prefix: /projects โ’ /projects/{project_id}/mcp/...)
call_router = APIRouter()


# โ”€โ”€ Schemas โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

class McpToolResponse(BaseModel):
    id: uuid.UUID
    tool_name: str
    display_name: str
    description: str
    category: str
    requires_approval: bool
    is_enabled: bool
    is_dangerous: bool

    model_config = {"from_attributes": True}


class McpToolUpdate(BaseModel):
    is_enabled: bool


class McpToolCallResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    tool_name: str
    agent_id: Optional[uuid.UUID]
    status: str
    input_json: Optional[dict[str, Any]]
    output_json: Optional[dict[str, Any]]
    error_message: Optional[str]
    requested_by: Optional[str]
    resolved_by: Optional[str]
    requested_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}


class InvokeRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=100)
    input_json: Optional[dict[str, Any]] = None
    requested_by: str = Field(default="user", min_length=1, max_length=255)


class ResolveRequest(BaseModel):
    resolved_by: str = "user"


# โ”€โ”€ Tool registry (global) โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

@tool_router.get(
    "/mcp/tools",
    response_model=list[McpToolResponse],
    summary="List all registered MCP tools",
)
def list_mcp_tools(
    session: Annotated[Session, Depends(get_session)],
) -> list[McpToolResponse]:
    tools = session.exec(select(McpTool).order_by(McpTool.category, McpTool.tool_name)).all()
    return [McpToolResponse.model_validate(t) for t in tools]


@tool_router.patch(
    "/mcp/tools/{tool_name}",
    response_model=McpToolResponse,
    summary="Enable or disable a tool",
)
def update_mcp_tool(
    tool_name: str,
    body: McpToolUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> McpToolResponse:
    tool = session.exec(
        select(McpTool).where(McpTool.tool_name == tool_name)
    ).first()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    tool.is_enabled = body.is_enabled
    tool.updated_at = datetime.now(UTC)
    session.commit()
    session.refresh(tool)
    return McpToolResponse.model_validate(tool)


# โ”€โ”€ Per-project call routes โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

@call_router.get(
    "/{project_id}/mcp/calls",
    response_model=list[McpToolCallResponse],
    summary="List MCP tool calls for a project",
)
def list_mcp_calls(
    project_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    status_filter: Optional[str] = None,
) -> list[McpToolCallResponse]:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    q = select(McpToolCall).where(McpToolCall.project_id == project_id)
    if status_filter:
        try:
            q = q.where(McpToolCall.status == McpCallStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
    q = q.order_by(McpToolCall.requested_at.desc())
    calls = session.exec(q).all()

    return [
        McpToolCallResponse(
            id=str(c.id),
            project_id=str(c.project_id),
            tool_name=c.tool_name,
            agent_id=str(c.agent_id) if c.agent_id else None,
            status=c.status,
            input_json=c.input_json,
            output_json=c.output_json,
            error_message=c.error_message,
            requested_by=c.requested_by,
            resolved_by=c.resolved_by,
            requested_at=c.requested_at,
            resolved_at=c.resolved_at,
        )
        for c in calls
    ]


@call_router.post(
    "/{project_id}/mcp/invoke",
    response_model=McpToolCallResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invoke an MCP tool for a project",
)
def invoke_mcp_tool(
    project_id: uuid.UUID,
    body: InvokeRequest,
    session: Annotated[Session, Depends(get_session)],
) -> McpToolCallResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tool = session.exec(
        select(McpTool).where(McpTool.tool_name == body.tool_name)
    ).first()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{body.tool_name}' not found")
    if not tool.is_enabled:
        raise HTTPException(status_code=400, detail=f"Tool '{body.tool_name}' is disabled")

    call = McpToolCall(
        project_id=project_id,
        tool_name=body.tool_name,
        input_json=body.input_json,
        requested_by=body.requested_by,
        status=McpCallStatus.pending,
    )
    session.add(call)
    session.commit()
    session.refresh(call)

    # Auto-execute if tool does not require approval
    if not tool.requires_approval:
        call = run_call(call, session)

    return McpToolCallResponse(
        id=str(call.id),
        project_id=str(call.project_id),
        tool_name=call.tool_name,
        agent_id=str(call.agent_id) if call.agent_id else None,
        status=call.status,
        input_json=call.input_json,
        output_json=call.output_json,
        error_message=call.error_message,
        requested_by=call.requested_by,
        resolved_by=call.resolved_by,
        requested_at=call.requested_at,
        resolved_at=call.resolved_at,
    )


@call_router.post(
    "/{project_id}/mcp/calls/{call_id}/approve",
    response_model=McpToolCallResponse,
    summary="Approve and execute a pending MCP tool call",
)
def approve_mcp_call(
    project_id: uuid.UUID,
    call_id: uuid.UUID,
    body: ResolveRequest,
    session: Annotated[Session, Depends(get_session)],
) -> McpToolCallResponse:
    call = _get_pending_call(session, project_id, call_id)
    call.status = McpCallStatus.approved
    call.resolved_by = body.resolved_by
    session.commit()
    call = run_call(call, session)
    return _call_response(call)


@call_router.post(
    "/{project_id}/mcp/calls/{call_id}/reject",
    response_model=McpToolCallResponse,
    summary="Reject a pending MCP tool call",
)
def reject_mcp_call(
    project_id: uuid.UUID,
    call_id: uuid.UUID,
    body: ResolveRequest,
    session: Annotated[Session, Depends(get_session)],
) -> McpToolCallResponse:
    call = _get_pending_call(session, project_id, call_id)
    call.status = McpCallStatus.rejected
    call.resolved_by = body.resolved_by
    call.resolved_at = datetime.now(UTC)
    session.commit()
    session.refresh(call)
    return _call_response(call)


# โ”€โ”€ Helpers โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€

def _get_pending_call(
    session: Session, project_id: uuid.UUID, call_id: uuid.UUID
) -> McpToolCall:
    call = session.exec(
        select(McpToolCall).where(
            McpToolCall.id == call_id,
            McpToolCall.project_id == project_id,
        )
    ).first()
    if not call:
        raise HTTPException(status_code=404, detail="Tool call not found")
    if call.status != McpCallStatus.pending:
        raise HTTPException(
            status_code=409,
            detail=f"Call is already '{call.status}' โ€” only pending calls can be resolved",
        )
    return call


def _call_response(call: McpToolCall) -> McpToolCallResponse:
    return McpToolCallResponse(
        id=str(call.id),
        project_id=str(call.project_id),
        tool_name=call.tool_name,
        agent_id=str(call.agent_id) if call.agent_id else None,
        status=call.status,
        input_json=call.input_json,
        output_json=call.output_json,
        error_message=call.error_message,
        requested_by=call.requested_by,
        resolved_by=call.resolved_by,
        requested_at=call.requested_at,
        resolved_at=call.resolved_at,
    )
