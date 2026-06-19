---
name: ai-sdlc-sprint
description: Sprint playbook for AI-SDLC Virtual Office. Use when starting a new sprint, checking which sprint is active, or planning implementation order. Covers all 24 sprints from requirement intake through CI/CD, with per-sprint tasks, outputs, and acceptance criteria.
license: project
---
# AI-DLC Development Sprint Skill
> Skill / Playbook เธชเธณเธซเธฃเธฑเธเนเธซเน Codex, Claude Code, เธซเธฃเธทเธญ AI Coding Agent เนเธเนเธเธฑเธ’เธเธฒเธฃเธฐเธเธ AI-DLC Virtual Office เธ•เนเธญเธเธฒเธ Requirement Specification

---

## 0. Purpose

เน€เธญเธเธชเธฒเธฃเธเธตเนเนเธเนเน€เธเนเธเนเธเธงเธ—เธฒเธเธเธฑเธ’เธเธฒ **AI-DLC Virtual Office** เธซเธฅเธฑเธเธเธฒเธเนเธ”เนเธฃเธฑเธเนเธเธฅเน Requirement เนเธฅเนเธง เน€เธเนเธ `requirements.md`, `brd.md`, `fsd.md` เธซเธฃเธทเธญ requirement transcript

เน€เธเนเธฒเธซเธกเธฒเธขเธเธทเธญเนเธซเน AI Coding Agent เน€เธเนเธ **Codex / Claude Code / Cursor / Kiro** เธชเธฒเธกเธฒเธฃเธ–เธ—เธณเธเธฒเธเธ•เนเธญเนเธ”เนเธญเธขเนเธฒเธเน€เธเนเธเธฅเธณเธ”เธฑเธ เนเธ”เธขเนเธกเนเธฃเธตเธ generate code เธ—เธฑเธเธ—เธต เนเธ•เนเธ•เนเธญเธเธเนเธฒเธเธเธฑเนเธเธ•เธญเธเธญเธญเธเนเธเธ Agent Contract, Prompt, Template, Database, API, Workflow, Backend, Frontend, Traceability เนเธฅเธฐ Virtual Office

---

## 1. Target System Overview

เธฃเธฐเธเธเธ—เธตเนเธ•เนเธญเธเธเธฑเธ’เธเธฒเธเธทเธญ **AI-DLC Virtual Office** เธชเธณเธซเธฃเธฑเธเธเนเธงเธข automate เธเธฑเนเธเธ•เธญเธ Software Development Life Cycle เธ”เนเธงเธข AI Agent

### Main Flow

```text
Requirement Source
โ“
Requirement Agent
โ“
Gap Analysis Agent
โ“
BA Agent
โ“
Solution Architect Agent
โ“
UX Agent
โ“
Developer Agent
โ“
QA Agent
โ“
Change Impact Agent
โ“
Traceability / GitHub / RAG / MCP
```

---

## 2. Recommended Tech Stack

| Layer | Recommended Tool |
|---|---|
| Frontend | React + Vite + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Virtual Office UI | React + PNG/SVG sprite, later Phaser.js if needed |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy or SQLModel |
| DB Migration | Alembic |
| AI Agent Orchestration | LangGraph or OpenAI Agents SDK |
| Prompt / Template | Markdown + Jinja2 |
| RAG | PostgreSQL + pgvector first, Qdrant later if needed |
| API Spec | OpenAPI / Swagger |
| Workflow | Database state machine first, LangGraph later |
| Source Control | GitHub |
| CI/CD | GitHub Actions |
| Container | Docker / Docker Compose |
| Testing | pytest, Playwright, Vitest |
| Documentation | Markdown |

---

## 3. Repository Structure

AI Coding Agent must create or follow this folder structure.

```text
ai-dlc-virtual-office/
  docs/
    product/
      vision.md
      scope.md
      glossary.md

    requirements/
      requirements.md
      requirement-backlog.md
      open-questions.md

    agents/
      requirement-agent.contract.json
      gap-analysis-agent.contract.json
      ba-agent.contract.json
      architect-agent.contract.json
      ux-agent.contract.json
      developer-agent.contract.json
      qa-agent.contract.json
      change-impact-agent.contract.json

    prompts/
      requirement-agent.system.md
      requirement-agent.task.md
      gap-analysis-agent.system.md
      gap-analysis-agent.task.md
      ba-agent.system.md
      architect-agent.system.md
      ux-agent.system.md
      developer-agent.system.md
      qa-agent.system.md
      change-impact-agent.system.md

    templates/
      requirement-summary.template.md
      gap-analysis-report.template.md
      brd.template.md
      fsd.template.md
      user-story.template.md
      architecture-design.template.md
      database-design.template.md
      api-spec.template.md
      screen-spec.template.md
      test-case.template.md
      uat-script.template.md
      change-impact-report.template.md

    database/
      erd.md
      table-spec.md
      migration-plan.md

    api/
      api-list.md
      openapi.yaml
      request-response-examples.md

    workflows/
      requirement-to-code.workflow.md
      agent-state-machine.md
      human-review-points.md

    traceability/
      traceability-model.md
      traceability-matrix-example.md

  backend/
    app/
      main.py
      core/
      db/
      api/
      schemas/
      services/
      agents/
      workflows/
      templates/
    alembic/
    tests/
    Dockerfile
    pyproject.toml

  frontend/
    src/
      components/
      pages/
      services/
      types/
      assets/
    package.json
    vite.config.ts

  infra/
    docker-compose.yml

  rag/
    documents/
    ingestion/

  mcp/
    servers/

  .github/
    workflows/
```

