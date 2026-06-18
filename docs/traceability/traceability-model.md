# Traceability Model

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Related:** `docs/database/schema.md` (DB-010: traceability_links), `docs/api/api-list.md` (API-045–047)

---

## Purpose

Every artifact produced in the pipeline must be traceable back to a requirement ID. The traceability model defines:

1. Which artifact types can be linked
2. What link types are valid
3. How the traceability matrix is read
4. How gaps in coverage are detected

---

## Artifact Types

| Type Key | Description | ID Format | Example |
|---|---|---|---|
| `requirement_input` | Raw uploaded requirement source | UUID | — |
| `document` (requirement_summary) | Requirement Summary from Step 1 | UUID + FR-XXX | FR-001 |
| `document` (gap_analysis_report) | Gap Analysis from Step 2 | UUID + GAP-XXX | GAP-001 |
| `document` (brd) | BRD section | UUID + BRD-XXX | BRD-001 |
| `document` (fsd) | FSD section | UUID + FSD-XXX | FSD-001 |
| `document` (user_story) | User Story | UUID + US-XXX | US-001 |
| `document` (architecture_design) | Architecture component | UUID + ARCH-XXX | ARCH-001 |
| `document` (database_design) | DB table/field | UUID + DB-XXX | DB-001 |
| `document` (api_spec) | API endpoint | UUID + API-XXX | API-001 |
| `document` (screen_spec) | UI Screen | UUID + UI-XXX | UI-001 |
| `document` (code_task_list) | Implementation task | UUID + TASK-XXX | TASK-BE-001 |
| `document` (test_cases) | Test case | UUID + TC-XXX | TC-001 |
| `pipeline_step` | Pipeline execution step | UUID | — |
| `task` | Work task in tasks table | UUID | — |

---

## Link Types

| Link Type | Direction | Meaning | Example |
|---|---|---|---|
| `derived_from` | downstream → upstream | This artifact was produced from the upstream artifact | FSD-001 `derived_from` FR-001 |
| `implements` | task/code → spec | This task implements this spec | TASK-BE-001 `implements` API-001 |
| `tests` | test case → spec | This test case verifies this spec | TC-001 `tests` FR-001 |
| `conflicts_with` | any → any | This artifact contradicts the linked artifact | GAP-001 `conflicts_with` FR-003 |

---

## Database Storage

Traceability links are stored in the `traceability_links` table (DB-010):

```
traceability_links
├── id              UUID PK
├── project_id      FK → projects
├── source_type     enum (requirement_input, document, task, pipeline_step)
├── source_id       UUID — ID of the source artifact
├── target_type     enum
├── target_id       UUID — ID of the target artifact
├── link_type       enum (derived_from, implements, tests, conflicts_with)
├── created_by      enum (agent, user)
├── created_at      timestamp
```

Links are created in two ways:
1. **Automatically** by the orchestrator after each pipeline step completes (agent → document links)
2. **Manually** by the Documentation Agent when building the traceability matrix (cross-document links)
3. **By the user** via API-046 (`POST /traceability/links`) for manual overrides

---

## Traceability Matrix Format

The standard traceability matrix is a table mapping each FR to all downstream artifacts:

| FR ID | FR Description | Gap? | BRD | FSD | User Story | API | UI Screen | Test Case |
|---|---|---|---|---|---|---|---|---|
| FR-001 | Accept multi-source requirement input | — | BRD-001 | FSD-001 | US-001 | API-006, API-007 | UI-002 | TC-001, TC-002 |
| FR-002 | Store requirement with metadata | — | BRD-001 | FSD-002 | US-002 | API-007, API-008 | UI-002 | TC-003 |
| FR-003 | Run 10-step pipeline | — | BRD-002 | FSD-003 | US-003 | API-010 | UI-003 | TC-004, TC-005 |

### Reading the Matrix

- Each row = one functional requirement
- Each column = one artifact type
- Cell value = the specific artifact ID(s) that trace to this FR
- Empty cell = **coverage gap** — this FR has no artifact of that type

### Coverage Gaps

A gap exists when:

| Gap Type | Condition | Severity |
|---|---|---|
| No FSD section | FR has no `derived_from` link to an FSD document | High |
| No test case | FR has no `tests` link to a test_cases document | High |
| No API endpoint | FR that requires data has no `implements` link to api_spec | Medium |
| No UI screen | FR that requires UI has no link to screen_spec | Medium |
| No user story | FR has no corresponding user story | Low |

---

## Example Traceability Links (JSON)

```json
[
  {
    "source_type": "document",
    "source_id": "<fsd-doc-uuid>",
    "source_ref": "FSD-001",
    "target_type": "document",
    "target_id": "<req-summary-uuid>",
    "target_ref": "FR-001",
    "link_type": "derived_from",
    "created_by": "agent"
  },
  {
    "source_type": "document",
    "source_id": "<test-cases-doc-uuid>",
    "source_ref": "TC-001",
    "target_type": "document",
    "target_id": "<req-summary-uuid>",
    "target_ref": "FR-001",
    "link_type": "tests",
    "created_by": "agent"
  },
  {
    "source_type": "task",
    "source_id": "<task-uuid>",
    "source_ref": "TASK-BE-001",
    "target_type": "document",
    "target_id": "<api-spec-uuid>",
    "target_ref": "API-006",
    "link_type": "implements",
    "created_by": "agent"
  }
]
```

---

## Orchestrator Auto-Link Rules

The orchestrator creates the following links automatically after each step:

| After Step | Source | Target | Link Type |
|---|---|---|---|
| Step 1 (Requirement Agent) | requirement_summary doc | requirement_input | derived_from |
| Step 2 (Gap Analysis) | gap_analysis_report doc | requirement_summary doc | derived_from |
| Step 3 (BA Agent) | brd, fsd, user_story docs | gap_analysis_report doc | derived_from |
| Step 4 (Architect Agent) | architecture, database_design, api_spec docs | fsd doc | derived_from |
| Step 5 (UX Agent) | screen_spec doc | fsd doc | derived_from |
| Step 6 (Developer Agent) | each task in code_task_list | corresponding api_spec section | implements |
| Step 7 (QA Agent) | each test_case | corresponding FR in requirement_summary | tests |

Human-created links (via API-046) supplement these auto-links.

---

## API Reference

| Operation | Endpoint | Description |
|---|---|---|
| View matrix | GET /projects/{id}/traceability | Returns all links for a project |
| Add link | POST /projects/{id}/traceability/links | Create a manual link |
| Remove link | DELETE /projects/{id}/traceability/links/{link_id} | Delete a link |
