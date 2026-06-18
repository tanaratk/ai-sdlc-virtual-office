# Human Review Points

**Project:** AI-SDLC Working Office  
**Version:** 1.0.0  
**Date:** 2026-06-18  
**Related:** `requirement-to-code.workflow.md`, `agent-state-machine.md`

---

## Overview

There are **5 human review gates** in the pipeline. At each gate the pipeline halts and waits for a human decision before the next agent can run. Gates exist to ensure correctness, completeness, and alignment before passing work downstream.

| Gate | After Step | Documents to Review | Decision |
|---|---|---|---|
| Gate 1 | Gap Analysis | Gap Analysis Report | Confirm gaps are correct |
| Gate 2 | BA Agent | BRD, FSD, User Stories | Confirm requirements are captured |
| Gate 3 | Architect Agent | Architecture Design, DB Design, API Spec | Confirm technical design |
| Gate 4 | UX Agent | Screen Spec | Approve before dev starts |
| Gate 5 | QA Agent | Test Cases, UAT Script | Confirm test coverage |

---

## Gate 1 — After Gap Analysis Agent

**Pipeline Status When Paused:** `waiting_for_user`  
**Document(s) to Review:** `gap_analysis_report` (1 document)  
**API Endpoints Used:** `GET /documents/{id}`, then `POST /documents/{id}/approve` or `/reject`

### What the reviewer checks

- All ambiguities and contradictions in the original requirement have been identified
- Each gap has a `GAP-NNN` ID
- Missing information is listed with suggested questions (`OQ-NNN`)
- Out-of-scope items are explicitly noted

### On Approve

```
gap_analysis_report.status = approved
pipeline_run.status = running
→ BA Agent step begins immediately
```

### On Reject

```
gap_analysis_report.status = rejected
pipeline_step[gap_analysis].status = failed
pipeline_run.status = failed
→ Reviewer provides rejection reason
→ User updates the original requirement input if needed
→ User triggers re-run of the gap_analysis step
→ New gap_analysis_report created; old one set to superseded
```

### Reviewer Checklist

- [ ] Every ambiguous requirement has been flagged
- [ ] Gap IDs (GAP-001, GAP-002…) are present
- [ ] Open questions (OQ-001…) are listed with enough context
- [ ] No critical requirements have been silently dropped
- [ ] Scope boundary is clearly stated

---

## Gate 2 — After BA Agent

**Pipeline Status When Paused:** `waiting_for_user`  
**Document(s) to Review:** `brd`, `fsd`, `user_story` (3 documents)  
**API Endpoints Used:** Approve or reject each document individually, then approve the pipeline step

### What the reviewer checks

**BRD:**
- Business objectives match stakeholder intent
- All functional requirements (FR-XXX) are listed
- All non-functional requirements (NFR-XXX) are listed
- Business rules (BR-XXX) are documented

**FSD:**
- Every FR from the BRD has a corresponding FSD section
- Acceptance criteria are specific and testable
- Edge cases are identified
- No technical implementation detail leaks into FSD

**User Stories:**
- Every FR has at least one user story
- Stories follow "As a [role], I want [goal], so that [benefit]"
- Each story has acceptance criteria
- Story IDs are traceable to FRs

### On Approve (All 3 Documents)

```
brd.status = approved
fsd.status = approved
user_story.status = approved
pipeline_run.status = running
→ Architect Agent step begins immediately
```

### On Reject (Any Document)

```
<document>.status = rejected
pipeline_step[brd_fsd_user_story].status = failed
pipeline_run.status = failed
→ Reviewer provides per-document rejection reason
→ User triggers re-run of the ba_agent step
→ BA Agent re-generates all 3 documents; old ones set to superseded
```

### Reviewer Checklist

- [ ] BRD covers all FRs from requirement-summary
- [ ] FSD has acceptance criteria for every FR
- [ ] User stories are independent and estimable
- [ ] No requirements added or silently dropped vs gap_analysis_report
- [ ] All IDs are sequential and unique (FR-XXX, NFR-XXX, BR-XXX)

---

## Gate 3 — After Architect Agent

**Pipeline Status When Paused:** `waiting_for_user`  
**Document(s) to Review:** `architecture_design`, `database_design`, `api_spec` (3 documents)  
**API Endpoints Used:** Approve or reject each document individually

### What the reviewer checks

**Architecture Design:**
- Component diagram is correct and complete
- Tech stack choices are justified
- Non-functional requirements (performance, scalability, security) are addressed
- Deployment topology is defined

