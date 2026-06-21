# AI-SDLC Virtual Office — CR Requirement Specification

**Document Type:** Change Request / Requirement Specification  
**Version:** 1.0  
**Project:** AI Agent Office / AI-SDLC Virtual Office  
**Scope:** ปรับปรุง UI, Menu, Project Setting, AI Model Setting และ Tech Stack Configuration  
**Target Users:** Project Owner, BA, SA, UX, Developer, QA, DevOps, AI Agent Admin  

---

## 1. Objective

ต้องการปรับระบบ AI Agent Office ให้มีประสบการณ์ใช้งานแบบ **Virtual Office 2D Pixel** ที่ดูมีชีวิตมากขึ้น และรองรับการกำหนดค่าระบบสำหรับการพัฒนา Application จริง เช่น การเลือก Tech Stack, Database, Application Type และ LLM Model ต่อ Agent ได้อย่างชัดเจน

เป้าหมายหลักของ CR นี้คือ:

1. ปรับ UI จาก Dashboard ธรรมดาให้เป็น Virtual Office แบบ 2D Pixel
2. ให้ Agent มีพฤติกรรมเหมือนพนักงานใน Office เช่น เดินไปมา, นั่งพัก, กดตู้น้ำ, กลับมาทำงานที่โต๊ะ
3. เพิ่ม Status Light หรือ Visual Status เพื่อดูสถานะการทำงานของ Agent ได้ง่าย
4. เพิ่ม Project Configuration สำหรับเลือก Tech Stack และ Application Type
5. ปรับเมนู AI Model Settings ให้ใช้งานง่ายขึ้น โดยแยก Tab ชัดเจน
6. ปรับเมนูด้านซ้ายให้สอดคล้องกับ Workflow จริง
7. ทบทวนเมนู Code Workspace ว่าควรแยกจาก Project อย่างไร

---

## 2. Change Request Summary

| CR No. | Area | Requirement | Priority |
|---|---|---|---|
| CR-001 | Virtual Office UI | ทำ UI เป็น 2D Pixel Office ที่ Agent เดินไปมาได้ | High |
| CR-002 | Agent Behavior | Agent เดินเล่น นั่งพัก กดตู้น้ำ และกลับโต๊ะเมื่อมีงาน | High |
| CR-003 | Agent Status | มีไฟ Status แสดงสถานะของ Agent | High |
| CR-004 | Tech Stack Setting | เลือก Frontend, Backend, Database และ Application Type ได้ | High |
| CR-005 | LLM Model Setting | เพิ่ม Claude และ OpenAI GPT Model ให้เลือกได้ | High |
| CR-006 | AI Model Settings Menu | แยก Tab: Available Ollama Model และ Per-Agent Model | High |
| CR-007 | Left Menu | เอา Requirement ออกจากเมนูหลักด้านซ้าย | Medium |
| CR-008 | Code Workspace | ปรับนิยามและหน้าที่ของ Code Workspace ไม่ให้ซ้ำกับ Project | Medium |

---

## 3. Functional Requirements

---

# FR-001: Virtual Office 2D Pixel UI

## Description

ระบบต้องมีหน้า Virtual Office แบบ **2D Pixel Art** เป็นหน้าหลักของการมองเห็น Agent ทั้งหมด โดยให้ Agent แต่ละตัวอยู่ในพื้นที่ Office และสามารถเคลื่อนไหวได้

## Requirement Details

1. แสดงพื้นที่ Office แบบ 2D Pixel เช่น:
   - โต๊ะทำงานของ Agent
   - โซนพักผ่อน
   - ตู้น้ำ / Coffee Station
   - Meeting Area
   - Board / Monitor สำหรับแสดง Pipeline Status
   - Gateway หรือ Door สำหรับแสดงการเข้าออกของ Agent

2. Agent ต้องมี Sprite หรือ Character แบบ 2D Pixel

3. Agent สามารถเดินไปมาในพื้นที่ Office ได้

4. Agent แต่ละตัวต้องมีตำแหน่งประจำ เช่น Desk หรือ Workstation

5. ผู้ใช้สามารถคลิก Agent เพื่อดูรายละเอียดได้ เช่น:
   - Agent Name
   - Agent Role
   - Current Task
   - Current Status
   - Assigned Project
   - Current Model ที่ใช้งาน
   - Last Activity

