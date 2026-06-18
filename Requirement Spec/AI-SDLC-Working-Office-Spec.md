# AI-SDLC Working Office — Requirement & Design Specification

**Document Version:** 1.0  
**Project Name:** AI-SDLC Working Office / AI Agent Virtual Office  
**Purpose:** Requirement & Design Spec สำหรับใช้เป็น Master Prompt / Development Specification เพื่อให้ AI Coding Tools เช่น Claude Code, Cursor, Windsurf, Lovable หรือ Bolt.new สร้างระบบ  
**Primary Goal:** สร้างระบบ Virtual Office แบบ Professional ที่ AI Agent ทำงานร่วมกันตามกระบวนการ SDLC ตั้งแต่ Requirement → Gap Analysis → BA → SA → UX → Developer → QA → Change Impact

---

# 1. Executive Summary

AI-SDLC Working Office คือเว็บแอปพลิเคชันแบบ 2D Virtual Office ที่มี AI Agent หลายตัวทำงานร่วมกันเหมือนทีมพัฒนา Software จริง

ระบบต้องแสดง Agent อยู่ใน Office Map แบบ 2D Pixel / Professional Virtual Office โดย Agent สามารถเดินไปยังห้องหรือโซนต่าง ๆ ตามขั้นตอนการทำงาน เช่น Requirement Room, Gap Analysis Room, BA Room, SA Room, UX Room, Developer Zone, QA Zone และ Impact Analysis Room

จุดเด่นของระบบไม่ใช่แค่ Virtual Office แต่เป็น **Agentic Software Factory** ที่ใช้ AI Agent ทำงานตาม SDLC จริง โดยรับ Requirement จาก Meeting, Chat, Document หรือ Manual Input แล้วส่งต่อกันเป็นลำดับจนได้ผลลัพธ์เป็น BRD, FSD, User Story, Architecture, API Spec, Database Design, Wireframe, Code, Test Case, UAT Script และ Change Impact Report

---

# 2. Business Objective

## 2.1 Objective

สร้างระบบ AI Working Office ที่สามารถช่วยทีมพัฒนา Software / Low-code / Workflow / Automation ทำงานได้เร็วขึ้น ลดปัญหา Requirement หลุด ลดการสื่อสารผิดพลาด และช่วย Generate เอกสารหรือ Code เบื้องต้นได้

## 2.2 Target Users

- Business Analyst
- Solution Architect
- Developer
- QA
- Project Manager
- Consultant
- Pre-sales / Solution Specialist
- Internal IT Team
- Automation / Workflow Team
- Low-code Platform Team

## 2.3 Business Value

- ลดเวลาการสรุป Requirement
- ตรวจสอบ Requirement ที่ขาด ไม่ชัด หรือขัดแย้ง
- สร้าง BRD / FSD / User Story อัตโนมัติ
- สร้าง Solution Design / Database / API Spec เบื้องต้น
- สร้าง Wireframe / Screen Spec
- Generate Code เบื้องต้น
- Generate Test Case และ UAT Script
- วิเคราะห์ผลกระทบเมื่อ Requirement เปลี่ยน
- ทำ Traceability ตั้งแต่ Requirement ถึง Test Case
- ใช้เป็น Demo / Showcase สำหรับลูกค้าได้

---

# 3. System Concept

ระบบประกอบด้วย 5 Layer หลัก

```text
[User Input Layer]
Meeting / Chat / Document / Manual Requirement / Audio Transcript

        ↓

[AI-SDLC Agent Layer]
Requirement Agent
Gap Analysis Agent
BA Agent
Solution Architect Agent
UX Agent
Developer Agent
QA Agent
Change Impact Agent
Documentation Agent
DevOps Agent
PM Agent

        ↓

[Workflow Orchestration Layer]
Task Routing
Agent Collaboration
Status Tracking
Approval / Review
Traceability

        ↓

[Application Layer]
Virtual Office UI
Task Board
Agent Chat
Document Viewer
Dashboard
Activity Log

        ↓

[Data & Integration Layer]
PostgreSQL
Qdrant
File Storage
LLM Provider
GitHub / MCP / External Tools
```

---

# 4. High-Level SDLC Agent Flow

```text
User
  |
  v
Requirement Agent
  |
  v
Gap Analysis Agent
  |
  v
BA Agent
  |
  v
Solution Architect Agent
  |
  v
UX Agent
  |
  v
Developer Agent
  |
  v
QA Agent
  |
  v
Change Impact Agent
  |
  v
Documentation / PM Summary
  |
  v
User Review
```

---

# 5. Core Agent Roles

## 5.1 Requirement Agent

### Purpose
รวบรวมและสรุป Requirement จากแหล่งข้อมูลต่าง ๆ

### Input
- Meeting transcript
- Chat conversation
- Word document
- PDF document
- Email content
- Manual requirement text
- Audio transcript

### Responsibilities
- สรุป Requirement หลัก
- แยก Business Objective
- แยก Scope
- แยก In Scope / Out of Scope
- แยก Assumption
- แยก Constraint
- แยก Stakeholder
- แยก Open Question
- แยก Business Rule เบื้องต้น

### Output
- Requirement Summary
- Requirement List
- Scope Summary
- Assumption List
- Constraint List
- Open Question List

### Example Output Structure

```markdown
# Requirement Summary

## Business Objective
...

## In Scope
...

## Out of Scope
...

## Functional Requirements
| ID | Requirement | Source | Priority |
|---|---|---|---|

## Non-Functional Requirements
| ID | Requirement | Category | Priority |
|---|---|---|---|

## Assumptions
...

## Constraints
...

## Open Questions
...
```

---

## 5.2 Gap Analysis Agent

### Purpose
ตรวจ Requirement ที่ขาด ไม่ชัด หรือขัดแย้งกัน

### Input
- Requirement Summary
- Transcript
- Document
- Chat log
- Previous version of requirement

### Responsibilities
- ตรวจ Missing Requirement
- ตรวจ Ambiguous Requirement
- ตรวจ Conflict Requirement
- ตรวจ Duplicate Requirement
- ตรวจ Dependency ที่ยังไม่ชัด
- ตรวจ Integration ที่ยังขาดรายละเอียด
- ตรวจ Business Rule ที่ยังไม่ครบ
- สร้างคำถามกลับ User / BA

