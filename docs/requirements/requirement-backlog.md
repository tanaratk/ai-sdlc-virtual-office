# Requirement Backlog

**Project:** AI-SDLC Working Office  
**Version:** 1.0  
**Date:** 2026-06-18  
**Status:** Baseline — Sprint 0

---

## Functional Requirements

| ID | Requirement | Priority | MVP | Status |
|---|---|---|---|---|
| FR-001 | Accept requirement input from multiple sources: manual text, meeting transcript, chat log, document upload (PDF, Word, Markdown), email content | Critical | MVP 1 | Open |
| FR-002 | Store each requirement input with project ID, input type, title, content, file URL, source owner, source date, tags, priority | Critical | MVP 1 | Open |
| FR-003 | Execute 10-step SDLC pipeline where each step is owned by one agent and produces one output document | Critical | MVP 1 | Open |
| FR-004 | Allow users to Approve or Reject each pipeline step output before the next step begins | Critical | MVP 1 | Open |
| FR-005 | Allow users to Re-run any pipeline step | High | MVP 1 | Open |
| FR-006 | Admin can Create, Edit, Delete, Activate/Deactivate agents | High | MVP 1 | Open |
| FR-007 | Admin can edit the system prompt of each agent | High | MVP 1 | Open |
| FR-008 | Admin can select the LLM model per agent | High | MVP 1 | Open |
| FR-009 | Track tasks through full status lifecycle: Backlog → New → Assigned → In Progress → Waiting User → Review → Approved → Rejected → Done → Failed | Critical | MVP 1 | Open |
| FR-010 | User can chat with each agent individually, with full chat history stored | High | MVP 1 | Open |
| FR-011 | Agents send structured handoff messages to the next agent, including payload and handoff reason | Critical | MVP 1 | Open |
| FR-012 | Store all agent-generated documents: Requirement Summary, Gap Analysis Report, BRD, FSD, User Story, Architecture, DB Design, API Spec, Wireframe Spec, Test Case, UAT Script, Change Impact Report | Critical | MVP 1 | Open |
| FR-013 | View documents in Markdown preview with version history and approval status | High | MVP 1 | Open |
| FR-014 | Export any document to Markdown | High | MVP 1 | Open |
| FR-015 | Maintain traceability matrix: Requirement → Gap → User Story → Screen → API → DB Table → Code Module → Test Case | High | MVP 3 | Open |
| FR-016 | Trigger Change Impact Agent when a requirement changes; identify all affected artifacts and estimate effort | Medium | MVP 5 | Open |
| FR-017 | Each agent has position (x, y) in virtual office and moves to relevant zone when task is assigned | Medium | MVP 4 | Open |
| FR-018 | Broadcast agent movement and status changes to all clients via WebSocket | Medium | MVP 4 | Open |
| FR-019 | User can click office map to command an agent to walk to that position | Low | MVP 4 | Open |
| FR-020 | Virtual Office shows named rooms per agent (Requirement Room, Gap Analysis Room, BA Room, etc.) | Medium | MVP 4 | Open |
| FR-021 | Agents display status bubbles: Thinking, Working, Reviewing, Done, Error | Medium | MVP 4 | Open |
| FR-022 | Project management: Create Project, list projects, select active project | Critical | MVP 1 | Open |
| FR-023 | LLM provider config: Ollama (base URL + model) and OpenAI (API key + model) | Critical | MVP 1 | Open |
| FR-024 | Log every agent run: agent name, input reference, prompt version, model, status, started_at, completed_at, error, output reference | Critical | MVP 1 | Open |
| FR-025 | Dashboard must display a Sprint Timeline view showing all sprints with sprint name, planned start date, planned end date, actual end date, duration, and status (Not Started / In Progress / Done / Overdue) | High | MVP 1 | Open |
| FR-026 | System must allow Project Admin to define MVP milestones with name, target date, and linked sprints; milestones must be shown on the timeline with visual indicators | High | MVP 1 | Open |
| FR-027 | System must alert users when a sprint deadline is approaching (≤3 days remaining) or overdue; alerts must appear in the dashboard header and in the PM Agent's summary output | High | MVP 1 | Open |
| FR-028 | PM Agent must include in its output: current sprint name, sprint progress (tasks done / total), days remaining to sprint deadline, next MVP milestone date, and list of overdue items | High | MVP 2 | Open |
| FR-029 | Project Admin must be able to update sprint start/end dates and move tasks between sprints via the Sprint Management screen | Medium | MVP 2 | Open |
| FR-030 | Before starting a pipeline run, the user must be able to select the project tech stack: Database (PostgreSQL, MS SQL, MySQL, MongoDB), Language/Framework (.NET, Node.js, Python/FastAPI, Java/Spring), and Platform (Web, Mobile, Both). The selection is stored per-project and injected into SA Agent, Developer Agent, and DevOps Agent prompts. | High | MVP 3 | Open |
| FR-031 | System must offer an Auto-Recommend mode for tech stack selection: when the user clicks "Recommend", the system analyzes the uploaded requirement inputs using LLM and suggests the most appropriate Database, Language/Framework, and Platform, with a short justification for each choice. The user may accept or override any recommendation before starting the pipeline. | Medium | MVP 3 | Open |

---

## Non-Functional Requirements

| ID | Requirement | Category | Priority | MVP | Status |
|---|---|---|---|---|---|
| NFR-001 | Dark theme, professional SaaS dashboard UI suitable for customer demos | Usability | High | MVP 1 | Open |
| NFR-002 | Agent WebSocket updates delivered within 500ms | Performance | High | MVP 4 | Open |
| NFR-003 | Support Ollama and OpenAI as interchangeable LLM providers per agent | Availability | Critical | MVP 1 | Open |
| NFR-004 | All data stored in PostgreSQL 15+ | Reliability | Critical | MVP 1 | Open |
| NFR-005 | Backend and DB containerisable with Docker Compose | Portability | High | MVP 1 | Open |
| NFR-006 | LLM input validated — max 32,000 characters per call | Reliability | High | MVP 1 | Open |
| NFR-007 | All agent outputs JSON-validated before DB save and Markdown render | Reliability | Critical | MVP 1 | Open |
| NFR-008 | System runnable on any machine with Docker + Node.js 20+ + Python 3.11+ | Portability | Medium | MVP 1 | Open |

---

## Business Rules

| ID | Rule | Priority | MVP | Status |
|---|---|---|---|---|
| BR-001 | Developer Agent must not generate code until all upstream documents are `approved` | Critical | MVP 3 | Open |
| BR-002 | Gap Analysis Agent must raise Approval Gap for any approval requirement missing Level/Role/SLA/Escalation | Critical | MVP 1 | Open |
| BR-003 | Every requirement must have a unique ID (FR-XXX, NFR-XXX, BR-XXX) | Critical | MVP 1 | Open |
| BR-004 | All agent outputs must be JSON-validated before saving to DB | Critical | MVP 1 | Open |
| BR-005 | Every agent run must be logged in pipeline_steps | Critical | MVP 1 | Open |
| BR-006 | Documents must be versioned; old versions retained | High | MVP 1 | Open |
| BR-007 | Human approval required at: post-Gap Analysis, post-BA, post-Architect, pre-Developer, post-QA | Critical | MVP 1 | Open |
| BR-008 | Pipeline run cannot be started until the project tech stack (DB, Language, Platform) has been either explicitly selected by the user or confirmed via Auto-Recommend. A pre-flight check must block the Run button if tech stack is unset. | High | MVP 3 | Open |