## Acceptance Criteria

- ผู้ใช้เห็น Virtual Office เป็นหน้าหลักได้
- Agent แสดงเป็นตัวละคร Pixel แยกตาม Role ได้
- Agent มีตำแหน่งใน Office ไม่ทับกัน
- คลิก Agent แล้วเห็นข้อมูลสถานะได้
- UI ต้องใช้งานได้บน Web Browser

---

# FR-002: Agent Idle Behavior

## Description

เมื่อ Agent ไม่มีงาน ให้มีพฤติกรรมแบบ Idle เพื่อให้ระบบดูมีชีวิต ไม่เหมือน Dashboard นิ่ง ๆ

## Requirement Details

เมื่อ Agent อยู่ในสถานะว่าง ระบบสามารถสุ่มพฤติกรรมได้ เช่น:

1. เดินไปมาในพื้นที่ Office
2. เดินไปนั่งที่โซนพักผ่อน
3. เดินไปกดตู้น้ำ / Coffee Station
4. ยืนคุยกับ Agent ตัวอื่นแบบ Idle Animation
5. กลับมานั่งที่โต๊ะเมื่อครบเวลา Idle

## Agent Idle States

| State | Description |
|---|---|
| IdleAtDesk | ว่างและนั่งอยู่ที่โต๊ะ |
| Walking | เดินไปมาใน Office |
| BreakArea | อยู่ในโซนพักผ่อน |
| WaterStation | ไปกดตู้น้ำ |
| Chatting | ยืนคุยกับ Agent อื่น |
| ReturningToDesk | กำลังเดินกลับโต๊ะ |

## Acceptance Criteria

- Agent ที่ไม่มีงานสามารถเปลี่ยนพฤติกรรม Idle ได้
- Animation ไม่รบกวนการทำงานหลักของระบบ
- เมื่อมี Task ใหม่ Agent ต้องหยุด Idle และกลับไปทำงาน
- สถานะ Idle ต้องแสดงใน Agent Detail Panel ได้

---

# FR-003: Agent Work Behavior

## Description

เมื่อถึงเวลาทำงาน หรือมี Task ถูก Assign ให้ Agent ต้องกลับมาที่โต๊ะและเปลี่ยนสถานะเป็น Working

## Requirement Details

1. เมื่อมี Task ใหม่ Agent ต้องเดินกลับมาที่โต๊ะ
2. Agent เปลี่ยนสถานะเป็น Working
3. แสดง Visual Effect ว่ากำลังทำงาน เช่น:
   - ไฟบนโต๊ะติด
   - Status Light เปลี่ยนสี
   - มี Loading / Thinking Bubble
   - มีข้อความ Current Task

4. เมื่อ Task เสร็จ Agent เปลี่ยนเป็น Completed หรือ Idle

5. หาก Task Error ให้ Agent แสดงสถานะ Error

## Work States

| State | Description |
|---|---|
| Assigned | ได้รับงานแล้ว |
| ReturningToDesk | กำลังกลับโต๊ะ |
| Working | กำลังทำงาน |
| WaitingInput | รอข้อมูลจาก User หรือ Agent อื่น |
| Completed | งานเสร็จแล้ว |
| Error | เกิดข้อผิดพลาด |

## Acceptance Criteria

- Agent กลับโต๊ะเมื่อมีงานใหม่
- Agent Status เปลี่ยนตาม Task Lifecycle
- ผู้ใช้เห็นได้ทันทีว่า Agent ไหนกำลังทำงาน
- Agent ที่ Error ต้องมองเห็นชัดเจน

---

# FR-004: Agent Status Light

## Description

ต้องมีไฟสถานะของ Agent เพื่อให้ผู้ใช้ดูภาพรวมได้ง่ายโดยไม่ต้องอ่านข้อความเยอะ

## Requirement Details

Agent แต่ละตัวต้องมี Status Light หรือ Status Indicator บนโต๊ะ / เหนือตัว Agent / Panel ด้านข้าง

## Recommended Status Colors

