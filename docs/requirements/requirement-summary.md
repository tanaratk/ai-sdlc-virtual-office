# Requirement Summary

**Project:** AI-SDLC Working Office  
**Source:** AI-SDLC-Working-Office-Spec.md v1.0  
**Prepared By:** Sprint 0 — Requirement Intake  
**Date:** 2026-06-18  
**Status:** Baseline

---

## Business Objective

Build a web-based 2D virtual office where AI agents collaborate through the full Software Development Lifecycle. Users upload raw requirements and a pipeline of AI agents automatically produces BRD, FSD, User Stories, Architecture, API Spec, Database Design, Wireframes, Test Cases, and Change Impact Reports — each traceable back to the original requirement.

---

## Scope

### In Scope
- 10-step SDLC agent pipeline (Requirement → Gap Analysis → BA → SA → UX → Dev → QA → Change Impact → Documentation → PM Summary)
- Multi-source requirement input (manual text, meeting transcript, chat log, document upload, markdown, email)
- AI agent management (CRUD, prompt editing, model selection, avatar, home zone)
- Task management with full status lifecycle
- Agent-to-agent handoff and collaboration
- Document generation and versioning
- Traceability matrix (Requirement → User Story → Screen → API → DB → Test Case)
- Change impact analysis
- 2D virtual office with agent movement and real-time status via WebSocket
- LLM provider configuration (Ollama + OpenAI)
- Document export to Markdown

### Out of Scope
- Mobile application
- Audio/video transcription (future)
- 3D office, A* pathfinding with collision (Phase 2)
- Enterprise multi-tenant, RBAC, SSO (Phase 2)
- Auto-merge to GitHub without human approval
- PDF export (Phase 2)
- Real-time collaborative editing (Phase 2)

---

## Functional Requirements

| ID | Requirement | Source | Priority |
|---|---|---|---|
| FR-001 | System must accept requirement input from multiple sources: manual text, meeting transcript, chat log, document upload (PDF, Word, Markdown), email content | Spec §7.1 | Critical |
| FR-002 | System must store each requirement input with: project ID, input type, title, content, file URL, source owner, source date, tags, priority | Spec §7.1 | Critical |
| FR-003 | System must execute a 10-step SDLC pipeline where each step is owned by one agent and produces one output document | Spec §7.2 | Critical |
| FR-004 | System must allow users to Approve or Reject each pipeline step output before the next step begins | Spec §7.2 | Critical |
| FR-005 | System must allow users to Re-run any pipeline step | Spec §7.2 | High |
| FR-006 | Admin must be able to Create, Edit, Delete, Activate/Deactivate agents | Spec §7.3 | High |
| FR-007 | Admin must be able to edit the system prompt of each agent | Spec §7.3 | High |
| FR-008 | Admin must be able to select the LLM model per agent | Spec §7.3 | High |
| FR-009 | System must track tasks through a full status lifecycle: Backlog → New → Assigned → In Progress → Waiting User → Review → Approved → Rejected → Done → Failed | Spec §7.4 | Critical |
| FR-010 | User must be able to chat with each agent individually, with full chat history stored | Spec §7.5 | High |
| FR-011 | Agents must be able to send structured handoff messages to the next agent, including payload fields and handoff reason | Spec §7.6 | Critical |
| FR-012 | System must store all agent-generated documents: Requirement Summary, Gap Analysis Report, BRD, FSD, User Story, Architecture, DB Design, API Spec, Wireframe Spec, Test Case, UAT Script, Change Impact Report | Spec §7.7 | Critical |
| FR-013 | User must be able to view documents in Markdown preview with version history and approval status | Spec §7.7 | High |
| FR-014 | User must be able to export any document to Markdown | Spec §7.7 | High |
| FR-015 | System must maintain a traceability matrix linking: Requirement → Gap → User Story → Screen → API → DB Table → Code Module → Test Case | Spec §7.8 | High |
| FR-016 | When a requirement changes, system must trigger Change Impact Agent to identify all affected artifacts and estimate effort | Spec §7.9 | Medium |
| FR-017 | Each agent must have a position (x, y) in the virtual office map and move to the relevant zone when a task is assigned | Spec §8.1 | Medium |
| FR-018 | Agent movement and status changes must be broadcast to all connected clients via WebSocket | Spec §8.1, §8.3 | Medium |
| FR-019 | User must be able to click a position on the office map to command an agent to walk there | Spec §8.1 | Low |
| FR-020 | Virtual Office must display named rooms: Requirement Room, Gap Analysis Room, BA Room, SA Room, UX Studio, Developer Zone, QA Lab, Change Impact Room, Documentation Room, PM Command Center, Meeting Room | Spec §6.1 | Medium |
| FR-021 | Agents must display status bubbles: Thinking, Working, Reviewing, Done, Error | Spec §6.3 | Medium |
| FR-022 | System must support project management: Create Project, view all projects, select active project | Spec §7.1 | Critical |
| FR-023 | System must support LLM provider configuration: Ollama (base URL + model) and OpenAI (API key + model) | Spec §9.2.6 | Critical |
| FR-024 | System must log every agent run with: agent name, input reference, prompt version, model name, status, started_at, completed_at, error message, output reference | Sprint Skill §Rule 5 | Critical |

