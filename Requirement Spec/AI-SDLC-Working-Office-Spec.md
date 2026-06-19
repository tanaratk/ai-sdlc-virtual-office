# AI-SDLC Working Office — Requirement & Design Specification

**Document Version:** 1.1  
**Project Name:** AI-SDLC Working Office / AI Agent Virtual Office

**Purpose:** Requirement & Design Specification สำหรับใช้เป็น Master Prompt / Development Specification เพื่อให้ AI Coding Tools เช่น Claude Code, Cursor, Windsurf, Lovable หรือ Bolt.new นำไปสร้างเว็บแอปพลิเคชันจริง โดยระบบต้องรองรับการทำงานของ AI Agent หลายบทบาทในกระบวนการพัฒนา Software ตั้งแต่รับ Requirement วิเคราะห์ ออกแบบ พัฒนา ทดสอบ ตรวจสอบผลกระทบ และติดตามสถานะการส่งมอบ Application อย่างเป็นระบบ

**Primary Goal:** สร้างระบบ Virtual Office แบบ Professional ที่ทำหน้าที่เป็น Agentic Software Development Platform โดยมี AI Agent ทำงานร่วมกันตามกระบวนการ SDLC จริง ตั้งแต่ Requirement → Gap Analysis → BA → SA → UX → Developer → QA → Change Impact เพื่อเปลี่ยน Business Requirement ให้กลายเป็น Application Output ที่สามารถพัฒนาต่อ ทดสอบ ตรวจสอบย้อนกลับ และเตรียมส่งมอบได้จริง ไม่ใช่เพียงการสร้างเอกสารประกอบโครงการ

**Important Requirement Clarification:** ระบบนี้ต้องถูกออกแบบเป็น Application Development Platform ที่สามารถสร้าง Project Workspace, Source Code File, Database Migration, API, UI Screen, Test File, Build/Preview และ Deployment-ready Package ได้จริง โดยเอกสาร BRD/FSD/User Story/API Spec/Test Case เป็นเพียง Development Artifact ที่สนับสนุนการสร้าง Application ไม่ใช่ผลลัพธ์สุดท้ายเพียงอย่างเดียว

---

# 1. Executive Summary

AI-SDLC Working Office คือเว็บแอปพลิเคชันแบบ 2D Virtual Office สำหรับบริหารและขับเคลื่อนกระบวนการพัฒนา Software ด้วย AI Agent หลายบทบาท โดยจำลองการทำงานเหมือนทีมพัฒนา Application จริง ตั้งแต่รับ Requirement วิเคราะห์ ออกแบบ พัฒนา ทดสอบ ไปจนถึงรองรับการเปลี่ยนแปลงของระบบ

ระบบไม่ได้มีเป้าหมายเป็นเพียงเครื่องมือสร้างเอกสาร แต่เป็น **Agentic Software Development Platform** หรือ **AI Software Factory** ที่ช่วยเปลี่ยน Requirement ให้กลายเป็น Application ที่สามารถนำไปพัฒนาต่อ รันทดสอบ ตรวจสอบ และส่งมอบได้จริง

ผู้ใช้งานสามารถเริ่มต้นจาก Meeting, Chat, Document หรือ Manual Input จากนั้น AI Agent แต่ละบทบาทจะทำงานร่วมกันตามกระบวนการ SDLC เช่น Requirement Agent, Gap Analysis Agent, BA Agent, Solution Architect Agent, UX Agent, Developer Agent, QA Agent และ Change Impact Agent

Agent แต่ละตัวจะมีหน้าที่ชัดเจนและส่งต่องานกันเป็นลำดับ โดยระบบต้องสามารถสร้างทั้งผลลัพธ์ด้านการวิเคราะห์และผลลัพธ์ด้านการพัฒนาระบบ เช่น Requirement Backlog, User Story, Application Flow, Data Model, API Design, UI Screen Spec, Source Code, Test Case, UAT Script, Deployment Package และ Change Impact Report

จุดสำคัญของ AI-SDLC Working Office คือการทำให้ AI Agent ไม่ได้หยุดอยู่ที่การช่วยเขียนเอกสาร แต่สามารถทำงานเป็นทีมพัฒนา Software เสมือนจริง โดยมี Workspace กลางสำหรับติดตามสถานะงาน ตรวจสอบ Traceability ระหว่าง Requirement → Design → Code → Test และช่วยให้ผู้ใช้งานสามารถควบคุมคุณภาพของ Application ได้ตลอดวงจรการพัฒนา

ในมุมของ User Experience ระบบจะแสดง Agent อยู่ใน Office Map แบบ 2D Pixel / Professional Virtual Office โดย Agent สามารถเดินไปยังห้องหรือโซนต่าง ๆ ตามขั้นตอนการทำงาน เช่น Requirement Room, Gap Analysis Room, BA Room, SA Room, UX Room, Developer Zone, QA Zone และ Impact Analysis Room เพื่อให้ผู้ใช้งานเห็นภาพการทำงานของ AI Agent ในแต่ละขั้นตอนอย่างชัดเจน

เป้าหมายหลักของระบบคือการสร้าง Application Development Workflow ที่ AI Agent สามารถช่วยลดเวลาการวิเคราะห์ ออกแบบ พัฒนา และทดสอบระบบ พร้อมทั้งเพิ่มความชัดเจนของ Requirement ลด Gap ระหว่างทีม Business และทีม Technical และทำให้การส่งมอบ Application มีความต่อเนื่อง ตรวจสอบย้อนกลับได้ และสามารถพัฒนาต่อยอดได้จริง


## 1.1 Version 1.1 Addendum — Application-Ready Direction

เอกสารเวอร์ชันนี้เพิ่มความชัดเจนว่า AI-SDLC Working Office ต้องเป็นระบบสำหรับสร้าง Application จริง ไม่ใช่เพียงระบบผลิตเอกสารตาม SDLC

### Key Additions
- เพิ่ม Application Builder Layer สำหรับสร้างไฟล์ Source Code จริง
- เพิ่ม Code Workspace สำหรับดู แก้ไข และจัดการไฟล์ที่ AI Agent สร้าง
- เพิ่ม Build / Preview / Test Execution เพื่อให้ User ตรวจสอบ Application Output ได้
- เพิ่ม Deployment-ready Package เช่น Dockerfile, docker-compose, migration, README และ .env.example
- เพิ่ม Traceability จาก Requirement → Design → Code File → Test Case → Build Result
- ปรับบทบาท Developer Agent และ DevOps Agent ให้สร้าง Output ที่พร้อมนำไปรันและพัฒนาต่อได้จริง

### Product Principle
```text
Documents are supporting artifacts.
The real product output is a working application workspace with source code, tests, configuration, build result, and deployment package.
```

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


## 2.4 Application-Ready Business Objective

ระบบต้องช่วยให้ทีมสามารถเปลี่ยน Requirement ให้กลายเป็น Application Project ที่จับต้องได้ โดยมีทั้งเอกสารประกอบ การออกแบบเชิงเทคนิค Source Code โครงสร้างฐานข้อมูล API UI Test และ Deployment Package อยู่ใน Workspace เดียวกัน

### Expected Business Outcome
- ลดเวลาจาก Requirement ไปสู่ Prototype / MVP
- ลดช่องว่างระหว่าง BA, SA, UX, Developer และ QA
- ทำให้ Requirement ทุกข้อสามารถ Trace ไปถึง Code และ Test ได้
- ทำให้ผู้ใช้งานสามารถ Preview หรือ Run Application Output ได้
- ทำให้ AI Coding Tools นำ Spec ไปสร้างระบบต่อได้ง่ายขึ้น
- ทำให้ระบบเป็น Showcase ด้าน AI Software Delivery ไม่ใช่แค่ Document Automation

### Application Output Definition
Application Output หมายถึงผลลัพธ์ที่สามารถนำไปใช้พัฒนา ทดสอบ หรือ Deploy ต่อได้ เช่น