| Status | Color | Meaning |
|---|---|---|
| Idle | Gray | ว่าง ไม่มีงาน |
| Ready | Blue | พร้อมรับงาน |
| Working | Green | กำลังทำงาน |
| WaitingInput | Yellow | รอข้อมูล / รออนุมัติ |
| Reviewing | Purple | กำลังตรวจสอบ |
| Completed | Cyan | งานเสร็จ |
| Error | Red | มีปัญหา |
| Offline | Dark Gray | ไม่พร้อมใช้งาน |

## Acceptance Criteria

- Agent ทุกตัวมี Status Light
- สีต้องสอดคล้องกับสถานะจริง
- เมื่อ Task Status เปลี่ยน สีต้องเปลี่ยนตาม
- ผู้ใช้สามารถเข้าใจสถานะโดยไม่ต้องเปิด Detail ได้

---

# FR-005: Project Tech Stack Configuration

## Description

เมื่อสร้าง Project หรือแก้ไข Project ต้องสามารถเลือก Tech Stack ที่ต้องการใช้สำหรับการ Generate Application ได้

## Requirement Details

ในหน้า Create Project / Project Settings ต้องมี Section: **Tech Stack Configuration**

### 5.1 Frontend Technology

ให้เลือกได้อย่างน้อย:

- React
- ASPX
- ASP.NET Web Forms
- ASP.NET MVC / Razor
- Other / Custom

### 5.2 Backend Technology

ให้เลือกได้อย่างน้อย:

- Node.js
- .NET / ASP.NET Core
- ASP.NET Framework
- Other / Custom

### 5.3 Database

ให้เลือกได้อย่างน้อย:

- PostgreSQL
- Microsoft SQL Server
- MySQL

### 5.4 Application Type

ให้เลือกได้อย่างน้อย:

- Web App
- Mobile App
- Web + Mobile App

### 5.5 Optional Deployment Target

แนะนำให้เพิ่มในอนาคต:

- Docker
- Kubernetes
- IIS
- Windows Server
- Linux Server
- Cloud Deployment
- On-Premise Deployment

## Acceptance Criteria

- User เลือก Tech Stack ได้ตอนสร้าง Project
- ค่า Tech Stack ถูกบันทึกใน Project Profile
- Agent ทุกตัวสามารถอ่านค่า Tech Stack นี้เพื่อใช้ Generate เอกสาร / Code / Test Case ได้
- Developer Agent ต้องใช้ Tech Stack ที่เลือกเป็นเงื่อนไขหลักในการ Generate Code

---

# FR-006: LLM Model Provider Configuration

## Description

ระบบต้องรองรับการเลือก LLM Model จากหลาย Provider เพื่อให้กำหนดได้ว่า Agent แต่ละตัวใช้ Model อะไร

## Requirement Details

ต้องเพิ่ม Model Provider ดังนี้:

### 6.1 Claude Models

- Claude Sonnet
- Claude Haiku
- Claude Opus

### 6.2 OpenAI ChatGPT Models

- GPT-5.3
- GPT-5.4
- GPT-5.5

### 6.3 Ollama Models

- แสดง Model ที่ติดตั้งอยู่ใน Ollama Local
- สามารถ Refresh รายชื่อ Model ได้
- แสดงสถานะว่า Model พร้อมใช้งานหรือไม่

> Note: ชื่อ Model จริงควรทำเป็น Configurable Dropdown เพราะชื่อ Version อาจเปลี่ยนในอนาคต

## Acceptance Criteria

- Admin สามารถเลือก Provider ได้
- Admin สามารถเลือก Model ได้
- Agent แต่ละตัวสามารถใช้ Model ต่างกันได้
- ระบบต้องรองรับการเพิ่ม Model ใหม่ในอนาคตโดยไม่ต้องแก้โค้ดเยอะ

---

# FR-007: AI Model Settings Menu Redesign

## Description

เมนู **AI Model Settings** เดิมต้องปรับให้ใช้งานง่ายขึ้น โดยแยกเป็น Tab ชัดเจน

## Required Tabs

### Tab 1: Available Ollama Model

ใช้สำหรับจัดการ Model ที่มาจาก Local Ollama

ข้อมูลที่ควรแสดง:

| Field | Description |
|---|---|
| Model Name | ชื่อ Model |
| Size | ขนาด Model |
| Status | Ready / Not Ready |
| Last Checked | เวลาที่ตรวจสอบล่าสุด |
| Action | Refresh / Test / Remove from List |

