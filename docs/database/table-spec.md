# Table Specification

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Total Tables:** 14

This document provides business context, validation rules, default seed data, and usage patterns for each table. For SQL DDL, see `schema.md`. For entity relationships, see `erd.md`.

---

## DB-001: `projects`

**Business Purpose:** Root entity for all work. Every pipeline run, document, and message belongs to a project.

**FR Ref:** FR-022 (Project management — Create, list, select active project)

**Validation Rules:**
- `name`: required, 1–255 characters, trimmed
- `status`: must be a valid `project_status` enum value
- `created_by`: required — user identifier (username or user ID)

**Seed Data:** No seed data required. Projects are created by users.

**Usage Patterns:**
- On app load: `SELECT * FROM projects WHERE status = 'active' ORDER BY created_at DESC`
- On project select: all child queries filter by `project_id`
- Archive: `UPDATE projects SET status = 'archived' WHERE id = $1`

---

## DB-002: `requirement_inputs`

**Business Purpose:** Stores raw uploaded or pasted requirement sources before the pipeline processes them.

**FR Ref:** FR-001 (accept multi-source input), FR-002 (store with metadata)

**Validation Rules:**
- `project_id`: must reference an existing project
- `input_type`: must be a valid `input_type` enum value
- `content`: required, not empty, max 32,000 characters (enforced at service layer, not DB)
- `source_date`: ISO 8601 format if provided
- `metadata_json`: optional, validated as JSONB — may contain `tags` (array), `priority` (string)

**Seed Data:** No seed data required.

**Usage Patterns:**
- `SELECT * FROM requirement_inputs WHERE project_id = $1 ORDER BY created_at DESC`
- Content passed as LLM input for Requirement Agent

---

## DB-003: `agents`

**Business Purpose:** Global registry of all AI agents. Agents exist independently of projects. Real-time status and position are updated here for the virtual office.

**FR Ref:** FR-006 (CRUD agents), FR-007 (edit system prompt), FR-008 (select LLM model), FR-017 (position in office), FR-021 (status bubbles)

**Validation Rules:**
- `name`: required, unique, slug format (e.g. `requirement-agent`)
- `status`: must be a valid `agent_status` enum value
- `location_x`, `location_y`: non-negative integers
- `model_provider`: must be a valid `model_provider` enum value
- `model_name`: required when `is_active = true`
- `is_active`: only active agents appear in the pipeline selector

**Seed Data (10 agents to insert on first run):**

| name | role | home_zone | model_provider | model_name |
|---|---|---|---|---|
| requirement-agent | requirement_analyst | requirement_room | ollama | qwen3:8b |
| gap-analysis-agent | gap_analyst | gap_analysis_room | ollama | qwen3:8b |
| ba-agent | business_analyst | ba_room | ollama | qwen3:8b |
| architect-agent | solution_architect | sa_room | ollama | qwen3:8b |
| ux-agent | ux_designer | ux_studio | ollama | qwen3:8b |
| developer-agent | developer | developer_zone | ollama | qwen3:8b |
| qa-agent | qa_engineer | qa_lab | ollama | qwen3:8b |
| change-impact-agent | change_analyst | change_impact_room | ollama | qwen3:8b |
| documentation-agent | documentation_manager | documentation_room | ollama | qwen3:8b |
| pm-agent | project_manager | pm_room | ollama | qwen3:8b |

**Usage Patterns:**
- WebSocket broadcasts UPDATE to `agents` → clients reflect live position and status
- `SELECT * FROM agents WHERE is_active = true` for pipeline agent selector

---

## DB-004: `tasks`

**Business Purpose:** Work items that track the assignment and progress of each pipeline step per project.

**FR Ref:** FR-009 (full task status lifecycle)

**Validation Rules:**
- `project_id`: must reference an existing project
- `status`: must be a valid `task_status` enum value
- `priority`: must be a valid `task_priority` enum value
- `pipeline_step`: must match a known pipeline step name when set (e.g. `requirement_summary`, `gap_analysis`)
- `output_document_id`: set only after the agent successfully creates the document

**Status Lifecycle:**
```
pending → in_progress → done
                     → failed
                     → cancelled
```

**Seed Data:** No seed data. Tasks are created when pipeline steps are triggered.

---

## DB-005: `pipeline_runs`

**Business Purpose:** Tracks one end-to-end pipeline execution for a project. A project can have multiple pipeline runs (re-runs).