- Frontend Source Code
- Backend Source Code
- Database Schema / Migration
- API Routes / Service Layer
- UI Components / Pages
- Unit Test / API Test / UI Test
- Dockerfile / docker-compose.yml
- README / Setup Guide
- Deployment-ready Package
- Build / Preview Result


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


## 3.1 Updated Concept — From SDLC Documents to Working Application

ระบบต้องมีแนวคิดเป็น Agentic Software Factory ที่ทำงานเป็น Development Pipeline จริง โดยมี Output หลักเป็น Application Workspace

```text
[Requirement Sources]
Meeting / Chat / Document / Manual Input

        ↓

[SDLC Understanding]
Requirement Summary / Gap / User Story / Acceptance Criteria

        ↓

[Solution & UX Design]
Architecture / Database / API / Screen Spec / Workflow

        ↓

[Application Builder]
Generate Frontend / Backend / Database Migration / Tests / Config

        ↓

[Validation & Preview]
Build / Run / Test / Review / Fix / Re-run

        ↓

[Delivery Package]
Source Code / Docker / README / Deployment Guide / Traceability
```

## 3.2 Additional Application Builder Layer

เพิ่ม Layer ใหม่สำหรับสร้าง Application จริง

```text
[Application Builder Layer]
Code Workspace
Generated File Manager
Frontend Generator
Backend Generator
Database Migration Generator
Test Generator
Build Runner
Preview Runner
Deployment Package Generator
Git Export / Download Package
```

Application Builder Layer ต้องเชื่อมกับ Agent Orchestrator เพื่อให้ Developer Agent, QA Agent และ DevOps Agent สามารถสร้างไฟล์จริง บันทึกไฟล์ ตรวจสอบ Build และส่งผลลัพธ์กลับมายัง UI ได้


---

# 4. High-Level SDLC Agent Flow

```text
User
  |
  v
Requirement Agent          → Requirement Summary
  |
  v  [Human Review Gate 1]
Gap Analysis Agent         → Gap Analysis Report
  |
  v  [Human Review Gate 2]
BA Agent                   → BRD + FSD + User Stories
  |
  v  [Human Review Gate 3]
Solution Architect Agent   → Architecture + DB Design + API Spec
  |
  v  [Human Review Gate 4]
UX Agent                   → Screen Spec + UX Flows
  |
  v  [Human Review Gate 5]
Developer Agent            → Generated Source Code (real files)
  |
  v
DevOps Agent               → Dockerfile + docker-compose + CI/CD
  |
  v  [Human Review Gate 6]
QA Agent                   → Test Cases + UAT Script
  |
  v
Change Impact Agent        → Change Impact Report
  |
  v
Documentation Agent        → Compiled Project Docs
  |
  v
PM Agent                   → Delivery Summary
  |
  v
User Review + GitHub Push
```


## 4.1 Updated End-to-End Application Flow

```text
User Requirement
  |
  v
Requirement Agent
  | creates Requirement Backlog
  v
Gap Analysis Agent
  | validates completeness
  v
BA Agent
  | creates User Stories and Acceptance Criteria
  v
Solution Architect Agent
  | creates Architecture, API, DB, Security, Deployment Design
  v
UX Agent
  | creates Screen Spec and Component Mapping
  v
Developer Agent
  | generates real source files into Code Workspace
  v
QA Agent
  | generates and maps tests to requirements and code
  v
DevOps Agent
  | creates Docker, env, build and deployment package
  v
Build / Preview / Test Runner
  | validates application output
  v
Change Impact Agent
  | checks impact when requirement changes
  v
User Review / Approve / Download / Continue Development
```

## 4.2 Required Output State

ทุก Pipeline Run ต้องมีสถานะ Output ดังนี้

- Draft Artifact: เอกสารหรือ Spec ที่ยังไม่ผ่าน Review
- Approved Artifact: Artifact ที่ User อนุมัติให้ใช้สร้าง Application
- Generated Code: Source Code ที่สร้างเป็นไฟล์จริง
- Buildable Application: Project ที่สามารถ Build ได้
- Previewable Application: Project ที่สามารถ Preview หรือ Run ได้
- Deployment-ready Package: Package ที่มี Docker / README / Config พร้อมส่งต่อ


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
Generate source code จริง (ไฟล์จริง ไม่ใช่ task list หรือ markdown description) ตาม FSD, Architecture, API Spec, DB Design และ Screen Spec โดยผลลัพธ์ต้องเป็น project ที่ developer สามารถ clone และรันต่อได้ทันที

### Recommended Model
`coder14b:latest` (qwen2.5-coder 14.8B, 128k context) — model เฉพาะสำหรับ code generation

### Input
- FSD (จาก BA Agent)
- Architecture + API Spec + DB Design (จาก SA Agent)
- Screen Spec + UX Flows (จาก UX Agent)
- Coding Standard

### Responsibilities
- Generate Backend Models (SQLAlchemy)
- Generate Database Migration (Alembic)
- Generate API Routes (FastAPI — 1 file per domain)
- Generate Pydantic Schemas
- Generate Frontend Types (TypeScript)
- Generate Frontend API Services
- Generate React Components (1 file per screen)
- Generate Page Components
- Generate README.md และ .env.example
- Save ไฟล์จริงลง filesystem (ไม่ใช่แค่บันทึกลง DB)
- Update File Manifest หลังทุก generation

### Generation Strategy
- แต่ละไฟล์ = 1 LLM call แยกกัน
- ลำดับ: models → schemas → routes → migrations → types → services → components → pages
- ถ้า LLM output มี syntax error → retry 1 ครั้ง ถ้ายังผิด → save as-is พร้อม flag `needs_review: true`
- Output เก็บที่ `generated_apps/{project_id}/` บน server filesystem

### Required Code Output Structure

Developer Agent ต้องสามารถสร้างไฟล์จริงตามโครงสร้าง เช่น

```text
generated-apps/{project_slug}/
├── frontend/
│   ├── src/pages/
│   ├── src/components/
│   ├── src/services/
│   ├── src/types/
│   └── package.json
├── backend/
│   ├── app/api/
│   ├── app/models/
│   ├── app/schemas/
│   ├── app/services/
│   └── requirements.txt
├── database/
│   ├── migrations/
│   └── seed/
├── tests/
├── docker-compose.yml
├── .env.example
└── README.md
```

### File Manifest Output

ทุกครั้งที่ Developer Agent สร้างไฟล์ ต้องสร้าง File Manifest

```json
{
  "project_id": "...",
  "generation_id": "...",
  "files": [
    {
      "path": "frontend/src/pages/ExpenseRequestPage.tsx",
      "type": "frontend_page",
      "related_user_story": "US-001",
      "related_requirement": "REQ-001"
    }
  ]
}
```


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
Generate deployment files จริงสำหรับ application ที่ Developer Agent สร้าง เพื่อให้ application พร้อม build และ run ได้ทันที

### Pipeline Position
ทำงานหลัง Developer Agent (step 6.5) ก่อน QA Agent

### Recommended Model
`coder14b:latest` (qwen2.5-coder 14.8B) — เหมาะสำหรับ YAML/Dockerfile generation

### Input
- Generated project structure (จาก Developer Agent)
- Architecture + DB Design (จาก SA Agent)
- .env requirements

### Responsibilities
- Generate `Dockerfile` สำหรับ frontend และ backend แยกกัน
- Generate `docker-compose.yml` รวม frontend, backend, database, redis (ถ้าจำเป็น)
- Generate `.env.example` จาก environment variables ที่ใช้ใน code
- Generate `.github/workflows/ci.yml` (GitHub Actions: lint, test, build)
- Generate `nginx.conf` สำหรับ production
- Generate `README.md` — วิธี setup, run, test
- Save ไฟล์ทั้งหมดลงใน `generated_apps/{project_id}/`

### Output Files
```text
generated_apps/{project_id}/
├── Dockerfile.frontend
├── Dockerfile.backend
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx.conf
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```


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


## 7.10 Application Workspace Management

### Requirement
ระบบต้องมี Application Workspace สำหรับเก็บ Source Code และไฟล์ทั้งหมดที่สร้างจาก Agent