### Gap Categories
- Missing
- Ambiguous
- Conflict
- Duplicate
- Dependency
- Risk
- Out of Scope Risk
- Integration Gap
- Data Gap
- Security Gap
- Approval Gap
- Reporting Gap

### Output
- Requirement Gap Report
- Critical Gap List
- Clarification Question List
- Risk List
- Recommendation

### Example Gap Rule

```text
ถ้า Requirement มีคำว่า "อนุมัติ" แต่ไม่มี Approval Level, Approver Role, SLA หรือ Escalation Rule
ให้สร้าง Gap ประเภท Approval Gap
```

### Example Output

```markdown
# Requirement Gap Report

## Critical Gaps
| Gap ID | Description | Impact | Question |
|---|---|---|---|

## Ambiguous Requirements
| Requirement ID | Issue | Suggested Clarification |
|---|---|---|

## Conflicts
| Conflict ID | Source A | Source B | Recommendation |
|---|---|---|---|

## Questions for User
1. ...
2. ...
```

---

## 5.3 BA Agent

### Purpose
แปลง Requirement เป็นเอกสาร BA ที่พร้อมใช้ในการพัฒนา

### Input
- Requirement Summary
- Gap Analysis Report
- Clarified Requirement

### Responsibilities
- สร้าง BRD
- สร้าง FSD
- สร้าง User Story
- สร้าง Acceptance Criteria
- สร้าง Business Process
- สร้าง Field Requirement
- สร้าง Validation Rule
- สร้าง Workflow Requirement

### Output
- BRD
- FSD
- User Story
- Acceptance Criteria
- Business Process Description
- Field / Screen Requirement

### User Story Format

```text
As a [role]
I want [feature]
So that [business value]
```

### Acceptance Criteria Format

```gherkin
Given [context]
When [action]
Then [expected result]
```

---

## 5.4 Solution Architect Agent

### Purpose
ออกแบบระบบในเชิง Technical Solution

### Input
- BRD
- FSD
- User Story
- Requirement Gap Report

### Responsibilities
- ออกแบบ Architecture
- ออกแบบ Database
- ออกแบบ API
- ออกแบบ Workflow
- ออกแบบ Integration
- ออกแบบ Security
- ออกแบบ Deployment
- ออกแบบ Error Handling
- ออกแบบ Audit Log

### Output
- Solution Architecture Document
- System Context Diagram
- Component Design
- Database Design
- API Design
- Workflow Design
- Integration Design
- Security Design
- Deployment Design

### Example Architecture Output

```markdown
# Solution Architecture

## Architecture Overview
...

## Component List
| Component | Responsibility | Technology |
|---|---|---|

## Database Design
...

## API Design
...

## Integration Design
...

## Security Design
...
```

---

## 5.5 UX Agent

### Purpose
สร้าง Wireframe, Screen Spec และ UX Flow เพื่อให้ Developer สร้าง UI ได้ตรงตาม Requirement

### Input
- FSD
- User Story
- Process Flow
- Screen Requirement

### Responsibilities
- ออกแบบ Screen List
- สร้าง Wireframe แบบ Text / JSON / Mermaid
- สร้าง Screen Spec
- สร้าง Field Spec
- สร้าง UX Flow
- สร้าง Design Token
- สร้าง UI Component Mapping
- สร้าง Prompt สำหรับ Figma / v0 / Claude Code

### Output
- Screen Inventory
- Wireframe Specification
- Screen Specification
- Field Specification
- UX Flow
- Design Token
- UI Component Mapping

### Example Screen Spec

```markdown
# Screen: Expense Request Form

## Purpose
ใช้สำหรับสร้างคำขอเบิกค่าใช้จ่าย

## Layout
- Header
- Requester Information
- Expense Detail Table
- Attachment Section
- Approval History
- Action Buttons

## Fields
| Field | Type | Required | Validation |
|---|---|---|---|
```

---

## 5.6 Developer Agent

### Purpose
Generate Code ตาม Requirement, Design และ Screen Spec

### Input
- FSD
- Architecture
- Database Design
- API Spec
- Screen Spec
- UX Design
- Coding Standard

### Responsibilities
- Generate Frontend Code
- Generate Backend Code
- Generate Database Migration
- Generate API
- Generate Unit Test
- Fix Bug
- Refactor Code
- Create README
- Prepare Dockerfile

### Output
- React / TypeScript Frontend
- FastAPI Backend
- SQLAlchemy Models
- API Routes
- Docker Compose
- Unit Tests
- README

---

## 5.7 QA Agent

### Purpose
สร้าง Test Case, UAT Script และตรวจสอบคุณภาพ

### Input
- Requirement
- FSD
- User Story
- Acceptance Criteria
- API Spec
- Code Output

### Responsibilities
- Generate Test Case
- Generate UAT Script
- Generate SIT Script
- Generate Regression Test
- ตรวจ Requirement Coverage
- ตรวจ Acceptance Criteria Coverage
- ตรวจ Bug Risk
- สรุป QA Result

### Output
- Test Case
- UAT Script
- SIT Script
- Regression Test Set
- QA Summary
- Defect List

### Test Case Format

```markdown
| Test ID | Scenario | Step | Expected Result | Type |
|---|---|---|---|---|
```

---

## 5.8 Change Impact Agent

### Purpose
วิเคราะห์ผลกระทบเมื่อ Requirement เปลี่ยน

### Input
- New Requirement
- Previous Requirement Version
- BRD
- FSD
- Architecture
- Database Design
- API Spec
- Code Mapping
- Test Case

### Responsibilities
- วิเคราะห์ Requirement ที่เปลี่ยน
- ระบุผลกระทบต่อ UI
- ระบุผลกระทบต่อ Database
- ระบุผลกระทบต่อ API
- ระบุผลกระทบต่อ Workflow
- ระบุผลกระทบต่อ Test Case
- ระบุผลกระทบต่อ Document
- ประเมิน Effort เบื้องต้น
- สร้าง Change Impact Report

### Output
- Change Impact Report
- Affected Component List
- Affected Screen List
- Affected API List
- Affected Table List
- Affected Test Case List
- Estimated Effort
- Risk Assessment

### Example Output

