# API List

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Base URL:** `/api/v1`  
**Auth:** None (MVP 1 — see OQ-001)  
**Total Endpoints:** 52  
**Full Spec:** `openapi.yaml`

---

## API Groups

| Group | Prefix | Endpoints | MVP |
|---|---|---|---|
| Projects | `/projects` | 5 | MVP 1 |
| Requirement Inputs | `/projects/{id}/inputs` | 4 | MVP 1 |
| Pipeline | `/projects/{id}/pipeline` | 7 | MVP 1 |
| Documents | `/projects/{id}/documents` | 6 | MVP 1 |
| Messages / Chat | `/projects/{id}/messages` | 2 | MVP 1 |
| Tasks | `/projects/{id}/tasks` | 3 | MVP 1 |
| Activity Log | `/projects/{id}/activity` | 1 | MVP 1 |
| Agents | `/agents` | 6 | MVP 1 |
| LLM Settings | `/settings/llm` | 4 | MVP 1 |
| Sprints | `/projects/{id}/sprints` | 3 | MVP 1 |
| Milestones | `/projects/{id}/milestones` | 3 | MVP 1 |
| Traceability | `/projects/{id}/traceability` | 3 | MVP 3 |
| RAG | `/rag` | 2 | MVP 5 |
| GitHub | `/github` | 3 | MVP 5 |
| MCP | `/mcp` | 3 | MVP 5 |
| WebSocket | `/ws` | 1 | MVP 4 |
| Health | `/health` | 1 | MVP 1 |

---

## Projects

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-001 | GET | `/projects` | List all projects (paginated) | projects | FR-022 |
| API-002 | POST | `/projects` | Create a new project | projects | FR-022 |
| API-003 | GET | `/projects/{project_id}` | Get project by ID | projects | FR-022 |
| API-004 | PATCH | `/projects/{project_id}` | Update project name/description/status | projects | FR-022 |
| API-005 | DELETE | `/projects/{project_id}` | Delete project (cascade) | projects | FR-022 |

---

## Requirement Inputs

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-006 | GET | `/projects/{project_id}/inputs` | List requirement inputs for a project | requirement_inputs | FR-001, FR-002 |
| API-007 | POST | `/projects/{project_id}/inputs` | Create requirement input (text or file) | requirement_inputs | FR-001, FR-002 |
| API-008 | GET | `/projects/{project_id}/inputs/{input_id}` | Get requirement input by ID | requirement_inputs | FR-002 |
| API-009 | DELETE | `/projects/{project_id}/inputs/{input_id}` | Delete requirement input | requirement_inputs | FR-002 |

---

## Pipeline

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-010 | POST | `/projects/{project_id}/pipeline/runs` | Start a new pipeline run | pipeline_runs, pipeline_steps | FR-003 |
| API-011 | GET | `/projects/{project_id}/pipeline/runs` | List all pipeline runs for a project | pipeline_runs | FR-003 |
| API-012 | GET | `/projects/{project_id}/pipeline/runs/{run_id}` | Get pipeline run status and current step | pipeline_runs | FR-003 |
| API-013 | GET | `/projects/{project_id}/pipeline/runs/{run_id}/steps` | List all steps for a run | pipeline_steps | FR-003 |
| API-014 | POST | `/projects/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/approve` | Approve a pipeline step output | pipeline_steps, documents | FR-004 |
| API-015 | POST | `/projects/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/reject` | Reject a pipeline step output | pipeline_steps, documents | FR-004 |
| API-016 | POST | `/projects/{project_id}/pipeline/runs/{run_id}/steps/{step_id}/rerun` | Re-run a specific pipeline step | pipeline_steps | FR-005 |

---

## Documents

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-017 | GET | `/projects/{project_id}/documents` | List documents (filter by type/status) | documents | FR-012 |
| API-018 | GET | `/projects/{project_id}/documents/{document_id}` | Get document with content | documents | FR-013 |
| API-019 | GET | `/projects/{project_id}/documents/{document_id}/versions` | List all versions of a document | documents | FR-013 |
| API-020 | POST | `/projects/{project_id}/documents/{document_id}/approve` | Approve a document | documents | FR-004 |
| API-021 | POST | `/projects/{project_id}/documents/{document_id}/reject` | Reject a document with reason | documents | FR-004 |
| API-022 | GET | `/projects/{project_id}/documents/{document_id}/export` | Export document as Markdown file | documents | FR-014 |

---

## Messages / Chat

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-023 | GET | `/projects/{project_id}/messages` | List messages (filter by agent/type) | messages | FR-010 |
| API-024 | POST | `/projects/{project_id}/messages` | Send message to an agent | messages | FR-010 |

---

## Tasks

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-025 | GET | `/projects/{project_id}/tasks` | List tasks (filter by status/agent) | tasks | FR-009 |
| API-026 | GET | `/projects/{project_id}/tasks/{task_id}` | Get task by ID | tasks | FR-009 |
| API-027 | PATCH | `/projects/{project_id}/tasks/{task_id}` | Update task status or priority | tasks | FR-009 |

---

## Activity Log

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-028 | GET | `/projects/{project_id}/activity` | Get recent activity events (paginated) | activity_logs | FR-018, FR-024 |

---

