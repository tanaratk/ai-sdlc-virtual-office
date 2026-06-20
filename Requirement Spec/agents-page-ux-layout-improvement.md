# Agents Page — UX / Layout Improvement Summary

**Project:** AI-SDLC Office / AI Agent Virtual Office  
**Scope:** ปรับเฉพาะหน้า `AI Platform > Agents`  
**Goal:** ทำให้หน้า Agents ใช้งานง่ายขึ้น อ่านง่ายขึ้น และเหมาะกับการ Configure Agent จำนวนมาก

---

## 1. เป้าหมายของหน้านี้

หน้า Agents ควรใช้สำหรับ:

```text
1. ดูรายชื่อ Agent ทั้งหมด
2. เห็นสถานะของ Agent ได้ทันที
3. ค้นหา / Filter Agent ได้ง่าย
4. เลือก Agent แล้ว Configure ได้เร็ว
5. ดู Skill Document / Prompt / Tool / Model ของ Agent ได้ในหน้าเดียว
```

---

## 2. ปัญหาจากหน้าปัจจุบัน

```text
1. รายชื่อ Agent ด้านซ้ายยาวมาก และไม่มี Search / Filter
2. ชื่อ Agent บางตัวถูกตัด ทำให้อ่านยาก
3. พื้นที่ด้านขวาว่างเยอะ แต่ข้อมูล Config มีน้อย
4. ยังไม่เห็นภาพรวมว่า Agent ทั้งหมดมีกี่ตัว Done / Idle / Error
5. Tab มีแค่ Configuration และ Skill Document ยังไม่พอสำหรับ Agent Management
6. ปุ่ม Save Model อยู่ใกล้ config เฉพาะ LLM แต่ยังไม่มี Save Agent / Test Agent / Reset
```

---

## 3. Layout ใหม่ที่แนะนำ

ให้จัดหน้าเป็น 3 ส่วนหลัก:

```text
+------------------------------------------------------+
| Agents Header                                        |
| Summary Cards + Search + Filter                      |
+-------------------------+----------------------------+
| Agent List              | Agent Detail Panel          |
| 30%                     | 70%                        |
+-------------------------+----------------------------+
```

---

## 4. Header ด้านบน

เพิ่ม Header ให้บอกภาพรวมของ Agent ทั้งหมด

```text
Agents

Manage AI agents, model configuration, skills, tools, and execution behavior.

Total Agents: 12 | Active: 0 | Done: 3 | Waiting: 8 | Failed: 1
[Create Agent] [Import Agent] [Export Config]
```

---

## 5. Agent Summary Cards

เพิ่ม Summary Card ด้านบนก่อนรายการ Agent

```text
Total Agents     12
Active           0
Done             3
Waiting          8
Failed           1
```

ใช้สีมาตรฐาน:

```text
Done    = Green
Running = Blue
Waiting = Gray
Failed  = Red
```

---

## 6. Agent List ด้านซ้าย

### 6.1 เพิ่ม Search

ควรมีช่อง Search ด้านบน List

```text
Search agent...
```

ค้นหาได้จาก:

```text
agent name
role
step
status
```

### 6.2 เพิ่ม Filter

```text
Status: All / Running / Done / Waiting / Failed
Role: All / BA / SA / UX / Developer / QA / DevOps
```

### 6.3 ปรับ Agent Card ให้ดูง่ายขึ้น

จากเดิม:

```text
gap-analysis-agent
gap_analyst
Done
```

ปรับเป็น:

```text
gap-analysis-agent
Role: Gap Analyst | Step 2
Status: Done
Model: qwen3:8b
```

หรือแบบ compact:

```text
[Icon] gap-analysis-agent          Done
       Gap Analyst • Step 2
       qwen3:8b
```

### 6.4 ไม่ควรตัดชื่อ Agent สำคัญ

ถ้าชื่อยาว ให้ใช้ 2 บรรทัด หรือ Tooltip

```text
developer-agent-backend
Backend Developer
```

แทนการแสดงเป็น:

```text
developer-agent-ba...
```

---

## 7. Agent Detail Panel ด้านขวา

พื้นที่ด้านขวาควรแสดงข้อมูล Agent แบบครบถ้วนมากขึ้น

### Header ของ Agent Detail

```text
gap-analysis-agent
Role: Gap Analyst
Step: 2
Category: Business
Status: Done

[Run Test] [View Logs] [Duplicate] [Disable Agent] [Save Changes]
```

---

## 8. Tabs ที่ควรมีใน Agent Detail

จากเดิมมี:

```text
Configuration
Skill Document
```

แนะนำเพิ่มเป็น:

```text
Overview
Model Config
Prompt / Skill
Tools
Memory / RAG
Execution Logs
```

---

## 9. Tab: Overview

ใช้ดูข้อมูลสรุปของ Agent

```text
Agent Name: gap-analysis-agent
Role: Gap Analyst
Pipeline Step: 2
Home Room: gap_analysis_room
Status: Done
Last Run: 2026-06-20 11:10
Last Duration: 00:01:32
Last Output: gap-analysis-report.md
```

Actions:

```text
[Run Test]
[Open Last Output]
[View Logs]
```

---

## 10. Tab: Model Config

ใช้ตั้งค่า LLM ของ Agent