### Features
- สร้าง Workspace ต่อ Project
- แสดง Folder Tree
- เปิดดูไฟล์ Source Code ได้
- แก้ไขไฟล์ Source Code ได้ใน Browser
- ดู Diff ระหว่าง Version ได้
- Rollback File Version ได้
- Download Workspace เป็น ZIP ได้
- Export ไป Git Repository ได้ในอนาคต

### Workspace Status
- Empty
- Generated
- Modified
- Build Pending
- Build Success
- Build Failed
- Test Pending
- Test Passed
- Test Failed
- Ready for Delivery

### Acceptance Criteria
- User สามารถเปิด Code Workspace ของ Project ได้
- User เห็นไฟล์ที่ Developer Agent สร้าง
- User สามารถดูว่าไฟล์ใดเกี่ยวข้องกับ Requirement ใด
- ระบบสามารถบันทึก Version ของไฟล์ได้
- ระบบสามารถ Download Application Package ได้

---

## 7.11 Real Code Generation Management

### Requirement
Developer Agent ต้องสร้าง Source Code เป็นไฟล์จริงใน Workspace ไม่ใช่แค่ Markdown Output

### Supported File Types
- `.tsx`, `.ts`, `.css`, `.json` สำหรับ Frontend
- `.py` สำหรับ Backend
- `.sql` หรือ Alembic migration สำหรับ Database
- `.md` สำหรับ README และเอกสารประกอบ
- `.yml`, `.yaml`, `.env.example` สำหรับ Deployment

### Code Generation Rules
- ทุกไฟล์ต้องมี path ชัดเจน
- ทุกไฟล์ต้อง map กลับไปยัง Requirement / User Story ได้
- ห้ามสร้างไฟล์ซ้ำโดยไม่บันทึก Version
- ถ้าแก้ไฟล์เดิม ต้องบันทึก Change Log
- ถ้า Build Failed ต้องส่ง Error กลับให้ Developer Agent แก้

### Acceptance Criteria
- Developer Agent สร้าง Frontend Page ได้อย่างน้อย 1 หน้า
- Developer Agent สร้าง Backend API ได้อย่างน้อย 1 endpoint
- Developer Agent สร้าง Database Model / Migration ได้
- ระบบบันทึก File Manifest ได้
- ระบบแสดง Generated Files ใน UI ได้

---

## 7.12 Build, Preview & Test Runner

### Requirement
ระบบต้องมีความสามารถในการตรวจสอบว่า Application Output สามารถ Build / Run / Test ได้

### Features
- Run frontend build command
- Run backend test command
- Run unit test / API test
- Capture build logs
- Capture test results
- Show status in Project Workspace
- Send failed logs back to Developer Agent or QA Agent

### MVP Approach
สำหรับ MVP สามารถเริ่มจาก Simulated Runner หรือ Local Command Runner แบบจำกัดก่อน แล้วค่อยเพิ่ม Containerized Runner ใน Phase 2

### Acceptance Criteria
- User เห็น Build Status ได้
- User เห็น Build Log ได้
- User เห็น Test Result ได้
- Pipeline สามารถหยุดที่สถานะ Failed ได้เมื่อ Build หรือ Test ไม่ผ่าน
- User สามารถสั่ง Re-run หลังแก้ไขได้

---

## 7.13 Application Preview

### Requirement
User ต้องสามารถ Preview Application Output หรืออย่างน้อยเปิดดู Generated UI ได้จาก Workspace

### Preview Levels
- Level 1: Static UI Preview จาก generated frontend files
- Level 2: Frontend dev server preview
- Level 3: Full stack preview with backend API
- Level 4: Docker Compose preview environment

### Acceptance Criteria
- User เห็นปุ่ม Preview Application
- ระบบแสดง Preview URL หรือ Preview Panel
- ถ้า Preview ไม่พร้อม ระบบต้องแสดงเหตุผลและขั้นตอนแก้ไข

---

## 7.14 Delivery Package Management

### Requirement
ระบบต้องสร้าง Package สำหรับส่งมอบ Application ที่ประกอบด้วย Source Code, Config, Test และ Setup Guide

### Package Content
- frontend source code
- backend source code
- database migration
- tests
- docker-compose.yml
- .env.example
- README.md
- deployment guide
- traceability matrix
- known limitations

### Acceptance Criteria
- User สามารถกด Generate Delivery Package ได้
- User สามารถ Download เป็น ZIP ได้
- Package ต้องมี README พร้อมวิธี Run
- Package ต้องมี Traceability Matrix แนบไปด้วย

---

## 7.15 Human Review Gates for Real Application Build

### Requirement
ระบบต้องมีจุดให้ User อนุมัติก่อนข้ามจากเอกสาร/Design ไปสู่การ Generate Code จริง

### Required Gates
1. Approve Requirement Summary
2. Approve Gap Resolution
3. Approve User Story / Acceptance Criteria
4. Approve Architecture / DB / API Design
5. Approve UX / Screen Spec
6. Approve Code Generation Plan
7. Approve Test Result
8. Approve Delivery Package

### Acceptance Criteria
- Pipeline ต้องหยุดรอ User Approval ตาม Gate ที่กำหนด
- User สามารถ Approve / Reject / Request Change ได้
- เมื่อ Reject ต้องสร้าง Task กลับไปยัง Agent ที่เกี่ยวข้อง

---

## 7.16 Traceability to Code and Build

### Requirement
Traceability ต้องไม่หยุดที่ Test Case แต่ต้องเชื่อมไปถึง Source Code, Build Result และ Deployment Package

### Extended Traceability Links
- Requirement → User Story
- User Story → Screen
- User Story → API
- API → Backend File
- Screen → Frontend File
- Data Model → Migration File
- User Story → Test File
- Test File → Test Run Result
- Generated File → Build Result
- Build Result → Delivery Package

### Output Example

```markdown
| Requirement ID | User Story | Screen | API | Code File | Test File | Build Result | Package |
|---|---|---|---|---|---|---|---|
```


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


### 9.2.7 Code Workspace

Features:
- Folder Tree
- Code Viewer
- Code Editor แบบพื้นฐาน
- File Version
- File Diff
- Requirement Mapping Panel
- Build Status Panel
- Test Result Panel
- Download Package Button

Layout:

```text
Left: Folder Tree
Center: Code Viewer / Editor
Right: File Metadata / Traceability / Build Log
Bottom: Terminal / Activity Log
```

---

### 9.2.8 Build & Preview Screen

Features:
- Build Application
- Run Test
- View Logs
- Preview URL / Preview iframe
- Failed Issue Summary
- Send Error to Developer Agent

---

### 9.2.9 Delivery Package Screen

Features:
- Package Summary
- Included Files
- README Preview
- Environment Variables
- Docker Compose Preview
- Download ZIP
- Export Git Repository in future


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


## 12.13 application_workspaces

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_name VARCHAR
root_path TEXT
status VARCHAR
current_generation_id UUID
build_status VARCHAR
test_status VARCHAR
preview_url TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.14 generated_files

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_id UUID
generation_id UUID
file_path TEXT
file_type VARCHAR
content TEXT
content_hash VARCHAR
version INTEGER
related_requirement_id VARCHAR
related_user_story_id VARCHAR
related_component VARCHAR
created_by_agent_id UUID
created_at TIMESTAMP
updated_at TIMESTAMP
```

## 12.15 file_versions

```sql
id UUID PRIMARY KEY
file_id UUID
version INTEGER
content TEXT
change_summary TEXT
changed_by_type VARCHAR
changed_by_id UUID
created_at TIMESTAMP
```

## 12.16 code_generations

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_id UUID
pipeline_run_id UUID
agent_id UUID
generation_type VARCHAR
status VARCHAR
input_document_ids JSONB
file_manifest_json JSONB
error_message TEXT
started_at TIMESTAMP
completed_at TIMESTAMP
created_at TIMESTAMP
```

