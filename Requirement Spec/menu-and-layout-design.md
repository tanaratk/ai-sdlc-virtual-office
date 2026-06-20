# AI-SDLC Office — Menu and Layout Design Guideline

**Document Version:** 1.0  
**Purpose:** สรุปคำแนะนำการจัดเรียงเมนู, layout, navigation และ UX design สำหรับ prototype ของระบบ AI-SDLC Office / AI Agent Virtual Office  
**Target Users:** BA, SA, Developer, QA, PM, Admin, AI Agent Operator  
**Design Goal:** ทำให้ผู้ใช้เข้าใจง่ายว่า Project อยู่ขั้นตอนไหน, ต้องทำอะไรต่อ, Agent ตัวไหนกำลังทำงาน, และผลลัพธ์ของ Pipeline อยู่ที่ไหน

---

## 1. Design Principle

ระบบควรถูกออกแบบในแนวคิด **Project Workspace**

หมายความว่า 1 Project ควรเป็นศูนย์กลางของงานทั้งหมด ตั้งแต่ Requirement, Pipeline, Documents, Code, QA, Traceability, Deployment และ Monitoring

ผู้ใช้ไม่ควรรู้สึกว่าต้องเปิดหลายเมนูเพื่อหาของ แต่ควรเข้า Project เดียวแล้วเห็นทุกอย่างที่เกี่ยวข้องกับ Project นั้น

### Core Concept

```text
Project = SDLC Delivery Workspace
```

ภายใน Project ควรมีข้อมูลหลักดังนี้

```text
Project Overview
Requirement Input
AI Pipeline Execution
Generated Documents
Generated Code
QA / Test Results
Traceability
Deployment Package
Monitoring Result
```

---

## 2. Recommended Main Menu Structure

เมนูด้านซ้ายควรแบ่งเป็นกลุ่มชัดเจน ไม่ควรวางทุกเมนูในระดับเดียวกัน เพราะจะทำให้ผู้ใช้สับสนว่าอะไรคือเมนูหลัก อะไรคือเครื่องมือเสริม

### Recommended Sidebar Menu

```text
AI-SDLC Office

Main
- Dashboard
- Projects
- Requirements

Delivery
- Pipeline Runs
- Documents
- Code Workspace
- Traceability
- Virtual Office
- Monitoring

AI Platform
- Agents
- RAG Knowledge Base
- Tool Registry
- AI Model Settings

Administration
- User Management
- Project Management
```

---

## 3. Menu Naming Recommendation

| Current Name | Recommended Name | Reason |
|---|---|---|
| Requirement Intake | Requirements | สั้นกว่า และเข้าใจง่ายกว่า |
| Agent Manager | Agents | ใช้คำตรงและเป็นมาตรฐาน |
| LLM Management | AI Model Settings | ผู้ใช้ทั่วไปเข้าใจง่ายกว่า LLM |
| Pipeline Monitor | Pipeline Runs | สื่อถึงประวัติและสถานะการรัน |
| Generated Code | Code Workspace | ไม่ใช่แค่ไฟล์ code แต่เป็นพื้นที่ทำงาน |
| Compile Docs | Document Package | สื่อถึงชุดเอกสารส่งมอบ |
| PM Summary | Delivery Summary | ใช้ได้ทั้ง PM และผู้บริหาร |
| MCP Tools | Tool Registry | สื่อถึง registry ของ tools |
| Knowledge Base | RAG Knowledge Base | ชัดเจนว่าใช้กับ AI/RAG |

---

## 4. Project Workspace Layout

หน้า Project Detail ไม่ควรแสดงทุก tool เป็น card อย่างเดียว เพราะเมื่อระบบโตขึ้น card จะเยอะและดูรก

แนะนำให้ใช้ **Workspace Tabs** เพื่อแยกหมวดการทำงานใน Project

### Recommended Project Tabs

