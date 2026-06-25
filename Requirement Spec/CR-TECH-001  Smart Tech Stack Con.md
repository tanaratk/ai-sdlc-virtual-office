# CR-TECH-001 : Smart Tech Stack Configuration

**Module:** Create Project
**Priority:** High
**Sprint:** Project Setup / AI Context Initialization

---

# Objective

ปรับปรุงหน้าสร้าง Project ให้สามารถเลือก Technology Stack ได้อย่างง่ายและรวดเร็ว โดยใช้แนวคิด **Preset + Preview + Advanced Customization**

ระบบต้องช่วยแนะนำ Tech Stack ที่เหมาะสม ลดความซับซ้อนในการตั้งค่า และส่งข้อมูล Technology Context ให้ AI Agent ทุกตัว เพื่อใช้ในการสร้าง Requirement, Design, Source Code, Test Case และ Deployment Configuration ได้อย่างถูกต้อง

---

# Business Goal

* ลดขั้นตอนการสร้าง Project
* ลดการเลือก Tech Stack ที่ไม่สัมพันธ์กัน
* เพิ่มความแม่นยำของ AI Agent ในการ Generate Code และ Document
* รองรับทั้ง Beginner และ Advanced User
* รองรับ Legacy และ Modern Technology Stack
* รองรับการขยาย Technology ในอนาคต

---

# UX Concept

ใช้แนวคิด

> **Simple by Default, Powerful when Needed**

ผู้ใช้ทั่วไปควรสร้าง Project ได้ภายใน **30 วินาที**

รายละเอียดขั้นสูงจะซ่อนไว้ในเมนู **Customize Stack**

---

# Functional Requirements

---

## FR-01 Tech Stack Preset

เพิ่มเมนูหลัก

```
Tech Stack Preset
```

เป็นขั้นตอนแรกหลังจากกรอก Project Name

ตัวอย่าง Preset

* React + .NET Core
* React + Node.js
* Angular + .NET Core
* Vue + Node.js
* ASP.NET MVC
* ASP.NET Web Forms
* Custom Stack

เมื่อเลือก Preset

ระบบต้อง Auto Fill

* Frontend
* Backend
* Database
* Programming Language
* Application Type
* Cloud Provider (Default)
* Authentication (Default)

---

## FR-02 Stack Preview

หลังเลือก Preset

ระบบต้องแสดง Preview ของ Tech Stack ทันที

ตัวอย่าง

```
Frontend
React 19

Backend
.NET 9

Language
TypeScript
C#

Database
SQL Server 2022

Application
Web Application

Cloud
Azure

Authentication
JWT

ORM
Entity Framework Core
```

ผู้ใช้สามารถกด Create Project ได้ทันทีโดยไม่ต้องเปิดเมนูอื่น

---

## FR-03 Customize Stack

สำหรับผู้ใช้ระดับ Advanced

มีปุ่ม

```
Customize Stack ▼
```

เมื่อเปิดแล้วจึงแสดงการตั้งค่าทั้งหมด

* Frontend
* Backend
* Programming Language
* Database
* Framework Version
* Cloud Provider
* Authentication
* ORM
* API Documentation
* Cache
* Queue
* Storage
* Search Engine
* Logging
* Monitoring
* Testing Framework
* Container Platform
* CI/CD Template

Advanced Settings จะถูกซ่อนเป็นค่าเริ่มต้น

---

## FR-04 Frontend / Backend Relationship

ระบบต้องแนะนำเฉพาะ Backend ที่เหมาะสมกับ Frontend

ตัวอย่าง

### React

Recommended

* .NET Core
* Node.js

---

### Angular

Recommended

* .NET Core
* Node.js

---

### Vue

Recommended

* Node.js
* .NET Core

---

### ASP.NET MVC

Recommended

* ASP.NET Framework
* ASP.NET Core

---

### ASP.NET Web Forms

Recommended

* ASP.NET Framework

---

### Custom

Allow All

---

## FR-05 Backend / Database Recommendation

เมื่อเลือก Backend

ระบบแนะนำ Database ที่เหมาะสม

Node.js

* PostgreSQL
* MySQL
* MongoDB

