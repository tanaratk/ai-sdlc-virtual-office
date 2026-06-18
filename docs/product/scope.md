# Product Scope

**Project:** AI-SDLC Working Office  
**Version:** 1.0  
**Source:** AI-SDLC-Working-Office-Spec.md Section 2–7

---

## In Scope

### MVP 1 — Requirement Loop
- Project creation and management
- Requirement input (manual text, meeting transcript, chat log, markdown document, email content)
- Requirement Agent — produces structured Requirement Summary
- Gap Analysis Agent — produces Gap Analysis Report with clarification questions
- Human review gate after Gap Analysis
- Document storage and Markdown export
- Basic pipeline status display

### MVP 2 — BA / SA Documents
- BA Agent — BRD, FSD, User Stories, Acceptance Criteria
- Solution Architect Agent — Architecture, Database Design, API Spec, Workflow Design
- Human review gate after BA and after Architect

### MVP 3 — Dev / QA / Traceability
- Developer Agent — development task list, skeleton code plan
- QA Agent — Test Cases, UAT Scripts, Requirement Coverage Report
- Traceability Matrix (Requirement → User Story → Screen → API → DB → Test)

### MVP 4 — Virtual Office Experience
- 2D virtual office map with rooms per agent
- Agent avatar with movement and status bubbles
- Click-to-open agent console from office map
- Real-time WebSocket updates

### MVP 5 — Integration Layer
- RAG — document ingestion and semantic search
- GitHub — issue/branch/commit linking
- MCP — tool registry for external tool calls
- Change Impact Agent — impact analysis on requirement changes

---

## Out of Scope (All MVPs)

- Mobile application
- Audio / video transcription (planned post-MVP)
- 3D virtual office
- Complex A* pathfinding with furniture collision (Phase 2)
- Multi-tenant enterprise RBAC
- Auto-merge to GitHub without human approval
- Export to PDF (Phase 2)
- Real-time multi-user collaborative editing
- Billing / subscription management
- SSO / OAuth authentication (Phase 2)

---

## Assumptions

1. Single-user or small-team usage in MVP — no enterprise multi-tenant in scope
2. LLM runs locally via Ollama (`qwen3:8b`) by default; OpenAI is an optional alternative
3. Users have basic technical knowledge to run Docker and set up PostgreSQL
4. Agent sprite assets will be provided separately or use placeholder icons in MVP
5. Phaser.js is used for the Virtual Office map in MVP 4; may be simplified to plain React in MVP 1–3
6. GitHub integration is optional and configured per-project

---

## Constraints

1. LLM context window limits input to ~32,000 characters per agent call
2. Agent output must be JSON-validated before saving to database
3. Developer Agent must not generate implementation code until BRD, FSD, Architecture, API, DB, and Screen Spec are all in `approved` status
4. All agent runs must be logged with input reference, model, and output reference