```text
Project: <Project Name>

[Overview] [Requirements] [Pipeline] [Documents] [Code] [QA] [Traceability] [Deploy] [Monitoring]
```

### Tab Description

| Tab | Purpose |
|---|---|
| Overview | สรุปสถานะ Project, Progress, Current Step, Next Action |
| Requirements | ดูไฟล์ requirement, upload เพิ่ม, version history |
| Pipeline | ดู pipeline execution, agent steps, logs, retry |
| Documents | ดู BRD, FSD, User Stories, Architecture, UX Spec, Technical Design |
| Code | ดู generated code, download, GitHub integration |
| QA | ดู test cases, UAT script, test report |
| Traceability | ดู mapping ระหว่าง Requirement → Design → Code → Test |
| Deploy | ดู build package, deployment checklist |
| Monitoring | ดู run result, error, system health, delivery status |

---

## 5. Project Overview Page Layout

หน้า Overview ควรเป็นหน้าแรกของ Project และต้องตอบคำถามให้ได้ทันทีว่า

```text
ตอนนี้ Project อยู่ขั้นไหน?
มีอะไรเสร็จแล้ว?
มีอะไร error?
ผู้ใช้ต้องทำอะไรต่อ?
```

### Recommended Layout

```text
Project Overview

Project Status: Pipeline Failed
Current Step: Gap Analysis
Completion: 1 / 11 steps
Last Run: 19 Jun 2026 22:30

Next Action
[Retry Failed Step] [Open Pipeline Console] [View Error Logs]

Summary Cards
- Requirement Files: 1
- Generated Documents: 2
- Generated Code Modules: 0
- Test Cases: 0
- Open Issues: 1
```

### Recommendation

ควรมีปุ่ม action ชัดเจน เช่น

```text
Retry Failed Step
Open Pipeline Console
View Error Logs
Review Documents
Approve Design
Generate Code
```

---

## 6. Pipeline Console Layout

หน้า Pipeline Console ควรออกแบบให้คล้าย **CI/CD Pipeline + Agent Execution Console**

จุดสำคัญคือผู้ใช้ต้องรู้ว่า Agent กำลังทำอะไร, step ไหนผ่านแล้ว, step ไหน error, และจะแก้ไขหรือ retry อย่างไร

### Recommended Pipeline Console Layout

```text
Pipeline Console

Top Summary Bar
------------------------------------------------
Status: Running
Progress: 1 / 11 steps
Current Step: Requirement Summary
Duration: 00:02:14
Last Error: Gap Analysis Agent failed

[Pause] [Retry Failed Step] [Stop] [View Logs]

Main Area
------------------------------------------------
Left Panel 70%: Pipeline Steps
Right Panel 30%: Current Agent / Logs / Output Preview
```

---

## 7. Pipeline Step Design

Pipeline step ควรใช้ status ที่เป็นมาตรฐานเดียวกันทั้งระบบ

### Recommended Status

```text
Done
Running
Waiting
Failed
Skipped
Need Review
```

### Example Pipeline Steps

```text
1. Requirement Summary              Done
2. Gap Analysis                     Failed
3. BRD + FSD + User Stories         Waiting
4. Requirement Approval             Need Review
5. Architecture + DB + API          Waiting
6. Screen Spec + UX Flows           Waiting
7. Design Approval                  Need Review
8. Technical Design                 Waiting
9. Generated Code + Fan-out         Waiting
10. Code Review                     Waiting
11. Generated Tests + Report        Waiting
12. Build + Deploy Package          Waiting
13. Monitoring Report               Waiting
```

---

## 8. Human Review Gate

ระบบ AI-SDLC ที่ใช้ทำงานจริงควรมี **Human Review / Approval Gate** โดยเฉพาะก่อนขั้นตอน Generate Code

เพราะถ้าให้ Agent วิ่งจาก Requirement ไปถึง Code ทันที อาจเกิด gap ระหว่างสิ่งที่ลูกค้าต้องการกับสิ่งที่ระบบสร้าง

