# Requirement-to-Code Workflow

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Related:** `agent-state-machine.md`, `human-review-points.md`

---

## Overview

The requirement-to-code workflow is the core pipeline of the system. It takes a raw requirement input and produces a code task list through 10 sequential agent steps, with 5 human review gates.

```
UPLOAD_SOURCE
      ↓
RUN_REQUIREMENT_AGENT        → produces: requirement_summary
      ↓
RUN_GAP_ANALYSIS_AGENT       → produces: gap_analysis_report
      ↓
WAIT_FOR_USER_REVIEW [Gate 1: Gap confirmed?]
      ↓ approved
RUN_BA_AGENT                 → produces: brd, fsd, user_story
      ↓
WAIT_FOR_USER_REVIEW [Gate 2: BRD/FSD/User Story confirmed?]
      ↓ approved
RUN_ARCHITECT_AGENT          → produces: architecture_design, database_design, api_spec
      ↓
WAIT_FOR_USER_REVIEW [Gate 3: Architecture confirmed?]
      ↓ approved
RUN_UX_AGENT                 → produces: screen_spec
      ↓
WAIT_FOR_USER_APPROVAL [Gate 4: Screen spec approved before Dev?]
      ↓ approved
RUN_DEVELOPER_AGENT          → produces: code_task_list
      ↓
RUN_QA_AGENT                 → produces: test_cases, uat_script
      ↓
WAIT_FOR_USER_REVIEW [Gate 5: Test cases confirmed?]
      ↓ approved
UPDATE_TRACEABILITY
      ↓
END
```

---

## Workflow Statuses

| Status | Description | Transitions To |
|---|---|---|
| `draft` | Pipeline run created, not yet started | `running` |
| `running` | At least one step is actively executing | `waiting_for_user`, `failed`, `completed` |
| `waiting_for_user` | Paused at a human review gate | `running` (on approve), `failed` (on reject) |
| `completed` | All steps finished successfully | — |
| `failed` | A step failed and was not retried, or user rejected | `running` (if user triggers re-run) |
| `cancelled` | User manually cancelled the run | — |

---

## Step Definitions

| Step # | Step Name | Agent | Input | Output | Gate After |
|---|---|---|---|---|---|
| 1 | `requirement_summary` | requirement-agent | requirement_input | requirement_summary doc | No |
| 2 | `gap_analysis` | gap-analysis-agent | requirement_summary (approved) | gap_analysis_report doc | **Gate 1** |
| 3 | `brd_fsd_user_story` | ba-agent | requirement_summary + gap_analysis_report (approved) | brd, fsd, user_story docs | **Gate 2** |
| 4 | `architecture_design` | architect-agent | brd + fsd + user_story (approved) | architecture_design, database_design, api_spec docs | **Gate 3** |
| 5 | `screen_spec` | ux-agent | fsd + architecture_design + api_spec (approved) | screen_spec doc | **Gate 4** |
| 6 | `code_task_list` | developer-agent | fsd + architecture_design + database_design + api_spec + screen_spec + user_story (all approved) | code_task_list doc | No |
| 7 | `test_cases` | qa-agent | fsd + user_story + api_spec (approved) | test_cases + uat_script docs | **Gate 5** |
| 8 | `traceability_update` | system | all docs + tasks | traceability_links records | No |

---

## Handoff Data Between Agents

Each agent receives a structured handoff payload when a step starts. The payload is constructed from the database state at the time the step begins.

### Step 1 → Step 2 (Requirement Agent → Gap Analysis Agent)

```json
{
  "handoff_from": "requirement-agent",
  "handoff_to": "gap-analysis-agent",
  "pipeline_run_id": "<uuid>",
  "project_id": "<uuid>",
  "input": {
    "requirement_summary_document_id": "<uuid>",
    "requirement_summary_content": "<markdown>",
    "original_input_id": "<uuid>",
    "original_input_type": "meeting_transcript"
  }
}
```

### Step 2 → Gate 1 → Step 3 (Gap Analysis → BA Agent)

```json
{
  "handoff_from": "gap-analysis-agent",
  "handoff_to": "ba-agent",
  "pipeline_run_id": "<uuid>",
  "project_id": "<uuid>",
  "input": {
    "requirement_summary_document_id": "<uuid>",
    "gap_analysis_report_document_id": "<uuid>",
    "gap_analysis_content": "<markdown>",
    "review_comment": "<human comment from Gate 1>"
  }
}
```

