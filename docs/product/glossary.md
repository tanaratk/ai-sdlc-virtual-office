# Glossary

**Project:** AI-SDLC Working Office  
**Version:** 1.0

---

| Term | Definition |
|---|---|
| Agent | An AI worker that performs a specific SDLC role (e.g. Requirement Agent, BA Agent). Each agent has a system prompt, a contract, and a home zone in the virtual office. |
| Agent Contract | A JSON file defining an agent's input schema, output schema, responsibilities, handoff rules, and pipeline position. |
| Agent Run | One execution of an agent. Logged with input reference, model name, status, start/end time, and output reference. |
| Approval Gap | A type of gap raised when a requirement mentions approval or sign-off but does not specify all four of: Approval Level, Approver Role, SLA, and Escalation Rule. |
| BRD | Business Requirements Document — a formal document describing what the system must do from a business perspective. Produced by the BA Agent. |
| Change Impact Report | A document listing all artifacts (screens, APIs, DB tables, test cases) affected by a requirement change. Produced by the Change Impact Agent. |
| Document | Any agent-generated output stored in the `documents` table (e.g. Requirement Summary, Gap Analysis Report, BRD). |
| FSD | Functional Specification Document — a detailed document describing how each feature behaves. Produced by the BA Agent. |
| Gap | A problem found in the Requirement Summary: missing, ambiguous, conflicting, duplicate, or incomplete information. |
| Handoff | The act of one agent completing its task and passing its output to the next agent in the pipeline, including a structured payload. |
| Home Zone | The default room/zone in the virtual office where an agent stands when idle. |
| Human Review Gate | A point in the pipeline where the workflow pauses and waits for a human to approve or reject the agent's output before continuing. |
| LLM | Large Language Model — the AI model powering each agent (e.g. qwen3:8b via Ollama, or GPT-4o via OpenAI). |
| MCP | Model Context Protocol — a standard for AI agents to call external tools (filesystem, GitHub, Figma, etc.). |
| Pipeline | The ordered sequence of 10 steps an agent team follows from Requirement to Deployment. |
| Pipeline Run | One end-to-end execution of the pipeline for a project. |
| Pipeline Step | One node in the pipeline, owned by one agent, producing one output document. |
| Project | The top-level entity in the system. All requirements, pipeline runs, agents, documents, and messages belong to a project. |
| RAG | Retrieval-Augmented Generation — using semantic search over stored documents to provide relevant context to an LLM. |
| Requirement Input | Raw source content uploaded by the user (meeting transcript, chat log, manual text, uploaded file). Stored in the `requirement_inputs` table. |
| Requirement Summary | The structured output of the Requirement Agent, containing FRs, NFRs, Stakeholders, Assumptions, Constraints, Business Rules, and Open Questions. |
| SDLC | Software Development Lifecycle — the full process from requirements to deployment. |
| Traceability | The ability to link every artifact (User Story, Screen, API, DB table, Test Case) back to its originating requirement ID. |
| User Story | A short description of a feature from a user's perspective: "As a [role] I want [feature] so that [value]." Produced by the BA Agent. |
| Virtual Office | The 2D map displayed in the browser where AI agents are shown as avatars moving between rooms as they work. |
| Zone | A named area in the virtual office map (e.g. `requirement_room`, `gap_analysis_room`, `ba_room`). Each agent has a home zone and moves to active zones when working. |