---

# 4. Development Sprint Plan

---

# Sprint 0: Requirement Intake & Baseline Review

## Objective

เธ•เธฃเธงเธเธชเธญเธ requirement เธ—เธตเนเนเธ”เนเธกเธฒ เนเธฅเธฐเนเธขเธเนเธซเนเน€เธเนเธเนเธเธฃเธเธชเธฃเนเธฒเธเธ—เธตเน Agent เนเธเนเธ•เนเธญเนเธ”เน

## Input

```text
requirements.md
meeting-transcript.md
chat-log.md
business-notes.md
existing-brd.md
existing-fsd.md
```

## Tasks for AI Coding Agent

1. Read all requirement files in `/docs/requirements/`
2. Extract functional requirements
3. Extract non-functional requirements
4. Extract business rules
5. Extract user roles
6. Extract integration points
7. Extract data entities
8. Extract open questions
9. Create requirement backlog

## Output Files

```text
docs/requirements/requirement-backlog.md
docs/requirements/open-questions.md
docs/requirements/requirement-summary.md
```

## Acceptance Criteria

- เธ—เธธเธ requirement เธ•เนเธญเธเธกเธต unique ID เน€เธเนเธ `REQ-001`
- เนเธขเธ Functional / Non-functional เธเธฑเธ”เน€เธเธ
- เธกเธตเธฃเธฒเธขเธเธฒเธฃเธเธณเธ–เธฒเธกเธ—เธตเนเธขเธฑเธเนเธกเนเธเธฑเธ”เน€เธเธ
- เนเธกเนเน€เธ”เธฒ requirement เน€เธญเธ เธ–เนเธฒเนเธกเนเธเธฑเธ”เนเธซเนเนเธชเนเนเธ open questions

---

# Sprint 1: Agent Contract Design

## Objective

เธญเธญเธเนเธเธเธชเธฑเธเธเธฒเธเธฒเธฃเธ—เธณเธเธฒเธเธเธญเธ Agent เนเธ•เนเธฅเธฐเธ•เธฑเธง เน€เธเธทเนเธญเนเธซเน input/output เธเธฑเธ”เน€เธเธเนเธฅเธฐเธ•เธฃเธงเธเธชเธญเธเนเธ”เน

## Tasks for AI Coding Agent

1. Create JSON contract for each Agent
2. Define input schema
3. Define output schema
4. Define validation rules
5. Define error handling
6. Define next agent handoff structure

## Required Agents

| Agent | Purpose |
|---|---|
| Requirement Agent | Summarize requirement |
| Gap Analysis Agent | Detect missing, unclear, conflicting requirements |
| BA Agent | Generate BRD, FSD, User Stories |
| Solution Architect Agent | Generate architecture, database, API, workflow |
| UX Agent | Generate screen list, wireframe spec, screen spec |
| Developer Agent | Generate backend/frontend skeleton and code tasks |
| QA Agent | Generate test cases and UAT scripts |
| Change Impact Agent | Analyze impact when requirement changes |

## Output Files

```text
docs/agents/requirement-agent.contract.json
docs/agents/gap-analysis-agent.contract.json
docs/agents/ba-agent.contract.json
docs/agents/architect-agent.contract.json
docs/agents/ux-agent.contract.json
docs/agents/developer-agent.contract.json
docs/agents/qa-agent.contract.json
docs/agents/change-impact-agent.contract.json
```

## Contract Template

```json
{
  "agent_name": "RequirementAgent",
  "version": "1.0.0",
  "purpose": "Summarize and structure requirements from source documents",
  "input": {
    "project_id": "string",
    "source_type": "meeting_transcript | chat_log | document | manual_input",
    "content": "string",
    "project_context": "string"
  },
  "output": {
    "summary": "string",
    "functional_requirements": [],
    "non_functional_requirements": [],
    "business_rules": [],
    "assumptions": [],
    "open_questions": [],
    "risks": []
  },
  "validation_rules": [
    "Every requirement must have an ID",
    "Do not invent requirements",
    "Unclear items must be added to open_questions"
  ],
  "next_agent": "GapAnalysisAgent"
}
```

## Acceptance Criteria

- เธ—เธธเธ Agent เธกเธต contract
- เธ—เธธเธ output เน€เธเนเธ JSON เธ—เธตเน validate เนเธ”เน
- เธ—เธธเธ Agent เธฃเธฐเธเธธ next_agent เธซเธฃเธทเธญ end state
- Contract เธ•เนเธญเธเธเธฃเนเธญเธกเธเธณเนเธเธชเธฃเนเธฒเธ Pydantic schema

---