Functions:

- Refresh Ollama Models
- Test Model Connection
- View Model Detail
- Set Default Local Model

### Tab 2: Per-Agent Model

ใช้สำหรับกำหนด Model ให้ Agent แต่ละตัว

ข้อมูลที่ควรแสดง:

| Field | Description |
|---|---|
| Agent Name | ชื่อ Agent |
| Agent Role | Role เช่น BA, SA, Dev, QA |
| Provider | Ollama / Claude / OpenAI |
| Model | Model ที่เลือก |
| Temperature | ค่าความสร้างสรรค์ |
| Max Token | จำนวน Token สูงสุด |
| Fallback Model | Model สำรอง |
| Status | ใช้งานได้ / มีปัญหา |

Functions:

- Assign Model per Agent
- Set Fallback Model
- Test Prompt
- Save Configuration
- Reset to Default

## Acceptance Criteria

- AI Model Settings ต้องมีอย่างน้อย 2 Tab
- Available Ollama Model ใช้ดู Model Local เท่านั้น
- Per-Agent Model ใช้กำหนด Model ให้ Agent แต่ละตัว
- ต้องไม่ปนกันระหว่าง Model Inventory กับ Agent Assignment

---

# FR-008: Left Menu Adjustment

## Description

ต้องปรับเมนูด้านซ้ายให้สอดคล้องกับ Flow การใช้งานจริง โดยเอา **Requirement** ออกจากเมนูหลัก เพราะ Requirement ควรอยู่ภายใน Project หลังจากสร้าง Project แล้ว

## Current Issue

เมนู Requirement อยู่ระดับเดียวกับ Project ทำให้ผู้ใช้สับสนว่า Requirement เป็น Global Menu หรือเป็นข้อมูลของ Project

## Required Change

ให้เอาเมนู **Requirement** ออกจาก Left Menu หลัก

Requirement ควรอยู่ใน Project Detail เช่น:

- Project Overview
- Requirement
- Gap Analysis
- BA Documents
- Solution Design
- UX/UI Spec
- Code Workspace
- QA Test Case
- Deployment
- Change Impact

## Recommended Left Menu

| Menu | Purpose |
|---|---|
| Dashboard | ภาพรวมระบบทั้งหมด |
| Virtual Office | หน้าหลัก 2D Pixel Agent Office |
| Projects | รายการ Project ทั้งหมด |
| Agent Management | จัดการ Agent และ Role |
| Pipeline | ดู Workflow การทำงานของ Agent |
| AI Model Settings | ตั้งค่า Model และ Per-Agent Model |
| Knowledge Base / RAG | จัดการเอกสารอ้างอิง |
| Integrations | ตั้งค่า GitHub, Figma, Jira, API, MCP |
| Settings | System Settings |

## Acceptance Criteria

- เมนู Requirement ไม่อยู่ใน Left Menu หลัก
- Requirement ต้องเข้าได้จาก Project Detail
- ผู้ใช้เข้าใจว่า Requirement เป็นส่วนหนึ่งของ Project Lifecycle

---

# FR-009: Code Workspace Redefinition

## Description

เมนู **Code Workspace** ปัจจุบันดูเหมือนซ้ำกับ Project จึงต้องปรับนิยามให้ชัดเจนว่าใช้ทำอะไร

## Current Issue

Code Workspace ปัจจุบันอาจดูเหมือนเป็นหน้า Project อีกหน้า ทำให้ผู้ใช้สับสน

## Recommended Definition

**Code Workspace คือพื้นที่สำหรับดูและจัดการผลลัพธ์ที่ Developer Agent สร้างขึ้นจาก Project นั้น ๆ** ไม่ใช่เมนูบริหาร Project

Code Workspace ควรอยู่ภายใน Project Detail ไม่ควรเป็น Global Menu หลัก ยกเว้นต้องการทำเป็นหน้ารวม Workspace ทุก Project

## Code Workspace Should Include

1. Generated Code Files
2. Folder Structure
3. Backend Code
4. Frontend Code
5. Database Script
6. API Spec
7. Environment File Template
8. Dockerfile / Compose File
9. Build Log
10. Test Result
11. Git Commit History
12. Pull Request Status
13. Deployment Package

## Recommended Layout

### Inside Project Detail