### Recommended Review Gates

```text
Requirement Review Gate
- หลัง Requirement Summary, Gap Analysis, BRD/FSD/User Story
- ให้ BA, SA หรือ User ตรวจและ approve

Design Review Gate
- หลัง Architecture, Database, API, UX Flow, Technical Design
- ให้ SA, UX, Technical Lead ตรวจและ approve

Code Review Gate
- หลัง Generated Code
- ให้ Developer หรือ Code Reviewer ตรวจ

QA Review Gate
- หลัง Generated Tests และ Test Report
- ให้ QA/PM ตรวจผลลัพธ์
```

### Recommended Pipeline with Review Gates

```text
1. Requirement Summary
2. Gap Analysis
3. BRD + FSD + User Stories
4. Human Review: Requirement Approval
5. Architecture + DB + API
6. Screen Spec + UX Flows
7. Human Review: Design Approval
8. Technical Design
9. Generated Code + Fan-out
10. Code Review
11. Generated Tests + Report
12. Build + Deploy Package
13. Monitoring Report
```

---

## 9. Agent Status Panel Recommendation

จาก prototype ปัจจุบัน Agent Status แสดง agent หลายตัวพร้อมกัน ทำให้พื้นที่ด้านซ้ายแคบและชื่อ agent ถูกตัด

แนะนำให้เปลี่ยนจากการแสดง agent ทุกตัว เป็น summary panel หรือ current agent panel

### Option 1: Agent Summary Panel

```text
Agents

Active: 1
Done: 3
Failed: 1
Idle: 7

[View All Agents]
```

### Option 2: Current Agent Panel

```text
Current Agent

Requirement Agent
Status: Running
Model: GPT / Claude
Input: 1 requirement file
Output: Requirement Summary

[View Logs]
```

### Recommendation

ให้แสดงเฉพาะ Agent ที่เกี่ยวข้องกับ current step ใน Pipeline Console

ส่วน Agent ทั้งหมดให้ไปดูในหน้า `Agents` หรือเปิดผ่าน modal `View All Agents`

---

## 10. Project Outputs Instead of Additional Tools

คำว่า `Additional tools` อาจทำให้ผู้ใช้คิดว่าเป็นของเสริม ทั้งที่จริง ๆ หลายอย่างเป็น output สำคัญของ Project

แนะนำให้เปลี่ยนหัวข้อเป็น

```text
Project Outputs
```

### Recommended Output Grouping

```text
Documents
- BRD / FSD
- Architecture Document
- UX Screen Spec
- Technical Design
- Delivery Summary

Development
- Code Workspace
- GitHub Issues
- Build Package

Quality
- QA Report
- Traceability Matrix
- Change Impact Analysis

Knowledge & Tools
- RAG Knowledge Base
- Tool Registry
- Virtual Office
```

---

## 11. Status Color Standard

ควรใช้สีของ status ให้เหมือนกันทั้งระบบ เพื่อให้ผู้ใช้เข้าใจทันที

| Status Type | Color | Meaning |
|---|---|---|
| Done / Success | Green | ทำสำเร็จแล้ว |
| Running / In Progress | Blue | กำลังทำงาน |
| Need Review / Warning | Yellow / Amber | รอคนตรวจหรือมีข้อควรระวัง |
| Failed / Error | Red | มี error ต้องแก้ไข |
| Waiting / Idle | Gray | รอทำงาน |
| AI Generated / Agent Output | Purple | ผลลัพธ์ที่สร้างโดย AI |

---

## 12. Recommended User Flow

Flow หลักที่ผู้ใช้ควรเห็นชัดเจนคือ

```text
1. Upload Requirement
2. Run AI Pipeline
3. Review Generated Documents
4. Approve Requirement / Design
5. Generate Code
6. Review Code
7. Generate Test Cases
8. Build Deployment Package
9. Monitor Delivery Result
```

### User Journey Example