.NET Core

* SQL Server
* PostgreSQL
* MySQL

ASP.NET Framework

* SQL Server

---

## FR-06 Programming Language

เพิ่มข้อมูล Programming Language

แต่ไม่บังคับให้ User เลือก

ระบบเลือกให้อัตโนมัติจาก Preset

ตัวอย่าง

React

→ TypeScript

.NET Core

→ C#

Node.js

→ TypeScript

ผู้ใช้สามารถเปลี่ยนได้ใน Customize Stack

---

## FR-07 Framework Version

รองรับ Version ของ Technology

ตัวอย่าง

React

* 18
* 19

.NET

* 8
* 9

Node.js

* 20
* 22

SQL Server

* 2019
* 2022

PostgreSQL

* 16
* 17

---

## FR-08 Compatibility Validation

หากผู้ใช้เลือก Technology ที่ไม่แนะนำ

ระบบต้องแสดง Warning

ตัวอย่าง

```
⚠ React + ASP.NET Web Forms

This combination is not recommended.

Recommended

React + ASP.NET Core
```

ผู้ใช้ยังสามารถเลือก

```
Proceed Anyway
```

ได้

---

## FR-09 AI Agent Context

เมื่อสร้าง Project

ระบบต้องบันทึก Tech Stack Context

ตัวอย่าง

```
Frontend

Backend

Programming Language

Framework Version

Database

Application Type

Cloud

Authentication

ORM

Container

Testing

Logging
```

Context นี้ต้องถูกส่งให้

* Requirement Agent
* Gap Analysis Agent
* BA Agent
* Solution Architect Agent
* UX Agent
* Developer Agent
* QA Agent
* DevOps Agent
* Documentation Agent

เพื่อใช้ Generate

* Requirement
* Architecture
* API
* Database
* UI
* Source Code
* Test Case
* Docker
* CI/CD
* Deployment Script

โดยไม่ต้องถามข้อมูลซ้ำ

---

## FR-10 Future Extensible

ระบบต้องสามารถเพิ่ม Technology ใหม่ได้โดยไม่ต้องแก้ไข UI

ตัวอย่าง

Frontend

* Next.js
* Blazor
* Svelte
* Nuxt

Backend

* NestJS
* Spring Boot
* FastAPI
* Go
* Rust

Database

* Oracle
* MariaDB
* Redis
* Cosmos DB

Cloud

* Azure
* AWS
* GCP
* On-Premise

---

# Suggested UI Layout

```
Project Name
Description

---------------------------------------

Tech Stack Preset

(●) React + .NET Core

( ) React + Node.js

( ) ASP.NET MVC

( ) ASP.NET Web Forms

( ) Angular + .NET Core

( ) Vue + Node.js

( ) Custom

---------------------------------------

Stack Preview

Frontend
React 19

Backend
.NET 9

Language
TypeScript / C#

Database
SQL Server

Application
Web Application

Cloud
Azure

---------------------------------------

Customize Stack ▼

(Default: Collapsed)

---------------------------------------

Create Project
```

---

# Non-Functional Requirements

* Auto Recommendation
* Intelligent Filtering
* Compatibility Validation
* AI-Friendly Context
* Extensible Configuration
* Backward Compatibility
* Fast Project Creation (<30 seconds)
* Responsive UI
* Future Technology Ready

---

# Expected Benefits

### User Experience

* สร้าง Project ได้รวดเร็ว
* ไม่ต้องเลือก Technology หลายรายการ
* UI สะอาด เข้าใจง่าย
* รองรับทั้ง Beginner และ Expert

### AI Agent

* เข้าใจ Technology Context ตั้งแต่เริ่มต้น
* Generate Code ได้แม่นยำ
* Generate Architecture ได้ถูกต้อง
* ลด Prompt Engineering
* ลดการถามข้อมูลซ้ำ

### System

* รองรับ Multi-Technology
* รองรับ Legacy และ Modern Stack
* เพิ่ม Tech Stack ใหม่ได้ง่าย
* รองรับการพัฒนาในอนาคตโดยไม่ต้องปรับโครงสร้าง UI