## 12.17 build_runs

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_id UUID
build_type VARCHAR
command TEXT
status VARCHAR
log_text TEXT
started_at TIMESTAMP
completed_at TIMESTAMP
created_at TIMESTAMP
```

## 12.18 test_runs

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_id UUID
test_type VARCHAR
command TEXT
status VARCHAR
passed_count INTEGER
failed_count INTEGER
skipped_count INTEGER
log_text TEXT
result_json JSONB
started_at TIMESTAMP
completed_at TIMESTAMP
created_at TIMESTAMP
```

## 12.19 delivery_packages

```sql
id UUID PRIMARY KEY
project_id UUID
workspace_id UUID
package_name VARCHAR
package_path TEXT
status VARCHAR
included_files_json JSONB
readme_document_id UUID
created_by_agent_id UUID
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


## 13.11 Application Workspace API

```text
GET    /api/projects/{project_id}/workspace
POST   /api/projects/{project_id}/workspace
GET    /api/workspaces/{workspace_id}/files
GET    /api/workspaces/{workspace_id}/files/{file_id}
PUT    /api/workspaces/{workspace_id}/files/{file_id}
GET    /api/workspaces/{workspace_id}/files/{file_id}/versions
POST   /api/workspaces/{workspace_id}/files/{file_id}/rollback
GET    /api/workspaces/{workspace_id}/manifest
```

## 13.12 Code Generation API

```text
POST   /api/projects/{project_id}/code-generation/plan
POST   /api/projects/{project_id}/code-generation/run
GET    /api/code-generations/{generation_id}
POST   /api/code-generations/{generation_id}/rerun
POST   /api/code-generations/{generation_id}/fix-build-error
```

## 13.13 Build / Test / Preview API

```text
POST   /api/workspaces/{workspace_id}/build
GET    /api/build-runs/{build_run_id}
POST   /api/workspaces/{workspace_id}/test
GET    /api/test-runs/{test_run_id}
POST   /api/workspaces/{workspace_id}/preview/start
POST   /api/workspaces/{workspace_id}/preview/stop
GET    /api/workspaces/{workspace_id}/preview/status
```

## 13.14 Delivery Package API

```text
POST   /api/workspaces/{workspace_id}/package
GET    /api/delivery-packages/{package_id}
GET    /api/delivery-packages/{package_id}/download
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


## 14.3 Additional Application Build Events

### Server to Client

```text
workspace.created
workspace.file.created
workspace.file.updated
workspace.manifest.updated

code_generation.started
code_generation.file_created
code_generation.completed
code_generation.failed

build.started
build.log
build.completed
build.failed

test.started
test.log
test.completed
test.failed

preview.started
preview.stopped
package.created
package.ready
```

### Client to Server

```text
workspace.file.save.request
code_generation.run.request
build.run.request
test.run.request
preview.start.request
package.create.request
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


## 15.4 Application Generation Execution Pattern

เมื่อ Pipeline มาถึง Developer Agent ระบบต้องทำงานตามขั้นตอนนี้

```text
1. Load approved User Stories
2. Load approved Architecture / API / DB / UX Spec
3. Create Code Generation Plan
4. Wait for Human Approval Gate
5. Generate files into Application Workspace
6. Save File Manifest
7. Run Build or Simulated Build
8. If build failed, send logs back to Developer Agent
9. Run QA-generated tests
10. Create Delivery Package
11. Update Traceability to code and test result
```

## 15.5 Code Generation Guardrails

- ห้าม Generate Code โดยไม่มี Requirement หรือ User Story ที่อ้างอิงได้
- ห้าม Overwrite ไฟล์โดยไม่สร้าง Version
- ห้ามสร้าง Secret หรือ API Key จริงลงใน Source Code
- ต้องใช้ `.env.example` สำหรับค่า Config
- ต้องแยก frontend, backend, database, tests ให้ชัดเจน
- ต้องสร้าง README ทุกครั้งที่สร้าง Delivery Package
- ต้องแสดง Known Limitations หาก Code ยังเป็น Prototype


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


Additional application-ready instructions:
- You must generate real source files, not only markdown explanations.
- Every generated file must include a target path.
- Every generated file must be mapped to a requirement ID or user story ID when possible.
- Create frontend, backend, database migration, tests, configuration, and README as needed.
- If you are modifying an existing file, provide a change summary.
- Ensure the generated application can be built or previewed with documented commands.
- If build logs are provided, fix the error and explain which files changed.

Expected output format:

```json
{
  "summary": "What was generated",
  "files": [
    {
      "path": "frontend/src/pages/ExamplePage.tsx",
      "type": "frontend_page",
      "content": "...",
      "related_requirement_id": "REQ-001",
      "related_user_story_id": "US-001"
    }
  ],
  "commands": {
    "install": "...",
    "build": "...",
    "run": "...",
    "test": "..."
  },
  "known_limitations": []
}
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
│   │   ├── workspace/
│   │   ├── build/
│   │   ├── delivery/
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
│   │   ├── CodeWorkspacePage.tsx
│   │   ├── BuildPreviewPage.tsx
│   │   ├── DeliveryPackagePage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/
│   │   ├── agentService.ts
│   │   ├── taskService.ts
│   │   ├── projectService.ts
│   │   ├── pipelineService.ts
│   │   ├── workspaceService.ts
│   │   ├── buildService.ts
│   │   ├── packageService.ts
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
│   │   ├── workspace_service.py
│   │   ├── code_generation_service.py
│   │   ├── build_service.py
│   │   ├── package_service.py
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

**Phase 1 — สร้างเสร็จแล้ว (Sprint 0–23):**

1. ✅ Virtual Office Dashboard
2. ✅ Agent List + Agent Status
3. ✅ Agent Movement แบบ simple
4. ✅ Project Creation
5. ✅ Requirement Input + File Upload (text/markdown)
6. ✅ Run SDLC Pipeline (Steps 1–7)
7. ✅ Generate Requirement Summary (Step 1)
8. ✅ Generate Gap Analysis (Step 2)
9. ✅ Generate BA Output — BRD, FSD, User Stories (Step 3)
10. ✅ Generate SA Output — Architecture, DB Design, API Spec (Step 4)
11. ✅ Generate UX Spec — Screen Spec, UX Flows (Step 5)
12. ✅ Developer Agent — Code Task List (Step 6) ← **ต้องอัปเกรดเป็น real code**
13. ✅ Generate QA Test Case (Step 7)
14. ✅ Activity Log + Document Viewer
15. ✅ PostgreSQL + Docker Compose + Celery + Redis
16. ✅ Auth + Admin pages + Pipeline Monitor
17. ✅ RAG + GitHub Integration + MCP
18. ✅ Traceability Matrix
19. ✅ Change Impact, Documentation, PM Agent (files มีแต่ยังไม่ต่อ pipeline)

**Phase 2 — MVP Code Generation Factory (Sprint 24–29):**

20. Per-Agent LLM model selection (แต่ละ agent เลือก model ได้)
21. Developer Agent สร้างไฟล์ code จริง (`.py`, `.tsx`, `.ts`, `.sql`)
22. Generated project เก็บใน `generated_apps/{project_id}/` บน filesystem
23. File Manifest mapping Requirement/User Story → Code File
24. Code Workspace UI — file tree + syntax highlighted viewer
25. Download generated application เป็น ZIP
26. DevOps Agent สร้าง Dockerfile + docker-compose.yml + CI/CD จริง
27. Pipeline Steps 8–10 ครบ (Change Impact → Documentation → PM)
28. GitHub push สำหรับ generated application

## 21.2 MVP Constraints (สิ่งที่ยังทำแบบ simplified ได้)

- Pixel Map ใช้ static background ได้
- Agent Sprite ใช้ placeholder PNG ได้
- Pathfinding ใช้ simple movement ได้
- File Upload รองรับ text/markdown ก่อน (PDF/Word = Phase 3)
- Generated code เป็น scaffold ที่ developer ต้อง refine ต่อ (ไม่ใช่ production-ready 100%)
- Build/run verification ทำแบบ dry-run check (ไม่ต้อง execute จริงในระบบ)

