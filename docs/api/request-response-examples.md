# Request / Response Examples

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18

This document shows end-to-end request/response flows for the most important user journeys.

---

## Journey 1 — Create Project and Upload Requirement

### Step 1: Create a new project — API-002

**Request:**
```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "E-Commerce Checkout Redesign",
  "description": "Redesign the checkout flow to reduce cart abandonment",
  "created_by": "tanarat.kit"
}
```

**Response 201:**
```json
{
  "id": "a1b2c3d4-0000-0000-0000-000000000001",
  "name": "E-Commerce Checkout Redesign",
  "description": "Redesign the checkout flow to reduce cart abandonment",
  "status": "active",
  "created_by": "tanarat.kit",
  "created_at": "2026-06-18T09:00:00Z",
  "updated_at": "2026-06-18T09:00:00Z"
}
```

---

### Step 2: Upload requirement input — API-007

**Request:**
```http
POST /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/inputs
Content-Type: application/json

{
  "input_type": "meeting_transcript",
  "title": "Kick-off meeting 2026-06-18",
  "content": "PM: We need to reduce checkout steps from 5 to 3. The current flow loses 40% of users at the payment page. Key requirements: 1) Guest checkout without registration. 2) Save card for future use. 3) Show estimated delivery date before payment. 4) Support PromptPay QR code. The deadline is end of Q3.",
  "source_owner": "tanarat.kit",
  "source_date": "2026-06-18T09:00:00Z",
  "metadata_json": {
    "tags": ["checkout", "payment", "ux"],
    "priority": "critical"
  }
}
```

**Response 201:**
```json
{
  "id": "b2c3d4e5-0000-0000-0000-000000000002",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "input_type": "meeting_transcript",
  "title": "Kick-off meeting 2026-06-18",
  "content": "PM: We need to reduce checkout steps from 5 to 3...",
  "source_owner": "tanarat.kit",
  "source_date": "2026-06-18T09:00:00Z",
  "created_at": "2026-06-18T09:01:00Z"
}
```

---

## Journey 2 — Start and Monitor Pipeline

### Step 3: Start pipeline run — API-010

**Request:**
```http
POST /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/pipeline/runs
Content-Type: application/json

{
  "input_id": "b2c3d4e5-0000-0000-0000-000000000002"
}
```

**Response 201:**
```json
{
  "id": "c3d4e5f6-0000-0000-0000-000000000003",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "status": "running",
  "current_step": "requirement_summary",
  "started_at": "2026-06-18T09:02:00Z",
  "completed_at": null,
  "created_at": "2026-06-18T09:02:00Z"
}
```

---

### Step 4: Check pipeline step status — API-013

**Request:**
```http
GET /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/pipeline/runs/c3d4e5f6-0000-0000-0000-000000000003/steps
```

**Response 200:**
```json
[
  {
    "id": "d4e5f6a7-0000-0000-0000-000000000004",
    "pipeline_run_id": "c3d4e5f6-0000-0000-0000-000000000003",
    "step_name": "requirement_summary",
    "agent_id": "agent-req-0000-0000-0000-000000000001",
    "status": "completed",
    "output_document_id": "e5f6a7b8-0000-0000-0000-000000000005",
    "started_at": "2026-06-18T09:02:00Z",
    "completed_at": "2026-06-18T09:03:30Z",
    "error_message": null
  },
  {
    "id": "d4e5f6a7-0000-0000-0000-000000000005",
    "pipeline_run_id": "c3d4e5f6-0000-0000-0000-000000000003",
    "step_name": "gap_analysis",
    "agent_id": "agent-gap-0000-0000-0000-000000000002",
    "status": "running",
    "output_document_id": null,
    "started_at": "2026-06-18T09:03:31Z",
    "completed_at": null,
    "error_message": null
  },
  {
    "id": "d4e5f6a7-0000-0000-0000-000000000006",
    "pipeline_run_id": "c3d4e5f6-0000-0000-0000-000000000003",
    "step_name": "brd_fsd_user_story",
    "agent_id": null,
    "status": "pending",
    "output_document_id": null,
    "started_at": null,
    "completed_at": null,
    "error_message": null
  }
]
```

---

## Journey 3 — Review and Approve a Document

### Step 5: Read the generated Requirement Summary — API-018

**Request:**
```http
GET /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/documents/e5f6a7b8-0000-0000-0000-000000000005
```

**Response 200:**
```json
{
  "id": "e5f6a7b8-0000-0000-0000-000000000005",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "document_type": "requirement_summary",
  "title": "Requirement Summary — E-Commerce Checkout Redesign",
  "content_markdown": "# Requirement Summary\n\n## 1. Business Objective\nReduce cart abandonment by simplifying the checkout process from 5 steps to 3...",
  "version": 1,
  "status": "draft",
  "created_by_agent_id": "agent-req-0000-0000-0000-000000000001",
  "approved_by": null,
  "created_at": "2026-06-18T09:03:30Z",
  "updated_at": "2026-06-18T09:03:30Z"
}
```

---

### Step 6: Approve the document — API-020

**Request:**
```http
POST /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/documents/e5f6a7b8-0000-0000-0000-000000000005/approve
Content-Type: application/json

{
  "approved_by": "tanarat.kit"
}
```

**Response 200:**
```json
{
  "id": "e5f6a7b8-0000-0000-0000-000000000005",
  "document_type": "requirement_summary",
  "title": "Requirement Summary — E-Commerce Checkout Redesign",
  "version": 1,
  "status": "approved",
  "approved_by": "tanarat.kit",
  "updated_at": "2026-06-18T09:10:00Z"
}
```

---

### Step 7: Reject a step and re-run — API-015, API-016