**Database Design:**
- All entities from FSD have tables
- Relationships and cardinalities are correct
- Every table has a primary key
- Indexes are defined for query-critical fields
- No data is impossible to retrieve with the defined schema

**API Spec:**
- Every FR that requires data has at least one API endpoint
- Request/response schemas match the database design
- HTTP methods follow REST conventions
- Error responses are defined

### On Approve (All 3 Documents)

```
architecture_design.status = approved
database_design.status = approved
api_spec.status = approved
pipeline_run.status = running
→ UX Agent step begins immediately
```

### On Reject (Any Document)

```
<document>.status = rejected
pipeline_step[architecture_design].status = failed
pipeline_run.status = failed
→ Reviewer provides rejection reason
→ User triggers re-run of architect_agent step
→ All 3 documents regenerated; old ones superseded
```

### Reviewer Checklist

- [ ] Architecture covers all NFRs
- [ ] DB tables have no obvious missing columns
- [ ] API endpoints cover all FRs
- [ ] No circular dependencies in architecture
- [ ] API naming is consistent (plural nouns, REST verbs)

---

## Gate 4 — Before Developer Agent (Hardest Gate)

**Pipeline Status When Paused:** `waiting_for_user`  
**Document(s) to Review:** `screen_spec` (1 document)  
**Critical:** This is the last gate before code generation. All 6 upstream documents must be `approved` before Developer Agent can start.

### Pre-flight check (automatic)

Before Developer Agent executes, the system automatically verifies:

| Document | Required Status |
|---|---|
| `fsd` | `approved` |
| `architecture_design` | `approved` |
| `database_design` | `approved` |
| `api_spec` | `approved` |
| `screen_spec` | `approved` |
| `user_story` | `approved` |

If any document is not `approved`, the step returns `UPSTREAM_NOT_APPROVED` immediately without calling the LLM.

### What the reviewer checks

**Screen Spec:**
- Every screen in the FSD has a corresponding screen entry (UI-NNN)
- Navigation flows are complete — no dead ends
- Each screen lists its data source (which API endpoint feeds it)
- Form fields have validation rules
- Empty states and error states are covered

### On Approve

```
screen_spec.status = approved
pipeline_run.status = running
→ Pre-flight check runs (all 6 docs verified as approved)
→ Developer Agent step begins
```

### On Reject

```
screen_spec.status = rejected
pipeline_step[screen_spec].status = failed
pipeline_run.status = failed
→ Reviewer provides rejection reason
→ User triggers re-run of ux_agent step
```

### Reviewer Checklist

- [ ] Every FSD feature has a screen entry
- [ ] All navigation paths are defined
- [ ] Each screen references the correct API endpoints
- [ ] Mobile/responsive behaviour is noted (if applicable)
- [ ] No screen is referenced in a flow but not defined

---

## Gate 5 — After QA Agent

**Pipeline Status When Paused:** `waiting_for_user`  
**Document(s) to Review:** `test_cases`, `uat_script` (2 documents)

### What the reviewer checks

**Test Cases:**
- Every FR has at least one test case (TC-NNN)
- Every test case has: preconditions, steps, expected result
- Negative / edge cases are included
- API-level tests cover all critical endpoints

**UAT Script:**
- UAT scenarios match business use cases from BRD
- Steps are written in plain language (non-technical)
- Pass/fail criteria are clear
- Sign-off section is present

### On Approve (Both Documents)

```
test_cases.status = approved
uat_script.status = approved
pipeline_step[test_cases].status = completed
→ Orchestrator calls UPDATE_TRACEABILITY
→ traceability_links are created/updated
→ pipeline_run.status = completed
```

### On Reject (Either Document)

```
<document>.status = rejected
pipeline_step[test_cases].status = failed
pipeline_run.status = failed
→ Reviewer provides rejection reason
→ User triggers re-run of qa_agent step
```

### Reviewer Checklist

- [ ] Every FR has test coverage
- [ ] At least one negative test per feature
- [ ] UAT steps are usable by a non-developer
- [ ] Critical paths (happy path + main error path) are covered
- [ ] Test IDs are sequential (TC-001, TC-002…)

---

## Review Timeout Policy

| Gate | Timeout | On Timeout |
|---|---|---|
| All gates | No automatic timeout (MVP 1) | Pipeline stays in `waiting_for_user` indefinitely |
| Future (MVP 3+) | Configurable per project | Send notification; optionally escalate |

---

## Who Can Approve

In MVP 1 there is no authentication. Any user who has access to the UI can approve or reject at any gate. The `approved_by` field is a free-text string.

Future versions (post-MVP 1) will enforce role-based approval when authentication is introduced (see OQ-001).