### MVP Minimum Working Application Output

MVP ต้องสามารถสร้างตัวอย่าง Application Output ขั้นต่ำดังนี้

```text
frontend/
  src/pages/{GeneratedPage}.tsx
  src/components/{GeneratedComponent}.tsx
  package.json

backend/
  app/main.py
  app/api/{generated_api}.py
  app/schemas/{generated_schema}.py
  requirements.txt

database/
  migrations/001_initial.sql

tests/
  test_api.py

README.md
.env.example
docker-compose.yml
```


---

# 22. Phase 3 Scope (หลัง Code Generation Factory เสร็จ)

1. A* Pathfinding + Real Tilemap
2. Agent Sprite Sheet Animation
3. File Upload PDF / Word / Audio Transcript
4. Figma / v0 Integration
5. Export PDF / Word
6. Multi Workspace + Multi-tenant
7. Change Request Versioning
8. Test Case Export Excel / UAT Script Export
9. Dashboard Analytics + Cost / Token Usage Tracking
10. Agent Marketplace
11. Advanced RBAC / Permissions
12. Production-grade Security
13. Real-time Multi-user Collaboration
14. LangGraph Orchestration (replaces current DB state machine)
15. Build Runner — execute generated code in sandbox container

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


## 23.1 Additional Acceptance Criteria for Application-Ready MVP

21. User เปิด Code Workspace ได้
22. User เห็น Folder Tree ของ Generated Application ได้
23. Developer Agent สร้างไฟล์ Source Code จริงได้
24. ระบบบันทึก File Manifest ได้
25. ระบบเชื่อม Requirement / User Story ไปยัง Code File ได้
26. User สามารถดู Build Status ได้
27. User สามารถดู Test Result ได้
28. User สามารถ Download Delivery Package เป็น ZIP ได้
29. Delivery Package มี README และ .env.example
30. ระบบแสดงสถานะว่า Application Output พร้อมพัฒนาต่อหรือยัง


---

# 24. Development Roadmap

## Phase 1 — SDLC Document Pipeline (✅ DONE — Sprint 0–23)

| Sprint | Scope | Status |
|---|---|---|
| 0 | Requirement Intake & Baseline | ✅ Done |
| 1 | Agent Contract Design | ✅ Done |
| 2 | Prompt & Template Design | ✅ Done |
| 3 | Database Design | ✅ Done |
| 4 | API Design | ✅ Done |
| 5 | Workflow Design | ✅ Done |
| 6 | Backend Skeleton | ✅ Done |
| 7 | Frontend Skeleton | ✅ Done |
| 8 | Requirement Agent MVP | ✅ Done |
| 9 | Gap Analysis Agent MVP | ✅ Done |
| 10 | BA Agent MVP | ✅ Done |
| 11 | SA Agent MVP | ✅ Done |
| 12 | UX Agent MVP | ✅ Done |
| 13 | Developer Agent MVP (task list) | ✅ Done |
| 14 | QA Agent MVP | ✅ Done |
| 15 | Traceability MVP | ✅ Done |
| 16 | Virtual Office MVP | ✅ Done |
| 17 | RAG MVP | ✅ Done |
| 18 | GitHub Integration MVP | ✅ Done |
| 19 | MCP MVP | ✅ Done |
| 20 | Change Impact Agent MVP | ✅ Done |
| 21 | Documentation Agent MVP | ✅ Done |
| 22 | PM Agent MVP | ✅ Done |
| 23 | Docker + CI/CD | ✅ Done |

---

## Phase 2 — Code Generation Factory (Sprint 24–29)

### Sprint 24 — Per-Agent LLM Selection
**Goal:** แต่ละ agent เลือก Ollama model ของตัวเองได้อิสระ

- เพิ่ม `model_name` override per agent ใน DB + migration
- UI ใน Agent Manager ให้เลือก/แก้ model ต่อ agent
- Backend ส่ง model ที่ถูกต้องเมื่อ agent รัน
- Default model assignment ตาม role:
  - Developer Agent, DevOps Agent → `coder14b:latest`
  - Gap Analysis, BA, SA → `qwen3.5:9b`
  - Change Impact → `deepseek-r1:14b`
  - ที่เหลือ → `qwen3:8b`
- **DoD:** Developer Agent รันด้วย `coder14b:latest` แยกจาก agent อื่น

### Sprint 25 — Developer Agent Rewrite — Code Generation
**Goal:** Developer Agent สร้างไฟล์ code จริง

- Rewrite `dev_agent.py` ให้ generate code แบบ multi-file (หลาย LLM calls)
- Generate backend: SQLAlchemy models → Pydantic schemas → FastAPI routes → Alembic migration
- Generate frontend: TypeScript types → API services → React components → page components
- Generate README.md + .env.example
- Save ไฟล์จริงลง `generated_apps/{project_id}/` บน server filesystem
- สร้าง File Manifest (JSON) หลังทุก generation
- Retry 1 ครั้งถ้า LLM output มี syntax error, flag `needs_review` ถ้ายังผิด
- **DoD:** กด Run Pipeline → มีไฟล์ `.py` และ `.tsx` จริงใน `generated_apps/`

### Sprint 26 — Code Output Viewer + Download
**Goal:** User ดูและดาวน์โหลด generated code ได้

- API: `GET /projects/{id}/code-output` — list file tree
- API: `GET /projects/{id}/code-output/file?path=...` — read file content
- API: `GET /projects/{id}/code-output/download` — ZIP download
- Frontend: "Generated Code" tab ใน Project Workspace
- File tree sidebar + syntax highlighted viewer (main panel)
- Download ZIP button
- **DoD:** User เห็น file tree, อ่าน code ได้, และ download ZIP ได้

### Sprint 27 — DevOps Agent
**Goal:** pipeline สร้าง deployment files จริง

- สร้าง `devops_agent.py` — generate Dockerfile, docker-compose.yml, .github/workflows/ci.yml, nginx.conf
- เพิ่ม step `devops` เข้า pipeline ระหว่าง `dev_tasks` และ `test_cases`
- เพิ่ม Celery task `run_devops_agent`
- Human review gate ก่อน devops step
- **DoD:** pipeline step "devops" generate `docker-compose.yml` และ `ci.yml` ลงใน `generated_apps/`

### Sprint 28 — Pipeline Steps 8–10 Completion
**Goal:** pipeline ครบ 10 ขั้นตอน

- Wire Change Impact Agent (step 8) เข้า `_NEXT_STEP` pipeline
- Wire Documentation Agent (step 9) เข้า pipeline
- Wire PM Agent (step 10) เข้า pipeline
- เพิ่ม Celery tasks สำหรับ step 8–10
- Frontend แสดง step 8–10 ใน pipeline progress
- **DoD:** pipeline รันครบ 10 steps จาก requirement ถึง PM report

### Sprint 29 — GitHub Push of Generated Application
**Goal:** push generated application ขึ้น GitHub repo ใหม่

- GitHub API: create new repo สำหรับ generated app (ใช้ GitHub integration เดิม)
- Push ไฟล์ทั้งหมดจาก `generated_apps/{project_id}/` ขึ้น repo
- แสดง repo URL ใน Project Workspace
- Optional: trigger GitHub Actions CI run หลัง push
- **DoD:** กด "Push to GitHub" → repo ใหม่บน GitHub มี code ทั้งหมด


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

# 31.1 Prompt for Claude Code — Implement Application Workspace

```text
Implement the Application Workspace module.

Requirements:
- Create backend models for application_workspaces, generated_files, file_versions, code_generations, build_runs, test_runs, and delivery_packages
- Create REST APIs for workspace, files, file versions, manifest, build, test, preview, and package
- Create frontend CodeWorkspacePage
- Show folder tree, code viewer, file metadata, traceability mapping, and build log panel
- Allow viewing and editing generated files
- Save file versions when content changes
- Do not delete existing project, agent, task, document, or pipeline features
```

---