```markdown
# Change Impact Report

## Change Summary
...

## Affected Areas
| Area | Item | Impact Level | Description |
|---|---|---|---|

## Estimated Effort
| Role | MD |
|---|---|
| BA | 2 |
| SA | 1 |
| Developer | 5 |
| QA | 3 |

## Risks
...
```

---

## 5.9 Documentation Agent

### Purpose
สร้างเอกสารโครงการจาก Output ของ Agent อื่น

### Output
- BRD Document
- FSD Document
- SAD Document
- API Document
- Test Document
- User Manual
- Deployment Guide
- Release Note

---

## 5.10 DevOps Agent

### Purpose
เตรียม Deployment, Docker, CI/CD และ Environment

### Output
- Dockerfile
- docker-compose.yml
- .env.example
- CI/CD Pipeline
- Deployment Guide
- Health Check
- Logging Guide

---

## 5.11 Project Manager Agent

### Purpose
ติดตามสถานะงานทั้งหมดและสรุปผลให้ผู้ใช้

### Responsibilities
- สร้าง Work Breakdown
- Assign Agent
- Monitor Progress
- Manage Timeline
- Summarize Status
- Highlight Risk
- Prepare Final Summary

### Output
- Project Plan
- Task Status
- Progress Summary
- Risk Summary
- Final Delivery Summary

---

# 6. Virtual Office Concept

## 6.1 Office Zones

ระบบต้องมี Office Map ที่แบ่งเป็นโซนตาม SDLC

```text
Reception / Input Area
Requirement Room
Gap Analysis Room
BA Room
Solution Architect Room
UX Studio
Developer Zone
QA Lab
Change Impact Room
Documentation Room
DevOps / Server Room
PM Command Center
Meeting Room
Dashboard Wall
Break Area
```

## 6.2 Agent Movement Flow

Agent ต้องเดินไปตาม Flow ของงาน

ตัวอย่าง:

```text
User ส่ง Requirement
→ Requirement Agent เดินไป Requirement Room
→ เมื่อสรุปเสร็จ เดินไปส่งงานที่ Gap Analysis Room
→ Gap Analysis Agent ทำงาน
→ ส่งต่อ BA Room
→ ส่งต่อ SA Room
→ ส่งต่อ UX Studio
→ ส่งต่อ Developer Zone
→ ส่งต่อ QA Lab
→ ส่งต่อ Change Impact Room
→ PM Agent สรุปผล
```

## 6.3 Visual Behavior

- Agent อยู่ที่โต๊ะของตัวเองเมื่อ Idle
- Agent เดินไปห้องที่เกี่ยวข้องเมื่อมี Task
- Agent แสดง Bubble Status เช่น Thinking, Working, Reviewing, Done
- Agent แสดง Chat Bubble สั้น ๆ เมื่อส่งงานต่อ
- เมื่อมี Meeting ทุก Agent ที่เกี่ยวข้องเดินไป Meeting Room
- เมื่อเกิด Error Agent แสดง Icon Error
- เมื่อ Task Complete Agent แสดง Done Bubble

---

# 7. Functional Requirements

## 7.1 User Input Management

### Requirement
ระบบต้องรองรับการรับ Requirement จากหลายแหล่ง

### Input Types
- Manual Text
- Meeting Transcript
- Chat Log
- Document Upload
- PDF Upload
- Word Upload
- Markdown Upload
- Future: Audio / Video Transcript

### Fields
- Project Name
- Input Type
- Requirement Text
- Uploaded File
- Source Date
- Source Owner
- Tags
- Priority

### Acceptance Criteria
- User สามารถสร้าง Requirement Input ได้
- User สามารถ Upload Document ได้
- ระบบสามารถเก็บ Source Reference ได้
- Requirement Agent สามารถนำ Input ไปประมวลผลได้

---

## 7.2 SDLC Pipeline Management

### Requirement
ระบบต้องสร้าง Pipeline งานตาม Agent Flow

### Pipeline Steps
1. Requirement Summary
2. Gap Analysis
3. BA Document
4. Solution Design
5. UX Design
6. Code Generation
7. QA Generation
8. Change Impact
9. Documentation
10. PM Summary

### Acceptance Criteria
- ระบบแสดง Pipeline Status ได้
- แต่ละ Step มี Owner Agent
- แต่ละ Step มี Output
- User สามารถ Re-run Step ได้
- User สามารถ Approve / Reject Output ได้

---

## 7.3 Agent Management

### Requirement
Admin ต้องสามารถจัดการ Agent ได้

### Agent Fields
- Agent Name
- Role
- Description
- Goal
- System Prompt
- Avatar
- Home Zone
- Default Model
- Skill List
- Active Status

### Actions
- Create Agent
- Edit Agent
- Delete Agent
- Activate / Deactivate
- Test Prompt
- Reset Memory

---

## 7.4 Task Management

### Requirement
ระบบต้องมี Task สำหรับติดตามงานของ Agent

### Task Fields
- Task ID
- Project ID
- Title
- Description
- Assigned Agent
- Status
- Priority
- Input Reference
- Output Reference
- Due Date
- Created By
- Created At
- Updated At

### Task Status
- Backlog
- New
- Assigned
- In Progress
- Waiting User
- Review
- Approved
- Rejected
- Done
- Failed

### Actions
- Create Task
- Assign Agent
- Run Task
- Pause Task
- Re-run Task
- Approve Output
- Reject Output
- View Activity

---

## 7.5 Agent Chat

### Requirement
User ต้องสามารถ Chat กับ Agent ได้

### Features
- Chat กับ Agent รายตัว
- Chat กับ Project Team
- Chat อ้างอิง Task
- Chat อ้างอิง Document
- เก็บ Chat History
- Agent สามารถแนะนำคำถามต่อได้

---

## 7.6 Agent Collaboration

### Requirement
Agent ต้องสามารถส่งงานต่อกันได้

### Features
- Agent-to-Agent Message
- Handoff Output
- Handoff Reason
- Collaboration Log
- Chain of Thought Summary แบบไม่เปิดเผย reasoning ละเอียด
- Traceability จาก Input ถึง Output

### Example Handoff

```json
{
  "from_agent": "Requirement Agent",
  "to_agent": "Gap Analysis Agent",
  "task_id": "TASK-001",
  "handoff_type": "requirement_summary",
  "message": "Please validate missing and ambiguous requirements."
}
```

