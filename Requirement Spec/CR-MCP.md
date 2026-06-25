# Additional Section for CR-MCP-Integration.md

# FR-8 Agent Workspace Synchronization Layer

## Objective

สร้างพื้นที่กลาง (Shared Workspace) สำหรับให้ทุก Agent ใช้ข้อมูลชุดเดียวกัน และทำงานบน Version เดียวกัน

Agent Workspace จะเป็น Single Source of Truth ของทั้งระบบ

# MCP & External Tool Automation Requirement

## Objective
ระบบ AI Agent Office ต้องสามารถเชื่อมต่อ external tools ผ่าน MCP หรือ API เพื่อให้ Agent ทำงานแบบ end-to-end automation ได้ ตั้งแต่ requirement, design, diagram, code generation, testing และ pull request

## Supported Connectors
- GitHub MCP
- Figma MCP
- Draw.io / diagrams.net Integration
- File System MCP
- Database MCP
- Browser / Playwright MCP

## Core Features

### 1. MCP Connector Management
- ผู้ใช้สามารถเพิ่ม แก้ไข ลบ และทดสอบ MCP Connector ได้
- ระบบต้องแสดงสถานะ connector เช่น Connected, Error, Expired, Disabled
- ระบบต้องรองรับการเก็บ credential/token แบบปลอดภัย
- แต่ละ project สามารถกำหนด connector ที่ใช้งานได้

### 2. Figma Integration
- ระบบต้องสามารถผูก Project กับ Figma File URL ได้
- UX Agent ต้องสามารถสร้าง wireframe หรือ screen design ผ่าน Figma MCP ได้
- UX Agent ต้องสามารถ update design กลับเข้า Figma Canvas ได้
- Developer Agent ต้องสามารถอ่าน design context จาก Figma เพื่อนำไป generate UI code ได้
- ระบบต้องมี Approval Gate ก่อนนำ design ไปใช้ generate code
- ระบบต้องบันทึก Design Version, Frame ID, Component Mapping และผู้อนุมัติ

### 3. GitHub Integration
- ระบบต้องสามารถผูก Project กับ GitHub Repository ได้
- Developer Agent ต้องสามารถสร้าง branch, commit code และ create pull request ได้
- QA Agent / Code Review Agent ต้องสามารถตรวจ PR และ comment ผลการ review ได้
- Requirement, User Story, Bug และ Change Request ต้องสามารถ sync เป็น GitHub Issue ได้
- ระบบต้องมี traceability ระหว่าง Requirement → Issue → Branch → Commit → Pull Request

### 4. Draw.io Integration
- Diagram Agent ต้องสามารถสร้าง diagram จาก requirement ได้
- รองรับ diagram ประเภท Workflow, Architecture, ERD, Sequence Diagram และ Deployment Diagram
- ระบบต้อง export diagram เป็น `.drawio`, `.png`, `.svg`
- Diagram file ต้องสามารถบันทึกเข้า GitHub repository ได้
- ทุก diagram ต้องมี version และ approval status

### 5. Agent Automation Workflow
- Requirement Agent สร้าง requirement baseline
- BA Agent สร้าง user story / process flow
- SA Agent สร้าง architecture และ API design
- UX Agent สร้าง Figma wireframe
- Diagram Agent สร้าง Draw.io diagram
- Developer Agent generate code และ push เข้า GitHub
- QA Agent run test และ comment กลับเข้า PR
- PM Agent แสดง progress, blocker และ approval status

## Non-Functional Requirements
- ต้องมี audit log ทุกครั้งที่ Agent เรียกใช้ MCP tool
- ต้องมี permission control ว่า Agent ตัวไหนเรียก tool อะไรได้
- ต้องมี approval ก่อน action สำคัญ เช่น push code, update Figma, create PR, delete file
- ต้องรองรับ retry เมื่อ connector error
- ต้องแสดง execution log และ tool call history


## Core Components

### Project Context Repository

เก็บข้อมูลกลางของ Project

