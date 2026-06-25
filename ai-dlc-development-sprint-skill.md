# AI-DLC Development Sprint Skill
> Skill / Playbook สำหรับให้ Codex, Claude Code, หรือ AI Coding Agent ใช้พัฒนาระบบ AI-DLC Virtual Office ต่อจาก Requirement Specification

---

## 0. Purpose

เอกสารนี้ใช้เป็นแนวทางพัฒนา **AI-DLC Virtual Office** หลังจากได้รับไฟล์ Requirement แล้ว เช่น `requirements.md`, `brd.md`, `fsd.md` หรือ requirement transcript

เป้าหมายคือให้ AI Coding Agent เช่น **Codex / Claude Code / Cursor / Kiro** สามารถทำงานต่อได้อย่างเป็นลำดับ โดยไม่รีบ generate code ทันที แต่ต้องผ่านขั้นตอนออกแบบ Agent Contract, Prompt, Template, Database, API, Workflow, Backend, Frontend, Traceability และ Virtual Office

---

## 1. Target System Overview

ระบบที่ต้องพัฒนาคือ **AI-DLC Virtual Office** สำหรับช่วย automate ขั้นตอน Software Development Life Cycle ด้วย AI Agent

### Main Flow

```text
Requirement Source
↓
Requirement Agent
↓
Gap Analysis Agent
↓
BA Agent
↓
Solution Architect Agent
↓
UX Agent
↓
Developer Agent
↓
QA Agent
↓
Change Impact Agent
↓
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

ตรวจสอบ requirement ที่ได้มา และแยกให้เป็นโครงสร้างที่ Agent ใช้ต่อได้

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

- ทุก requirement ต้องมี unique ID เช่น `REQ-001`
- แยก Functional / Non-functional ชัดเจน
- มีรายการคำถามที่ยังไม่ชัดเจน
- ไม่เดา requirement เอง ถ้าไม่ชัดให้ใส่ใน open questions

---

# Sprint 1: Agent Contract Design

## Objective

ออกแบบสัญญาการทำงานของ Agent แต่ละตัว เพื่อให้ input/output ชัดเจนและตรวจสอบได้

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

- ทุก Agent มี contract
- ทุก output เป็น JSON ที่ validate ได้
- ทุก Agent ระบุ next_agent หรือ end state
- Contract ต้องพร้อมนำไปสร้าง Pydantic schema

---

# Sprint 2: Prompt & Template Design

## Objective

สร้าง prompt และ document template ที่ใช้ซ้ำได้ ไม่ใช่ prompt แบบ manual ครั้งเดียว

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

ออกแบบฐานข้อมูลเพื่อรองรับ Project, Requirement, Agent Run, Document, Workflow และ Traceability

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

ออกแบบ API ให้ Frontend และ Agent Runtime เรียกใช้งานได้

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

ออกแบบ workflow การทำงานของ Agent ตั้งแต่รับ requirement ถึง generate code/test

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
↓
UPLOAD_SOURCE
↓
RUN_REQUIREMENT_AGENT
↓
RUN_GAP_ANALYSIS_AGENT
↓
WAIT_FOR_USER_REVIEW
↓
RUN_BA_AGENT
↓
RUN_ARCHITECT_AGENT
↓
RUN_UX_AGENT
↓
WAIT_FOR_USER_APPROVAL
↓
RUN_DEVELOPER_AGENT
↓
RUN_QA_AGENT
↓
UPDATE_TRACEABILITY
↓
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

สร้าง Backend Skeleton ด้วย FastAPI เพื่อรองรับ project, requirement, agent run และ document generation

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

สร้าง Frontend Skeleton ด้วย React + Vite + TypeScript เพื่อให้ผู้ใช้ upload requirement และ run Agent ได้

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

Implement Requirement Agent จริง เพื่อสรุป requirement จาก input

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
↓
Prompt Loader
↓
Prompt Builder
↓
LLM Call
↓
Output Parser
↓
Output Validator
↓
Save Agent Run
↓
Save Requirement Items
↓
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

Implement Gap Analysis Agent เพื่อตรวจ requirement ที่ไม่ครบ ไม่ชัด หรือขัดแย้งกัน

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

สร้าง BRD, FSD และ User Story จาก requirement ที่ผ่านการ review แล้ว

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

สร้าง Architecture, Database Design, API Design และ Workflow Design จาก requirement/FSD

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

สร้าง screen list, screen spec และ wireframe instruction จาก requirement/FSD

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

ให้ Developer Agent generate coding tasks และ skeleton code โดยไม่ทำ production code แบบไร้การควบคุม

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

สร้าง Test Case, UAT Script และ Requirement Coverage Report

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

สร้าง traceability ระหว่าง requirement, document, API, DB, screen, code task และ test case

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

สร้างหน้า Virtual Office แบบ 2D dashboard ให้เห็น Agent และสถานะงาน

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

เพิ่มความสามารถในการค้นข้อมูลจาก requirement, document template, coding standard และ project knowledge

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

เชื่อมระบบกับ GitHub เพื่อให้ generated code/task เชื่อมกับ requirement และ traceability ได้

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

เพิ่ม MCP เพื่อให้ Agent เรียก tool ภายนอกได้อย่างเป็นมาตรฐาน

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

วิเคราะห์ผลกระทบเมื่อ requirement เปลี่ยน

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

พิสูจน์ว่า AI ช่วยลดปัญหา requirement ไม่ครบได้จริง

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

ให้ AI ช่วยสร้างเอกสาร BA/SA จาก requirement ที่ผ่าน review แล้ว

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

เชื่อม requirement ไปถึง code task และ test case

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

ทำให้ผู้ใช้เห็นภาพว่า Agent แต่ละตัวกำลังทำอะไร

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

เชื่อมระบบกับ knowledge base, code repository และ external tools

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
↓
Validate
↓
Save to DB
↓
Render Markdown
↓
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
↓
Upload/Paste Requirement
↓
Run Requirement Agent
↓
Run Gap Analysis Agent
↓
Show Requirement Summary
↓
Show Open Questions
↓
Save Output
↓
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
↓
Gap detection
↓
Human review
↓
Approved requirement baseline
```