---

## 7.7 Document Output Management

### Requirement
ระบบต้องเก็บ Output ที่ Agent สร้าง

### Document Types
- Requirement Summary
- Gap Analysis Report
- BRD
- FSD
- User Story
- Architecture Design
- Database Design
- API Spec
- Wireframe Spec
- Code Package
- Test Case
- UAT Script
- Change Impact Report
- Final Summary

### Actions
- View
- Edit
- Version
- Approve
- Export Markdown
- Export PDF in future
- Download

---

## 7.8 Traceability Matrix

### Requirement
ระบบต้องเชื่อมความสัมพันธ์ตั้งแต่ Requirement ถึง Test Case

### Traceability Links
- Requirement → Gap
- Requirement → User Story
- User Story → Screen
- User Story → API
- User Story → Database Table
- User Story → Code Module
- User Story → Test Case
- Change Request → Affected Items

### Output Example

```markdown
| Requirement ID | User Story | Screen | API | Table | Test Case |
|---|---|---|---|---|---|
```

---

## 7.9 Change Impact Analysis

### Requirement
เมื่อ User เปลี่ยน Requirement ระบบต้องวิเคราะห์ผลกระทบ

### Input
- Original Requirement
- New Requirement
- Current Design
- Current Code Mapping
- Current Test Case

### Output
- Impact Summary
- Affected Screens
- Affected APIs
- Affected Tables
- Affected Workflow
- Affected Test Cases
- Estimated MD
- Risk Level

---

# 8. Agent Movement & Navigation Requirements

## 8.1 Movement Features

Agent ต้องสามารถเดินใน Virtual Office ได้

### Required Features
1. Agent มีตำแหน่ง x, y
2. Agent มี target_x, target_y
3. Agent มี current_zone
4. Agent มี home_zone
5. Agent เดินไปยัง Zone ตาม Task ได้
6. User คลิกตำแหน่งบน Map เพื่อสั่ง Agent เดินได้
7. Agent เดินไปหา Agent อื่นได้
8. Agent เดินไป Meeting Room ได้
9. Agent ไม่เดินทะลุกำแพงหรือ furniture
10. ระบบ Broadcast Movement ผ่าน WebSocket

## 8.2 Movement Status

- idle
- walking
- thinking
- working
- reviewing
- meeting
- waiting_user
- done
- error

## 8.3 Movement Events

### Server to Client

```text
agent.movement.started
agent.position.updated
agent.movement.completed
agent.status.changed
agent.zone.changed
```

### Client to Server

```text
agent.move.request
agent.move_to_zone.request
agent.follow_pipeline.request
```

## 8.4 Pathfinding

### MVP
- Simple linear movement
- Basic collision block
- Move to predefined coordinates

### Phase 2
- Grid-based movement
- A* Pathfinding
- Collision with furniture
- Avoid collision between Agents
- Multi-Agent route planning

## 8.5 Zone Coordinates

Example:

```json
{
  "requirement_room": { "x": 150, "y": 180 },
  "gap_room": { "x": 320, "y": 180 },
  "ba_room": { "x": 500, "y": 180 },
  "sa_room": { "x": 680, "y": 180 },
  "ux_studio": { "x": 860, "y": 180 },
  "developer_zone": { "x": 320, "y": 420 },
  "qa_lab": { "x": 520, "y": 420 },
  "impact_room": { "x": 720, "y": 420 },
  "meeting_room": { "x": 960, "y": 420 }
}
```

---

# 9. UI / UX Requirements

## 9.1 Design Direction

UI ต้องเป็น Professional SaaS Dashboard + 2D Virtual Office

### Style
- Modern
- Clean
- Dark Theme
- Professional
- Pixel / Chibi Character
- Suitable for Customer Demo

### Recommended Tools for Design
- Figma สำหรับ Master UI
- v0 by Vercel สำหรับ Dashboard Component
- Tiled Map Editor สำหรับ Office Map
- Aseprite / Piskel สำหรับ Sprite Sheet
- Canva สำหรับ Mockup / Presentation

## 9.2 Main Screens

### 9.2.1 Office Dashboard

Layout:

```text
Left Sidebar: Agent List / Pipeline
Center: Virtual Office Map
Right Sidebar: Task Detail / Chat
Bottom: Activity Log
Top Bar: Project Selector / LLM Status / Settings
```

Required Components:
- Agent List
- SDLC Pipeline Status
- Virtual Office Canvas
- Task Detail Panel
- Chat Panel
- Activity Feed
- Status Summary

---

### 9.2.2 Project Workspace

Features:
- Project Overview
- Requirement Inputs
- SDLC Pipeline
- Generated Documents
- Traceability Matrix
- Change Requests

---

### 9.2.3 Task Board

Kanban Columns:
- Backlog
- In Progress
- Review
- Done
- Failed

---

### 9.2.4 Agent Management

Features:
- Agent List
- Agent Profile
- Prompt Editor
- Skill Configuration
- Model Setting
- Avatar Setting
- Home Zone Setting

---

### 9.2.5 Document Viewer

Features:
- Markdown Preview
- Version History
- Approval Status
- Export
- Edit Mode

---

### 9.2.6 Settings

Features:
- LLM Provider
- API Key
- Ollama Base URL
- Default Model
- Database Status
- Theme
- Workspace Setting

---

# 10. Design Asset Requirements

## 10.1 UI Assets

| Asset | Format | Usage |
|---|---|---|
| Logo | SVG / PNG | Header / Login |
| Icons | SVG | Sidebar / Buttons |
| Agent Avatar | PNG Sprite Sheet | Phaser Agent |
| Office Map | JSON + PNG Tileset | Phaser Tilemap |
| Background | PNG | Office Canvas |
| UI Reference | PNG / Figma | Code Mapping |

## 10.2 Code Mapping

