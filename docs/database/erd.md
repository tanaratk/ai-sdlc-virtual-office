# Entity Relationship Diagram (ERD)

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Database:** PostgreSQL 15+  
**Total Tables:** 14

---

## Entity Groups

| Group | Tables | Purpose |
|---|---|---|
| Core | `projects`, `requirement_inputs` | Project and input management |
| Agent | `agents`, `agent_memories` | Agent registry and memory |
| Pipeline | `pipeline_runs`, `pipeline_steps` | Execution tracking |
| Work | `tasks` | Task assignment and status |
| Output | `documents` | Agent-generated documents |
| Communication | `messages`, `activity_logs` | Agent chat and audit log |
| Traceability | `traceability_links` | Artifact linkage |
| Config | `llm_settings` | LLM provider configuration |
| Timeline | `sprints`, `milestones` | Sprint schedule and deadlines (FR-025–FR-029) |

---

## Mermaid ER Diagram

```mermaid
erDiagram
    projects {
        UUID id PK
        VARCHAR name
        TEXT description
        project_status status
        VARCHAR created_by
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    requirement_inputs {
        UUID id PK
        UUID project_id FK
        input_type input_type
        VARCHAR title
        TEXT content
        TEXT file_url
        TIMESTAMPTZ created_at
    }

    agents {
        UUID id PK
        VARCHAR name
        VARCHAR role
        TEXT system_prompt
        agent_status status
        INTEGER location_x
        INTEGER location_y
        model_provider model_provider
        VARCHAR model_name
        BOOLEAN is_active
    }

    tasks {
        UUID id PK
        UUID project_id FK
        UUID assigned_agent_id FK
        UUID input_reference_id FK
        UUID output_document_id FK
        VARCHAR title
        task_status status
        task_priority priority
        VARCHAR pipeline_step
    }

    pipeline_runs {
        UUID id PK
        UUID project_id FK
        pipeline_run_status status
        VARCHAR current_step
        TIMESTAMPTZ started_at
        TIMESTAMPTZ completed_at
    }

    pipeline_steps {
        UUID id PK
        UUID pipeline_run_id FK
        UUID agent_id FK
        UUID output_document_id FK
        VARCHAR step_name
        pipeline_step_status status
        JSONB input_json
        TEXT error_message
    }

    documents {
        UUID id PK
        UUID project_id FK
        UUID created_by_agent_id FK
        document_type document_type
        VARCHAR title
        TEXT content_markdown
        INTEGER version
        document_status status
        VARCHAR approved_by
    }

    messages {
        UUID id PK
        UUID project_id FK
        UUID task_id FK
        actor_type sender_type
        UUID sender_id
        actor_type receiver_type
        UUID receiver_id
        TEXT content
        message_type message_type
    }

    activity_logs {
        UUID id PK
        UUID project_id FK
        UUID task_id FK
        UUID agent_id FK
        event_type event_type
        TEXT message
        JSONB metadata_json
        TIMESTAMPTZ created_at
    }

    traceability_links {
        UUID id PK
        UUID project_id FK
        link_actor_type source_type
        UUID source_id
        link_actor_type target_type
        UUID target_id
        link_type link_type
    }

    llm_settings {
        UUID id PK
        model_provider provider
        TEXT base_url
        VARCHAR model_name
        TEXT api_key_encrypted
        FLOAT temperature
        INTEGER max_tokens
        BOOLEAN is_active
    }

    agent_memories {
        UUID id PK
        UUID agent_id FK
        UUID project_id FK
        memory_type memory_type
        TEXT content
        VARCHAR embedding_id
        FLOAT importance_score
    }

    sprints {
        UUID id PK
        UUID project_id FK
        INTEGER sprint_number
        VARCHAR name
        DATE planned_start
        DATE planned_end
        DATE actual_end
        sprint_status status
        INTEGER story_points_total
        INTEGER story_points_done
    }

    milestones {
        UUID id PK
        UUID project_id FK
        VARCHAR name
        TEXT description
        DATE target_date
        DATE actual_date
        milestone_status status
        INTEGER mvp_number
    }

    projects ||--o{ requirement_inputs : "has many"
    projects ||--o{ tasks : "has many"
    projects ||--o{ pipeline_runs : "has many"
    projects ||--o{ documents : "has many"
    projects ||--o{ messages : "has many"
    projects ||--o{ activity_logs : "has many"
    projects ||--o{ traceability_links : "has many"
    projects ||--o{ agent_memories : "has many"
    projects ||--o{ sprints : "has many"
    projects ||--o{ milestones : "has many"

    agents ||--o{ tasks : "assigned to"
    agents ||--o{ pipeline_steps : "executes"
    agents ||--o{ documents : "creates"
    agents ||--o{ activity_logs : "generates"
    agents ||--o{ agent_memories : "stores"

    pipeline_runs ||--o{ pipeline_steps : "contains"

    requirement_inputs ||--o{ tasks : "triggers"

    tasks ||--o{ messages : "has"
    tasks ||--o{ activity_logs : "has"

    documents ||--o| pipeline_steps : "output of"
    documents ||--o| tasks : "output of"
```

---

## Relationship Narrative

### projects (Root Entity)
`projects` is the anchor for all data. Every table (except `agents` and `llm_settings`) has a `project_id` FK. Deleting a project cascades to all child records.

### Requirement Flow
`requirement_inputs` → (triggers) `tasks` → (executes via) `pipeline_runs` → `pipeline_steps` → (produces) `documents`

### Agent Lifecycle
`agents` are globally registered (not per-project). They are assigned to `tasks`, execute `pipeline_steps`, create `documents`, and store context in `agent_memories`.

### Communication Layer
`messages` stores both agent handoff messages and user-to-agent chat. `activity_logs` is the append-only audit trail for the office activity feed.

### Traceability
`traceability_links` is a polymorphic many-to-many table. It can link any artifact type (`requirement_input`, `document`, `task`, `pipeline_step`) to any other, enabling full SDLC traceability.

### Timeline (Sprint 3 addition)
`sprints` and `milestones` support FR-025–FR-029: sprint schedule view, deadline alerts, and PM Agent reporting.

---

## Enum Types Summary

| Enum | Values |
|---|---|
| `project_status` | active, archived, completed |
| `input_type` | manual_text, meeting_transcript, chat_log, markdown_document, email_content, audio_transcript |
| `agent_status` | idle, working, done, error |
| `sprite_direction` | up, down, left, right |
| `model_provider` | ollama, openai |
| `task_status` | pending, in_progress, done, failed, cancelled |
| `task_priority` | low, medium, high, critical |
| `pipeline_run_status` | pending, running, completed, failed, cancelled |
| `pipeline_step_status` | pending, running, completed, failed, skipped |
| `document_type` | requirement_summary, gap_analysis_report, brd, fsd, user_story, architecture_doc, database_design, api_spec, screen_spec, test_cases, uat_script, change_impact_report, code_task_list |
| `document_status` | draft, review, approved, rejected, superseded |
| `actor_type` | agent, user, system |
| `message_type` | handoff, chat, notification, system |
| `event_type` | task_started, task_completed, task_failed, agent_moved, document_created, pipeline_step_started, pipeline_step_completed, handoff_sent, user_message |
| `link_type` | derived_from, implements, tests, conflicts_with |
| `link_actor_type` | requirement_input, document, task, pipeline_step |
| `memory_type` | context, decision, fact, instruction |
| `sprint_status` | not_started, in_progress, done, overdue |
| `milestone_status` | not_started, in_progress, done, overdue |