# Sprint 2: Prompt & Template Design

## Objective

เธชเธฃเนเธฒเธ prompt เนเธฅเธฐ document template เธ—เธตเนเนเธเนเธเนเธณเนเธ”เน เนเธกเนเนเธเน prompt เนเธเธ manual เธเธฃเธฑเนเธเน€เธ”เธตเธขเธง

## Tasks for AI Coding Agent

1. Create system prompt for each Agent
2. Create task prompt for each Agent
3. Create review prompt if required
4. Create correction prompt if required
5. Create markdown document template
6. Ensure output format matches Agent Contract

## Output Files

```text
docs/prompts/requirement-agent.system.md
docs/prompts/requirement-agent.task.md
docs/prompts/gap-analysis-agent.system.md
docs/prompts/gap-analysis-agent.task.md
docs/prompts/ba-agent.system.md
docs/prompts/architect-agent.system.md
docs/prompts/ux-agent.system.md
docs/prompts/developer-agent.system.md
docs/prompts/qa-agent.system.md
docs/prompts/change-impact-agent.system.md

docs/templates/requirement-summary.template.md
docs/templates/gap-analysis-report.template.md
docs/templates/brd.template.md
docs/templates/fsd.template.md
docs/templates/user-story.template.md
docs/templates/architecture-design.template.md
docs/templates/database-design.template.md
docs/templates/api-spec.template.md
docs/templates/screen-spec.template.md
docs/templates/test-case.template.md
docs/templates/uat-script.template.md
docs/templates/change-impact-report.template.md
```

## Prompt Rules

Every prompt must include:

```text
Role
Objective
Input
Rules
Output Format
Validation Criteria
Handoff Instruction
```

## Requirement Agent Prompt Example

```text
Role:
You are Requirement Agent for AI-DLC.

Objective:
Analyze source content and extract structured requirements.

Rules:
- Do not invent requirements.
- If information is unclear, add it to open_questions.
- Separate functional and non-functional requirements.
- Assign unique requirement IDs.
- Preserve business meaning.

Output:
Return JSON matching requirement-agent.contract.json.
```

## Acceptance Criteria

- Prompt output matches contract
- Prompt is reusable
- Template can generate Markdown document
- Template supports requirement ID and traceability ID

---

# Sprint 3: Database Design

## Objective

เธญเธญเธเนเธเธเธเธฒเธเธเนเธญเธกเธนเธฅเน€เธเธทเนเธญเธฃเธญเธเธฃเธฑเธ Project, Requirement, Agent Run, Document, Workflow เนเธฅเธฐ Traceability

## Tasks for AI Coding Agent

1. Create table specification
2. Create ERD markdown
3. Define primary keys and foreign keys
4. Define status fields
5. Define audit fields
6. Define traceability model
7. Prepare migration plan

## Core Tables

| Table | Purpose |
|---|---|
| projects | Project master |
| source_documents | Uploaded transcript/chat/document |
| requirements | Requirement items |
| requirement_versions | Requirement version history |
| agents | Agent definitions |
| agent_runs | Agent execution history |
| agent_outputs | Agent generated output |
| documents | Generated documents |
| document_versions | Document version history |
| workflows | Workflow definitions |
| workflow_runs | Workflow execution history |
| workflow_steps | Workflow step history |
| traceability_links | Links between requirement/design/code/test |
| api_specs | API specification |
| database_specs | Database design output |
| screen_specs | UX screen specification |
| test_cases | QA test case |
| change_impacts | Change impact report |
| rag_documents | RAG source documents |
| embeddings | Vector embeddings if using pgvector |

## Output Files

```text
docs/database/erd.md
docs/database/table-spec.md
docs/database/migration-plan.md
```

## Acceptance Criteria

- Every major artifact can be stored
- Every Agent run is traceable
- Requirement versioning is supported
- Traceability link supports many-to-many relation
- Database design is ready for Alembic migration

---

# Sprint 4: API Design

## Objective

เธญเธญเธเนเธเธ API เนเธซเน Frontend เนเธฅเธฐ Agent Runtime เน€เธฃเธตเธขเธเนเธเนเธเธฒเธเนเธ”เน

## Tasks for AI Coding Agent

1. Create API list
2. Define request/response schema
3. Define error response format
4. Define authentication placeholder
5. Generate initial OpenAPI spec
6. Map API to database tables

## Required API Groups

| API Group | Example Endpoint |
|---|---|
| Project | `GET /projects`, `POST /projects` |
| Source Document | `POST /sources/upload`, `GET /sources/{id}` |
| Requirement | `GET /requirements`, `POST /requirements` |
| Agent | `POST /agents/run`, `GET /agents/runs/{id}` |
| Document | `POST /documents/generate`, `GET /documents/{id}` |
| Workflow | `POST /workflows/run`, `GET /workflows/runs/{id}` |
| Traceability | `GET /traceability`, `POST /traceability/link` |
| RAG | `POST /rag/ingest`, `POST /rag/search` |
| GitHub | `POST /github/repos`, `POST /github/commit` |
| MCP | `GET /mcp/tools`, `POST /mcp/tools/run` |