# 31.2 Prompt for Claude Code — Implement Real Code Generation

```text
Enhance the Developer Agent so it generates real application source files into the Application Workspace.

The Developer Agent must generate:
- Frontend React TypeScript pages and components
- Backend FastAPI routes, schemas, services, and models
- Database migration files
- Test files
- README.md
- .env.example
- docker-compose.yml when needed

Rules:
- Every file must have a path
- Every file must be saved into generated_files
- Every file must be included in the file manifest
- Every file should map to requirement_id or user_story_id where possible
- Do not only output markdown explanation
- Preserve previous file versions before overwriting
```

---

# 31.3 Prompt for Claude Code — Implement Build, Test, Preview, and Package

```text
Implement Build, Test, Preview, and Delivery Package features.

Requirements:
- Add build runner service
- Add test runner service
- Store build logs and test logs
- Show build/test status in the UI
- Add Preview Application button
- Add package generator that creates a ZIP of the generated workspace
- Include README, .env.example, docker-compose.yml, source code, tests, and traceability matrix in the package
- If build fails, send logs back to Developer Agent for fix suggestions

For MVP, a simulated runner is acceptable if local command execution is not ready, but the data model and UI must be ready for real execution.
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


## 32.1 Clarification

แม้ MVP ยังไม่ต้องทำ Full GitHub commit automation หรือ Production-grade security แต่ MVP ต้องมี Application Workspace และ Generated Source Files จริง เพื่อให้ตรงกับเป้าหมายหลักของระบบที่ต้องการสร้าง Application Output ไม่ใช่เอกสารอย่างเดียว


---

# 33. Per-Agent LLM Model Configuration

## 33.1 Available Models (Ollama — ติดตั้งแล้ว)

| Model | Params | Context | Capability | ขนาด |
|---|---|---|---|---|
| `coder14b:latest` | 14.8B | **128k** | completion + tools | 9.0 GB |
| `qwen2.5-coder:14b-ctx65k` | 14.8B | 65k | completion + tools | 9.0 GB |
| `qwen3.5:9b` | 9.7B | **262k** | completion | 6.6 GB |
| `qwen3:8b` | 8B | 32k | completion | 5.2 GB |
| `deepseek-r1:14b` | 14B | 32k | reasoning | 9.0 GB |
| `qwen2.5:14b` | 14B | 32k | completion | 9.0 GB |

## 33.2 Recommended Model Per Agent

| Agent | Recommended Model | เหตุผล |
|---|---|---|
| Developer Agent | `coder14b:latest` | Code-specific 14.8B + 128k context — รับ spec ทั้งหมดในครั้งเดียว |
| DevOps Agent | `coder14b:latest` | Dockerfile/YAML/CI-CD generation ต้องการ model เข้าใจ infra config |
| Gap Analysis Agent | `qwen3.5:9b` | Context 262k — อ่าน requirement ยาวๆ ได้ครบ |
| BA Agent | `qwen3.5:9b` | Context ใหญ่ — process requirement หลาย source ได้ |
| SA Agent | `qwen3.5:9b` | Architecture reasoning ต้องการ context ใหญ่สำหรับ FSD |
| Change Impact Agent | `deepseek-r1:14b` | Reasoning model — วิเคราะห์ผลกระทบซับซ้อนได้ดี |
| Requirement Agent | `qwen3:8b` | Fast + ใช้งานได้ดีอยู่แล้ว |
| UX Agent | `qwen3:8b` | Screen spec generation |
| QA Agent | `qwen3:8b` | Test case generation |
| Documentation Agent | `qwen3:8b` | Document compilation |
| PM Agent | `qwen3:8b` | Summary — ไม่ต้องการ model ใหญ่ |

## 33.3 Per-Agent Model Override (Sprint 24)

- แต่ละ agent มีฟิลด์ `model_name` ใน DB ที่ override global default ได้
- ถ้า `model_name` ว่างเปล่า → ใช้ global default จาก LLM Settings
- Admin สามารถเปลี่ยน model ต่อ agent ได้จาก Agent Management UI

---

# 34. Risks & Recommendations

## Risk 1: Scope ใหญ่มากเกินไป
Recommendation: ทำ MVP Pipeline + Dashboard ก่อน อย่าเริ่มด้วย Agent เดินซับซ้อน (Phase 1 เสร็จแล้ว)

## Risk 2: UI ไม่สวยถ้าให้ Claude ออกแบบเอง
Recommendation: ใช้ Figma หรือ v0 ทำ UI reference ก่อน แล้วให้ Claude Code เขียนตาม

## Risk 3: Agent Output ไม่สม่ำเสมอ
Recommendation: ใช้ structured output format และ template สำหรับแต่ละ Agent + Pydantic validation

## Risk 4: Local LLM อาจตอบไม่ดีเท่า API
Recommendation: ใช้ `coder14b:latest` สำหรับ code generation (ดีกว่า qwen3:8b มาก), ใช้ OpenAI สำหรับ demo สำคัญ

## Risk 5: Generated Code มี Syntax Error
Recommendation: retry 1 ครั้ง, flag `needs_review`, แสดงให้ user เห็นว่าไฟล์ไหนต้อง review

## Risk 6: Movement ใช้เวลามาก
Recommendation: ทำ simple movement ก่อน แล้วค่อยเพิ่ม A* (Phase 3)

---

# 34. Final Product Vision

ระบบนี้ควรถูกวางตำแหน่งเป็น

```text
AI-SDLC Working Office
An Agentic Software Factory for requirement analysis, solution design, real application code generation, testing, preview, deployment packaging, and change impact analysis.
```

ไม่ใช่แค่ Virtual Office สวย ๆ แต่เป็นเครื่องมือช่วยทีม Software Delivery ทำงานจริงแบบ End-to-End

---

# 35. Final Summary

AI-SDLC Working Office มี **4 คุณค่าหลัก**

1. **Visual Collaboration**
   เห็น Agent เดินและทำงานใน Virtual Office ตาม pipeline ของจริง

2. **SDLC Automation**
   Agent ทำงานครบทุกขั้นตอน: Requirement → Gap → BA → SA → UX → Code → DevOps → QA → Change Impact → PM

3. **Real Code Generation**
   Developer Agent สร้าง source code จริง (`.py`, `.tsx`, `.sql`) ที่ developer นำไปต่อยอดได้ทันที
   DevOps Agent สร้าง Dockerfile, docker-compose.yml, GitHub Actions CI/CD จริง

4. **Traceability & Change Impact**
   เชื่อม Requirement → Design → Code File → Test Case
   วิเคราะห์ผลกระทบเมื่อ Requirement เปลี่ยน

**Phase 1** (เสร็จแล้ว): SDLC Document Pipeline ครบ 7 steps + infra + UI
**Phase 2** (กำลังทำ): Code Generation Factory — Developer Agent สร้าง code จริง, DevOps Agent, Pipeline ครบ 10 steps, GitHub push
**Phase 3** (ภายหลัง): A* Pathfinding, Real Tilemap, PDF/Word upload, Build Runner sandbox, Multi-tenant


---

# 36. Final Requirement Clarification for AI Coding Tools

เมื่อนำเอกสารนี้ไปใช้กับ Claude Code, Cursor, Windsurf, Lovable หรือ Bolt.new ต้องตีความว่าเป้าหมายของระบบคือการสร้าง Web Application จริงที่มี Frontend, Backend, Database, Agent Orchestration, Code Workspace, Build/Test Status และ Delivery Package

AI Coding Tool ห้ามตีความระบบนี้เป็นเพียง Document Generator หรือ Chatbot ที่ผลิต BRD/FSD เท่านั้น

## Required Implementation Priority

1. สร้างระบบ AI-SDLC Working Office ให้รันได้จริง
2. สร้าง Project / Agent / Task / Pipeline / Document / Activity Core ก่อน
3. เพิ่ม Application Workspace และ Generated Files
4. เพิ่ม Developer Agent ที่สร้าง Source Code เป็นไฟล์จริง
5. เพิ่ม Build/Test/Preview/Package Flow
6. เพิ่ม Traceability ไปถึง Code File และ Test Result
7. ค่อยเพิ่ม Animation, RAG, GitHub, MCP และ Advanced Integration ภายหลัง

## Definition of Done

ระบบถือว่าตรงตามความต้องการเมื่อ User สามารถใส่ Requirement แล้วระบบสร้างได้ทั้ง:

- Requirement Artifact
- BA/SA/UX Artifact
- Generated Source Code
- Generated Database/API/UI/Test Files
- Build/Test Status
- Delivery Package
- Traceability ตั้งแต่ Requirement ถึง Code และ Test

```text
The final output must be a real application workspace, not only generated documents.
```


---

# 37. Revised Pipeline Architecture (Phase 3 Standard)

> **Decision Date:** 2026-06-19  
> **Status:** APPROVED — supersedes the 10-step pipeline defined in Section 9  
> **Owner:** Product / Architecture

---

## 37.1 Three-Layer Pipeline Overview

```
BUSINESS LAYER
  [1] Requirement Agent   → docs/requirements.md
  [2] Gap Analysis Agent  → docs/gap_report.md
  [3] BA Agent            → docs/fsd.md + docs/user_stories.md
  GATE: BA Approved → unlock Design Layer