* Project Information
* Requirement Version
* Design Version
* Diagram Version
* Source Code Version
* Current Stage
* Project Status

ตัวอย่าง

Requirement V5
↓
BA Agent

Requirement V5
↓
SA Agent

Requirement V5
↓
UX Agent

ทุก Agent ต้องทำงานบน Version เดียวกัน

---

### Artifact Repository

เก็บผลลัพธ์ทั้งหมดของ Agent

รองรับ

* Requirement
* User Story
* BRD
* FSD
* Architecture Design
* ERD
* Workflow Diagram
* Wireframe
* Mockup
* Source Code
* Test Cases
* UAT Scripts
* Release Notes

---

### Version Repository

เก็บ Version ของ Artifact ทุกประเภท

ตัวอย่าง

Requirement V1 → V2 → V3

Design V1 → V2 → V3

Code V1 → V2 → V3

สามารถย้อนกลับ (Rollback) ได้

---

### Agent Memory

เก็บข้อมูลระยะยาวของ Project

รองรับ

* Business Decisions
* Architecture Decisions
* Design Decisions
* Open Issues
* Pending Tasks
* Known Constraints
* Lessons Learned

---

### MCP Resource Mapping

เชื่อมโยง Artifact กับ External Tools

ตัวอย่าง

Requirement
↓
Workspace
↓
Figma File

Architecture
↓
Workspace
↓
Draw.io Diagram

Code
↓
Workspace
↓
GitHub Repository

---

# FR-9 Approval Workflow Engine

## Objective

ควบคุมการอนุมัติระหว่าง Agent และ Human

รองรับ Human-in-the-Loop

---

## Approval Stages

Requirement Approval

* Draft
* Review
* Approved
* Rejected

Design Approval

* Draft
* Review
* Approved
* Rejected

Architecture Approval

* Draft
* Review
* Approved
* Rejected

Code Review Approval

* Open
* Review
* Approved
* Rejected

Deployment Approval

* Pending
* Approved
* Rejected

---

## Approval Rules

ตัวอย่าง

Requirement Agent
↓
Submit

BA Lead
↓
Approve

SA Agent
↓
Continue

หากไม่อนุมัติ

SA Agent จะไม่สามารถทำงานต่อได้

---

# FR-10 Event Bus & Automation Engine

## Objective

ทำให้ Agent ทำงานอัตโนมัติตาม Event

Event Driven Architecture

---

## Supported Events

Requirement Updated

Requirement Approved

Design Created

Design Approved

Diagram Updated

Code Generated

Commit Created

Pull Request Created

Test Completed

Deployment Approved

---

## Event Processing Flow

Requirement Updated

↓

Publish Event

↓

Event Bus

↓

Trigger

BA Agent

SA Agent

UX Agent

Developer Agent

---

## Automation Rules

ตัวอย่าง

IF Requirement Approved

THEN Start BA Agent

---

IF Design Approved

THEN Start Developer Agent

---

IF Pull Request Created

THEN Start QA Agent

---

IF QA Passed

THEN Create Deployment Request

---

# Architecture Update

Previous Architecture

Agent
↓
MCP Gateway
↓
External Tools

New Architecture

Agents

Requirement Agent

Gap Analysis Agent

BA Agent

SA Agent

UX Agent

Developer Agent

QA Agent

PM Agent

↓

Agent Workspace Synchronization Layer

* Project Context Repository
* Artifact Repository
* Version Repository
* Agent Memory

↓

Approval Workflow Engine

↓

Event Bus & Automation Engine

↓

MCP Gateway

↓

GitHub MCP

Figma MCP

Draw.io MCP

Playwright MCP

Database MCP

RAG MCP

Future MCP Connectors

↓

External Systems

GitHub

Figma

Draw.io

Jira

Confluence

Slack

Teams

Database

SAP

Salesforce

ServiceNow

---

# Expected Benefits

* Single Source of Truth
* Full Traceability
* Human-in-the-Loop Governance
* Event Driven Automation
* Enterprise Scalability
* Future MCP Expansion
* Agentic Software Factory Readiness
