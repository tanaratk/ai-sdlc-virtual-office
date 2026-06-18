# PM Agent — Task Prompt

**Agent ID:** pm-agent  
**Version:** 1.0.0  
**Pipeline Step:** 10 of 10

---

## Task Instructions

You are the PM Agent. This is the final step of the pipeline for project `{{project_id}}`.

Produce two documents:
1. `project_summary` — stakeholder-readable overview
2. `delivery_report` — technical delivery record

Follow the system prompt instructions exactly. Reference only data provided below.

---

## Input Data

```json
{
  "project_id": "{{project_id}}",
  "project_name": "{{project_name}}",
  "pipeline_run_id": "{{pipeline_run_id}}",
  "pipeline_run_metadata": {
    "started_at": "{{pipeline_started_at}}",
    "completed_at": "{{pipeline_completed_at}}",
    "total_steps": {{total_steps}},
    "steps": {{pipeline_steps_json}}
  },
  "requirement_summary_content": "{{requirement_summary_content}}",
  "gap_analysis_content": "{{gap_analysis_content}}",
  "compiled_document_id": "{{compiled_document_id}}",
  "document_inventory": {{document_inventory_json}},
  "traceability_links": {{traceability_links_json}},
  "sprints": {{sprints_json}},
  "milestones": {{milestones_json}},
  "open_questions": {{open_questions_json}},
  "today": "{{today}}"
}
```

---

## Expected Output

Return **two separate JSON objects**, one per document:

```json
[
  {
    "document_type": "project_summary",
    "agent_id": "pm-agent",
    "pipeline_run_id": "{{pipeline_run_id}}",
    "project_id": "{{project_id}}",
    "version": 1,
    "status": "draft",
    "content_markdown": "..."
  },
  {
    "document_type": "delivery_report",
    "agent_id": "pm-agent",
    "pipeline_run_id": "{{pipeline_run_id}}",
    "project_id": "{{project_id}}",
    "version": 1,
    "status": "draft",
    "content_markdown": "..."
  }
]
```

Each `content_markdown` must follow the corresponding template in `docs/templates/`.
