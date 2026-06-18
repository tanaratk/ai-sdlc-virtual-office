# Gap Analysis Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Analyse the provided Requirement Summary and produce a structured **Gap Analysis Report** identifying all gaps, ambiguities, conflicts, and risks.

---

## Input Data

```
project_id: {{project_id}}
requirement_document_id: {{requirement_document_id}}
context_notes: {{context_notes}}

--- REQUIREMENT SUMMARY CONTENT ---
{{content_markdown}}
--- END OF CONTENT ---

{{#if previous_content_markdown}}
--- PREVIOUS VERSION (for change comparison) ---
{{previous_content_markdown}}
--- END OF PREVIOUS VERSION ---
{{/if}}
```

---

## Expected Output

A complete Gap Analysis Report following `docs/templates/gap-analysis-report.template.md`.

Required sections (always include):
1. Gap Summary (with proceed / hold recommendation)
2. Critical Gaps
3. Ambiguous Requirements
4. Conflicts
5. Risk List
6. Clarification Questions
7. Recommendations

Optional sections (include only if gaps found):
- Duplicate Requirements
- Dependency Gaps
- Integration Gaps
- Data Gaps
- Security Gaps
- Approval Gaps
- Reporting Gaps

---

## Special Instructions

- Apply the Approval Gap rule to **every** requirement mentioning approval, authorisation, or sign-off
- If `previous_content_markdown` is provided, compare old vs new and flag newly introduced gaps or resolved gaps
- If `context_notes` specifies a focus area (e.g. "focus on approval flow"), prioritise those gaps but do not skip others
- Return only the Gap Analysis Report document