**Reject:**
```http
POST /api/v1/projects/a1b2c3d4-.../pipeline/runs/c3d4e5f6-.../steps/d4e5f6a7-.../reject
Content-Type: application/json

{
  "reason": "Gap analysis missed the PromptPay integration requirement. Please re-analyse."
}
```

**Response 200:**
```json
{
  "id": "d4e5f6a7-0000-0000-0000-000000000005",
  "step_name": "gap_analysis",
  "status": "failed",
  "error_message": "Rejected by user: Gap analysis missed the PromptPay integration requirement."
}
```

**Re-run:**
```http
POST /api/v1/projects/a1b2c3d4-.../pipeline/runs/c3d4e5f6-.../steps/d4e5f6a7-.../rerun
```

**Response 202:**
```json
{
  "id": "d4e5f6a7-0000-0000-0000-000000000005",
  "step_name": "gap_analysis",
  "status": "running",
  "started_at": "2026-06-18T09:15:00Z"
}
```

---

## Journey 4 — Agent Chat

### Step 8: Send message to Requirement Agent — API-024

**Request:**
```http
POST /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/messages
Content-Type: application/json

{
  "receiver_id": "agent-req-0000-0000-0000-000000000001",
  "receiver_type": "agent",
  "content": "Can you clarify what you meant by 'out of scope: mobile app'? We may need a mobile web view.",
  "message_type": "chat"
}
```

**Response 201:**
```json
{
  "id": "f6a7b8c9-0000-0000-0000-000000000006",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "sender_type": "user",
  "sender_id": "user-tanarat-000-0000-0000-000000000001",
  "receiver_type": "agent",
  "receiver_id": "agent-req-0000-0000-0000-000000000001",
  "content": "Can you clarify what you meant by 'out of scope: mobile app'?",
  "message_type": "chat",
  "created_at": "2026-06-18T09:20:00Z"
}
```

---

## Journey 5 — Sprint Timeline

### Step 9: List sprints with deadline status — API-039

**Request:**
```http
GET /api/v1/projects/a1b2c3d4-0000-0000-0000-000000000001/sprints
```

**Response 200:**
```json
[
  {
    "id": "sprint-0001-0000-0000-0000-000000000001",
    "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "sprint_number": 0,
    "name": "Sprint 0 — Requirement Intake",
    "planned_start": "2026-06-18",
    "planned_end": "2026-06-18",
    "actual_end": "2026-06-18",
    "status": "done",
    "story_points_total": 5,
    "story_points_done": 5,
    "days_remaining": 0
  },
  {
    "id": "sprint-0002-0000-0000-0000-000000000002",
    "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "sprint_number": 1,
    "name": "Sprint 1 — Agent Contract Design",
    "planned_start": "2026-06-19",
    "planned_end": "2026-06-20",
    "actual_end": null,
    "status": "in_progress",
    "story_points_total": 8,
    "story_points_done": 3,
    "days_remaining": 2
  }
]
```

---

## Journey 6 — Error Handling Examples

### 404 Not Found

```http
GET /api/v1/projects/00000000-0000-0000-0000-000000000000
```

**Response 404:**
```json
{
  "error_code": "NOT_FOUND",
  "message": "Project with ID 00000000-0000-0000-0000-000000000000 not found",
  "detail": null
}
```

---

### 422 Validation Error

```http
POST /api/v1/projects
Content-Type: application/json

{}
```

**Response 422:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "detail": [
    { "loc": ["body", "name"], "msg": "field required", "type": "value_error.missing" },
    { "loc": ["body", "created_by"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```

---

### 503 LLM Unavailable

```http
POST /api/v1/projects/a1b2c3d4-.../pipeline/runs
```

**Response 503:**
```json
{
  "error_code": "LLM_UNAVAILABLE",
  "message": "Ollama provider at http://localhost:11434 is not responding. Please check that Ollama is running.",
  "detail": null
}
```

---

### 503 Upstream Not Approved (Developer Agent blocked)

```http
POST /api/v1/projects/a1b2c3d4-.../pipeline/runs/{run_id}/steps/{step_id}/rerun
```

**Response 503:**
```json
{
  "error_code": "UPSTREAM_NOT_APPROVED",
  "message": "Developer Agent cannot run until all upstream documents are approved.",
  "detail": {
    "unapproved_documents": [
      { "id": "doc-fsd-001", "type": "fsd", "status": "draft" },
      { "id": "doc-screen-001", "type": "screen_spec", "status": "review" }
    ]
  }
}
```

---

## WebSocket Events

**Connect:**
```
WS ws://localhost:8000/ws/a1b2c3d4-0000-0000-0000-000000000001
```

**Agent status change event (server → client):**
```json
{
  "event": "agent_status_changed",
  "data": {
    "agent_id": "agent-req-0000-0000-0000-000000000001",
    "agent_name": "requirement-agent",
    "status": "working",
    "message": "Processing requirement input..."
  },
  "timestamp": "2026-06-18T09:02:05Z"
}
```

**Agent move event (server → client):**
```json
{
  "event": "agent_moved",
  "data": {
    "agent_id": "agent-req-0000-0000-0000-000000000001",
    "from_x": 100,
    "from_y": 100,
    "to_x": 150,
    "to_y": 100
  },
  "timestamp": "2026-06-18T09:02:03Z"
}
```

**Pipeline step completed event (server → client):**
```json
{
  "event": "pipeline_step_completed",
  "data": {
    "run_id": "c3d4e5f6-0000-0000-0000-000000000003",
    "step_name": "requirement_summary",
    "status": "completed",
    "output_document_id": "e5f6a7b8-0000-0000-0000-000000000005"
  },
  "timestamp": "2026-06-18T09:03:30Z"
}
```