Once requirement quality is stable, BA/SA/Dev/QA Agents will produce better and safer results.

---

# Sprint 44: Virtual Office — Phaser.js 2D Pixel Office (FR-001, FR-002, FR-003, FR-004)

## Objective

เปลี่ยน VirtualOfficePage จาก React status board เป็น Phaser 3 game เต็มหน้าจอ โดยใช้ LimeZu Modern Interiors tileset และ character sprites แต่ละตัวแทน Agent ที่เดินเล่นใน office และแสดงสถานะ real-time จาก backend

## References

- FR-001: Virtual Office 2D Pixel UI
- FR-002: Agent Idle Behavior
- FR-003: Agent Work Behavior
- FR-004: Agent Status Light
- ADD-001: Agent Role & Desk Mapping
- Spec: `Requirement Spec/AI-SDLC-Virtual-Office-CR-Requirement-Spec.md`

## Assets (already placed in frontend/public/)

### Tileset

| File | Key | Tile Size |
|---|---|---|
| `public/tilesets/Interiors_16x16.png` | `interiors` | 16x16 px |

### Character Sprites (spritesheet: 3 cols x N rows, 48x48 px per frame)

| File | Agent role (matches backend) |
|---|---|
| `public/sprites/agent_AC.png` | `architect-agent` |
| `public/sprites/agent_BA.png` | `ba-agent` |
| `public/sprites/agent_CI.png` | `change-impact-agent` |
| `public/sprites/agent_RV.png` | `code-review-agent` |
| `public/sprites/agent_DA1.png` | `developer-agent` |
| `public/sprites/agent_DAB.png` | `developer-agent-backend` |
| `public/sprites/agent_DAF.png` | `developer-agent-frontend` |
| `public/sprites/agent_DAP.png` | `developer-agent-platform` |
| `public/sprites/agent_DEO.png` | `devops-agent` |
| `public/sprites/agent_DOC.png` | `documentation-agent` |
| `public/sprites/agent_GAP.png` | `gap-analysis-agent` |
| `public/sprites/agent_MON.png` | `monitoring-agent` |
| `public/sprites/agent_PM.png` | `pm-agent` |
| `public/sprites/agent_QA.png` | `qa-agent` |
| `public/sprites/agent_REQ.png` | `requirement-agent` |
| `public/sprites/agent_TD.png` | `technical-design-agent` |
| `public/sprites/agent_UX.png` | `ux-agent` |

## Tasks

### Task 1: Install Phaser

```bash
cd frontend && npm install phaser
```

### Task 2: Modify `frontend/src/pages/VirtualOfficePage.tsx`