---

## Non-Functional Requirements

| ID | Requirement | Category | Priority |
|---|---|---|---|
| NFR-001 | UI must use a dark theme, modern professional SaaS dashboard style suitable for customer demos | Usability | High |
| NFR-002 | Agent position updates and status changes must be delivered to the client within 500ms via WebSocket | Performance | High |
| NFR-003 | System must support Ollama (local) and OpenAI as interchangeable LLM providers per agent | Availability | Critical |
| NFR-004 | All data must be stored in PostgreSQL 15+ | Reliability | Critical |
| NFR-005 | Backend and database must be containerisable with Docker Compose for local development | Portability | High |
| NFR-006 | LLM input must be validated — content must not exceed 32,000 characters per agent call | Reliability | High |
| NFR-007 | All agent outputs must be JSON-validated before being saved to the database and rendered to Markdown | Reliability | Critical |
| NFR-008 | System must run on any machine with Docker, Node.js 20+, and Python 3.11+ | Portability | Medium |

---

## Stakeholders

| Role | Responsibility | Involvement |
|---|---|---|
| Business Analyst | Define and review requirements, approve BRD/FSD | Approver |
| Solution Architect | Review architecture and DB/API design | Approver |
| Developer | Receive and implement tasks from approved design docs | User |
| QA Engineer | Review and approve test cases and UAT scripts | Approver |
| Project Manager | Monitor pipeline progress and agent status | User |
| Admin | Manage agents, prompts, models, and system settings | Owner |
| Consultant / Pre-sales | Use system as demo for customers | User |

---

## Assumptions

1. MVP 1 targets single-user or small team usage — no multi-tenant architecture required
2. Ollama with `qwen3:8b` is the default LLM for all agents; OpenAI is an optional alternative
3. Agent sprite artwork will be provided separately or use placeholders in MVP 1–3
4. Phaser.js virtual office is implemented in MVP 4; MVPs 1–3 use a simplified status dashboard
5. GitHub and MCP integrations are implemented in MVP 5 only

---

## Constraints

1. LLM context window: maximum 32,000 characters per agent call
2. Developer Agent must not generate implementation code until BRD, FSD, Architecture, API Spec, DB Design, and Screen Spec are all in `approved` status
3. Every generated artifact must include a requirement ID reference
4. Every agent run must be logged regardless of success or failure
5. Tech stack is fixed: React + Vite + TypeScript + Tailwind (frontend), FastAPI + SQLAlchemy + PostgreSQL (backend)

---

## Business Rules

| ID | Rule |
|---|---|
| BR-001 | Developer Agent must not generate implementation code until requirement_status, fsd_status, architecture_status, api_status, database_status, and screen_status are all `approved` |
| BR-002 | Gap Analysis Agent must raise an Approval Gap whenever a requirement mentions approval, authorisation, or sign-off but does not specify all four of: Approval Level, Approver Role, SLA, Escalation Rule |
| BR-003 | Every requirement must have a unique ID (FR-XXX, NFR-XXX, BR-XXX) |
| BR-004 | All agent outputs must be JSON-validated before being saved to the database |
| BR-005 | Every agent run must create a record in the agent_runs / pipeline_steps table |
| BR-006 | Agent-generated documents must be versioned; superseded versions must be retained |
| BR-007 | Human approval is required at: after Gap Analysis, after BA, after Architect, before Developer Agent, after QA |

---

## Open Questions

See [`open-questions.md`](open-questions.md) for the full list.
