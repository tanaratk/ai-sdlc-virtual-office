# Solution Architect Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Using the approved BA documents, produce three architecture documents: **Architecture Design**, **Database Design**, and **API Specification**.

---

## Input Data

```
project_id: {{project_id}}
brd_document_id: {{brd_document_id}}
fsd_document_id: {{fsd_document_id}}
user_story_document_id: {{user_story_document_id}}
tech_stack_overrides: {{tech_stack_overrides}}
context_notes: {{context_notes}}

--- FSD CONTENT ---
{{fsd_content_markdown}}
--- END ---

--- USER STORIES CONTENT ---
{{user_story_content_markdown}}
--- END ---
```

---

## Expected Output

Three separate documents:

**1. Architecture Design** following `docs/templates/architecture-design.template.md`
- System Overview
- Architecture Diagram Description (C4 Level 2)
- Component List (COMP-XXX)
- Technology Stack
- Deployment Design (Docker Compose)
- Security Design
- Architecture Decisions (ADR format)

**2. Database Design** following `docs/templates/database-design.template.md`
- ERD Description
- Table List (referencing FSD-XXX data requirements)
- Table Specifications (with columns, types, constraints, FKs)
- Enum Types
- Indexes

**3. API Specification** following `docs/templates/api-spec.template.md`
- API Overview (base URL, auth, versioning)
- Endpoint List (API-XXX referencing FSD-XXX)
- Endpoint Details (request/response schemas with examples)
- Common Schemas
- Error Codes

---

## Special Instructions

- Default tech stack: FastAPI + PostgreSQL + React + Vite + TypeScript + Tailwind. Apply `tech_stack_overrides` if provided
- Assign DB-XXX IDs to tables (DB-001, DB-002, …) and API-XXX IDs to endpoints (API-001, API-002, …)
- Every table must reference a FSD-XXX data requirement
- Every endpoint must reference a FSD-XXX specification
- All timestamps must use TIMESTAMPTZ; all PKs must use UUID
- Produce all three documents in a single response, clearly separated by document type headers
