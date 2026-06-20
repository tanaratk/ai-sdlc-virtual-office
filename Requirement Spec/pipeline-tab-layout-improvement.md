# Pipeline Tab — Layout Improvement Summary

**Project:** AI-SDLC Office / AI Agent Virtual Office  
**Scope:** ปรับเฉพาะหน้า `Project Workspace > Pipeline`  
**Goal:** ทำให้หน้า Pipeline อ่านง่าย เห็นสถานะชัด และรู้ว่าต้องทำอะไรต่อ

---

## 1. เป้าหมายของ Tab Pipeline

หน้า Pipeline ควรเป็นหน้า **Pipeline Control Center** สำหรับดูและควบคุมการทำงานของ AI Agents

ผู้ใช้ควรเห็นทันทีว่า:

```text
1. Pipeline อยู่สถานะอะไร
2. ตอนนี้อยู่ Step ไหน
3. สำเร็จไปแล้วกี่ Step
4. Fail ที่ Step ไหน
5. Output ของแต่ละ Step อยู่ที่ไหน
6. ต้องกดอะไรต่อ
```

---

## 2. Layout ที่ควรปรับ

จากเดิม:

```text
Left: Agent Status
Right: Agent Pipeline 11 Steps
```

ให้ปรับเป็น:

```text
Top: Pipeline Summary Bar
Main Left: Pipeline Steps
Main Right: Current Step Detail
Bottom: Execution Logs
```

โครงสร้างแนะนำ:

```text
+------------------------------------------------------+
| Pipeline Summary Bar                                 |
| Status | Progress | Current Step | Last Error         |
| [Run Pipeline] [Retry Failed Step] [View Logs]       |
+------------------------------------------------------+

+--------------------------------+---------------------+
| Pipeline Steps                 | Current Step Detail |
| 70%                            | 30%                 |
+--------------------------------+---------------------+

+------------------------------------------------------+
| Execution Logs / Activity Timeline                   |
+------------------------------------------------------+
```

---

## 3. Agent Status

### สิ่งที่ต้องแก้

ไม่ควรแสดง Agent Status เป็น List ยาวด้านซ้าย เพราะทำให้รกและอ่านยาก

### ให้เปลี่ยนเป็น Agent Summary

แสดงเป็นแถบเล็กด้านบนหรือใน Summary Bar:

```text
Agents: Active 0 | Done 2 | Failed 1 | Waiting 8
[View All Agents]
```

เมื่อกด `View All Agents` ค่อยเปิดเป็น Drawer หรือ Modal

```text
All Agents

Failed
- Solution Architect Agent
  [View Logs] [Retry]

Done
- BA Agent
- Developer Agent

Waiting
- Gap Analysis Agent
- UX Agent
- QA Agent
- DevOps Agent
```

---

## 4. Pipeline Summary Bar

ให้เพิ่ม Summary Bar ด้านบนของ Tab Pipeline

### กรณี Pending

```text
Status: Pending
Progress: 0 / 11
Current Step: -
Last Error: -
[Run Pipeline] [View Logs]
```

### กรณี Running

```text
Status: Running
Progress: 1 / 11
Current Step: Requirement Summary
Duration: 00:01:35
[Pause] [Stop] [View Logs]
```

### กรณี Failed

```text
Status: Failed
Progress: 1 / 11
Failed Step: Gap Analysis
Last Error: Missing input document
[Retry Failed Step] [View Error] [Edit Requirement]
```

---

## 5. Pipeline Steps

แต่ละ Step ควรแสดงข้อมูลมากกว่าเดิม

จากเดิม:

```text
1. Requirement Summary
Requirement Agent
```

ปรับเป็น:

```text
1. Requirement Summary
Agent: Requirement Agent
Status: Waiting
Output: requirement-summary.md
[View Output] [View Logs] [Retry Step]
```

### ถ้า Step ยังไม่ Run

```text
Status: Waiting
Output: -
[View Output - Disabled]
[View Logs - Disabled]
```

### ถ้า Step สำเร็จ

```text
Status: Done
Output: requirement-summary.md
[Open Output] [View Logs] [Regenerate]
```

### ถ้า Step ล้มเหลว