```text
Provider: Ollama (local)
Model: qwen3:8b (5.2 GB)
Temperature: 0.2
Max Tokens: 4096
Timeout: 120 sec
Fallback Model: GPT-4.1 / Claude / None
```

Actions:

```text
[Test Model]
[Save Model Config]
[Reset to Default]
```

> หมายเหตุ: ปุ่มควรเปลี่ยนจาก `Save Model` เป็น `Save Model Config` เพื่อสื่อความหมายชัดขึ้น

---

## 11. Tab: Prompt / Skill

รวม Skill Document และ Prompt เข้าไว้ด้วยกัน

```text
System Prompt
Role Instruction
Input Contract
Output Contract
Validation Rules
```

Actions:

```text
[Edit Skill]
[Preview Prompt]
[Validate Skill]
[Save Skill]
```

---

## 12. Tab: Tools

แสดง Tools ที่ Agent ใช้ได้

```text
Enabled Tools:
- Requirement Parser
- Document Generator
- RAG Search
- GitHub Tool

Tool Permission:
Read / Write / Execute
```

Actions:

```text
[Add Tool]
[Remove Tool]
[Test Tool]
```

---

## 13. Tab: Memory / RAG

ใช้กำหนด Knowledge Base ที่ Agent ใช้ค้นหา

```text
Knowledge Base:
- Requirement KB
- Project Documents
- Architecture Standards

Retrieval Mode:
Hybrid Search / Vector Search / Keyword Search

Top K: 5
```

Actions:

```text
[Test Retrieval]
[Save RAG Config]
```

---

## 14. Tab: Execution Logs

ใช้ดูประวัติการ Run ของ Agent

```text
Last Runs

2026-06-20 11:10  Done    00:01:32
2026-06-20 10:42  Failed  00:00:45
2026-06-20 09:15  Done    00:01:20
```

Actions:

```text
[View Full Log]
[Download Log]
[Copy Error]
```

---

## 15. ปุ่มหลักที่ควรมี

ใน Agent Detail ควรมีปุ่มหลักด้านบนขวา:

```text
[Run Test]
[View Logs]
[Save Changes]
```

ถ้า Agent มี Error:

```text
[View Error]
[Retry Agent]
[Disable Agent]
```

---

## 16. Status Standard

ใช้ Status ชุดเดียวกับ Pipeline

```text
Waiting     = ยังไม่เริ่ม / รอทำงาน
Running     = กำลังทำงาน
Done        = สำเร็จ
Failed      = ล้มเหลว
Disabled    = ปิดใช้งาน
```

เปลี่ยนคำว่า:

```text
Idle -> Waiting
Error -> Failed
```

---

## 17. Layout ตัวอย่าง

```text
Agents

Total 12 | Running 0 | Done 3 | Waiting 8 | Failed 1
[Create Agent] [Import Agent] [Export Config]

+------------------------------+-----------------------------------------+
| Search agent...              | gap-analysis-agent                      |
| Status Filter                | Role: Gap Analyst | Step 2 | Done       |
| Role Filter                  | [Run Test] [View Logs] [Save Changes]  |
|                              |-----------------------------------------|
| Agent List                   | Tabs                                    |
| - architect-agent   Failed   | Overview | Model Config | Prompt       |
| - ba-agent          Done     | Tools | Memory/RAG | Logs              |
| - gap-analysis      Done     |-----------------------------------------|
| - developer-agent   Done     | Selected Tab Content                    |
| - qa-agent          Waiting  |                                         |
+------------------------------+-----------------------------------------+
```

---

## 18. สิ่งที่ควรแก้ตาม Priority

### Priority 1 — ควรแก้ก่อน

```text
1. เพิ่ม Search Agent
2. เพิ่ม Filter ตาม Status / Role
3. เพิ่ม Summary Cards ด้านบน
4. ปรับ Agent Card ไม่ให้ชื่อตัดอ่านยาก
5. เปลี่ยน Idle เป็น Waiting และ Error เป็น Failed
```

### Priority 2 — ควรทำต่อ

```text
6. เพิ่ม Overview Tab
7. เพิ่ม Run Test / View Logs / Save Changes
8. เพิ่ม Execution Logs Tab
9. เพิ่ม Last Run / Last Output / Duration
```

### Priority 3 — สำหรับใช้งานจริง

```text
10. เพิ่ม Tools Tab
11. เพิ่ม Memory / RAG Tab
12. เพิ่ม Prompt / Skill Editor
13. เพิ่ม Import / Export Agent Config
14. เพิ่ม Duplicate / Disable Agent
```

---

## 19. สรุปสั้นที่สุด

หน้า Agents ควรปรับจาก:

```text
Agent List + Basic Model Config
```

เป็น:

```text
Agent Management Console
```

โดยมี 5 ส่วนหลัก:

```text
1. Agent Summary
2. Search / Filter
3. Agent List แบบอ่านง่าย
4. Agent Detail Panel
5. Tabs สำหรับ Overview, Model, Skill, Tools, RAG, Logs
```

เป้าหมายคือให้ผู้ใช้สามารถ:

```text
หา Agent ได้เร็ว
รู้สถานะ Agent ทันที
ตั้งค่า Model ได้ง่าย
ดู Prompt / Skill / Tool ได้ครบ
Test Agent และดู Logs ได้ในหน้าเดียว
```