```
Project Detail
 ├─ Overview
 ├─ Requirement
 ├─ Gap Analysis
 ├─ BA / User Story
 ├─ Solution Design
 ├─ UX/UI Spec
 ├─ Code Workspace
 ├─ QA / Test Case
 ├─ Deployment
 └─ Change Impact
```

### Code Workspace Tabs

| Tab | Description |
|---|---|
| Files | โครงสร้างไฟล์ที่ Generate |
| Preview | Preview Web App / UI |
| API | API Endpoint ที่ Generate |
| Database | Table, ERD, Script |
| Build & Test | Build Log และ Test Result |
| Git | Commit, Branch, Pull Request |
| Deployment | Package, Docker, Release Note |

## Acceptance Criteria

- Code Workspace ต้องไม่ซ้ำกับ Project List
- Code Workspace ต้องอยู่ใน Project Detail
- มีความชัดเจนว่าเป็นพื้นที่ดู Code Artifact
- Developer Agent ต้องส่ง Output มาที่ Code Workspace

---

## 4. Recommended Additional Requirements

จาก Requirement ที่ให้มา แนะนำเพิ่มสิ่งต่อไปนี้เพื่อให้ระบบพร้อมใช้งานจริงมากขึ้น

---

# ADD-001: Agent Role & Desk Mapping

Agent แต่ละตัวควรมีโต๊ะหรือพื้นที่ประจำตาม Role เช่น:

| Agent | Desk Zone |
|---|---|
| Requirement Agent | Intake Desk |
| Gap Analysis Agent | Review Desk |
| BA Agent | Document Desk |
| SA Agent | Architecture Desk |
| UX Agent | Design Desk |
| Developer Agent | Code Desk |
| QA Agent | Test Desk |
| DevOps Agent | Deployment Desk |
| Change Impact Agent | Impact Desk |
| PM Agent | Control Desk |

เหตุผล: ทำให้ Virtual Office ดูเข้าใจง่าย และ User รู้ว่า Agent แต่ละตัวทำงานตรงไหน

---

# ADD-002: Work Queue Board

ควรมี Board กลางใน Virtual Office สำหรับแสดง Queue งาน เช่น:

- Backlog
- In Progress
- Waiting User
- Review
- Completed
- Error

เหตุผล: ผู้ใช้เห็นภาพรวม Pipeline โดยไม่ต้องเข้าเมนูลึก

---

# ADD-003: Agent Activity Timeline

เมื่อคลิก Agent ควรเห็น Timeline ล่าสุด เช่น:

- รับ Requirement แล้ว
- ตรวจ Gap แล้ว
- Generate User Story แล้ว
- ส่งต่อ SA Agent แล้ว
- รอ User Approve

เหตุผล: ช่วย Trace งานของ Agent และตรวจสอบย้อนหลังได้

---

# ADD-004: Project Lifecycle Stage

Project ควรมี Stage ชัดเจน เช่น:

1. Requirement Intake
2. Gap Analysis
3. BA / User Story
4. Solution Design
5. UX/UI Design
6. Technical Design
7. Code Generation
8. QA Generation
9. Deployment Package
10. Change Impact

เหตุผล: ทำให้ระบบ AI-SDLC เป็น Workflow จริง ไม่ใช่แค่ Agent Chat

---

# ADD-005: Approval Gate

แต่ละ Stage ควรมีจุด Approve เช่น:

- Approve Requirement ก่อนส่ง BA
- Approve User Story ก่อนส่ง SA
- Approve Solution Design ก่อนให้ Dev Generate Code
- Approve UX ก่อนเริ่ม Frontend
- Approve Test Case ก่อน UAT

เหตุผล: ลด Gap ระหว่าง User กับ AI Agent และป้องกัน Generate Code ผิดจาก Requirement

---

# ADD-006: Project Template

ควรมี Template ให้เลือกตอนสร้าง Project เช่น:

- Internal Web App
- Workflow App
- Mobile App
- CRUD Application
- Approval System
- Reporting Dashboard
- AI Chatbot / RAG App

เหตุผล: ช่วยให้ Agent รู้โครงสร้างพื้นฐานตั้งแต่ต้น

---

# ADD-007: Tech Stack Preset

นอกจากเลือกทีละ Field ควรมี Preset เช่น:

| Preset | Frontend | Backend | Database |
|---|---|---|---|
| Modern Web App | React | Node.js | PostgreSQL |
| Enterprise .NET | ASP.NET Core | .NET | MS SQL Server |
| Legacy ASP.NET | ASPX / Web Forms | ASP.NET Framework | MS SQL Server |
| Open Source Stack | React | Node.js | MySQL / PostgreSQL |

เหตุผล: ผู้ใช้เลือกง่ายขึ้น และลดการเลือกผิดชุด

---

# ADD-008: Model Fallback & Cost Control

ควรมีการตั้งค่า Fallback Model และ Cost Control เช่น:

- Primary Model
- Fallback Model
- Local Model First
- Cloud Model Only
- Max Token per Request
- Daily Budget Limit
- Agent Usage Log

เหตุผล: ควบคุมค่าใช้จ่ายและลดปัญหาเมื่อ Model บางตัวใช้งานไม่ได้

---

# ADD-009: Integration Setting

ควรมีเมนู Integrations สำหรับเชื่อมต่อ Tool ที่ใช้ใน SDLC เช่น:

- GitHub / GitLab
- Figma
- Jira / Azure DevOps
- Slack / Teams
- MCP Server
- RAG / Vector DB
- CI/CD Pipeline

เหตุผล: ระบบ Agent Office ต้องเชื่อมกับเครื่องมือจริงเพื่อให้ทำงานครบ Lifecycle

---

# ADD-010: Audit Log & Traceability

ทุกการทำงานของ Agent ควรมี Log เช่น:

- ใครสั่งงาน
- Agent ไหนทำงาน
- ใช้ Model อะไร
- Prompt คืออะไร
- Output คืออะไร
- ส่งต่อให้ Agent ไหน
- User Approve หรือ Reject เมื่อไหร่

เหตุผล: สำคัญมากสำหรับระบบที่ใช้ในงานจริง โดยเฉพาะ Enterprise

---

## 5. Data Model Recommendation

ควรมี Entity หลักดังนี้

### 5.1 Project

| Field | Description |
|---|---|
| project_id | รหัส Project |
| project_name | ชื่อ Project |
| description | รายละเอียด |
| application_type | Web App / Mobile App |
| frontend_stack | React / ASPX / etc. |
| backend_stack | Node.js / .NET / etc. |
| database_stack | PostgreSQL / MS SQL / MySQL |
| project_stage | Stage ปัจจุบัน |
| status | Active / Completed / On Hold |
| created_by | ผู้สร้าง |
| created_at | วันที่สร้าง |

### 5.2 Agent

| Field | Description |
|---|---|
| agent_id | รหัส Agent |
| agent_name | ชื่อ Agent |
| role | Role ของ Agent |
| status | Idle / Working / Error |
| desk_position | ตำแหน่งโต๊ะ |
| current_position | ตำแหน่งปัจจุบันใน Office |
| assigned_model_id | Model ที่ใช้ |
| current_task_id | งานที่กำลังทำ |

### 5.3 AI Model

| Field | Description |
|---|---|
| model_id | รหัส Model |
| provider | Ollama / Claude / OpenAI |
| model_name | ชื่อ Model |
| model_type | Local / Cloud |
| status | Ready / Disabled / Error |
| max_token | Max Token |
| cost_profile | Cost Setting |

### 5.4 Agent Task

| Field | Description |
|---|---|
| task_id | รหัส Task |
| project_id | Project ที่เกี่ยวข้อง |
| agent_id | Agent ที่รับผิดชอบ |
| task_type | Requirement / BA / SA / Dev / QA |
| status | Queue / Working / Waiting / Completed / Error |
| input_artifact | Input |
| output_artifact | Output |
| started_at | เวลาเริ่ม |
| completed_at | เวลาจบ |

### 5.5 Artifact

| Field | Description |
|---|---|
| artifact_id | รหัส Artifact |
| project_id | Project ที่เกี่ยวข้อง |
| artifact_type | Requirement / BRD / API Spec / Code / Test Case |
| version | Version |
| content | เนื้อหา |
| created_by_agent | Agent ที่สร้าง |
| approval_status | Draft / Approved / Rejected |

---

## 6. UX / UI Structure Recommendation