```text
Figma Frame: Office Dashboard
→ frontend/src/pages/OfficePage.tsx

Figma Component: Agent Card
→ frontend/src/components/agents/AgentCard.tsx

Figma Component: Pipeline Step
→ frontend/src/components/pipeline/PipelineStep.tsx

Figma Component: Task Board
→ frontend/src/components/tasks/TaskBoard.tsx

Figma Component: Chat Panel
→ frontend/src/components/chat/AgentChatPanel.tsx

Figma Component: Document Viewer
→ frontend/src/components/documents/DocumentViewer.tsx

Map JSON
→ frontend/src/assets/maps/office-map.json

Tileset PNG
→ frontend/src/assets/tiles/office-tiles.png

Agent Sprite
→ frontend/src/assets/agents/{agent-role}.png
```

---

# 11. Technical Architecture

## 11.1 Recommended Tech Stack

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zustand
- Phaser.js
- Socket.IO Client or Native WebSocket
- React Router

### Backend
- FastAPI
- Python
- SQLAlchemy
- Alembic
- Pydantic
- WebSocket
- LangGraph or CrewAI
- Uvicorn

### Database
- PostgreSQL

### Vector Database
- Qdrant

### LLM
- OpenAI API
- Ollama
- Future: Claude, Gemini

### Deployment
- Docker Compose
- Optional Nginx
- Optional Cloudflare Tunnel

---

## 11.2 System Components

```text
Frontend Web App
  - Office UI
  - Agent UI
  - Task UI
  - Chat UI
  - Document UI

Backend API
  - Agent API
  - Task API
  - Project API
  - Document API
  - LLM API
  - WebSocket API

Agent Orchestrator
  - Pipeline Runner
  - Agent Manager
  - Handoff Manager
  - Memory Manager
  - Tool Manager

Data Store
  - PostgreSQL
  - Qdrant
  - File Storage
```

---

# 12. Database Design

## 12.1 projects

```sql
id UUID PRIMARY KEY
name VARCHAR
description TEXT
status VARCHAR
created_by VARCHAR
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.2 requirement_inputs

```sql
id UUID PRIMARY KEY
project_id UUID
input_type VARCHAR
title VARCHAR
content TEXT
file_url TEXT
source_owner VARCHAR
source_date TIMESTAMP
metadata_json JSONB
created_at TIMESTAMP
```

## 12.3 agents

```sql
id UUID PRIMARY KEY
name VARCHAR
role VARCHAR
description TEXT
goal TEXT
system_prompt TEXT
avatar_url TEXT
home_zone VARCHAR
current_zone VARCHAR
status VARCHAR
location_x INTEGER
location_y INTEGER
target_x INTEGER
target_y INTEGER
sprite_direction VARCHAR
model_provider VARCHAR
model_name VARCHAR
is_active BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.4 tasks

```sql
id UUID PRIMARY KEY
project_id UUID
title VARCHAR
description TEXT
assigned_agent_id UUID
status VARCHAR
priority VARCHAR
pipeline_step VARCHAR
input_reference_id UUID
output_document_id UUID
due_date TIMESTAMP
created_by VARCHAR
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.5 pipeline_runs

```sql
id UUID PRIMARY KEY
project_id UUID
status VARCHAR
current_step VARCHAR
started_at TIMESTAMP
completed_at TIMESTAMP
created_at TIMESTAMP
```

## 12.6 pipeline_steps

```sql
id UUID PRIMARY KEY
pipeline_run_id UUID
step_name VARCHAR
agent_id UUID
status VARCHAR
input_json JSONB
output_document_id UUID
started_at TIMESTAMP
completed_at TIMESTAMP
error_message TEXT
```

## 12.7 documents

```sql
id UUID PRIMARY KEY
project_id UUID
document_type VARCHAR
title VARCHAR
content_markdown TEXT
version INTEGER
status VARCHAR
created_by_agent_id UUID
approved_by VARCHAR
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.8 messages

```sql
id UUID PRIMARY KEY
project_id UUID
task_id UUID
sender_type VARCHAR
sender_id UUID
receiver_type VARCHAR
receiver_id UUID
content TEXT
message_type VARCHAR
metadata_json JSONB
created_at TIMESTAMP
```

## 12.9 activity_logs

```sql
id UUID PRIMARY KEY
project_id UUID
task_id UUID
agent_id UUID
event_type VARCHAR
message TEXT
metadata_json JSONB
created_at TIMESTAMP
```

## 12.10 traceability_links

```sql
id UUID PRIMARY KEY
project_id UUID
source_type VARCHAR
source_id UUID
target_type VARCHAR
target_id UUID
link_type VARCHAR
created_at TIMESTAMP
```

## 12.11 llm_settings

```sql
id UUID PRIMARY KEY
provider VARCHAR
base_url TEXT
model_name VARCHAR
api_key_encrypted TEXT
temperature FLOAT
max_tokens INTEGER
is_active BOOLEAN
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.12 agent_memories

```sql
id UUID PRIMARY KEY
agent_id UUID
project_id UUID
memory_type VARCHAR
content TEXT
embedding_id VARCHAR
importance_score FLOAT
created_at TIMESTAMP
```

---

# 13. API Design

## 13.1 Project API

```text
GET    /api/projects
POST   /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

## 13.2 Requirement Input API

```text
GET    /api/projects/{project_id}/inputs
POST   /api/projects/{project_id}/inputs
GET    /api/inputs/{input_id}
DELETE /api/inputs/{input_id}
```

## 13.3 Agent API

```text
GET    /api/agents
POST   /api/agents
GET    /api/agents/{agent_id}
PUT    /api/agents/{agent_id}
DELETE /api/agents/{agent_id}

POST   /api/agents/{agent_id}/chat
POST   /api/agents/{agent_id}/move
POST   /api/agents/{agent_id}/move-to-zone
POST   /api/agents/{agent_id}/reset-memory
```

## 13.4 Task API

```text
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}

POST   /api/tasks/{task_id}/assign
POST   /api/tasks/{task_id}/run
POST   /api/tasks/{task_id}/approve
POST   /api/tasks/{task_id}/reject
POST   /api/tasks/{task_id}/rerun
```

## 13.5 Pipeline API

```text
POST   /api/projects/{project_id}/pipeline/run
GET    /api/projects/{project_id}/pipeline/status
GET    /api/pipeline-runs/{run_id}
POST   /api/pipeline-runs/{run_id}/pause
POST   /api/pipeline-runs/{run_id}/resume
POST   /api/pipeline-steps/{step_id}/rerun
```

## 13.6 Document API

