# Open Questions

**Project:** AI-SDLC Working Office  
**Version:** 1.0  
**Date:** 2026-06-18  
**Status:** Unresolved — needs answer before implementation

---

## Critical (Must answer before MVP 1)

| ID | Question | Area | Raised By |
|---|---|---|---|
| OQ-001 | Is user authentication required in MVP 1? The spec does not mention login, roles, or session management. If not, who can access the system and change agent settings? | Security / Auth | Sprint 0 |
| OQ-002 | Should the system support multiple users working on the same project simultaneously, or is MVP 1 single-user only? This affects database design (user ownership fields) and WebSocket routing. | Architecture | Sprint 0 |
| OQ-003 | What is the maximum file size for uploaded requirement documents? The spec mentions PDF, Word, Markdown uploads but does not specify limits. | Input Management | Sprint 0 |
| OQ-004 | How should the system handle LLM timeout or error during an agent run? Should it auto-retry, notify the user, or mark the step as failed and stop the pipeline? | Error Handling | Sprint 0 |
| OQ-005 | Who provides the agent sprite artwork for the virtual office? Is a placeholder (colored circle with initials) acceptable for MVP 1–3? | UI / Assets | Sprint 0 |

---

## High (Should answer before MVP 1 ends)

| ID | Question | Area | Raised By |
|---|---|---|---|
| OQ-006 | The spec mentions LangGraph or OpenAI Agents SDK for orchestration. Which should be implemented first? LangGraph adds significant complexity; a simple database state machine may be sufficient for MVP 1. | Architecture | Sprint 0 |
| OQ-007 | Should the system support multiple LLM configurations simultaneously (e.g. one agent uses Ollama, another uses OpenAI), or is one active config applied to all agents? | LLM Config | Sprint 0 |
| OQ-008 | The spec mentions `qwen3:8b` as default model. What is the minimum hardware requirement (RAM, GPU/CPU) for running this locally? Should this be documented in README? | Deployment | Sprint 0 |
| OQ-009 | Should requirement input content be stored as plain text in the DB, or should file uploads be stored in an object storage (S3, MinIO) with only the URL stored? | Storage | Sprint 0 |
| OQ-010 | Is there a requirement to show the LLM's chain-of-thought / reasoning to the user, or should only the final structured output be shown? The spec mentions "Chain of Thought Summary without exposing detailed reasoning." | UX | Sprint 0 |

---

## Medium (Clarify during MVP 2)

| ID | Question | Area | Raised By |
|---|---|---|---|
| OQ-011 | What is the output format of the BA Agent — should BRD, FSD, and User Stories be one combined document or three separate documents per pipeline run? | Output Design | Sprint 0 |
| OQ-012 | Should the system support requirement change tracking (versioning of FR/NFR items), or only document versioning? | Traceability | Sprint 0 |
| OQ-013 | The spec mentions a PM Agent and Documentation Agent in Section 5.9–5.11 but they are not listed in the core 8 agents in the sprint skill. Are they in scope for MVP? | Scope | Sprint 0 |
| OQ-014 | Should the traceability matrix be generated automatically as agents run, or manually linked by the user? | Traceability | Sprint 0 |
| OQ-015 | What level of detail is expected in the Architect Agent output — high-level overview or component-level design with specific technology choices? | Output Quality | Sprint 0 |

---

## Low (Clarify before MVP 4–5)

| ID | Question | Area | Raised By |
|---|---|---|---|
| OQ-016 | Should the virtual office use Phaser.js for the 2D map in MVP 4, or a simpler CSS/SVG layout? Phaser.js adds a large dependency but enables full game-like movement. | Technology | Sprint 0 |
| OQ-017 | What tile map format is expected for the virtual office? The spec mentions Tiled Map Editor. Does an existing map asset exist? | Virtual Office | Sprint 0 |
| OQ-018 | Should RAG use pgvector (keeping all data in PostgreSQL) or Qdrant (separate vector store)? The sprint skill recommends pgvector first. | RAG | Sprint 0 |
| OQ-019 | For GitHub integration in MVP 5 — should the system create GitHub Issues from development tasks automatically, or only on explicit user command? | Integration | Sprint 0 |
| OQ-020 | Should MCP tool calls require per-call user approval in the UI, or is pre-registration of approved tools sufficient? | MCP / Security | Sprint 0 |