## Agents

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-029 | GET | `/agents` | List all agents with status and position | agents | FR-006 |
| API-030 | POST | `/agents` | Create a new agent | agents | FR-006 |
| API-031 | GET | `/agents/{agent_id}` | Get agent by ID | agents | FR-006 |
| API-032 | PATCH | `/agents/{agent_id}` | Update agent (prompt, model, avatar, zone) | agents | FR-006, FR-007, FR-008 |
| API-033 | DELETE | `/agents/{agent_id}` | Deactivate agent (soft delete) | agents | FR-006 |
| API-034 | PATCH | `/agents/{agent_id}/position` | Update agent position on office map | agents | FR-017 |

---

## LLM Settings

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-035 | GET | `/settings/llm` | List LLM configurations | llm_settings | FR-023 |
| API-036 | POST | `/settings/llm` | Create a new LLM configuration | llm_settings | FR-023 |
| API-037 | PATCH | `/settings/llm/{setting_id}` | Update LLM configuration | llm_settings | FR-023 |
| API-038 | POST | `/settings/llm/{setting_id}/activate` | Set this configuration as active | llm_settings | FR-023 |

---

## Sprints

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-039 | GET | `/projects/{project_id}/sprints` | List sprints with status and progress | sprints | FR-025 |
| API-040 | POST | `/projects/{project_id}/sprints` | Create a sprint | sprints | FR-025, FR-029 |
| API-041 | PATCH | `/projects/{project_id}/sprints/{sprint_id}` | Update sprint dates or status | sprints | FR-029 |

---

## Milestones

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-042 | GET | `/projects/{project_id}/milestones` | List milestones with status | milestones | FR-026 |
| API-043 | POST | `/projects/{project_id}/milestones` | Create a milestone | milestones | FR-026 |
| API-044 | PATCH | `/projects/{project_id}/milestones/{milestone_id}` | Update milestone status or target date | milestones | FR-026, FR-028 |

---

## Traceability

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-045 | GET | `/projects/{project_id}/traceability` | Get full traceability matrix | traceability_links | FR-015 |
| API-046 | POST | `/projects/{project_id}/traceability/links` | Create traceability link | traceability_links | FR-015 |
| API-047 | DELETE | `/projects/{project_id}/traceability/links/{link_id}` | Delete traceability link | traceability_links | FR-015 |

---

## RAG (MVP 5)

| API ID | Method | Path | Description | DB Table | FR Ref |
|---|---|---|---|---|---|
| API-048 | POST | `/rag/ingest` | Ingest a document into the vector store | agent_memories | MVP 5 |
| API-049 | POST | `/rag/search` | Semantic search over ingested documents | agent_memories | MVP 5 |

---

## GitHub (MVP 5)

| API ID | Method | Path | Description | FR Ref |
|---|---|---|---|---|
| API-050 | POST | `/github/issues` | Create GitHub Issues from tasks | MVP 5 |
| API-051 | POST | `/github/commits` | Push generated code to GitHub repo | MVP 5 |
| API-052 | GET | `/github/status` | Get GitHub integration connection status | MVP 5 |

---

## MCP (MVP 5)

| API ID | Method | Path | Description | FR Ref |
|---|---|---|---|---|
| API-053 | GET | `/mcp/tools` | List available MCP tools | MVP 5 |
| API-054 | POST | `/mcp/tools/run` | Execute an MCP tool | MVP 5 |
| API-055 | GET | `/mcp/tools/{tool_id}/history` | Get MCP tool execution history | MVP 5 |

---

## WebSocket

| API ID | Protocol | Path | Description | FR Ref |
|---|---|---|---|---|
| API-056 | WS | `/ws/{project_id}` | Real-time agent status, position, and activity broadcast | FR-018, FR-021 |

---

## Health

| API ID | Method | Path | Description |
|---|---|---|---|
| API-057 | GET | `/health` | System health check (DB, LLM provider connectivity) |

---

## Common Response Schemas

| Schema | Used By |
|---|---|
| `ProjectResponse` | API-001, 002, 003, 004 |
| `RequirementInputResponse` | API-006, 007, 008 |
| `PipelineRunResponse` | API-010, 011, 012 |
| `PipelineStepResponse` | API-013, 014, 015, 016 |
| `DocumentResponse` | API-017, 018, 020, 021 |
| `AgentResponse` | API-029, 030, 031, 032 |
| `MessageResponse` | API-023, 024 |
| `TaskResponse` | API-025, 026, 027 |
| `SprintResponse` | API-039, 040, 041 |
| `MilestoneResponse` | API-042, 043, 044 |
| `PaginatedResponse<T>` | API-001, 006, 017, 023, 025, 028 |
| `ErrorResponse` | All endpoints |

---

## Error Response Format

```json
{
  "error_code": "NOT_FOUND",
  "message": "Project with ID abc-123 not found",
  "detail": null
}
```

| HTTP Status | Error Code | When |
|---|---|---|
| 400 | BAD_REQUEST | Malformed request body |
| 404 | NOT_FOUND | Resource ID does not exist |
| 409 | CONFLICT | Duplicate or state conflict |
| 422 | VALIDATION_ERROR | Pydantic validation failure |
| 500 | INTERNAL_ERROR | Unhandled server exception |
| 503 | LLM_UNAVAILABLE | LLM provider timeout or unreachable |
| 503 | UPSTREAM_NOT_APPROVED | Developer Agent triggered before all docs approved |