DESIGN LAYER
  [4] SA Agent            → docs/architecture.md + docs/db_schema.md + docs/api_spec.md
  [5] UX Agent            → docs/screen_spec.md + docs/ux_flows.md
  [6] Technical Design Agent → docs/dev_tasks.md
  GATE: Technical Design Approved → unlock Delivery Layer

DELIVERY LAYER
  [7] Developer Agent(s)  → app/** (source code, scalable to N instances)
  [8] Code Review Agent   → docs/code_review.md
  [9] QA Agent            → tests/** + docs/test_report.md
  [10] DevOps Agent       → Dockerfile + docker-compose + build + deploy
  [11] Monitoring Agent   → docs/monitoring_report.md + live metrics

ON-DEMAND
  [12] Change Impact Agent → docs/change_impact.md (triggered on requirement change)
```

---

## 37.2 Agent Contracts

### Agent 1 — Requirement Agent
```
INPUT : raw text / file (txt, md, pdf, docx, audio transcript)
OUTPUT: docs/requirements.md
  Sections: Executive Summary, FR-XXX, NFR-XXX, BR-XXX,
            Assumptions, Out of Scope
GATE  : Human review
NEXT  : Gap Analysis Agent
```

### Agent 2 — Gap Analysis Agent
```
INPUT : docs/requirements.md
OUTPUT: docs/gap_report.md
  Sections: Missing Info (GAP-XXX), Ambiguities, Conflicts,
            Risks, Open Questions (OQ-XXX)
GATE  : Human review
NEXT  : BA Agent
```

### Agent 3 — BA Agent
```
INPUT : docs/requirements.md + docs/gap_report.md
OUTPUT: docs/fsd.md           (Functional Spec + Acceptance Criteria per FR)
        docs/user_stories.md  (US-XXX: As a / I want / So that / AC)
GATE  : Human APPROVE → unlock Design Layer
NEXT  : SA Agent
```

### Agent 4 — SA Agent (Solution Architect)
```
INPUT : docs/fsd.md + docs/user_stories.md + docs/requirements.md
OUTPUT: docs/architecture.md  (tech stack, component diagram, deployment)
        docs/db_schema.md     (tables, columns, types, indexes, FK)
        docs/api_spec.md      (OpenAPI-style endpoints + request/response)
GATE  : Human review
NEXT  : UX Agent
```

### Agent 5 — UX Agent
```
INPUT : docs/fsd.md + docs/user_stories.md + docs/architecture.md
OUTPUT: docs/screen_spec.md   (UI-XXX screens, fields, actions, validation)
        docs/ux_flows.md      (user journey in Mermaid)
GATE  : Human review
NEXT  : Technical Design Agent
```

### Agent 6 — Technical Design Agent (NEW)
```
INPUT : docs/fsd.md + docs/architecture.md + docs/db_schema.md
        docs/api_spec.md + docs/screen_spec.md
OUTPUT: docs/dev_tasks.md
  Format per task:
    TASK-XXX | domain(backend|frontend|db|test) | file_path |
    description | depends_on | FR-ref | estimated_lines
GATE  : Human APPROVE → unlock Delivery Layer
NEXT  : Developer Agent(s)
SCALING NOTE: task count determines how many Developer Agent instances to spawn
```

### Agent 7 — Developer Agent (Scalable to N instances)
```
INPUT : docs/dev_tasks.md (task slice)
        docs/architecture.md + docs/db_schema.md
        docs/api_spec.md + docs/screen_spec.md
OUTPUT: app/backend/**       (FastAPI routes, models, services)
        app/frontend/**      (React pages, components, hooks)
        app/db/migrations/** (Alembic migration files)

SCALING RULES:
  <= 30 files : 1 Developer Agent instance
  31-80 files : 2 instances (backend-agent + frontend-agent)
  > 80 files  : 3 instances (backend + frontend + db/infra)
  Each instance writes to its own domain slice
  Code Review Agent waits for ALL instances to complete

GATE  : All instances done
NEXT  : Code Review Agent
```

### Agent 8 — Code Review Agent (NEW)
```
INPUT : app/**  (all generated source files)
        docs/api_spec.md + docs/db_schema.md
OUTPUT: docs/code_review.md
  Sections: Security Issues (CRIT/HIGH/MED/LOW), Logic Errors,
            API Contract Violations, DB Schema Violations,
            Missing Error Handling, Recommendations
GATE  : CRIT/HIGH issues block → must fix before QA
        MED/LOW → human can approve and proceed
NEXT  : QA Agent
```

### Agent 9 — QA Agent (Generate + Run)
```
INPUT : app/**  (source code)
        docs/api_spec.md + docs/screen_spec.md + docs/user_stories.md
OUTPUT (files):
  tests/unit/test_*.py          (pytest unit tests per module)
  tests/api/test_api_*.py       (httpx integration tests per endpoint)
  tests/e2e/test_*.spec.ts      (Playwright UI tests per screen)
  docs/test_report.md           (pass/fail summary + coverage)

EXECUTION:
  - Run pytest inside Docker container against running app
  - Run Playwright against deployed frontend
  - Capture exit code + stdout/stderr
  - Write test_report.md

GATE  : All tests pass → auto-proceed
        Failures → human can override or request fix
NEXT  : DevOps Agent
```

### Agent 10 — DevOps Agent (Build + Deploy + Rollback)
```
INPUT : docs/architecture.md + app/**
OUTPUT (files):
  Dockerfile.backend
  Dockerfile.frontend
  docker-compose.yml        (local dev)
  docker-compose.prod.yml   (production)
  nginx.conf
  .env.example
  .github/workflows/ci.yml
  .github/workflows/deploy.yml

ACTIONS:
  1. Build Docker images (docker build)
  2. Run docker-compose up
  3. Health check: GET /health → 200
  4. On failure: docker-compose down, rollback to previous image
  5. Write docs/build_report.md

GATE  : Health check pass → auto-proceed to Monitoring
NEXT  : Monitoring Agent
```

### Agent 11 — Monitoring Agent (NEW)
```
INPUT : Running containers (Docker API)
        docs/api_spec.md (for endpoint health checks)
OUTPUT: docs/monitoring_report.md  (initial report after deploy)
        Live metrics: response time, error rate, CPU/memory
        Alerts: 5xx spike, container restart, OOM

POLLING: every 30s for first 10 minutes post-deploy
TRIGGER: also callable on-demand at any time
```

### Agent 12 — Change Impact Agent (On-demand only)
```
TRIGGER: User changes/adds requirement after pipeline completes
INPUT : Original docs/requirements.md + new requirement text
        All existing docs + app/** code
OUTPUT: docs/change_impact.md
  Sections: Changed Requirements, Affected Documents,
            Affected Code Files, Affected Tests,
            Estimated Re-work, Recommended Action

HANDOFF: None — user decides which layer to re-run from
```

---

## 37.3 Approval Gates

| Gate | After | Condition | Effect |
|------|-------|-----------|--------|
| BA Approved | Agent 3 | Human approves FSD | Unlocks Design Layer |
| Technical Design Approved | Agent 6 | Human approves dev_tasks.md | Unlocks Delivery Layer |
| Code Review | Agent 8 | No CRIT/HIGH issues | Unlocks QA |
| QA Pass | Agent 9 | All tests pass (or override) | Unlocks DevOps |
| Deploy Health | Agent 10 | /health returns 200 | Unlocks Monitoring |

---

## 37.4 Output File Structure Per Project

```
{workspace}/{project_name}/
├── docs/
│   ├── requirements.md       [Agent 1]
│   ├── gap_report.md         [Agent 2]
│   ├── fsd.md                [Agent 3]
│   ├── user_stories.md       [Agent 3]
│   ├── architecture.md       [Agent 4]
│   ├── db_schema.md          [Agent 4]
│   ├── api_spec.md           [Agent 4]
│   ├── screen_spec.md        [Agent 5]
│   ├── ux_flows.md           [Agent 5]
│   ├── dev_tasks.md          [Agent 6]
│   ├── code_review.md        [Agent 8]
│   ├── test_report.md        [Agent 9]
│   ├── build_report.md       [Agent 10]
│   ├── monitoring_report.md  [Agent 11]
│   └── change_impact.md      [Agent 12, on-demand]
├── app/
│   ├── backend/              [Agent 7]
│   ├── frontend/             [Agent 7]
│   └── db/migrations/        [Agent 7]
└── tests/
    ├── unit/                 [Agent 9]
    ├── api/                  [Agent 9]
    └── e2e/                  [Agent 9]
```

---

## 37.5 Multi-Developer Agent Fan-out

Technical Design Agent tags each task with a domain:

```markdown
## TASK-001 | backend  | app/backend/routes/auth.py       | FR-001
## TASK-015 | frontend | app/frontend/src/pages/Login.tsx  | FR-001
## TASK-030 | database | app/db/migrations/0001_users.py   | FR-002
```

Pipeline spawns N instances based on task count:
- <= 30 tasks: 1 instance (developer-agent-1)
- 31-80 tasks: 2 instances (developer-agent-1: backend, developer-agent-2: frontend)
- > 80 tasks:  3 instances (+ developer-agent-3: database/infra)

Agent rows in DB: developer-agent-1, developer-agent-2, developer-agent-3
Created on-demand via migration if not exists.

---

## 37.6 Phase 3 Sprint Plan

| Sprint | Title | Scope |
|--------|-------|-------|
| 30 | Pipeline Rewire | 3-layer chain, gate logic, pipeline.py + tasks.py |
| 31 | Agent File Output | All agents write docs to workspace filesystem |
| 32 | Technical Design Agent | NEW agent — gen dev_tasks.md |
| 33 | Code Review Agent | NEW agent — static + LLM review of generated code |
| 34 | QA Agent Rewrite | Generate test files (.py/.spec.ts) + run + report |
| 35 | DevOps Agent — Build+Deploy | docker build + compose up + health check + rollback |
| 36 | Monitoring Agent | NEW agent — Docker API + endpoint polling |
| 37 | Multi-Developer Agent | Fan-out Celery tasks, N instances, work distribution |
| 38 | Agent Contract Refactor | SA/UX/Dev read FSD directly (remove stale BA dependency) |
| 39 | Change Impact On-demand | UI trigger, re-run from affected layer |


---

# 38. Agent Skill Document (skill.md)

> **Decision Date:** 2026-06-19
> **Status:** APPROVED — prerequisite before Sprint 30
> **Scope:** Agent Manager UI + Backend agents table

---

## 38.1 Concept

Each agent owns a **Skill Document** (`skill.md`) that describes:
- Role and responsibilities
- Capabilities and limitations
- Input contract (what it needs)
- Output contract (what it produces)
- Prompting style / behaviour notes
- Example use cases

The Skill Document serves two purposes:
1. **Human-readable reference** — team members understand what each agent does
2. **LLM context injection** — agent uses its own skill.md as part of the system prompt

---

## 38.2 Storage

| Option | Decision |
|--------|----------|
| DB field `skill_markdown` in `agents` table | ✅ Primary storage (editable via API) |
| File `{workspace}/agents/{agent-name}/skill.md` | Optional export only |

Storing in DB allows the Agent Manager UI to fetch, display, and edit without filesystem access.

---

## 38.3 Skill Document Structure

```markdown
# {Agent Name} — Skill Document

## Role
{one-paragraph description of what this agent does in the pipeline}

## Layer
{Business | Design | Delivery | On-demand}

## Pipeline Position
Step {N} of 12

## Capabilities
- {capability 1}
- {capability 2}
...

## Input Contract
| Field | Source | Required |
|-------|--------|----------|
| {field} | {previous agent / user} | Yes/No |

## Output Contract
| File | Description |
|------|-------------|
| {filename} | {description} |

## Behaviour Notes
- {prompting style note}
- {known limitation}
- {LLM model preference}

## Example
**Input:** {brief example input}
**Output:** {brief example output excerpt}
```

---

## 38.4 DB Schema Change

Add column to `agents` table:

```sql
ALTER TABLE agents ADD COLUMN skill_markdown TEXT;
```

Migration: `0011_agent_skill_markdown.py`

Default value: auto-generated skill.md content per agent role (seeded in migration).

---

## 38.5 API Changes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agents/{agent_id}` | Already returns agent — add `skill_markdown` field |
| PATCH | `/agents/{agent_id}` | Already exists — accept `skill_markdown` in body |

No new endpoints needed — extend existing ones.

---

## 38.6 Agent Manager UI Changes

### Current AgentDetailPanel shows:
- Name, Role, Status, Model, Zone

### After this feature:
- All existing fields
- **Skill Document tab** — rendered markdown view of skill.md
- **Edit button** — switches to raw textarea editor
- **Save button** — calls PATCH /agents/{id} with updated skill_markdown
- **Reset button** — restore to default skill content

### UI Layout:

```
┌─────────────────────────────────────────────────┐
│  developer-agent                    [Edit] [✕]  │
│  Role: developer | Status: Idle                 │
│  Model: coder14b:latest | Zone: developer_zone  │
├─────────────────────────────────────────────────┤
│  [Info]  [Skill Document]                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  # Developer Agent — Skill Document             │
│  ## Role                                        │
│  Generates real source code files from ...      │
│  ## Capabilities                                │
│  - Python/FastAPI backend generation            │
│  - React/TypeScript frontend generation         │
│  ...                                            │
│                                [Edit Skill]     │
└─────────────────────────────────────────────────┘
```

---

## 38.7 Default Skill Content Per Agent

| Agent | Model | Layer |
|-------|-------|-------|
| requirement-agent | qwen3:8b | Business |
| gap-analysis-agent | qwen3.5:9b | Business |
| ba-agent | qwen3.5:9b | Business |
| architect-agent | qwen3.5:9b | Design |
| ux-agent | qwen3:8b | Design |
| technical-design-agent | qwen3.5:9b | Design |
| developer-agent | coder14b:latest | Delivery |
| code-review-agent | deepseek-r1:14b | Delivery |
| qa-agent | qwen3:8b | Delivery |
| devops-agent | coder14b:latest | Delivery |
| monitoring-agent | qwen3:8b | Delivery |
| change-impact-agent | deepseek-r1:14b | On-demand |

---

## 38.8 Implementation Sprints

| Sprint | Scope |
|--------|-------|
| 30-pre | Add `skill_markdown` column (migration 0011) |
| 30-pre | Seed default skill.md content for all 12 agents |
| 30-pre | Update AgentResponse schema + PATCH endpoint |
| 30-pre | Update AgentDetailPanel — show + edit skill.md |

This sprint must complete before Sprint 30 (Pipeline Rewire) begins.
