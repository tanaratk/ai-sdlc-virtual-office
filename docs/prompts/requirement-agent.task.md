# Requirement Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Analyse the provided requirement source and produce a structured **Requirement Summary** document.

---

## Input Data

```
project_id: {{project_id}}
input_type: {{input_type}}
title: {{title}}
source_owner: {{source_owner}}
source_date: {{source_date}}
priority: {{priority}}
context_notes: {{context_notes}}

--- REQUIREMENT SOURCE CONTENT ---
{{content}}
--- END OF CONTENT ---
```

---

## Expected Output

A complete Requirement Summary document following `docs/templates/requirement-summary.template.md`.

Sections required:
1. Business Objective
2. Scope (In Scope / Out of Scope)
3. Functional Requirements (table, FR-XXX IDs)
4. Non-Functional Requirements (table, NFR-XXX IDs)
5. Stakeholders (table)
6. Assumptions (numbered list)
7. Constraints (numbered list)
8. Business Rules (BR-XXX IDs)
9. Open Questions (numbered list)

---

## Special Instructions

- `input_type` is `{{input_type}}` — adjust your extraction approach accordingly:
  - `meeting_transcript`: focus on action items and decisions
  - `chat_log`: extract agreed requirements from conversation
  - `manual_text`: treat as direct requirement specification
  - `markdown_document`: parse sections and extract structured requirements
  - `email_content`: extract requests, decisions, and constraints
- If `context_notes` is provided, pay special attention to the areas highlighted
- Do not exceed your output format — return only the Requirement Summary document