- ลบ React status board เดิมออก
- โหลด Phaser ผ่าน dynamic import('phaser') ใน useEffect (หลีกเลี่ยง SSR / Vite issue)
- สร้าง Phaser.Game instance เต็มหน้าจอ (width/height = container clientWidth/clientHeight)
- cleanup game.destroy(true) on component unmount
- mount game ลงใน div ref ที่มี style width:100% height:100%

### Task 3: สร้าง `frontend/src/game/scenes/OfficeScene.ts`

#### PRELOAD

โหลด tileset key 'interiors', frameWidth:16, frameHeight:16

โหลด agent sprites ทุกไฟล์, frameWidth:48, frameHeight:48

SPRITE_MAP:
- agent_AC  -> architect-agent
- agent_BA  -> ba-agent
- agent_CI  -> change-impact-agent
- agent_RV  -> code-review-agent
- agent_DA1 -> developer-agent
- agent_DAB -> developer-agent-backend
- agent_DAF -> developer-agent-frontend
- agent_DAP -> developer-agent-platform
- agent_DEO -> devops-agent
- agent_DOC -> documentation-agent
- agent_GAP -> gap-analysis-agent
- agent_MON -> monitoring-agent
- agent_PM  -> pm-agent
- agent_QA  -> qa-agent
- agent_REQ -> requirement-agent
- agent_TD  -> technical-design-agent
- agent_UX  -> ux-agent

#### MAP (Graphics-based, ไม่ใช้ Tiled)

- World size: 40x30 tiles = 640x480 px (TILE_SIZE = 16)
- Floor: Graphics fillRect ทั้ง map สี 0xc8c8c8
- Wall: สี 0x8b7355 หนา 1 tile รอบแต่ละห้อง ยกเว้น tile ที่เป็น door gap

#### ห้อง 5 ห้อง (tile coordinates)

| Room | tx | ty | tw | th | Door gap (2 tiles) |
|---|---|---|---|---|---|
| Requirement Room | 1 | 1 | 10 | 8 | ผนังล่าง tx=5-6 |
| Meeting Room | 12 | 1 | 10 | 8 | ผนังล่าง tx=16-17 |
| Developer Room | 1 | 11 | 15 | 10 | ผนังบน tx=7-8 |
| QA Lab | 23 | 11 | 10 | 10 | ผนังบน tx=27-28 |
| Control Room | 30 | 1 | 9 | 8 | ผนังล่าง tx=34-35 |

Label ชื่อห้อง: this.add.text(tx*16+4, ty*16+4, 'Room Name', { color:'#ffffff', fontSize:'10px' })

#### ANIMATIONS (สร้างครั้งเดียวใน create())

- walk_down  : frames [0,1,2],   frameRate 8, repeat -1
- walk_left  : frames [3,4,5],   frameRate 8, repeat -1
- walk_right : frames [6,7,8],   frameRate 8, repeat -1
- walk_up    : frames [9,10,11], frameRate 8, repeat -1

Key format: `${spriteKey}_walk_down` เป็นต้น

#### AGENT PLACEMENT

| Agent role | Sprite key | Room | Start tile (tx, ty) |
|---|---|---|---|
| requirement-agent | agent_REQ | Requirement Room | 3, 3 |
| gap-analysis-agent | agent_GAP | Requirement Room | 7, 5 |
| ba-agent | agent_BA | Meeting Room | 14, 3 |
| architect-agent | agent_AC | Meeting Room | 18, 3 |
| ux-agent | agent_UX | Meeting Room | 16, 5 |
| technical-design-agent | agent_TD | Meeting Room | 14, 6 |
| developer-agent | agent_DA1 | Developer Room | 4, 14 |
| developer-agent-backend | agent_DAB | Developer Room | 7, 14 |
| developer-agent-frontend | agent_DAF | Developer Room | 10, 14 |
| developer-agent-platform | agent_DAP | Developer Room | 13, 14 |
| code-review-agent | agent_RV | Developer Room | 4, 17 |
| qa-agent | agent_QA | QA Lab | 25, 14 |
| devops-agent | agent_DEO | QA Lab | 28, 14 |
| monitoring-agent | agent_MON | QA Lab | 25, 18 |
| documentation-agent | agent_DOC | Control Room | 32, 3 |
| pm-agent | agent_PM | Control Room | 35, 5 |
| change-impact-agent | agent_CI | Control Room | 32, 6 |

pixel x = tx * 16 + 8, pixel y = ty * 16 + 8