### Step 3 → Gate 2 → Step 4 (BA Agent → Architect Agent)

```json
{
  "handoff_from": "ba-agent",
  "handoff_to": "architect-agent",
  "input": {
    "brd_document_id": "<uuid>",
    "fsd_document_id": "<uuid>",
    "user_story_document_id": "<uuid>",
    "review_comment": "<human comment from Gate 2>"
  }
}
```

### Step 4 → Gate 3 → Step 5 (Architect Agent → UX Agent)

```json
{
  "handoff_from": "architect-agent",
  "handoff_to": "ux-agent",
  "input": {
    "fsd_document_id": "<uuid>",
    "architecture_design_document_id": "<uuid>",
    "api_spec_document_id": "<uuid>",
    "review_comment": "<human comment from Gate 3>"
  }
}
```

### Step 5 → Gate 4 → Step 6 (UX Agent → Developer Agent)

```json
{
  "handoff_from": "ux-agent",
  "handoff_to": "developer-agent",
  "input": {
    "fsd_document_id": "<uuid>",
    "architecture_design_document_id": "<uuid>",
    "database_design_document_id": "<uuid>",
    "api_spec_document_id": "<uuid>",
    "screen_spec_document_id": "<uuid>",
    "user_story_document_id": "<uuid>",
    "review_comment": "<human comment from Gate 4>"
  }
}
```

### Step 6 → Step 7 (Developer Agent → QA Agent)

```json
{
  "handoff_from": "developer-agent",
  "handoff_to": "qa-agent",
  "input": {
    "fsd_document_id": "<uuid>",
    "user_story_document_id": "<uuid>",
    "api_spec_document_id": "<uuid>",
    "code_task_list_document_id": "<uuid>"
  }
}
```

---

## Failure Handling

### Step Failure Types

| Failure Type | Error Code | Cause | Recovery |
|---|---|---|---|
| LLM timeout | `LLM_TIMEOUT` | LLM provider did not respond within timeout_seconds | Automatic retry (up to max_retries) |
| LLM output invalid JSON | `LLM_INVALID_OUTPUT` | LLM returned unparseable or schema-invalid JSON | Automatic retry with stricter prompt |
| Upstream not approved | `UPSTREAM_NOT_APPROVED` | Developer Agent triggered before all docs approved | Block — user must approve all docs first |
| User rejected output | `USER_REJECTED` | Human reviewer rejected the step output | User triggers re-run after fixing input |
| Unhandled exception | `INTERNAL_ERROR` | Unexpected server error | Automatic retry once; then mark failed |

### Step-Level Failure Behaviour

```
step_status = failed
pipeline_run_status = failed
→ Frontend shows failure reason in step detail
→ User can: fix input → re-run step (API-016)
→ Re-run resets step_status = pending → running
→ If re-run succeeds: pipeline resumes from that step
```

### Pipeline-Level Cancellation

```
User calls: PATCH /projects/{id}/pipeline/runs/{run_id}  { "status": "cancelled" }
→ In-flight step receives cancellation signal
→ step_status = skipped
→ pipeline_run_status = cancelled
→ No further steps execute
```

---

## Retry Policy

| Scenario | Max Retries | Backoff | Notes |
|---|---|---|---|
| LLM timeout | 3 | 5s, 15s, 30s | Exponential backoff |
| LLM invalid output | 2 | 5s, 10s | Retry with tighter JSON instruction in prompt |
| Internal error | 1 | 5s | Log full stack trace |
| User rejected | 0 (auto) | — | User must manually trigger re-run |

Retry counter is stored in `pipeline_steps.retry_count`. Once `retry_count >= max_retries`, the step is marked `failed` without further attempts.

---

## Workflow Invariants

1. Steps execute **strictly in order** — step N+1 cannot start until step N is `completed`.
2. A human review gate **pauses the pipeline** — the next step does not start until the gate is resolved.
3. **Developer Agent** is hard-blocked if any of the 6 upstream documents are not `approved` (returns `UPSTREAM_NOT_APPROVED`).
4. When a step is re-run, the **previous output document** for that step is set to `status = superseded` before the new document is created.
5. A pipeline run can only be cancelled while `status = running` or `status = waiting_for_user`.
6. Once `status = completed` or `status = cancelled`, no further step transitions are allowed.