**FR Ref:** FR-003 (10-step pipeline), FR-005 (re-run any step)

**Validation Rules:**
- `project_id`: must reference an existing project
- `status`: must be a valid `pipeline_run_status` enum value
- `completed_at`: must be NULL when status is `pending` or `running`

**Status Lifecycle:**
```
pending → running → completed
                 → failed
                 → cancelled
```

**Usage Patterns:**
- `SELECT * FROM pipeline_runs WHERE project_id = $1 ORDER BY created_at DESC LIMIT 1` — get latest run
- One `pipeline_run` creates 10 `pipeline_steps` records on start

---

## DB-006: `pipeline_steps`

**Business Purpose:** One row per pipeline step per run. The authoritative log of every agent execution. Required by BR-005.

**FR Ref:** FR-024 (log every agent run), BR-005 (every run must be logged)

**Validation Rules:**
- `pipeline_run_id`: must reference an existing pipeline run
- `step_name`: must be one of: `requirement_summary`, `gap_analysis`, `brd_fsd_user_story`, `architecture_design`, `screen_spec`, `code_task_list`, `test_cases`, `change_impact`, `documentation`, `pm_summary`
- `error_message`: set only when `status = 'failed'`
- `output_document_id`: set only when `status = 'completed'`

**Usage Patterns:**
- `SELECT * FROM pipeline_steps WHERE pipeline_run_id = $1 ORDER BY id` — get all steps for a run
- On agent completion: UPDATE status, set completed_at, set output_document_id

---

## DB-007: `documents`

**Business Purpose:** Stores all agent-generated output documents. Documents are versioned — when a step is re-run, a new document is created and the old one is set to `superseded`.

**FR Ref:** FR-012 (store all document types), FR-013 (view with version history), FR-014 (export)

**Validation Rules:**
- `project_id`: must reference an existing project
- `document_type`: must be a valid `document_type` enum value
- `content_markdown`: required, not empty
- `version`: auto-incremented per `(project_id, document_type)` combination
- `status`: `approved` or `rejected` can only be set by a user action (not automatically)
- `approved_by`: required when `status = 'approved'`

**Document Type to Agent Mapping:**

| document_type | Created By |
|---|---|
| requirement_summary | requirement-agent |
| gap_analysis_report | gap-analysis-agent |
| brd | ba-agent |
| fsd | ba-agent |
| user_story | ba-agent |
| architecture_design | architect-agent |
| database_design | architect-agent |
| api_spec | architect-agent |
| screen_spec | ux-agent |
| code_task_list | developer-agent |
| test_cases | qa-agent |
| uat_script | qa-agent |
| change_impact_report | change-impact-agent |

**Usage Patterns:**
- Get latest approved FSD: `SELECT * FROM documents WHERE project_id = $1 AND document_type = 'fsd' AND status = 'approved' ORDER BY version DESC LIMIT 1`

---

## DB-008: `messages`

**Business Purpose:** Stores all communication: agent-to-agent handoff messages, user-to-agent chat, and system notifications.

**FR Ref:** FR-010 (user can chat with agents), FR-011 (agent handoff messages)

**Validation Rules:**
- `sender_type` and `receiver_type`: must be valid `actor_type` enum values
- `sender_id` / `receiver_id`: must reference the correct entity for the given actor type
- `content`: required, not empty
- `message_type = 'handoff'`: `metadata_json` must contain handoff payload fields

**Usage Patterns:**
- Chat history: `SELECT * FROM messages WHERE project_id = $1 AND ((sender_id = $agent_id) OR (receiver_id = $agent_id)) ORDER BY created_at ASC`
- Handoff payload: stored in `metadata_json` as JSONB

---

## DB-009: `activity_logs`

**Business Purpose:** Append-only event log. Powers the office activity feed and provides an audit trail. Never update or delete rows.

**FR Ref:** FR-018 (broadcast status changes), FR-024 (log every agent run)

**Validation Rules:**
- `event_type`: must be a valid `event_type` enum value
- `message`: required, human-readable description
- Rows must NEVER be updated or deleted — append only

**Usage Patterns:**
- Activity feed: `SELECT * FROM activity_logs WHERE project_id = $1 ORDER BY created_at DESC LIMIT 50`
- Agent move events: `event_type = 'agent_moved'`, `metadata_json = {"from_x": 100, "from_y": 100, "to_x": 200, "to_y": 150}`

