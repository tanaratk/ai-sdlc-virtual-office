# QA Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Using the approved FSD, User Stories, and API Specification, produce a **Test Cases** document and a **UAT Script**.

---

## Input Data

```
project_id: {{project_id}}
fsd_document_id: {{fsd_document_id}}
user_story_document_id: {{user_story_document_id}}
api_document_id: {{api_document_id}}
screen_document_id: {{screen_document_id}}
context_notes: {{context_notes}}

--- FSD CONTENT ---
{{fsd_content_markdown}}
--- END ---

--- USER STORIES CONTENT ---
{{user_story_content_markdown}}
--- END ---

--- API SPECIFICATION CONTENT ---
{{api_content_markdown}}
--- END ---

{{#if screen_content_markdown}}
--- SCREEN SPECIFICATION CONTENT ---
{{screen_content_markdown}}
--- END ---
{{/if}}
```

---

## Expected Output

Two separate documents:

**1. Test Cases** following `docs/templates/test-case.template.md`
- Test Summary (count by type)
- Functional Test Cases (TC-XXX referencing FSD-XXX and US-XXX)
- API Test Cases (TC-XXX referencing API-XXX)
- Edge Case Tests
- Negative Tests

**2. UAT Script** following `docs/templates/uat-script.template.md`
- UAT Overview (scope, target users, pass criteria)
- UAT Scenarios (UAT-XXX, written for non-technical users)
- Sign-Off Criteria (specific TC-XXX IDs that must pass)

---

## Special Instructions

- TC IDs are globally sequential — do not restart per section
- Every FSD specification must have at least one TC
- Every API endpoint must have at least one happy-path TC and one error TC
- UAT scenarios must use plain business language — no technical jargon
- If `screen_content_markdown` is provided, include UI smoke test cases for each screen
- Sign-off criteria must name at least 5 specific TC-XXX IDs as mandatory passes