## 6.1 Global Left Menu

```
Dashboard
Virtual Office
Projects
Agent Management
Pipeline
AI Model Settings
Knowledge Base / RAG
Integrations
Settings
```

## 6.2 Project Detail Menu

```
Project Overview
Requirement
Gap Analysis
BA / User Story
Solution Design
UX/UI Spec
Technical Design
Code Workspace
QA / Test Case
Deployment
Change Impact
Activity Log
```

## 6.3 AI Model Settings Tabs

```
AI Model Settings
 ├─ Available Ollama Model
 ├─ Per-Agent Model
 ├─ Provider Credentials
 ├─ Fallback Policy
 └─ Usage Log
```

## 6.4 Virtual Office Screen Layout

```
[Top Bar]
Project Selector | Current Stage | Overall Status | Notifications

[Main Area]
2D Pixel Virtual Office
- Agent Desks
- Meeting Area
- Break Area
- Water Station
- Pipeline Board

[Right Panel]
Selected Agent Detail
- Agent Status
- Current Task
- Model Used
- Activity Timeline
- Action Buttons

[Bottom Panel]
Task Queue / Alerts / Approval Needed
```

---

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Performance | Animation ต้องไม่ทำให้หน้าเว็บหน่วง |
| Scalability | รองรับ Agent หลายตัวในอนาคต |
| Configurability | Model และ Tech Stack ต้องเพิ่มได้จาก Config |
| Maintainability | แยก Virtual Office Engine ออกจาก Business Logic |
| Security | API Key ของ Claude/OpenAI ต้องเก็บแบบเข้ารหัส |
| Auditability | ทุก Agent Action ต้องมี Log |
| Usability | User ต้องเข้าใจสถานะ Agent ได้ภายใน 5 วินาที |
| Browser Support | รองรับ Chrome, Edge, Safari |

---

## 8. Suggested Technical Architecture

## 8.1 Frontend

แนะนำใช้:

- React
- Canvas / Phaser.js / PixiJS สำหรับ 2D Pixel Office
- Tailwind CSS หรือ CSS Module
- Zustand / Redux สำหรับ State Management

## 8.2 Backend

รองรับได้หลาย Stack ตาม Project Setting:

- Node.js API
- .NET / ASP.NET Core API
- Python FastAPI สำหรับ Agent Orchestration ถ้ามีอยู่แล้ว

## 8.3 Database

รองรับ:

- PostgreSQL
- Microsoft SQL Server
- MySQL

## 8.4 AI Provider Layer

ควรทำเป็น Adapter Pattern เช่น:

```
LLMProviderAdapter
 ├─ OllamaAdapter
 ├─ ClaudeAdapter
 └─ OpenAIAdapter
```

เหตุผล: เพิ่ม Model Provider ใหม่ได้ง่าย

## 8.5 Agent Runtime

ควรแยกเป็น:

- Agent Definition
- Agent Prompt
- Agent Model Config
- Agent Task Queue
- Agent Output Artifact
- Agent Status Event

---

## 9. Revised Menu Recommendation

## 9.1 Remove From Main Menu

ให้เอาออกจาก Main Left Menu:

- Requirement

เหตุผล: Requirement เป็นข้อมูลภายใน Project ไม่ใช่ Global Module

## 9.2 Keep / Add Main Menu

ควรมี Main Menu ดังนี้:

1. Dashboard
2. Virtual Office
3. Projects
4. Agent Management
5. Pipeline
6. AI Model Settings
7. Knowledge Base / RAG
8. Integrations
9. Settings

## 9.3 Code Workspace Decision

แนะนำให้ **ย้าย Code Workspace เข้าไปอยู่ภายใน Project Detail**

ไม่ควรเป็น Main Menu หลัก ยกเว้นต้องการทำเป็น Global Code Center เพื่อดู Code ทุก Project รวมกัน

ถ้าจะเก็บไว้เป็น Main Menu ควรเปลี่ยนชื่อเป็น:

- Code Center
- Artifact Workspace
- Generated Code Hub

แต่ถ้าใช้งานตาม SDLC จริง แนะนำให้ใช้แบบนี้:

```
Projects > Select Project > Code Workspace
```

---

## 10. Acceptance Criteria Summary