```text
User opens Project
→ sees Project Overview
→ uploads requirement files
→ clicks Run Pipeline
→ monitors agent execution
→ reviews generated documents
→ approves requirement/design
→ generates code
→ reviews test report
→ downloads deploy package
→ checks monitoring result
```

---

## 13. MVP Layout Recommendation

สำหรับ MVP ไม่ควรทำทุกเมนูให้ลึกทั้งหมดตั้งแต่แรก เพราะจะทำให้ UI ใหญ่เกินไปและพัฒนาใช้เวลามาก

แนะนำให้ทำ 5 หน้าหลักให้แน่นก่อน

```text
1. Dashboard
2. Project Workspace
3. Requirement Intake / Requirements
4. Pipeline Console
5. Documents / Outputs
```

### Phase 2 Features

```text
Virtual Office
Traceability
MCP Tools
RAG Knowledge Base
GitHub Integration
Deployment
Monitoring
Change Impact
```

---

## 14. Recommended Dashboard Layout

Dashboard ควรแสดงภาพรวมทุก project และ pipeline status

### Dashboard Components

```text
Top KPI Cards
- Total Projects
- Running Pipelines
- Failed Pipelines
- Pending Reviews
- Completed Deliverables

Main Section
- Recent Projects
- Pipeline Run Status
- Pending Approval Tasks
- Agent Health Summary

Right Panel
- Recent Activities
- Errors / Alerts
- Quick Actions
```

### Quick Actions

```text
Create Project
Upload Requirement
Run Pipeline
Review Documents
Open Failed Pipeline
```

---

## 15. Recommended Project Card

หน้า Projects ควรแสดง Project Card ที่เห็นสถานะชัดเจน

### Project Card Example

```text
Project Name: AI-SDLC Office
Status: Pipeline Failed
Current Step: Gap Analysis
Progress: 1 / 11
Last Run: 19 Jun 2026 22:30
Owner: BA / PM

[Open Workspace] [Retry Pipeline] [View Logs]
```

### Project Status Examples

```text
Draft
Requirement Uploaded
Pipeline Running
Need Review
Pipeline Failed
Ready for Code Generation
QA Completed
Deployment Ready
Completed
```

---

## 16. Recommended Requirement Page

หน้า Requirements ควรเน้นการจัดการ requirement input และ version

### Layout

```text
Requirements

Upload Area
- Drag and drop files
- Supported files: PDF, DOCX, TXT, MD, XLSX

Requirement Files
- File name
- Uploaded by
- Uploaded date
- Version
- Status

Requirement Summary
- AI extracted summary
- Key business needs
- Scope
- Assumptions
- Risks

Actions
[Upload More] [Run Requirement Summary] [Proceed to Pipeline]
```

---

## 17. Recommended Documents Page

หน้า Documents ควรจัดเป็นหมวดเอกสาร ไม่ใช่แสดงไฟล์รวมกันทั้งหมด

### Document Groups

```text
Business Documents
- Requirement Summary
- Gap Analysis
- BRD
- FSD
- User Stories

Solution Design
- Architecture Design
- Database Design
- API Design
- Workflow Design

UX / UI Design
- Screen Spec
- UX Flow
- Wireframe Reference

Delivery Documents
- Technical Design
- QA Test Case
- UAT Script
- Deployment Package
- PM Summary
```

### Document Status

```text
Draft
Generated
Need Review
Approved
Rejected
Regenerated
```

---

## 18. Recommended Traceability Page

Traceability ควรแสดงเป็น matrix เพื่อดูความเชื่อมโยงของ requirement ถึง test case

### Traceability Matrix

```text
Requirement ID | BRD Section | FSD Section | API | Screen | Code Module | Test Case | Status
REQ-001        | BRD-1.1     | FSD-2.1     | API-01 | SCR-01 | auth-service | TC-001 | Covered
REQ-002        | BRD-1.2     | FSD-2.2     | API-02 | SCR-02 | user-service | TC-002 | Missing Test
```

