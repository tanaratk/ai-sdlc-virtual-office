# CLAUDE.md — AI-SDLC Working Office

This file is read automatically by Claude Code at the start of every session.
It provides full project context so no manual re-briefing is needed.

---

## What This Project Is

**AI-SDLC Working Office** is an Agentic Software Factory — a web application where AI agents
collaborate through the full Software Development Lifecycle inside a 2D virtual office.

Users upload raw requirements (meeting transcript, chat log, document, manual text) and a
10-step pipeline of AI agents automatically produces BRD, FSD, User Stories, Architecture,
API Spec, Database Design, Wireframes, Test Cases, and Change Impact Reports.
Every output is traceable back to a requirement ID.

- **Repo:** https://github.com/tanaratk/ai-sdlc-virtual-office
- **Branch:** master
- **Working dir:** D:\AI_Office

---

## First Thing to Do Every Session

1. Read `PROGRESS.md` — it has the current sprint, completed work, and what is next
2. Read `ai-dlc-development-sprint-skill.md` — the full 20-sprint development playbook
3. Never start coding without checking which sprint is active

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Virtual Office | Phaser.js (MVP 4+), plain React for MVP 1–3 |
| UI Components | shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy + SQLModel |
| Database | PostgreSQL 15+ |
| Migrations | Alembic |
| Agent Orchestration | Database state machine (MVP 1), LangGraph (later) |
| LLM (default) | Ollama — model `qwen3:8b` |
| LLM (optional) | OpenAI |
| Templates | Markdown + Jinja2 |
| RAG | pgvector first, Qdrant later |
| Testing | pytest (backend), Vitest + Playwright (frontend) |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Folder Structure

```
ai-sdlc-virtual-office/
├── docs/
│   ├── product/            # Vision, scope, glossary
│   ├── requirements/       # Requirement summary, backlog, open questions
│   ├── agents/             # Agent contracts (JSON) — one per agent
│   ├── prompts/            # Agent system prompts + task prompts (Markdown)
│   ├── templates/          # Output document templates (Markdown)
│   ├── database/           # Schema, ERD, table spec, migration plan
│   ├── api/                # API list, OpenAPI spec, examples
│   ├── workflows/          # State machine, workflow specs, review points
│   └── traceability/       # Traceability model and matrix examples
├── backend/                # FastAPI application
├── frontend/               # React + Vite application
├── infra/                  # Docker Compose, CI/CD
├── rag/                    # Document ingestion and vector store
├── mcp/                    # MCP server configs
├── .github/workflows/      # GitHub Actions
├── ai-dlc-development-sprint-skill.md   # Sprint playbook — READ THIS
├── PROGRESS.md             # Session tracker — READ THIS FIRST
├── CLAUDE.md               # This file
└── README.md
```

> **Note:** Agent contracts live in `docs/agents/` (not `docs/contracts/`).
> The old `docs/contracts/` folder will be renamed in Sprint 1.

---

## The 10-Step SDLC Pipeline

| Step | Agent | Output |
|---|---|---|
| 1 | Requirement Agent | Requirement Summary |
| 2 | Gap Analysis Agent | Gap Analysis Report |
| 3 | BA Agent | BRD + FSD + User Stories |
| 4 | Solution Architect Agent | Architecture + DB Design + API Spec |
| 5 | UX Agent | Screen Inventory + Screen Spec + UX Flow |
| 6 | Developer Agent | Code task list + skeleton code |
| 7 | QA Agent | Test Cases + UAT Scripts |
| 8 | Change Impact Agent | Change Impact Report |
| 9 | Documentation Agent | Compiled project documents |
| 10 | PM Agent | Project summary + delivery report |

Human review gates: after step 2, after step 3, after step 4, before step 6, after step 7.

---

## Agent Contract Convention

Every agent has one contract file at `docs/agents/<agent-id>.contract.json`.

Structure:
```json
{
  "agent":          { "id", "name", "role", "version", "description", "home_zone", "model_provider", "default_model" },
  "input":          { "required_fields", "optional_fields", "constraints" },
  "output":         { "document_type", "format", "template_ref", "sections", "metadata" },
  "responsibilities": [],
  "handoff":        { "on_success", "on_failure" },
  "pipeline_step":  { "step_name", "step_order", "total_steps", "timeout_seconds" },
  "office_behaviour": { "idle_zone", "active_zone", "status_on_start", "status_on_complete", "chat_bubble_on_handoff" }
}
```