```text
GET    /api/projects/{project_id}/documents
POST   /api/projects/{project_id}/documents
GET    /api/documents/{document_id}
PUT    /api/documents/{document_id}
POST   /api/documents/{document_id}/approve
POST   /api/documents/{document_id}/export
```

## 13.7 Chat API

```text
GET    /api/projects/{project_id}/messages
GET    /api/tasks/{task_id}/messages
POST   /api/messages
```

## 13.8 Activity API

```text
GET    /api/projects/{project_id}/activity
GET    /api/tasks/{task_id}/activity
GET    /api/agents/{agent_id}/activity
```

## 13.9 LLM API

```text
GET    /api/settings/llm
POST   /api/settings/llm
PUT    /api/settings/llm/{id}
POST   /api/llm/test
```

## 13.10 Change Impact API

```text
POST   /api/projects/{project_id}/change-impact/analyze
GET    /api/projects/{project_id}/change-impact/reports
GET    /api/change-impact/{report_id}
```

---

# 14. WebSocket Events

## 14.1 Server to Client

```text
agent.status.changed
agent.movement.started
agent.position.updated
agent.movement.completed
agent.zone.changed

task.created
task.updated
task.completed
task.failed

pipeline.started
pipeline.step.started
pipeline.step.completed
pipeline.step.failed
pipeline.completed

document.created
document.updated
document.approved

message.created
activity.created
```

## 14.2 Client to Server

```text
agent.move.request
agent.chat.send
task.run.request
pipeline.run.request
document.approve.request
```

---

# 15. LLM & Agent Orchestration Design

## 15.1 LLM Provider

ระบบต้องรองรับ

- OpenAI
- Ollama
- Future: Claude
- Future: Gemini

## 15.2 Agent Execution Pattern

แต่ละ Agent ทำงานแบบนี้

```text
1. Receive Input
2. Load Agent Prompt
3. Load Project Context
4. Load Relevant Memory
5. Generate Output
6. Save Document
7. Save Activity Log
8. Handoff to Next Agent
9. Update Status
```

## 15.3 Recommended Orchestration

### MVP
ใช้ Custom Python Orchestrator ก่อน

### Phase 2
ใช้ LangGraph เพื่อทำ State Machine

### Phase 3
รองรับ CrewAI / MCP Tools

---

# 16. Agent System Prompts

## 16.1 Requirement Agent Prompt

```text
You are the Requirement Agent in an AI-SDLC Working Office.

Your responsibility is to summarize requirements from meeting transcripts, chat logs, documents, and user input.

You must produce structured requirement output including:
- Business objective
- Scope
- In scope
- Out of scope
- Functional requirements
- Non-functional requirements
- Assumptions
- Constraints
- Stakeholders
- Open questions

Write clearly and professionally.
Do not invent missing information.
If information is missing, mark it as "Need clarification".
```

## 16.2 Gap Analysis Agent Prompt

```text
You are the Gap Analysis Agent.

Your responsibility is to review requirements and identify:
- Missing requirements
- Ambiguous requirements
- Conflicting requirements
- Duplicate requirements
- Integration gaps
- Data gaps
- Security gaps
- Approval workflow gaps
- Reporting gaps
- Risks

For each gap, provide:
- Gap ID
- Description
- Impact
- Severity
- Clarification question
- Recommended action

Do not solve the requirement silently. Always make missing information visible.
```

## 16.3 BA Agent Prompt

```text
You are the BA Agent.

Your responsibility is to convert validated requirements into:
- BRD
- FSD
- User stories
- Acceptance criteria
- Business process description
- Field requirement
- Validation rules

Use clear structure and tables.
Acceptance criteria must use Given / When / Then format.
```

## 16.4 Solution Architect Agent Prompt

```text
You are the Solution Architect Agent.

Your responsibility is to design the technical solution based on BRD, FSD, and user stories.

You must produce:
- Architecture overview
- Component design
- Database design
- API design
- Workflow design
- Integration design
- Security design
- Deployment design
- Error handling
- Audit logging

Make practical technology decisions.
Separate assumptions from confirmed requirements.
```

## 16.5 UX Agent Prompt

```text
You are the UX Agent.

Your responsibility is to create wireframes, screen specifications, UX flows, and UI component mapping.

You must produce:
- Screen inventory
- Wireframe description
- Screen layout
- Field specification
- Validation behavior
- Button/action behavior
- Navigation flow
- Design tokens
- Component mapping for React

Do not create vague UI.
Be specific enough for a developer or AI coding tool to implement.
```

## 16.6 Developer Agent Prompt

```text
You are the Developer Agent.

Your responsibility is to generate clean, maintainable code based on requirement, FSD, architecture, API spec, database design, and UX screen spec.

You must:
- Follow the project folder structure
- Use React, Vite, TypeScript, Tailwind CSS for frontend
- Use FastAPI, SQLAlchemy, PostgreSQL for backend
- Create reusable components
- Create API services
- Create database models
- Create migration files
- Add useful comments
- Avoid hardcoding where configuration is needed
```

## 16.7 QA Agent Prompt

```text
You are the QA Agent.

Your responsibility is to create test cases, UAT scripts, SIT scripts, regression test sets, and QA review summary.

You must cover:
- Positive cases
- Negative cases
- Boundary cases
- Permission cases
- Workflow cases
- Integration cases
- Error handling cases

Map each test case back to requirement ID or user story ID.
```

## 16.8 Change Impact Agent Prompt

```text
You are the Change Impact Agent.

Your responsibility is to analyze the impact of requirement changes.

You must compare old and new requirements and identify impact on:
- Requirement documents
- User stories
- Screens
- APIs
- Database tables
- Workflow
- Code modules
- Test cases
- Deployment
- Timeline
- Effort

Provide estimated MD by role and risk level.
```

---

# 17. Frontend Folder Structure

