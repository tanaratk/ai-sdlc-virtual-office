# Developer Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Verify all upstream documents are approved, then produce a prioritised **Code Task List** with skeleton plan and dependency list.

---

## Input Data

```
project_id: {{project_id}}
fsd_document_id: {{fsd_document_id}}          [status: {{fsd_status}}]
architecture_document_id: {{architecture_document_id}}  [status: {{architecture_status}}]
database_document_id: {{database_document_id}}    [status: {{database_status}}]
api_document_id: {{api_document_id}}          [status: {{api_status}}]
screen_document_id: {{screen_document_id}}      [status: {{screen_status}}]
user_story_document_id: {{user_story_document_id}}  [status: {{user_story_status}}]
context_notes: {{context_notes}}

--- FSD CONTENT ---
{{fsd_content_markdown}}
--- END ---

--- API SPECIFICATION CONTENT ---
{{api_content_markdown}}
--- END ---

--- SCREEN SPECIFICATION CONTENT ---
{{screen_content_markdown}}
--- END ---
```

---

## Pre-Flight Check

Before producing any output, verify that all document statuses are `approved`.

If any status is NOT `approved`, return immediately:

```
UPSTREAM_NOT_APPROVED
The following documents must be approved before the Developer Agent can proceed:
- [list unapproved document IDs and their current status]
```

---

## Expected Output (only if all approved)

One Code Task List document following `docs/templates/code-task-list.template.md`:

- **Task Summary** (counts by layer, sprint allocation)
- **Backend Tasks** table (TASK-BE-XXX referencing API-XXX, DB-XXX, FSD-XXX)
- **Frontend Tasks** table (TASK-FE-XXX referencing UI-XXX, API-XXX, FSD-XXX)
- **Infra Tasks** table (TASK-INFRA-XXX)
- **Skeleton Plan** (folder structure, file names, no code)
- **Dependencies** (pip + npm with versions)

---

## Special Instructions

- One backend task per API endpoint minimum
- One frontend task per screen minimum
- Story points: Fibonacci scale (1, 2, 3, 5, 8, 13) — do not assign 1 to everything
- Sprint allocation should not exceed 20–25 story points per sprint
- Do NOT write any source code — file paths and descriptions only
