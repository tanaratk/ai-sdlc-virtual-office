# Change Impact Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Analyse the impact of the described requirement change across all provided downstream documents and produce a **Change Impact Report**.

---

## Input Data

```
project_id: {{project_id}}
changed_requirement_ids: {{changed_requirement_ids}}
context_notes: {{context_notes}}

--- CHANGE DESCRIPTION ---
{{change_description}}
--- END ---

--- CURRENT REQUIREMENT SUMMARY ---
{{requirement_content_markdown}}
--- END ---

{{#if fsd_content_markdown}}
--- FSD CONTENT ---
{{fsd_content_markdown}}
--- END ---
{{/if}}

{{#if api_content_markdown}}
--- API SPECIFICATION CONTENT ---
{{api_content_markdown}}
--- END ---
{{/if}}
```

---

## Expected Output

One Change Impact Report following `docs/templates/change-impact-report.template.md`:

- **Change Summary** (what changed, old vs new, overall severity)
- **Affected Artifacts** table (every impacted FSD-XXX, API-XXX, DB-XXX, UI-XXX, TC-XXX)
- Impact sections for each provided document type (BRD, FSD, API, DB, Screen, Test Case)
- **Effort Estimate** table (by layer with days)
- **Risk Assessment** table
- **Recommendations** (which agents to re-run, owner, urgency)

---

## Special Instructions

- Explicitly flag: `Breaking API Change: Yes/No` and `DB Migration Required: Yes/No` for every API and DB impact
- If a document was not provided, note it as "Not analysed — document not provided" in the affected artifacts section
- Effort estimates must be conservative — multiply raw estimate × 1.3
- Recommendations must name specific agents to re-run (e.g. "Re-run BA Agent for FSD-003")
- Overall severity: Critical if any breaking change or migration; High if 3+ FSD specs affected; Medium if 1–2 specs; Low if docs only