```text
frontend/
├── src/
│   ├── assets/
│   │   ├── agents/
│   │   ├── maps/
│   │   ├── tiles/
│   │   └── icons/
│   ├── components/
│   │   ├── agents/
│   │   ├── activity/
│   │   ├── chat/
│   │   ├── documents/
│   │   ├── layout/
│   │   ├── office/
│   │   ├── pipeline/
│   │   ├── tasks/
│   │   └── ui/
│   ├── pages/
│   │   ├── OfficePage.tsx
│   │   ├── ProjectPage.tsx
│   │   ├── TaskBoardPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   ├── AgentsPage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/
│   │   ├── agentService.ts
│   │   ├── taskService.ts
│   │   ├── projectService.ts
│   │   ├── pipelineService.ts
│   │   └── websocketService.ts
│   ├── stores/
│   │   ├── agentStore.ts
│   │   ├── taskStore.ts
│   │   ├── projectStore.ts
│   │   └── uiStore.ts
│   ├── types/
│   ├── lib/
│   ├── App.tsx
│   └── main.tsx
```

---

# 18. Backend Folder Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── agents.py
│   │   ├── tasks.py
│   │   ├── projects.py
│   │   ├── pipeline.py
│   │   ├── documents.py
│   │   ├── messages.py
│   │   ├── activity.py
│   │   └── settings.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── websocket.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── agent_service.py
│   │   ├── task_service.py
│   │   ├── pipeline_service.py
│   │   ├── document_service.py
│   │   ├── llm_service.py
│   │   └── movement_service.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── requirement_agent.py
│   │   ├── gap_analysis_agent.py
│   │   ├── ba_agent.py
│   │   ├── sa_agent.py
│   │   ├── ux_agent.py
│   │   ├── developer_agent.py
│   │   ├── qa_agent.py
│   │   └── change_impact_agent.py
│   ├── orchestrator/
│   │   ├── pipeline_orchestrator.py
│   │   ├── handoff_manager.py
│   │   └── traceability_manager.py
│   └── main.py
├── alembic/
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

# 19. Docker Compose Requirement

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_office

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ai_office
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
```

---

# 20. Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_office
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_MODEL=qwen3:8b
QDRANT_URL=http://qdrant:6333
SECRET_KEY=change-me
```

---

# 21. MVP Scope

## 21.1 MVP Must Have

1. Virtual Office Dashboard
2. Agent List
3. 8 Core SDLC Agents
4. Agent Status
5. Agent Movement แบบ simple
6. Project Creation
7. Requirement Input
8. Run SDLC Pipeline
9. Generate Requirement Summary
10. Generate Gap Analysis
11. Generate BA Output
12. Generate SA Output
13. Generate UX Spec
14. Generate QA Test Case
15. Activity Log
16. Document Viewer
17. PostgreSQL Persistence
18. LLM Integration with Ollama or OpenAI
19. Docker Compose
20. README

## 21.2 MVP Can Use Mock

- Pixel Map ใช้ static background ได้
- Agent Sprite ใช้ placeholder PNG ได้
- Pathfinding ใช้ simple movement ได้
- Code Generation เป็น markdown output ก่อน ยังไม่ต้องเขียนไฟล์จริง
- File Upload รองรับ text/markdown ก่อน

---

# 22. Phase 2 Scope

1. A* Pathfinding
2. Real Tilemap
3. Agent Sprite Sheet Animation
4. File Upload PDF / Word
5. Audio Transcript Integration
6. Qdrant RAG
7. GitHub Integration
8. MCP Tool Integration
9. Real Code File Generation
10. Figma / v0 Integration
11. Export PDF / Word
12. Multi Workspace
13. User Permission
14. Human Approval Gate
15. Change Request Versioning
16. Test Case Export Excel
17. UAT Script Export
18. Dashboard Analytics
19. Cost / Token Usage Tracking
20. Agent Marketplace

---

# 23. Acceptance Criteria

MVP ถือว่าผ่านเมื่อ:

1. เปิดเว็บแล้วเห็น Office Dashboard
2. เห็น Agent อย่างน้อย 8 ตัว
3. Agent มี Status และตำแหน่ง
4. Agent เดินไป Zone ได้แบบ simple movement
5. User สร้าง Project ได้
6. User ใส่ Requirement Input ได้
7. User กด Run Pipeline ได้
8. Requirement Agent สร้าง Requirement Summary ได้
9. Gap Analysis Agent สร้าง Gap Report ได้
10. BA Agent สร้าง BRD/FSD/User Story ได้
11. SA Agent สร้าง Architecture/API/DB Design ได้
12. UX Agent สร้าง Screen Spec ได้
13. QA Agent สร้าง Test Case ได้
14. Change Impact Agent วิเคราะห์ Change ได้
15. Output ถูกเก็บเป็น Document
16. Activity Log แสดงการทำงานของ Agent
17. WebSocket update status/movement ได้
18. ข้อมูลเก็บใน PostgreSQL
19. Run ด้วย Docker Compose ได้
20. มี README ติดตั้งและรันระบบ

---

# 24. Development Roadmap

## Sprint 1 — Project Skeleton
- Setup frontend
- Setup backend
- Setup docker-compose
- Setup PostgreSQL
- Setup base API
- Setup layout

## Sprint 2 — Core Data & API
- Projects
- Agents
- Tasks
- Documents
- Activity Logs
- Messages

## Sprint 3 — UI Dashboard
- Office Dashboard
- Agent List
- Task Panel
- Activity Feed
- Document Viewer

## Sprint 4 — Agent Movement
- Office Map
- Agent Position
- Click-to-move
- Move-to-zone
- WebSocket movement

## Sprint 5 — LLM Integration
- LLM Settings
- Ollama Integration
- OpenAI Integration
- Agent Prompt Execution

## Sprint 6 — SDLC Pipeline
- Pipeline Orchestrator
- Requirement Agent
- Gap Agent
- BA Agent
- SA Agent
- UX Agent
- QA Agent
- Change Impact Agent

## Sprint 7 — Traceability & Document
- Document version
- Traceability matrix
- Approve / reject
- Export markdown

## Sprint 8 — Polish & Demo
- UI polish
- Demo data
- README
- Error handling
- Docker final check

---

# 25. Prompt for Claude Code — Start Architecture First

Use this prompt first. Do not ask AI to generate the whole system at once.

