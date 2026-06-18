# AI-SDLC Working Office

A 2D virtual office where AI agents collaborate through the full software development lifecycle — from raw requirements to deployment-ready artefacts.

Each agent occupies a room in the office, picks up tasks from the pipeline, produces a structured document, and hands off to the next agent automatically.

---

## Overview

| Item | Detail |
|---|---|
| Frontend | React + Vite + TypeScript + Tailwind CSS + Phaser.js |
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| Default LLM | Ollama (`qwen3:8b`) — also supports OpenAI |
| Pipeline | 10 steps, fully automated agent handoff |
| UI Screens | Dashboard, Upload, Agent Console, Document Viewer |

---

## Pipeline

The system runs a 10-step pipeline. Each step is handled by one agent. Agents hand off automatically when their document is complete.

| Step | Agent | Output Document |
|---|---|---|
| 1 | Requirement Agent | Requirement Summary |
| 2 | Gap Analysis Agent | Gap Analysis Report |
| 3 | BA Agent | BRD + FSD + User Stories |
| 4 | Solution Architect Agent | Architecture Doc |
| 5 | UX Agent | UX Spec + Screen Inventory |
| 6 | Developer Agent | Source Code |
| 7 | QA Agent | Test Plan |
| 8 | Change Impact Agent | Change Impact Report |
| 9 | Review Agent | Review Summary |
| 10 | Deploy Agent | Deployment Report |

---

## Folder Structure

```
ai-sdlc-virtual-office/
├── docs/
│   ├── contracts/          # Agent contracts (JSON) — inputs, outputs, handoff rules
│   │   ├── requirement-agent.contract.json
│   │   └── gap-analysis-agent.contract.json
│   ├── prompts/            # Agent system prompts (Markdown)
│   │   ├── requirement-agent.system.md
│   │   └── gap-analysis-agent.system.md
│   ├── templates/          # Output document templates (Markdown)
│   │   ├── requirement-summary.template.md
│   │   └── gap-analysis-report.template.md
│   └── database/
│       └── schema.md       # Full PostgreSQL schema with enums, FKs, indexes
├── backend/                # FastAPI application (to be implemented)
├── frontend/               # React + Phaser.js application (to be implemented)
├── infra/                  # Docker, CI/CD config (to be implemented)
├── PROGRESS.md             # Session-by-session task tracker
└── README.md
```

---

## Key Documents

| Document | Path | Description |
|---|---|---|
| Requirement Agent Contract | `docs/contracts/requirement-agent.contract.json` | Input/output spec for step 1 |
| Gap Analysis Agent Contract | `docs/contracts/gap-analysis-agent.contract.json` | Input/output spec for step 2 |
| Requirement Agent Prompt | `docs/prompts/requirement-agent.system.md` | Full system prompt with per-section instructions |
| Gap Analysis Agent Prompt | `docs/prompts/gap-analysis-agent.system.md` | Full system prompt with 12 gap categories, approval gap trigger rule |
| Requirement Summary Template | `docs/templates/requirement-summary.template.md` | Output template with 9 sections |
| Gap Analysis Report Template | `docs/templates/gap-analysis-report.template.md` | Output template with 14 sections |
| Database Schema | `docs/database/schema.md` | 12 tables, enum types, FK relationships, indexes |
| UI Design | [Figma](https://www.figma.com/design/fwTNT7ztQLI1Hj0Bj0EaJb) | Dashboard, Upload, Agent Console, Document Viewer |

---

## Database

12 PostgreSQL tables. See [`docs/database/schema.md`](docs/database/schema.md) for the full schema.

Core tables:

| Table | Purpose |
|---|---|
| `projects` | One row per project |
| `requirement_inputs` | Raw input files and text uploaded by the user |
| `agents` | Agent registry with live position and status |
| `tasks` | Work items assigned to agents |
| `pipeline_runs` | One row per end-to-end pipeline execution |
| `pipeline_steps` | One row per step per run |
| `documents` | All agent-generated output documents |
| `messages` | Agent-to-agent and user-to-agent messages |
| `activity_logs` | Append-only event log for the activity feed |
| `traceability_links` | Links between requirements, documents, and tests |
| `llm_settings` | LLM provider config (Ollama / OpenAI) |
| `agent_memories` | Per-agent, per-project long-term memory for RAG |

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- [Ollama](https://ollama.ai) with `qwen3:8b` pulled

```bash
ollama pull qwen3:8b
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL and OLLAMA_BASE_URL
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Environment Variables

| Variable | Example | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://user:pass@localhost:5432/aisdlc` | PostgreSQL connection string |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | `qwen3:8b` | Default Ollama model |
| `OPENAI_API_KEY` | `sk-...` | Optional — only needed if using OpenAI |

---

## Agent Contracts

Every agent follows the same contract structure:

```
agent       — id, name, role, model
input       — required and optional fields, constraints
output      — document type, sections, metadata
responsibilities — what the agent must do
handoff     — next agent, trigger, payload fields
pipeline_step — step order and timeout
office_behaviour — zones, status transitions, chat bubble
```

Contracts live in `docs/contracts/`. System prompts live in `docs/prompts/`.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes
4. Open a pull request

---

## Licence

MIT
