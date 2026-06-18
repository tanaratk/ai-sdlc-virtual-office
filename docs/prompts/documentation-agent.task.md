# Documentation Agent — Task Prompt

**Agent ID:** documentation-agent  
**Version:** 1.0.0  
**Pipeline Step:** 9 of 10

---

## Task Instructions

You are the Documentation Agent. Compile all approved documents for project `{{project_id}}` into one structured documentation package.

Follow the system prompt instructions exactly. Your only job is to assemble — do not write new content.

---

## Input Data

```json
{
  "project_id": "{{project_id}}",
  "pipeline_run_id": "{{pipeline_run_id}}",
  "documents": {
    "requirement_summary": {
      "id": "{{requirement_summary_document_id}}",
      "content": "{{requirement_summary_content}}"
    },
    "gap_analysis_report": {
      "id": "{{gap_analysis_document_id}}",
      "content": "{{gap_analysis_content}}"
    },
    "brd": {
      "id": "{{brd_document_id}}",
      "content": "{{brd_content}}"
    },
    "fsd": {
      "id": "{{fsd_document_id}}",
      "content": "{{fsd_content}}"
    },
    "user_story": {
      "id": "{{user_story_document_id}}",
      "content": "{{user_story_content}}"
    },
    "architecture_design": {
      "id": "{{architecture_document_id}}",
      "content": "{{architecture_content}}"
    },
    "database_design": {
      "id": "{{database_design_document_id}}",
      "content": "{{database_design_content}}"
    },
    "api_spec": {
      "id": "{{api_spec_document_id}}",
      "content": "{{api_spec_content}}"
    },
    "screen_spec": {
      "id": "{{screen_spec_document_id}}",
      "content": "{{screen_spec_content}}"
    },
    "code_task_list": {
      "id": "{{code_task_list_document_id}}",
      "content": "{{code_task_list_content}}"
    },
    "test_cases": {
      "id": "{{test_cases_document_id}}",
      "content": "{{test_cases_content}}"
    },
    "uat_script": {
      "id": "{{uat_script_document_id}}",
      "content": "{{uat_script_content}}"
    }
  },
  "traceability_links": {{traceability_links_json}},
  "project_name": "{{project_name}}",
  "today": "{{today}}"
}
```

---

## Expected Output

A single valid Markdown document following `docs/templates/compiled-documents.template.md` with all 16 sections populated.

The document metadata header must be:

```json
{
  "document_type": "compiled_documents",
  "agent_id": "documentation-agent",
  "pipeline_run_id": "{{pipeline_run_id}}",
  "project_id": "{{project_id}}",
  "version": 1,
  "status": "draft"
}
```