```text
Status: Failed
Error: Missing requirement context
[View Error] [Retry Step] [Edit Input]
```

---

## 6. Current Step Detail Panel

ให้เพิ่ม Panel ด้านขวา เพื่อแสดงรายละเอียดของ Step ที่เลือก

ตัวอย่าง:

```text
Current Step

Step 1: Requirement Summary
Agent: Requirement Agent
Status: Waiting

Input:
- requirement-file-001.md

Expected Output:
- requirement-summary.md
- requirement-scope.md

Actions:
[Run This Step]
[View Prompt]
[View Logs]
```

ถ้า Step สำเร็จ:

```text
Current Step

Step 1: Requirement Summary
Status: Done
Duration: 01:23

Generated Outputs:
- requirement-summary.md
- requirement-risk.md

Actions:
[Open Document]
[Regenerate]
[Approve]
```

ถ้า Step Fail:

```text
Current Step

Step 2: Gap Analysis
Status: Failed

Error:
Requirement context is missing or invalid.

Actions:
[View Logs]
[Retry Step]
[Edit Input]
[Skip Step]
```

---

## 7. Execution Logs

ควรมี Logs อยู่ด้านล่าง หรือเปิดเป็น Drawer ได้

```text
Execution Logs

[11:00:01] Pipeline started
[11:00:05] Requirement Agent running
[11:01:20] Requirement Summary generated
[11:01:30] Gap Analysis failed: Missing business rule
```

ปุ่มที่ควรมี:

```text
[View Full Logs]
[Download Logs]
[Copy Error]
```

---

## 8. Status Standard

ให้ใช้ Status มาตรฐานเดียวกันทั้งหน้า

```text
Waiting     = ยังไม่เริ่ม / รอทำงาน
Running     = กำลังทำงาน
Done        = สำเร็จ
Failed      = ล้มเหลว
Need Review = รอคนตรวจ
Skipped     = ข้าม
```

### คำที่ควรเปลี่ยน

```text
Idle -> Waiting
Error -> Failed
```

---

## 9. Review Gate ใน Pipeline

ควรเพิ่มจุดให้คนตรวจเอกสารก่อน Generate Code

แนะนำเพิ่มอย่างน้อย 2 จุด:

```text
Requirement Review Gate
Design Review Gate
```

Pipeline ที่แนะนำ:

```text
1. Requirement Summary
2. Gap Analysis
3. BRD + FSD + User Stories
4. Requirement Review Gate
5. Architecture + DB + API
6. Screen Spec + UX Flows
7. Design Review Gate
8. Technical Design
9. Generated Code + Fan-out
10. Code Review
11. Generated Tests + Report
12. Build + Deploy Package
13. Monitoring Report
```

ถ้ายังไม่อยากเพิ่ม Step ให้ใส่ Status `Need Review` หลัง Step 3 และ Step 6 แทน

---

## 10. สิ่งที่ต้องแก้ตาม Priority

### Priority 1

```text
1. เอา Agent Status list ด้านซ้ายออก
2. เพิ่ม Pipeline Summary Bar
3. แบ่งหน้าเป็น Pipeline Steps 70% + Current Step Detail 30%
4. เพิ่ม Action ในแต่ละ Step เช่น View Output, View Logs, Retry Step
```

### Priority 2

```text
5. เพิ่ม Execution Logs ด้านล่าง
6. เปลี่ยน Idle เป็น Waiting
7. ทำ Status Badge ให้ชัดเจน
```

### Priority 3

```text
8. เพิ่ม Requirement Review Gate
9. เพิ่ม Design Review Gate
10. เพิ่ม Approval ก่อน Generate Code
```

---

## 11. สรุปสุดท้าย

Tab Pipeline ควรปรับจาก:

```text
Agent Status + Pipeline Step List
```

เป็น:

```text
Pipeline Control Center
```

โดยมี 5 ส่วนหลัก:

```text
1. Pipeline Summary Bar
2. Agent Summary
3. Pipeline Steps
4. Current Step Detail
5. Execution Logs
```

เป้าหมายคือให้ผู้ใช้รู้ทันทีว่า:

```text
ตอนนี้อยู่ Step ไหน
Fail ตรงไหน
Output อยู่ไหน
ต้องกดอะไรต่อ
```
