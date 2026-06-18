from fastapi import APIRouter

from app.api.routes import (
    activity,
    agents,
    change_impact,
    documents,
    health,
    inputs,
    messages,
    milestones,
    pipeline,
    projects,
    settings,
    sprints,
    tasks,
    traceability,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
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
