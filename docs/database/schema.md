# Database Schema

**Version:** 1.1.0  
**Database:** PostgreSQL 15+  
**ORM:** SQLAlchemy (Python / FastAPI backend)  
**Source:** Spec Section 12; Sprint 3 additions: sprints, milestones (FR-025–FR-029)

---

## Tables

1. [projects](#1-projects)
2. [requirement_inputs](#2-requirement_inputs)
3. [agents](#3-agents)
4. [tasks](#4-tasks)
5. [pipeline_runs](#5-pipeline_runs)
6. [pipeline_steps](#6-pipeline_steps)
7. [documents](#7-documents)
8. [messages](#8-messages)
9. [activity_logs](#9-activity_logs)
10. [traceability_links](#10-traceability_links)
11. [llm_settings](#11-llm_settings)
12. [agent_memories](#12-agent_memories)
13. [sprints](#13-sprints)
14. [milestones](#14-milestones)

---

## Enum Types

```sql
CREATE TYPE project_status      AS ENUM ('active', 'archived', 'completed');

CREATE TYPE input_type          AS ENUM (
    'manual_text', 'meeting_transcript', 'chat_log',
    'markdown_document', 'email_content', 'audio_transcript'
);

CREATE TYPE agent_status        AS ENUM ('idle', 'working', 'done', 'error');
CREATE TYPE sprite_direction    AS ENUM ('up', 'down', 'left', 'right');
CREATE TYPE model_provider      AS ENUM ('ollama', 'openai');

CREATE TYPE task_status         AS ENUM ('pending', 'in_progress', 'done', 'failed', 'cancelled');
CREATE TYPE task_priority       AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TYPE pipeline_run_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE pipeline_step_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped');

CREATE TYPE document_type       AS ENUM (
    'requirement_summary', 'gap_analysis_report',
    'brd', 'fsd', 'user_story',
    'architecture_doc', 'ux_spec', 'test_plan', 'change_impact_report'
);
CREATE TYPE document_status     AS ENUM ('draft', 'review', 'approved', 'rejected', 'superseded');

CREATE TYPE actor_type          AS ENUM ('agent', 'user', 'system');
CREATE TYPE message_type        AS ENUM ('handoff', 'chat', 'notification', 'system');

CREATE TYPE event_type          AS ENUM (
    'task_started', 'task_completed', 'task_failed',
    'agent_moved', 'document_created',
    'pipeline_step_started', 'pipeline_step_completed',
    'handoff_sent', 'user_message'
);

CREATE TYPE link_type           AS ENUM ('derived_from', 'implements', 'tests', 'conflicts_with');
CREATE TYPE link_actor_type     AS ENUM ('requirement_input', 'document', 'task', 'pipeline_step');

CREATE TYPE memory_type         AS ENUM ('context', 'decision', 'fact', 'instruction');

CREATE TYPE sprint_status       AS ENUM ('not_started', 'in_progress', 'done', 'overdue');
CREATE TYPE milestone_status    AS ENUM ('not_started', 'in_progress', 'done', 'overdue');
```

---

## 1. projects

Stores each project in the system. All other tables reference `project_id`.

```sql
CREATE TABLE projects (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    description  TEXT,
    status       project_status NOT NULL DEFAULT 'active',
    created_by   VARCHAR(255) NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| name | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULL | |
| status | project_status | NOT NULL | default: `active` |
| created_by | VARCHAR(255) | NOT NULL | user identifier |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_projects_status ON projects(status);
```

---

## 2. requirement_inputs

Raw input documents uploaded by the user before the pipeline starts.

```sql
CREATE TABLE requirement_inputs (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    input_type   input_type  NOT NULL,
    title        VARCHAR(255),
    content      TEXT        NOT NULL,
    file_url     TEXT,
    source_owner VARCHAR(255),
    source_date  TIMESTAMPTZ,
    metadata_json JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| input_type | input_type | NOT NULL | |
| title | VARCHAR(255) | NULL | e.g. "Kick-off meeting 2026-06-18" |
| content | TEXT | NOT NULL | max 32,000 chars per agent call |
| file_url | TEXT | NULL | path to uploaded file in object storage |
| source_owner | VARCHAR(255) | NULL | |
| source_date | TIMESTAMPTZ | NULL | |
| metadata_json | JSONB | NULL | tags, priority, extra fields |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_requirement_inputs_project_id ON requirement_inputs(project_id);
CREATE INDEX idx_requirement_inputs_input_type  ON requirement_inputs(input_type);
```

---

## 3. agents

Agent registry — one row per agent type. Updated in real time as agents move and change state.

```sql
CREATE TABLE agents (
    id               UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(255)   NOT NULL UNIQUE,
    role             VARCHAR(100)   NOT NULL,
    description      TEXT,
    goal             TEXT,
    system_prompt    TEXT,
    avatar_url       TEXT,
    home_zone        VARCHAR(100),
    current_zone     VARCHAR(100),
    status           agent_status   NOT NULL DEFAULT 'idle',
    location_x       INTEGER        NOT NULL DEFAULT 0,
    location_y       INTEGER        NOT NULL DEFAULT 0,
    target_x         INTEGER,
    target_y         INTEGER,
    sprite_direction sprite_direction NOT NULL DEFAULT 'down',
    model_provider   model_provider NOT NULL DEFAULT 'ollama',
    model_name       VARCHAR(100)   NOT NULL DEFAULT 'qwen3:8b',
    is_active        BOOLEAN        NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| name | VARCHAR(255) | NOT NULL | unique, e.g. `requirement-agent` |
| role | VARCHAR(100) | NOT NULL | e.g. `requirement_analyst` |
| description | TEXT | NULL | |
| goal | TEXT | NULL | |
| system_prompt | TEXT | NULL | full system prompt text |
| avatar_url | TEXT | NULL | sprite sheet path |
| home_zone | VARCHAR(100) | NULL | e.g. `requirement_room` |
| current_zone | VARCHAR(100) | NULL | live position zone |
| status | agent_status | NOT NULL | default: `idle` |
| location_x | INTEGER | NOT NULL | pixel x on office map |
| location_y | INTEGER | NOT NULL | pixel y on office map |
| target_x | INTEGER | NULL | movement destination x |
| target_y | INTEGER | NULL | movement destination y |
| sprite_direction | sprite_direction | NOT NULL | facing direction |
| model_provider | model_provider | NOT NULL | default: `ollama` |
| model_name | VARCHAR(100) | NOT NULL | default: `qwen3:8b` |
| is_active | BOOLEAN | NOT NULL | default: `true` |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_agents_status    ON agents(status);
CREATE INDEX idx_agents_is_active ON agents(is_active);
```

---

## 4. tasks

Work items assigned to agents. Each task maps to one pipeline step.

```sql
CREATE TABLE tasks (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID          NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title               VARCHAR(255)  NOT NULL,
    description         TEXT,
    assigned_agent_id   UUID          REFERENCES agents(id) ON DELETE SET NULL,
    status              task_status   NOT NULL DEFAULT 'pending',
    priority            task_priority NOT NULL DEFAULT 'medium',
    pipeline_step       VARCHAR(100),
    input_reference_id  UUID          REFERENCES requirement_inputs(id) ON DELETE SET NULL,
    output_document_id  UUID,
    due_date            TIMESTAMPTZ,
    created_by          VARCHAR(255)  NOT NULL,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NULL | |
| assigned_agent_id | UUID | NULL | FK → agents.id |
| status | task_status | NOT NULL | default: `pending` |
| priority | task_priority | NOT NULL | default: `medium` |
| pipeline_step | VARCHAR(100) | NULL | e.g. `requirement_summary`, `gap_analysis` |
| input_reference_id | UUID | NULL | FK → requirement_inputs.id |
| output_document_id | UUID | NULL | FK → documents.id (added after document is created) |
| due_date | TIMESTAMPTZ | NULL | |
| created_by | VARCHAR(255) | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_tasks_project_id        ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_agent_id ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_status            ON tasks(status);
CREATE INDEX idx_tasks_pipeline_step     ON tasks(pipeline_step);
```

---

## 5. pipeline_runs

Tracks each end-to-end pipeline execution for a project.

```sql
CREATE TABLE pipeline_runs (
    id           UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID               NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status       pipeline_run_status NOT NULL DEFAULT 'pending',
    current_step VARCHAR(100),
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ        NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| status | pipeline_run_status | NOT NULL | default: `pending` |
| current_step | VARCHAR(100) | NULL | name of the step currently executing |
| started_at | TIMESTAMPTZ | NULL | set when first step begins |
| completed_at | TIMESTAMPTZ | NULL | set when final step finishes |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_pipeline_runs_project_id ON pipeline_runs(project_id);
CREATE INDEX idx_pipeline_runs_status     ON pipeline_runs(status);
```

---

## 6. pipeline_steps

One row per step per pipeline run. Records input, output, timing, and errors.

```sql
CREATE TABLE pipeline_steps (
    id               UUID                 PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_run_id  UUID                 NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    step_name        VARCHAR(100)         NOT NULL,
    agent_id         UUID                 REFERENCES agents(id) ON DELETE SET NULL,
    status           pipeline_step_status NOT NULL DEFAULT 'pending',
    input_json       JSONB,
    output_document_id UUID               REFERENCES documents(id) ON DELETE SET NULL,
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    error_message    TEXT
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| pipeline_run_id | UUID | NOT NULL | FK → pipeline_runs.id |
| step_name | VARCHAR(100) | NOT NULL | e.g. `requirement_summary`, `gap_analysis` |
| agent_id | UUID | NULL | FK → agents.id |
| status | pipeline_step_status | NOT NULL | default: `pending` |
| input_json | JSONB | NULL | payload passed to the agent |
| output_document_id | UUID | NULL | FK → documents.id |
| started_at | TIMESTAMPTZ | NULL | |
| completed_at | TIMESTAMPTZ | NULL | |
| error_message | TEXT | NULL | set on failure |

**Indexes:**
```sql
CREATE INDEX idx_pipeline_steps_pipeline_run_id ON pipeline_steps(pipeline_run_id);
CREATE INDEX idx_pipeline_steps_agent_id        ON pipeline_steps(agent_id);
CREATE INDEX idx_pipeline_steps_status          ON pipeline_steps(status);
```

---

## 7. documents

All agent-generated output documents (Requirement Summary, Gap Analysis Report, BRD, FSD, etc.).

```sql
CREATE TABLE documents (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID            NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    document_type       document_type   NOT NULL,
    title               VARCHAR(255)    NOT NULL,
    content_markdown    TEXT            NOT NULL,
    version             INTEGER         NOT NULL DEFAULT 1,
    status              document_status NOT NULL DEFAULT 'draft',
    created_by_agent_id UUID            REFERENCES agents(id) ON DELETE SET NULL,
    approved_by         VARCHAR(255),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| document_type | document_type | NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| content_markdown | TEXT | NOT NULL | full document body |
| version | INTEGER | NOT NULL | default: `1`, increment on re-generation |
| status | document_status | NOT NULL | default: `draft` |
| created_by_agent_id | UUID | NULL | FK → agents.id |
| approved_by | VARCHAR(255) | NULL | user who approved the document |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_documents_project_id     ON documents(project_id);
CREATE INDEX idx_documents_document_type  ON documents(document_type);
CREATE INDEX idx_documents_status         ON documents(status);
CREATE INDEX idx_documents_created_by_agent_id ON documents(created_by_agent_id);
```

---

## 8. messages

Agent-to-agent and user-to-agent messages, including handoff payloads.

```sql
CREATE TABLE messages (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id    UUID         NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id       UUID         REFERENCES tasks(id) ON DELETE SET NULL,
    sender_type   actor_type   NOT NULL,
    sender_id     UUID         NOT NULL,
    receiver_type actor_type   NOT NULL,
    receiver_id   UUID         NOT NULL,
    content       TEXT         NOT NULL,
    message_type  message_type NOT NULL DEFAULT 'chat',
    metadata_json JSONB,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| task_id | UUID | NULL | FK → tasks.id |
| sender_type | actor_type | NOT NULL | `agent` / `user` / `system` |
| sender_id | UUID | NOT NULL | ID of sender (agent or user) |
| receiver_type | actor_type | NOT NULL | `agent` / `user` / `system` |
| receiver_id | UUID | NOT NULL | ID of receiver |
| content | TEXT | NOT NULL | message body |
| message_type | message_type | NOT NULL | default: `chat` |
| metadata_json | JSONB | NULL | e.g. handoff payload |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_messages_project_id  ON messages(project_id);
CREATE INDEX idx_messages_task_id     ON messages(task_id);
CREATE INDEX idx_messages_sender_id   ON messages(sender_id);
CREATE INDEX idx_messages_receiver_id ON messages(receiver_id);
CREATE INDEX idx_messages_created_at  ON messages(created_at DESC);
```

---

## 9. activity_logs

Append-only event log for the office activity feed and audit trail.

```sql
CREATE TABLE activity_logs (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id    UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id       UUID        REFERENCES tasks(id) ON DELETE SET NULL,
    agent_id      UUID        REFERENCES agents(id) ON DELETE SET NULL,
    event_type    event_type  NOT NULL,
    message       TEXT        NOT NULL,
    metadata_json JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| task_id | UUID | NULL | FK → tasks.id |
| agent_id | UUID | NULL | FK → agents.id |
| event_type | event_type | NOT NULL | |
| message | TEXT | NOT NULL | human-readable event description |
| metadata_json | JSONB | NULL | structured event data |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_activity_logs_project_id  ON activity_logs(project_id);
CREATE INDEX idx_activity_logs_agent_id    ON activity_logs(agent_id);
CREATE INDEX idx_activity_logs_event_type  ON activity_logs(event_type);
CREATE INDEX idx_activity_logs_created_at  ON activity_logs(created_at DESC);
```

---

## 10. traceability_links

Links between any two artefacts (requirement → document → test, etc.) for full traceability across the pipeline.

```sql
CREATE TABLE traceability_links (
    id           UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID           NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    source_type  link_actor_type NOT NULL,
    source_id    UUID           NOT NULL,
    target_type  link_actor_type NOT NULL,
    target_id    UUID           NOT NULL,
    link_type    link_type      NOT NULL,
    created_at   TIMESTAMPTZ    NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| source_type | link_actor_type | NOT NULL | type of source artefact |
| source_id | UUID | NOT NULL | ID of source artefact |
| target_type | link_actor_type | NOT NULL | type of target artefact |
| target_id | UUID | NOT NULL | ID of target artefact |
| link_type | link_type | NOT NULL | `derived_from` / `implements` / `tests` / `conflicts_with` |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_traceability_links_project_id ON traceability_links(project_id);
CREATE INDEX idx_traceability_links_source_id  ON traceability_links(source_id);
CREATE INDEX idx_traceability_links_target_id  ON traceability_links(target_id);
```

---

## 11. llm_settings

LLM provider configuration. Only one row should be `is_active = true` at a time.

```sql
CREATE TABLE llm_settings (
    id                UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    provider          model_provider NOT NULL,
    base_url          TEXT,
    model_name        VARCHAR(100)   NOT NULL,
    api_key_encrypted TEXT,
    temperature       FLOAT          NOT NULL DEFAULT 0.7,
    max_tokens        INTEGER        NOT NULL DEFAULT 4096,
    is_active         BOOLEAN        NOT NULL DEFAULT false,
    created_at        TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ    NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| provider | model_provider | NOT NULL | `ollama` / `openai` |
| base_url | TEXT | NULL | required for Ollama (e.g. `http://localhost:11434`) |
| model_name | VARCHAR(100) | NOT NULL | e.g. `qwen3:8b` / `gpt-4o` |
| api_key_encrypted | TEXT | NULL | encrypted; NULL for Ollama |
| temperature | FLOAT | NOT NULL | default: `0.7` |
| max_tokens | INTEGER | NOT NULL | default: `4096` |
| is_active | BOOLEAN | NOT NULL | only one active config at a time |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_llm_settings_is_active ON llm_settings(is_active);
```

---

## 12. agent_memories

Per-agent, per-project memory entries used for long-term context and RAG.

```sql
CREATE TABLE agent_memories (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id         UUID        NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    project_id       UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    memory_type      memory_type NOT NULL,
    content          TEXT        NOT NULL,
    embedding_id     VARCHAR(255),
    importance_score FLOAT       NOT NULL DEFAULT 0.5,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| agent_id | UUID | NOT NULL | FK → agents.id |
| project_id | UUID | NOT NULL | FK → projects.id |
| memory_type | memory_type | NOT NULL | `context` / `decision` / `fact` / `instruction` |
| content | TEXT | NOT NULL | memory text |
| embedding_id | VARCHAR(255) | NULL | reference ID in the vector store |
| importance_score | FLOAT | NOT NULL | 0.0–1.0; default: `0.5` |
| created_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_agent_memories_agent_id   ON agent_memories(agent_id);
CREATE INDEX idx_agent_memories_project_id ON agent_memories(project_id);
CREATE INDEX idx_agent_memories_memory_type ON agent_memories(memory_type);
CREATE INDEX idx_agent_memories_importance  ON agent_memories(importance_score DESC);
```

---

## 13. sprints

Sprint schedule per project, supporting FR-025–FR-029 (Timeline feature).

```sql
CREATE TABLE sprints (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID          NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sprint_number       INTEGER       NOT NULL,
    name                VARCHAR(255)  NOT NULL,
    planned_start       DATE          NOT NULL,
    planned_end         DATE          NOT NULL,
    actual_end          DATE,
    status              sprint_status NOT NULL DEFAULT 'not_started',
    story_points_total  INTEGER       NOT NULL DEFAULT 0,
    story_points_done   INTEGER       NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    UNIQUE (project_id, sprint_number)
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| sprint_number | INTEGER | NOT NULL | unique per project, e.g. 0–20 |
| name | VARCHAR(255) | NOT NULL | e.g. "Sprint 1 — Agent Contract Design" |
| planned_start | DATE | NOT NULL | |
| planned_end | DATE | NOT NULL | deadline |
| actual_end | DATE | NULL | set when status → done |
| status | sprint_status | NOT NULL | default: `not_started` |
| story_points_total | INTEGER | NOT NULL | default: 0 |
| story_points_done | INTEGER | NOT NULL | default: 0 |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_status     ON sprints(status);
CREATE INDEX idx_sprints_planned_end ON sprints(planned_end);
```

---

## 14. milestones

MVP milestone tracking per project, supporting FR-026 and FR-028.

```sql
CREATE TABLE milestones (
    id          UUID             PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID             NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name        VARCHAR(255)     NOT NULL,
    description TEXT,
    target_date DATE             NOT NULL,
    actual_date DATE,
    status      milestone_status NOT NULL DEFAULT 'not_started',
    mvp_number  INTEGER          NOT NULL,
    created_at  TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ      NOT NULL DEFAULT now()
);
```

| Column | Type | Nullable | Notes |
|---|---|---|---|
| id | UUID | NOT NULL | PK |
| project_id | UUID | NOT NULL | FK → projects.id |
| name | VARCHAR(255) | NOT NULL | e.g. "MVP 1 — Requirement Loop" |
| description | TEXT | NULL | |
| target_date | DATE | NOT NULL | target completion date |
| actual_date | DATE | NULL | set when status → done |
| status | milestone_status | NOT NULL | default: `not_started` |
| mvp_number | INTEGER | NOT NULL | 1–5 |
| created_at | TIMESTAMPTZ | NOT NULL | auto |
| updated_at | TIMESTAMPTZ | NOT NULL | auto |

**Indexes:**
```sql
CREATE INDEX idx_milestones_project_id  ON milestones(project_id);
CREATE INDEX idx_milestones_target_date ON milestones(target_date);
CREATE INDEX idx_milestones_status      ON milestones(status);
```

---

## Relationships Summary

```
projects
├── requirement_inputs   (project_id)
├── tasks                (project_id)
├── pipeline_runs        (project_id)
├── documents            (project_id)
├── messages             (project_id)
├── activity_logs        (project_id)
├── traceability_links   (project_id)
└── agent_memories       (project_id)

agents
├── tasks                (assigned_agent_id)
├── pipeline_steps       (agent_id)
├── documents            (created_by_agent_id)
├── activity_logs        (agent_id)
└── agent_memories       (agent_id)

pipeline_runs
└── pipeline_steps       (pipeline_run_id)

tasks
├── messages             (task_id)
└── activity_logs        (task_id)
```