## Output Files

```text
docs/api/api-list.md
docs/api/openapi.yaml
docs/api/request-response-examples.md
```

## Acceptance Criteria

- API supports Sprint 5 backend implementation
- Every API has request and response example
- Every response includes success/error structure
- API can be tested in Swagger/Postman/Bruno

---

# Sprint 5: Workflow Design

## Objective

เธญเธญเธเนเธเธ workflow เธเธฒเธฃเธ—เธณเธเธฒเธเธเธญเธ Agent เธ•เธฑเนเธเนเธ•เนเธฃเธฑเธ requirement เธ–เธถเธ generate code/test

## Tasks for AI Coding Agent

1. Define workflow state machine
2. Define Agent execution order
3. Define human review points
4. Define failure handling
5. Define retry policy
6. Define workflow status
7. Define handoff data between Agents

## Initial Workflow

```text
START
โ“
UPLOAD_SOURCE
โ“
RUN_REQUIREMENT_AGENT
โ“
RUN_GAP_ANALYSIS_AGENT
โ“
WAIT_FOR_USER_REVIEW
โ“
RUN_BA_AGENT
โ“
RUN_ARCHITECT_AGENT
โ“
RUN_UX_AGENT
โ“
WAIT_FOR_USER_APPROVAL
โ“
RUN_DEVELOPER_AGENT
โ“
RUN_QA_AGENT
โ“
UPDATE_TRACEABILITY
โ“
END
```

## Workflow Status

```text
draft
running
waiting_for_user
completed
failed
cancelled
```

## Human Review Points

| Review Point | Reason |
|---|---|
| After Gap Analysis | User must answer missing/unclear requirements |
| After BA Agent | Confirm BRD/FSD/User Story |
| After Architect Agent | Confirm architecture, DB, API |
| Before Developer Agent | Prevent wrong code generation |
| After QA Agent | Confirm test coverage |

## Output Files

```text
docs/workflows/requirement-to-code.workflow.md
docs/workflows/agent-state-machine.md
docs/workflows/human-review-points.md
```

## Acceptance Criteria

- Workflow has clear states
- Agent handoff is defined
- Human review is included
- Failure and retry are defined

---

# Sprint 6: Backend Skeleton

## Objective

เธชเธฃเนเธฒเธ Backend Skeleton เธ”เนเธงเธข FastAPI เน€เธเธทเนเธญเธฃเธญเธเธฃเธฑเธ project, requirement, agent run เนเธฅเธฐ document generation

## Tasks for AI Coding Agent

1. Initialize FastAPI project
2. Create app structure
3. Add config management
4. Add database connection
5. Add SQLAlchemy/SQLModel models
6. Add Alembic migration
7. Add API routes
8. Add service layer
9. Add basic tests
10. Add Dockerfile

## Backend Structure

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      logging.py
    db/
      session.py
      models.py
      base.py
    api/
      routes/
        projects.py
        sources.py
        requirements.py
        agents.py
        documents.py
        workflows.py
        traceability.py
        rag.py
    schemas/
      project.py
      source.py
      requirement.py
      agent.py
      document.py
      workflow.py
      traceability.py
    services/
      project_service.py
      source_service.py
      requirement_service.py
      agent_service.py
      document_service.py
      workflow_service.py
      traceability_service.py
    agents/
      base_agent.py
      requirement_agent.py
      gap_analysis_agent.py
    workflows/
      requirement_workflow.py
    templates/
    tests/
  alembic/
  Dockerfile
  pyproject.toml
```

## MVP Backend APIs

Must implement first:

```text
POST /projects
GET /projects
POST /sources/upload
GET /sources/{id}
POST /agents/run/requirement
POST /agents/run/gap-analysis
GET /agents/runs/{id}
GET /requirements
POST /documents/generate/requirement-summary
GET /documents/{id}
```

## Acceptance Criteria

- Backend starts successfully
- Swagger UI works
- PostgreSQL connection works
- Alembic migration works
- Can create project
- Can upload source content
- Can run mock Requirement Agent
- Can store agent output

---

# Sprint 7: Frontend Skeleton

## Objective

เธชเธฃเนเธฒเธ Frontend Skeleton เธ”เนเธงเธข React + Vite + TypeScript เน€เธเธทเนเธญเนเธซเนเธเธนเนเนเธเน upload requirement เนเธฅเธฐ run Agent เนเธ”เน

## Tasks for AI Coding Agent

1. Initialize React Vite TypeScript project
2. Add Tailwind CSS
3. Add layout
4. Add routing
5. Add API client
6. Add pages
7. Add components
8. Add basic state management
9. Add document viewer
10. Add agent run status display

## Frontend Structure

```text
frontend/
  src/
    app/
      App.tsx
      router.tsx
    components/
      layout/
        AppLayout.tsx
        Sidebar.tsx
        Topbar.tsx
      agent/
        AgentCard.tsx
        AgentRunStatus.tsx
        AgentConsole.tsx
      document/
        DocumentViewer.tsx
      requirement/
        RequirementUpload.tsx
        RequirementList.tsx
      traceability/
        TraceabilityMatrix.tsx
      virtual-office/
        VirtualOfficeMap.tsx
        AgentAvatar.tsx
    pages/
      Dashboard.tsx
      ProjectWorkspace.tsx
      RequirementIntake.tsx
      AgentConsolePage.tsx
      DocumentReview.tsx
      TraceabilityPage.tsx
      VirtualOfficePage.tsx
      Settings.tsx
    services/
      apiClient.ts
      projectApi.ts
      sourceApi.ts
      agentApi.ts
      documentApi.ts
    types/
      project.ts
      requirement.ts
      agent.ts
      document.ts
      workflow.ts