```text
You are a Senior Software Architect and Full-Stack AI Application Engineer.

I want to build a project called AI-SDLC Working Office.

It is a professional 2D virtual office where AI agents work together through a software development lifecycle.

Core agents:
1. Requirement Agent
2. Gap Analysis Agent
3. BA Agent
4. Solution Architect Agent
5. UX Agent
6. Developer Agent
7. QA Agent
8. Change Impact Agent
9. Documentation Agent
10. DevOps Agent
11. Project Manager Agent

The system must include:
- React + Vite + TypeScript + Tailwind CSS frontend
- Phaser.js virtual office map
- FastAPI backend
- PostgreSQL database
- WebSocket real-time updates
- Ollama and OpenAI LLM integration
- Agent movement inside the office
- SDLC pipeline from requirement to QA and change impact
- Document output management
- Activity log
- Traceability matrix

Please create:
1. Final project architecture
2. Folder structure
3. Database schema
4. API design
5. Frontend page/component plan
6. Backend service plan
7. Development roadmap

Do not generate full code yet.
First produce the implementation plan and confirm the build sequence.
```

---

# 26. Prompt for Claude Code — Generate Project Skeleton

```text
Based on the approved architecture, generate the project skeleton.

Create:
- frontend React Vite TypeScript Tailwind project
- backend FastAPI project
- PostgreSQL connection
- Docker Compose
- .env.example
- README

Do not implement SDLC agent logic yet.
Only create the runnable skeleton.
```

---

# 27. Prompt for Claude Code — Implement Core Models

```text
Implement the backend database models and migrations.

Create SQLAlchemy models and Pydantic schemas for:
- projects
- requirement_inputs
- agents
- tasks
- pipeline_runs
- pipeline_steps
- documents
- messages
- activity_logs
- traceability_links
- llm_settings
- agent_memories

Create CRUD services and basic REST APIs.
```

---

# 28. Prompt for Claude Code — Implement UI

```text
Implement the frontend UI using React, TypeScript, Tailwind CSS, and shadcn/ui.

Create pages:
- OfficePage
- ProjectPage
- TaskBoardPage
- DocumentsPage
- AgentsPage
- SettingsPage

Create components:
- AgentCard
- AgentList
- PipelineStatus
- TaskPanel
- ActivityLog
- DocumentViewer
- AgentChatPanel
- OfficeCanvas placeholder

Use mock data first.
Make the design professional, dark theme, SaaS dashboard style.
Do not create a childish UI.
```

---

# 29. Prompt for Claude Code — Implement Agent Movement

```text
Implement the virtual office movement system.

Use Phaser.js in the frontend.

Requirements:
- Show office background
- Show agents as sprites or placeholder images
- Each agent has x,y position
- Click an agent to select
- Click a map position to move selected agent
- Move agent smoothly to target
- Update agent status to walking
- Change status to idle when arrived
- Add move-to-zone function
- Broadcast movement through WebSocket
- Save location_x, location_y, target_x, target_y in backend

For MVP, use simple movement.
Prepare the code so A* pathfinding can be added later.
```

---

# 30. Prompt for Claude Code — Implement SDLC Pipeline

```text
Implement the SDLC agent pipeline.

Pipeline steps:
1. Requirement Agent
2. Gap Analysis Agent
3. BA Agent
4. Solution Architect Agent
5. UX Agent
6. Developer Agent
7. QA Agent
8. Change Impact Agent
9. Documentation Agent
10. Project Manager Agent

Each step must:
- update agent status
- move agent to related office zone
- call LLM service with the correct system prompt
- save output as document
- create activity log
- handoff to next agent
- update pipeline status

Use Ollama first as default provider.
Also support OpenAI if API key is configured.
```

---

# 31. Prompt for Claude Code — Implement Polish

```text
Polish the application for customer demo.

Improve:
- UI spacing
- Typography
- Agent cards
- Pipeline visualization
- Activity log
- Document viewer
- Loading states
- Error handling
- Empty states
- Demo sample project
- README setup guide

Make the application look like a professional AI software factory.
```

---

# 32. Non-Goals for MVP

MVP ยังไม่ต้องทำสิ่งต่อไปนี้:

- Login / Permission แบบเต็ม
- Payment
- Multi-tenant เต็มรูปแบบ
- Real-time multi-user collaboration แบบสมบูรณ์
- Full GitHub commit automation
- Production-grade security
- Full BPMN editor
- Full Figma integration
- Real voice/video processing
- Excel export แบบสมบูรณ์

---

# 33. Risks & Recommendations

## Risk 1: Scope ใหญ่มากเกินไป
Recommendation: ทำ MVP Pipeline + Dashboard ก่อน อย่าเริ่มด้วย Agent เดินซับซ้อน

## Risk 2: UI ไม่สวยถ้าให้ Claude ออกแบบเอง
Recommendation: ใช้ Figma หรือ v0 ทำ UI reference ก่อน แล้วให้ Claude Code เขียนตาม

## Risk 3: Agent Output ไม่สม่ำเสมอ
Recommendation: ใช้ structured output format และ template สำหรับแต่ละ Agent

## Risk 4: Local LLM อาจตอบไม่ดีเท่า API
Recommendation: ใช้ Ollama สำหรับ dev/test และใช้ OpenAI สำหรับ demo สำคัญ

## Risk 5: Movement ใช้เวลามาก
Recommendation: ทำ simple movement ก่อน แล้วค่อยเพิ่ม A*

---

# 34. Final Product Vision

ระบบนี้ควรถูกวางตำแหน่งเป็น

```text
AI-SDLC Working Office
An Agentic Software Factory for requirement analysis, solution design, code generation, testing, and change impact analysis.
```

ไม่ใช่แค่ Virtual Office สวย ๆ แต่เป็นเครื่องมือช่วยทีม Software Delivery ทำงานจริงแบบ End-to-End

---

# 35. Final Summary

AI-SDLC Working Office ต้องมี 3 คุณค่าหลัก

1. **Visual Collaboration**  
   เห็น Agent เดินและทำงานใน Virtual Office

2. **SDLC Automation**  
   Agent ทำงานตามขั้นตอน Requirement → Design → Code → Test

3. **Traceability & Change Impact**  
   เชื่อม Requirement ถึง Test Case และวิเคราะห์ผลกระทบเมื่อ Requirement เปลี่ยน

ระบบควรเริ่มจาก MVP ที่ใช้งานได้จริงก่อน แล้วค่อยเพิ่มความสามารถด้าน Animation, RAG, GitHub, MCP, Export และ Multi-user ภายหลัง