### Traceability Status

```text
Covered
Missing Design
Missing Code
Missing Test
Changed
Impacted
```

---

## 19. Recommended Virtual Office Position

Virtual Office เป็น feature ที่ดีสำหรับ visualization แต่ไม่ควรเป็น flow หลักของ MVP

แนะนำให้ใช้เป็น visual monitoring ของ agent มากกว่าเป็นหน้าหลักในการทำงาน

### Virtual Office Purpose

```text
Show agent working status visually
Show which agent is active
Show collaboration between agents
Show pipeline progress in friendly UI
```

### Recommendation

ควรอยู่ในกลุ่ม Delivery หรือเป็น tab ภายใน Project

```text
Project Workspace → Virtual Office
```

---

## 20. Key Improvements from Current Prototype

จาก prototype ปัจจุบัน แนะนำแก้ก่อน 6 จุดหลัก

```text
1. จัดเมนูซ้ายเป็นกลุ่ม Main / Delivery / AI Platform / Administration
2. เปลี่ยนหน้า Project Detail เป็น Workspace Tabs
3. เปลี่ยน Additional tools เป็น Project Outputs
4. เพิ่ม Review / Approval Gate ก่อน Generate Code
5. ลด Agent Status Panel ให้แสดงเฉพาะ Summary หรือ Current Agent
6. ปรับ Pipeline Console ให้มี Summary, Logs, Error และ Retry ชัดเจน
```

---

## 21. Recommended Implementation Priority

### Sprint 1: Navigation & Project Workspace

```text
- Reorganize sidebar menu
- Add Project Workspace tabs
- Improve Project Overview page
- Rename Additional tools to Project Outputs
```

### Sprint 2: Pipeline Console Improvement

```text
- Add top summary bar
- Standardize pipeline status
- Add current agent panel
- Add retry failed step action
- Add error log view
```

### Sprint 3: Review Gate

```text
- Add Need Review status
- Add Requirement Approval step
- Add Design Approval step
- Add Approve / Reject / Regenerate actions
```

### Sprint 4: Documents & Outputs

```text
- Group generated documents by category
- Add document status
- Add download/export action
- Add document version history
```

### Sprint 5: Traceability & Monitoring

```text
- Add traceability matrix
- Add project monitoring summary
- Add agent run history
- Add pipeline run history
```

---

## 22. Final Recommended Information Architecture

```text
AI-SDLC Office

Dashboard

Projects
└── Project Workspace
    ├── Overview
    ├── Requirements
    ├── Pipeline
    ├── Documents
    ├── Code
    ├── QA
    ├── Traceability
    ├── Deploy
    └── Monitoring

Agents
RAG Knowledge Base
Tool Registry
AI Model Settings

User Management
Project Management
```

---

## 23. Final Summary

Prototype ปัจจุบันมีทิศทางที่ถูกต้องแล้ว โดยมี workflow หลักคือ Upload Requirement → Run AI Pipeline → Review Documents

สิ่งที่ควรปรับคือการจัดโครงสร้างเมนูและ layout ให้ชัดเจนขึ้น เพื่อให้ระบบดูเป็น professional SDLC workspace มากกว่าเป็นชุดเครื่องมือที่กระจายกัน

แนวทางที่แนะนำคือ

```text
Project เป็นศูนย์กลาง
Pipeline เป็น execution core
Documents / Code / QA เป็น output
Agents / LLM / MCP / RAG เป็น platform layer
Admin แยกออกจากงาน delivery
```

เมื่อนำแนวทางนี้ไปใช้ ผู้ใช้จะเข้าใจง่ายขึ้นว่า

```text
ตอนนี้งานอยู่ขั้นไหน
ใครหรือ agent ตัวไหนกำลังทำงาน
มี error ตรงไหน
ต้อง review หรือ approve อะไร
ผลลัพธ์อยู่ที่ไหน
จะไปขั้นตอนถัดไปอย่างไร
```