---

## DB-010: `traceability_links`

**Business Purpose:** Many-to-many polymorphic table linking any two artifacts for full SDLC traceability.

**FR Ref:** FR-015 (traceability matrix)

**Validation Rules:**
- `source_type` and `target_type`: must be valid `link_actor_type` enum values
- `source_id` / `target_id`: must reference a valid record of the corresponding type
- Duplicate links (same source_id + target_id + link_type) should be rejected at service layer

**Link Type Meanings:**

| link_type | Meaning |
|---|---|
| derived_from | Target artifact was created based on source (e.g. FSD derived from Requirement) |
| implements | Target artifact implements source (e.g. API endpoint implements FSD spec) |
| tests | Target artifact tests source (e.g. Test Case tests FSD spec) |
| conflicts_with | Source and target conflict — needs resolution |

**Usage Patterns:**
- Traceability matrix query: `SELECT * FROM traceability_links WHERE project_id = $1 AND source_type = 'requirement_input' ORDER BY source_id`

---

## DB-011: `llm_settings`

**Business Purpose:** Stores LLM provider configuration. Only one row should have `is_active = true` at any time.

**FR Ref:** FR-023 (LLM provider config: Ollama + OpenAI)

**Validation Rules:**
- `base_url`: required when `provider = 'ollama'`
- `api_key_encrypted`: required when `provider = 'openai'`
- `temperature`: must be between 0.0 and 2.0
- `max_tokens`: must be between 1 and 32000
- Only one row with `is_active = true` is allowed — enforced at service layer

**Seed Data (insert on first run):**

```sql
INSERT INTO llm_settings (provider, base_url, model_name, temperature, max_tokens, is_active)
VALUES ('ollama', 'http://localhost:11434', 'qwen3:8b', 0.7, 4096, true);
```

---

## DB-012: `agent_memories`

**Business Purpose:** Stores per-agent, per-project memory for long-term context and RAG retrieval.

**FR Ref:** MVP 5 (RAG)

**Validation Rules:**
- `importance_score`: must be between 0.0 and 1.0
- `embedding_id`: set after the content is embedded into the vector store

**Usage Patterns:**
- Retrieve high-importance memories: `SELECT * FROM agent_memories WHERE agent_id = $1 AND project_id = $2 ORDER BY importance_score DESC LIMIT 10`
- RAG retrieval: query by `embedding_id` in pgvector

---

## DB-013: `sprints`

**Business Purpose:** Tracks sprint schedule with planned and actual dates for the Sprint Timeline feature.

**FR Ref:** FR-025 (Sprint Timeline view), FR-027 (deadline alerts), FR-029 (admin can update sprint dates)

**Validation Rules:**
- `sprint_number`: must be unique per `project_id`, positive integer
- `planned_start`: must be before `planned_end`
- `actual_end`: set when sprint status changes to `done`
- `story_points_done`: must be ≤ `story_points_total`
- `status`: must be a valid `sprint_status` enum value

**Sprint Status Lifecycle:**
```
not_started → in_progress → done
                          → overdue (if planned_end < today and status != done)
```

**Note:** `overdue` status is computed — set by a background job or on-read calculation when `planned_end < current_date AND status = 'in_progress'`.

**Seed Data:** Pre-populate with Sprint 0–20 schedule from `docs/product/timeline.md` on project creation.

---

## DB-014: `milestones`

**Business Purpose:** Tracks MVP milestones with target dates for the dashboard milestone indicator.

**FR Ref:** FR-026 (MVP milestone tracking), FR-028 (PM Agent includes next milestone date)

**Validation Rules:**
- `mvp_number`: must be between 1 and 5 for this project
- `target_date`: required
- `actual_date`: set when status changes to `done`
- `status`: must be a valid `milestone_status` enum value

**Seed Data:** Pre-populate with MVP 1–5 milestones from `docs/product/timeline.md` on project creation:

| mvp_number | name | target_date |
|---|---|---|
| 1 | MVP 1 — Requirement Loop | 2026-07-18 |
| 2 | MVP 2 — BA / SA Documents | 2026-08-01 |
| 3 | MVP 3 — Dev / QA / Traceability | 2026-08-18 |
| 4 | MVP 4 — Virtual Office | 2026-08-27 |
| 5 | MVP 5 — Integration Layer | 2026-09-07 |