#### IDLE WALK BEHAVIOR

ทุก 2-4 วินาที (random delay):
- สุ่ม target pixel (x, y) ภายใน room boundary (inset 1 tile จากขอบ)
- คำนวณ angle = Phaser.Math.Angle.Between(current, target)
- setVelocity(cos(angle)*40, sin(angle)*40)
- เลือก animation ตามทิศ: |dx| > |dy| → left/right, else → up/down
- เมื่อถึง target (distance < 4px) → หยุด velocity, แสดง idle frame (frame 1)
- schedule delay ใหม่

หาก status = 'running':
- หยุด idle walk
- เล่น animation walk_down (working pose)
- ไม่สุ่ม target ใหม่จนกว่า status จะกลับเป็น idle

#### STATUS DOT

this.add.arc() radius 5px ที่ offset (+20, -20) จาก sprite center, depth สูงกว่า sprite

| Status | Color | Effect |
|---|---|---|
| running | 0x6366f1 (indigo) | tween alpha 1 to 0.3 yoyo repeat -1, duration 800 |
| completed / done | 0x34d399 (emerald) | static |
| idle / default | 0xffffff alpha 0.3 | static |
| error | 0xef4444 (red) | static |
| waiting | 0xf59e0b (amber) | static |

#### NAME LABEL

this.add.text(x, y-20, role, { color:'#ffffff', fontSize:'9px', stroke:'#000000', strokeThickness:2 })

#### CLICK INTERACTION

sprite.setInteractive({ useHandCursor: true })
sprite.on('pointerdown', () => this.events.emit('agent:selected', agentData))

### Task 4: สร้าง `frontend/src/game/AgentManager.ts`

AGENT_CONFIG array:
- agentId, spriteKey, room (17 agents ตาม SPRITE_MAP ด้านบน)

Poll GET /api/agents ทุก 3,000 ms:
- เปรียบเทียบ status เก่า-ใหม่
- ถ้าเปลี่ยน -> callback updateStatusDot(agentId, newStatus)

### Task 5: Glass Drawer (React component ใน VirtualOfficePage)

- Absolute positioned, right:0 top:0 height:100%
- Width: 320px, style: bg-white/70 backdrop-blur-md border-l
- ปิดด้วย X button หรือ Escape key
- แสดง: Agent Name, Role badge, Status badge, Current Task, Model, Last Active

### Task 6: Camera

- this.cameras.main.setBounds(0, 0, 640, 480)
- default zoom = 2 (เพื่อให้ sprite 48px ดูชัด)
- WASD / Arrow keys scroll (speed 150 / zoom px per second)
- Scroll wheel zoom: clamp(zoom - deltaY*0.001, 1, 3)

## Files to Create / Modify

```
frontend/src/pages/VirtualOfficePage.tsx     (modify - replace with Phaser host)
frontend/src/game/scenes/OfficeScene.ts      (create)
frontend/src/game/AgentManager.ts            (create)
frontend/src/game/config.ts                  (create - Phaser.Game config)
```

## Acceptance Criteria

- [ ] npm install phaser เสร็จ, package.json มี phaser dependency
- [ ] VirtualOfficePage โหลด Phaser canvas ที่ /office ไม่ crash
- [ ] Floor + 5 ห้องแสดงถูกต้องตาม tile coordinates
- [ ] Agent sprites แสดงในห้องของตัวเองถูกต้อง
- [ ] Animation walk_down/left/right/up เล่นได้
- [ ] Idle walk: agent เดินวนใน room ไม่หลุดขอบ
- [ ] Status dot: สีถูกต้อง, running = pulse animation
- [ ] คลิก agent -> glass drawer เปิดแสดงข้อมูล
- [ ] WASD/arrow scroll camera
- [ ] Scroll wheel zoom 1x-3x
- [ ] game.destroy() on unmount ไม่ memory leak
- [ ] npm run build ผ่านใน Docker

## Definition of Done

```
[ ] phaser อยู่ใน package.json
[ ] VirtualOfficePage host Phaser game
[ ] OfficeScene preload -> create -> update ทำงาน
[ ] Rooms + agent sprites แสดงบน canvas
[ ] AgentManager poll /api/agents และอัปเดต status dots
[ ] Click agent -> drawer แสดงข้อมูล
[ ] Camera scroll + zoom ทำงาน
[ ] Docker rebuild ผ่าน
[ ] PROGRESS.md อัปเดต Sprint 44 = Done
```