---

## Document ID Conventions

Every artifact must reference a requirement ID where possible.

| Artifact | ID Format |
|---|---|
| Functional Requirements | FR-001, FR-002 … |
| Non-Functional Requirements | NFR-001, NFR-002 … |
| Business Rules | BR-001, BR-002 … |
| Gaps | GAP-001, GAP-002 … |
| BRD sections | BRD-001 … |
| FSD sections | FSD-001 … |
| API endpoints | API-001 … |
| DB tables/fields | DB-001 … |
| Screens | UI-001 … |
| Test cases | TC-001 … |
| Open questions | OQ-001 … |

---

## Golden Rules (from ai-dlc-development-sprint-skill.md)

1. **Do not write backend or frontend code before these files exist:**
   - `docs/agents/*.contract.json`
   - `docs/prompts/*.md`
   - `docs/templates/*.md`
   - `docs/database/table-spec.md`
   - `docs/api/api-list.md`
   - `docs/workflows/*.md`

2. **Developer Agent must not generate implementation code** until
   `requirement_status`, `fsd_status`, `architecture_status`, `api_status`,
   `database_status`, and `screen_status` are all `approved`.

3. **Every generated artifact must link to a requirement ID** (FR-XXX, NFR-XXX, etc.)

4. **All agent outputs must be JSON first**, then validated, then rendered to Markdown.

5. **Every agent run must be logged** in `pipeline_steps` — no exceptions.

6. **Version everything:** requirements, contracts, prompts, templates, documents,
   DB design, API design, screen spec, test cases.

7. **Do not implement in early MVP:** complex workflow engine, 3D office, MCP tools,
   auto-merge to GitHub, large enterprise RAG, multi-tenant security, advanced RBAC.

---

## MVP Release Plan

| MVP | Scope | Status |
|---|---|---|
| MVP 1 | Requirement Loop: project + upload + Requirement Agent + Gap Analysis Agent + basic UI | Not started |
| MVP 2 | BA + SA documents: BRD, FSD, User Story, Architecture, DB Design, API Spec | Not started |
| MVP 3 | Dev/QA/Traceability: task list, skeleton plan, test cases, traceability matrix | Not started |
| MVP 4 | Virtual Office: 2D map, agent avatars, WebSocket movement | Not started |
| MVP 5 | Integration Layer: RAG, GitHub, MCP, Change Impact Agent | Not started |

---

## Key Decisions Made

| Decision | Value | Reason |
|---|---|---|
| Default LLM | Ollama `qwen3:8b` | Local, free, no API key needed for dev |
| DB table name | `requirement_inputs` (not `source_documents`) | Matches spec Section 12.2 |
| Agent contracts folder | `docs/agents/` | Matches sprint skill Section 3 |
| Traceability table | `traceability_links` with `link_type` enum | Supports many-to-many between any artifact types |
| RAG storage | pgvector first | Keeps stack simple; migrate to Qdrant later if needed |
| Virtual Office renderer | Phaser.js in MVP 4 | Plain React status board in MVP 1–3 |
| Workflow engine | DB state machine first | LangGraph added in later MVP |

---

## What NOT to Do

- Do not rename `requirement_inputs` table to `source_documents`
- Do not skip the JSON validation step between LLM output and DB save
- Do not let Developer Agent generate production code before all upstream docs are approved
- Do not put agent contracts in `docs/contracts/` — use `docs/agents/`
- Do not merge PRs without human review (GitHub integration rule)
- Do not add emojis to files unless explicitly requested
- Do not create markdown documentation files speculatively — only when a sprint requires them

---

## Workflow with This Agent

- Work **one sprint at a time** — complete, commit, then wait for confirmation
- After each sprint: report what was done and ask "พร้อมไป Sprint N ได้เลยไหมครับ?"
- Commit message format: `feat(sprint-N): <description>`
- Always update `PROGRESS.md` when a sprint completes

---

## Important Files to Read When Resuming

| File | When to Read |
|---|---|
| `PROGRESS.md` | Always — first thing every session |
| `ai-dlc-development-sprint-skill.md` | Before starting any sprint |
| `docs/requirements/requirement-backlog.md` | Before creating contracts or prompts |
| `docs/requirements/open-questions.md` | Before making assumptions in implementation |
| `docs/database/schema.md` | Before writing any DB models or migrations |
| `Requirement Spec/AI-SDLC-Working-Office-Spec.md` | When spec detail is needed for a specific section |