```

## MVP Pages

| Page | Purpose |
|---|---|
| Dashboard | Show projects and status |
| Project Workspace | Work inside selected project |
| Requirement Intake | Upload/paste requirement |
| Agent Console | Run Requirement/Gap Agent |
| Document Review | View generated requirement summary |
| Traceability Page | Basic traceability matrix |
| Virtual Office Page | Simple room/agent status UI |

## Acceptance Criteria

- Frontend starts successfully
- User can create/open project
- User can paste/upload requirement
- User can click Run Requirement Agent
- User can view generated output
- User can view basic Agent status

---

# Sprint 8: Requirement Agent MVP

## Objective

Implement Requirement Agent เธเธฃเธดเธ เน€เธเธทเนเธญเธชเธฃเธธเธ requirement เธเธฒเธ input

## Tasks for AI Coding Agent

1. Load requirement-agent contract
2. Load requirement-agent prompt
3. Build prompt using input content
4. Call selected LLM provider
5. Validate JSON output
6. Save agent run
7. Save requirements
8. Save document output
9. Return result to frontend

## Agent Runtime Pattern

```text
Input Validator
โ“
Prompt Loader
โ“
Prompt Builder
โ“
LLM Call
โ“
Output Parser
โ“
Output Validator
โ“
Save Agent Run
โ“
Save Requirement Items
โ“
Return Result
```

## Acceptance Criteria

- Agent reads uploaded requirement
- Agent returns structured JSON
- Every requirement has ID
- Agent does not invent missing information
- Output is saved in database
- User can view output in frontend

---

# Sprint 9: Gap Analysis Agent MVP

## Objective

Implement Gap Analysis Agent เน€เธเธทเนเธญเธ•เธฃเธงเธ requirement เธ—เธตเนเนเธกเนเธเธฃเธ เนเธกเนเธเธฑเธ” เธซเธฃเธทเธญเธเธฑเธ”เนเธขเนเธเธเธฑเธ

## Tasks for AI Coding Agent

1. Load existing requirements
2. Load gap-analysis-agent contract
3. Build gap analysis prompt
4. Detect missing information
5. Detect unclear requirement
6. Detect conflicting requirement
7. Generate questions for user
8. Save gap report
9. Show gap report in frontend

## Gap Categories

```text
missing_requirement
unclear_requirement
conflicting_requirement
missing_actor
missing_business_rule
missing_exception_flow
missing_integration_detail
missing_data_field
missing_security_requirement
missing_non_functional_requirement
```

## Acceptance Criteria

- Agent identifies gaps
- Agent generates questions
- Gap item links to requirement ID
- User can review gap report
- System can mark gap as resolved

---

# Sprint 10: BA Agent MVP

## Objective

เธชเธฃเนเธฒเธ BRD, FSD เนเธฅเธฐ User Story เธเธฒเธ requirement เธ—เธตเนเธเนเธฒเธเธเธฒเธฃ review เนเธฅเนเธง

## Tasks for AI Coding Agent

1. Load reviewed requirements
2. Generate BRD
3. Generate FSD
4. Generate User Stories
5. Generate acceptance criteria
6. Save documents
7. Link documents to requirement IDs

## Output Files / Records

```text
BRD
FSD
User Story Backlog
Acceptance Criteria
```

## Acceptance Criteria

- BRD generated from approved requirements only
- FSD includes functional detail
- User Story includes role, goal, benefit
- Acceptance criteria is testable
- Every section links to requirement ID

---

# Sprint 11: Solution Architect Agent MVP

## Objective

เธชเธฃเนเธฒเธ Architecture, Database Design, API Design เนเธฅเธฐ Workflow Design เธเธฒเธ requirement/FSD

## Tasks for AI Coding Agent

1. Analyze approved FSD
2. Generate architecture overview
3. Generate database design
4. Generate API design
5. Generate workflow design
6. Generate integration design
7. Generate security consideration
8. Save technical documents
9. Create traceability links

## Output Documents

```text
architecture-design.md
database-design.md
api-spec.md
workflow-design.md
integration-design.md
security-design.md
```

## Acceptance Criteria

- Architecture maps to requirement IDs
- Database tables map to requirement IDs
- API endpoints map to requirement IDs
- Workflow steps map to requirement IDs
- Output is reviewable by human SA

---

# Sprint 12: UX Agent MVP

## Objective

เธชเธฃเนเธฒเธ screen list, screen spec เนเธฅเธฐ wireframe instruction เธเธฒเธ requirement/FSD

## Tasks for AI Coding Agent

1. Analyze FSD
2. Generate screen list
3. Generate screen specification
4. Generate field list per screen
5. Generate validation rules per screen
6. Generate user interaction flow
7. Generate wireframe prompt for Figma/manual design

## Output Documents

```text
screen-list.md
screen-spec.md
field-spec.md
ui-flow.md
wireframe-instruction.md
```

## Acceptance Criteria

- Every screen links to requirement ID
- Every field has data type or validation rule
- Main user journey is documented
- UX output can be used by designer or frontend developer

---

# Sprint 13: Developer Agent MVP

## Objective

เนเธซเน Developer Agent generate coding tasks เนเธฅเธฐ skeleton code เนเธ”เธขเนเธกเนเธ—เธณ production code เนเธเธเนเธฃเนเธเธฒเธฃเธเธงเธเธเธธเธก

## Important Rule

Developer Agent must not generate full production code until these documents are approved:

```text
approved-requirements
approved-fsd
approved-architecture
approved-database-design
approved-api-spec
approved-screen-spec
```

## Tasks for AI Coding Agent

1. Generate backend task list
2. Generate frontend task list
3. Generate database migration task list
4. Generate API implementation plan
5. Generate skeleton code
6. Generate TODO markers
7. Link code task to requirement ID
8. Create GitHub branch or commit if enabled

## Output Documents

```text
development-task-list.md
backend-implementation-plan.md
frontend-implementation-plan.md
migration-plan.md
```

## Acceptance Criteria

- Code task links to requirement ID
- Skeleton code follows existing architecture
- No uncontrolled generation
- Human approval required before merge
- Generated code has tests or test placeholders

---

# Sprint 14: QA Agent MVP

## Objective

เธชเธฃเนเธฒเธ Test Case, UAT Script เนเธฅเธฐ Requirement Coverage Report

## Tasks for AI Coding Agent

1. Read requirements
2. Read user stories
3. Read API spec
4. Read screen spec
5. Generate test cases
6. Generate UAT script
7. Generate negative test cases
8. Generate requirement coverage matrix
9. Link test case to requirement ID

## Output Documents

```text
test-case.md
uat-script.md
negative-test-case.md
requirement-coverage-report.md
```

## Acceptance Criteria

- Every important requirement has at least one test case
- Test case includes precondition, steps, expected result
- UAT script is understandable by business user
- Coverage report shows missing test coverage

---

# Sprint 15: Traceability MVP

## Objective

เธชเธฃเนเธฒเธ traceability เธฃเธฐเธซเธงเนเธฒเธ requirement, document, API, DB, screen, code task เนเธฅเธฐ test case

## Tasks for AI Coding Agent

1. Create traceability link model
2. Create traceability API
3. Create traceability matrix UI
4. Create coverage report
5. Link requirement to generated artifacts
6. Support impact analysis

## Traceability Types

```text
requirement_to_brd
requirement_to_fsd
requirement_to_user_story
requirement_to_architecture
requirement_to_database
requirement_to_api
requirement_to_screen
requirement_to_code_task
requirement_to_test_case
requirement_to_uat
```

## Acceptance Criteria

- User can see requirement coverage
- User can see unlinked requirements
- User can see test coverage
- Change Impact Agent can use traceability data

---

# Sprint 16: Virtual Office MVP

## Objective

เธชเธฃเนเธฒเธเธซเธเนเธฒ Virtual Office เนเธเธ 2D dashboard เนเธซเนเน€เธซเนเธ Agent เนเธฅเธฐเธชเธ–เธฒเธเธฐเธเธฒเธ

## Tasks for AI Coding Agent

1. Create virtual office page
2. Create room components
3. Create agent avatar components
4. Display agent status
5. Display workflow status
6. Allow clicking Agent to open console
7. Allow clicking room to open related work
8. Show waiting-for-user state

## Initial Rooms

```text
Requirement Room
Gap Analysis Room
BA Room
Architect Room
UX Room
Developer Room
QA Room
Traceability Room
Control Room
```

## Agent Status

```text
idle
running
waiting_for_user
completed
failed
```

## Acceptance Criteria

- User can see Agent status visually
- User can click Agent
- User can click Room
- Virtual Office reflects actual workflow state
- No need for complex animation in MVP

---

# Sprint 17: RAG MVP

## Objective

เน€เธเธดเนเธกเธเธงเธฒเธกเธชเธฒเธกเธฒเธฃเธ–เนเธเธเธฒเธฃเธเนเธเธเนเธญเธกเธนเธฅเธเธฒเธ requirement, document template, coding standard เนเธฅเธฐ project knowledge

## Tasks for AI Coding Agent

1. Create document ingestion pipeline
2. Chunk documents
3. Create embeddings
4. Store embeddings in pgvector or Qdrant
5. Create RAG search API
6. Add RAG context to selected Agents
7. Show source citation in Agent output

## RAG Sources

```text
requirements
BRD/FSD
architecture documents
API spec
database spec
coding standard
company template
previous project document
```

## Acceptance Criteria

- Documents can be ingested
- Search returns relevant chunks
- Agent can use RAG context
- Agent output references source document
- RAG can be disabled per Agent

---

# Sprint 18: GitHub Integration MVP

## Objective

เน€เธเธทเนเธญเธกเธฃเธฐเธเธเธเธฑเธ GitHub เน€เธเธทเนเธญเนเธซเน generated code/task เน€เธเธทเนเธญเธกเธเธฑเธ requirement เนเธฅเธฐ traceability เนเธ”เน

## Tasks for AI Coding Agent

1. Add GitHub settings
2. Connect repository
3. Create branch per project or feature
4. Create issue from development task
5. Commit generated skeleton if enabled
6. Link commit/PR to requirement ID
7. Run GitHub Actions

## Acceptance Criteria

- Project can connect GitHub repo
- Requirement can link to issue/branch/commit
- Developer Agent can create coding task
- Human approval required before merge
- GitHub action status can be shown in system

---

# Sprint 19: MCP MVP

## Objective

เน€เธเธดเนเธก MCP เน€เธเธทเนเธญเนเธซเน Agent เน€เธฃเธตเธขเธ tool เธ เธฒเธขเธเธญเธเนเธ”เนเธญเธขเนเธฒเธเน€เธเนเธเธกเธฒเธ•เธฃเธเธฒเธ

## Important Rule

Do not implement MCP before core Agent workflow is stable.

## MCP Tools Candidate

```text
filesystem
github
database
figma
browser
document-generator
test-runner
```

## Tasks for AI Coding Agent

1. Add MCP tool registry
2. Add MCP server configuration
3. Add MCP tool permission model
4. Allow Agent to call approved tools
5. Log all MCP tool calls
6. Link MCP action to agent_run

## Acceptance Criteria

- MCP tools are registered
- Agent can call approved tool only
- Tool call is logged
- User can review tool result
- Dangerous tools require approval

---

# Sprint 20: Change Impact Agent MVP

## Objective

เธงเธดเน€เธเธฃเธฒเธฐเธซเนเธเธฅเธเธฃเธฐเธ—เธเน€เธกเธทเนเธญ requirement เน€เธเธฅเธตเนเธขเธ

## Tasks for AI Coding Agent

1. Detect changed requirement
2. Compare requirement versions
3. Find linked BRD/FSD/API/DB/screen/code/test
4. Generate impact report
5. Suggest affected documents
6. Suggest affected test cases
7. Mark items that require review

## Output Document

```text
change-impact-report.md
```

## Acceptance Criteria

- Requirement version comparison works
- Impact links are traceable
- Report lists affected artifacts
- User can approve/reject change impact

---

# 5. MVP Release Plan

## MVP 1: Requirement Loop

### Scope

```text
Project
Requirement Upload
Requirement Agent
Gap Analysis Agent
Requirement Summary
Gap Report
Basic UI
Basic Database
```

### Goal

เธเธดเธชเธนเธเธเนเธงเนเธฒ AI เธเนเธงเธขเธฅเธ”เธเธฑเธเธซเธฒ requirement เนเธกเนเธเธฃเธเนเธ”เนเธเธฃเธดเธ

### Must Have

- Upload/paste requirement
- Run Requirement Agent
- Run Gap Analysis Agent
- Show open questions
- Save output
- Export Markdown

### Not Included

```text
Dev Agent
QA Agent
Virtual Office animation
GitHub
MCP
Large RAG
```

---

## MVP 2: BA/SA Document Generation

### Scope

```text
BA Agent
BRD
FSD
User Story
Architect Agent
Architecture Design
Database Design
API Spec
Workflow Design
```

### Goal

เนเธซเน AI เธเนเธงเธขเธชเธฃเนเธฒเธเน€เธญเธเธชเธฒเธฃ BA/SA เธเธฒเธ requirement เธ—เธตเนเธเนเธฒเธ review เนเธฅเนเธง

### Must Have

- Generate BRD
- Generate FSD
- Generate User Story
- Generate Architecture
- Generate Database Design
- Generate API Spec
- Human review status

---

## MVP 3: Dev/QA/Traceability

### Scope

```text
Developer Agent
QA Agent
Code Task Generation
Test Case Generation
Traceability Matrix
Coverage Report
```

### Goal

เน€เธเธทเนเธญเธก requirement เนเธเธ–เธถเธ code task เนเธฅเธฐ test case

### Must Have

- Generate development task
- Generate skeleton code plan
- Generate test case
- Generate UAT script
- Requirement coverage matrix
- Traceability link

---

## MVP 4: Virtual Office Experience

### Scope

```text
2D Virtual Office
Agent Avatar
Room Status
Workflow Monitor
Agent Console
Notification
```

### Goal

เธ—เธณเนเธซเนเธเธนเนเนเธเนเน€เธซเนเธเธ เธฒเธเธงเนเธฒ Agent เนเธ•เนเธฅเธฐเธ•เธฑเธงเธเธณเธฅเธฑเธเธ—เธณเธญเธฐเนเธฃ

### Must Have

- Agent status
- Room status
- Click Agent
- Click Room
- Waiting for user state
- Workflow timeline

---

## MVP 5: Integration Layer

### Scope

```text
RAG
GitHub
MCP
Change Impact Agent
```

### Goal

เน€เธเธทเนเธญเธกเธฃเธฐเธเธเธเธฑเธ knowledge base, code repository เนเธฅเธฐ external tools

### Must Have

- RAG search
- GitHub issue/branch/commit link
- MCP tool registry
- Change impact report

---

# 6. Coding Agent Operating Rules

AI Coding Agent must follow these rules.

## Rule 1: Do not code before design artifacts exist

Before implementing backend/frontend, check that these files exist:

```text
docs/agents/*.contract.json
docs/prompts/*.md
docs/templates/*.md
docs/database/table-spec.md
docs/api/api-list.md
docs/workflows/*.md
```

If missing, create them first.

---

## Rule 2: Requirement ID is mandatory

Every generated artifact must link to requirement ID when possible.

Examples:

```text
REQ-001
BRD-001
FSD-001
API-001
DB-001
UI-001
TC-001
```

---

## Rule 3: Human review is mandatory before code generation

Developer Agent must not generate implementation code unless these statuses are approved:

```text
requirement_status = approved
fsd_status = approved
architecture_status = approved
api_status = approved
database_status = approved
screen_status = approved
```

---

## Rule 4: Keep Agent output structured

All Agent output must be JSON first, then rendered to Markdown document using template.

```text
Agent JSON Output
โ“
Validate
โ“
Save to DB
โ“
Render Markdown
โ“
Show in UI
```

---

## Rule 5: Log every Agent run

Every Agent execution must create record in `agent_runs`.

Minimum fields:

```text
agent_name
input_reference
prompt_version
model_name
status
started_at
completed_at
error_message
output_reference
```

---

## Rule 6: Version everything

Version these artifacts:

```text
requirements
agent contracts
prompts
templates
documents
database design
api design
screen spec
test cases
```

---

## Rule 7: Start simple

Do not implement the following in early MVP unless explicitly required:

```text
complex workflow engine
3D virtual office
MCP tools
auto merge to GitHub
large enterprise RAG
multi-tenant security
advanced RBAC
```

---

# 7. Definition of Done

A sprint is done only when:

```text
[ ] Required files are created
[ ] Required API or UI is working
[ ] Output links to requirement ID
[ ] Data is saved in PostgreSQL
[ ] Agent run is logged
[ ] Error handling exists
[ ] Basic test exists
[ ] README or usage note is updated
```

---

# 8. Recommended Build Order for Coding Agent

When starting from a fresh repository, follow this order:

```text
1. Create docs structure
2. Create Agent Contract files
3. Create Prompt files
4. Create Template files
5. Create Database spec
6. Create API spec
7. Create Workflow spec
8. Generate Backend skeleton
9. Generate Frontend skeleton
10. Implement Requirement Agent
11. Implement Gap Analysis Agent
12. Implement Requirement Review UI
13. Implement BA Agent
14. Implement Architect Agent
15. Implement Traceability
16. Implement QA Agent
17. Implement Virtual Office UI
18. Implement RAG
19. Implement GitHub integration
20. Implement MCP
21. Implement Change Impact Agent
```

---

# 9. First Implementation Target

For the first implementation cycle, build only this flow:

```text
Create Project
โ“
Upload/Paste Requirement
โ“
Run Requirement Agent
โ“
Run Gap Analysis Agent
โ“
Show Requirement Summary
โ“
Show Open Questions
โ“
Save Output
โ“
Export Markdown
```

## First Cycle Acceptance Criteria

```text
[ ] User can create project
[ ] User can paste requirement
[ ] System can run Requirement Agent
[ ] System can run Gap Analysis Agent
[ ] Result is saved
[ ] Result is displayed
[ ] Markdown can be exported
[ ] Every requirement has ID
[ ] Every gap links to requirement ID or source section
```

---

# 10. Instruction for Codex / Claude Code

Use this instruction when asking an AI Coding Agent to work on this project.

```text
You are working on the AI-DLC Virtual Office project.

Follow the sprint plan in docs/ai-dlc-development-sprint-skill.md.

Do not jump directly to implementation before creating or checking:
- Agent contracts
- Prompts
- Templates
- Database spec
- API spec
- Workflow spec

Start with MVP 1: Requirement Loop.

Implement only:
- Project creation
- Requirement upload/paste
- Requirement Agent
- Gap Analysis Agent
- Requirement Summary display
- Gap Report display
- Save output to PostgreSQL
- Export Markdown

Every generated artifact must link to requirement IDs.
All Agent outputs must be JSON validated before rendering to Markdown.
Every Agent run must be logged.
Do not implement GitHub, MCP, advanced RAG, or complex Virtual Office animation until MVP 1 is complete.
```

---

# 11. Final Notes

This project should be built incrementally.

The highest-value first milestone is not full AI code generation.  
The highest-value first milestone is:

```text
Requirement quality improvement
โ“
Gap detection
โ“
Human review
โ“
Approved requirement baseline
```

Once requirement quality is stable, BA/SA/Dev/QA Agents will produce better and safer results.