| ID | Acceptance Criteria |
|---|---|
| AC-001 | ระบบมีหน้า Virtual Office แบบ 2D Pixel |
| AC-002 | Agent เดินไปมาและมี Idle Behavior ได้ |
| AC-003 | Agent กลับโต๊ะเมื่อมี Task |
| AC-004 | Agent ทุกตัวมี Status Light |
| AC-005 | สร้าง Project แล้วเลือก Tech Stack ได้ |
| AC-006 | เลือก Database ได้: PostgreSQL, MS SQL, MySQL |
| AC-007 | เลือก Application Type ได้: Web App, Mobile App |
| AC-008 | รองรับ Claude Sonnet, Haiku, Opus |
| AC-009 | รองรับ OpenAI GPT-5.3, GPT-5.4, GPT-5.5 |
| AC-010 | AI Model Settings แยก Tab Available Ollama Model และ Per-Agent Model |
| AC-011 | Requirement ถูกย้ายไปอยู่ใน Project Detail |
| AC-012 | Code Workspace ไม่ซ้ำกับ Project และใช้สำหรับ Code Artifact |
| AC-013 | มี Activity Log ของ Agent |
| AC-014 | มี Approval Gate ใน Project Lifecycle |
| AC-015 | Config Model / Tech Stack สามารถขยายเพิ่มได้ในอนาคต |

---

## 11. Implementation Priority

## Phase 1: Menu & Project Configuration

1. ปรับ Left Menu
2. ย้าย Requirement เข้า Project Detail
3. เพิ่ม Tech Stack Configuration ใน Project
4. ปรับ Code Workspace ให้เป็น Sub-Menu ของ Project
5. ปรับ AI Model Settings เป็น Tab

## Phase 2: AI Model Management

1. Available Ollama Model Tab
2. Per-Agent Model Tab
3. Provider Credentials
4. Fallback Model
5. Model Test Function

## Phase 3: Virtual Office Core

1. สร้าง 2D Pixel Office Layout
2. วาง Agent Desk
3. แสดง Agent Sprite
4. แสดง Status Light
5. คลิก Agent แล้วแสดง Detail Panel

## Phase 4: Agent Animation & Behavior

1. Idle Animation
2. Walking Behavior
3. Water Station Behavior
4. Returning to Desk Behavior
5. Working Animation
6. Error Animation

## Phase 5: Traceability & Workflow

1. Agent Task Queue
2. Activity Timeline
3. Approval Gate
4. Artifact Versioning
5. Audit Log

---

## 12. Final Recommendation

สิ่งที่ควรทำเพิ่มเติมจาก Requirement ที่ระบุมา คือ:

1. เพิ่ม **Approval Gate** ก่อนให้ Agent ทำงานข้าม Stage
2. เพิ่ม **Project Template** เพื่อให้สร้าง Project ได้เร็ว
3. เพิ่ม **Tech Stack Preset** เพื่อเลือก Stack เป็นชุด
4. เพิ่ม **Agent Activity Timeline** เพื่อดูว่า Agent ทำอะไรไปแล้ว
5. เพิ่ม **Audit Log** เพื่อใช้ตรวจสอบย้อนหลัง
6. เพิ่ม **Fallback Model** เพราะ Cloud Model หรือ Local Model อาจใช้งานไม่ได้บางช่วง
7. เพิ่ม **Integration Menu** สำหรับ GitHub, Figma, Jira, MCP และ RAG
8. ย้าย **Code Workspace** ไปไว้ใน Project Detail เพื่อไม่ให้สับสนกับ Project

---

## 13. Definition of Done

CR นี้ถือว่าเสร็จเมื่อ:

1. UI Menu ถูกปรับตาม Requirement
2. Project สามารถเลือก Tech Stack และ Application Type ได้
3. AI Model Settings มี Tab แยกชัดเจน
4. Agent แต่ละตัวเลือก Model ได้
5. Virtual Office แสดง Agent 2D Pixel พร้อม Status Light ได้
6. Agent มี Idle และ Work Behavior ขั้นพื้นฐาน
7. Requirement อยู่ภายใน Project Detail แล้ว
8. Code Workspace ถูกนิยามใหม่และไม่ซ้ำกับ Project
9. มีเอกสาร Requirement Spec สำหรับส่งต่อ Developer / Claude Code / Codex

