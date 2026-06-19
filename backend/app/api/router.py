from fastapi import APIRouter

from app.api.routes import (
    activity,
    admin,
    agents,
    auth,
    change_impact,
    documents,
    documentation,
    generated_code,
    github,
    health,
    inputs,
    mcp,
    messages,
    milestones,
    pipeline,
    pm,
    projects,
    rag,
    settings,
    sprints,
    tasks,
    traceability,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(inputs.router, prefix="/projects", tags=["Requirement Inputs"])
api_router.include_router(pipeline.router, prefix="/projects", tags=["Pipeline"])
api_router.include_router(documents.router, prefix="/projects", tags=["Documents"])
api_router.include_router(messages.router, prefix="/projects", tags=["Messages"])
api_router.include_router(tasks.router, prefix="/projects", tags=["Tasks"])
api_router.include_router(activity.router, prefix="/projects", tags=["Activity"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(settings.router, prefix="/settings", tags=["LLM Settings"])
api_router.include_router(sprints.router, prefix="/projects", tags=["Sprints"])
api_router.include_router(milestones.router, prefix="/projects", tags=["Milestones"])
api_router.include_router(traceability.router, prefix="/projects", tags=["Traceability"])
api_router.include_router(change_impact.router, prefix="/projects", tags=["Change Impact"])
api_router.include_router(documentation.router, prefix="/projects", tags=["Documentation"])
api_router.include_router(pm.router, prefix="/projects", tags=["PM Agent"])
api_router.include_router(github.router, prefix="/projects", tags=["GitHub"])
api_router.include_router(mcp.tool_router, tags=["MCP"])
api_router.include_router(mcp.call_router, prefix="/projects", tags=["MCP"])
api_router.include_router(rag.router, prefix="/projects", tags=["RAG"])
api_router.include_router(generated_code.router, prefix="/projects", tags=["Generated Code"])
