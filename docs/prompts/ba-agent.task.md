# BA Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Using the approved Requirement Summary and Gap Analysis Report, produce three BA documents: **BRD**, **FSD**, and **User Stories**.

---

## Input Data

```
project_id: {{project_id}}
requirement_document_id: {{requirement_document_id}}
gap_document_id: {{gap_document_id}}
context_notes: {{context_notes}}
excluded_fr_ids: {{excluded_fr_ids}}

--- REQUIREMENT SUMMARY ---
{{requirement_content_markdown}}
--- END ---

--- GAP ANALYSIS REPORT ---
{{gap_content_markdown}}
--- END ---
```

---

## Expected Output

Three separate documents:

**1. BRD** following `docs/templates/brd.template.md`
- Executive Summary
- Business Objectives (BO-XXX)
- Stakeholders
- Business Requirements (BR-XXX, referencing FR-XXX)
- Business Rules
- Assumptions and Constraints
- Success Criteria

**2. FSD** following `docs/templates/fsd.template.md`
- Overview
- Functional Specifications (FSD-XXX referencing FR-XXX, with Given/When/Then acceptance criteria)
- Business Rules
- Data Requirements
- Integration Requirements (if applicable)
- Non-Functional Requirements
- Open Items (all unresolved gaps from Gap Analysis)

**3. User Stories** following `docs/templates/user-story.template.md`
- User Story List (US-XXX, "As a / I want to / So that")
- Acceptance Criteria (Given/When/Then per story)
- Story Map (grouped by Epic)

---

## Special Instructions

- Every FSD specification must reference at least one FR-XXX
- Every User Story must reference at least one FSD-XXX
- Open items from the Gap Analysis must appear as FSD open items — do not drop them
- If `excluded_fr_ids` is provided, skip those FRs and note them as excluded
- Produce all three documents in a single response, clearly separated by document type headers
