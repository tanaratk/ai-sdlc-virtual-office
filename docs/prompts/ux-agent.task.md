# UX Agent — Task Prompt

**Version:** 1.0.0

---

## Task

Using the approved FSD and Architecture documents, produce a complete **Screen Specification** document.

---

## Input Data

```
project_id: {{project_id}}
fsd_document_id: {{fsd_document_id}}
architecture_document_id: {{architecture_document_id}}
api_document_id: {{api_document_id}}
design_system_notes: {{design_system_notes}}
context_notes: {{context_notes}}

--- FSD CONTENT ---
{{fsd_content_markdown}}
--- END ---

--- API SPECIFICATION CONTENT ---
{{api_content_markdown}}
--- END ---
```

---

## Expected Output

One Screen Specification document following `docs/templates/screen-spec.template.md`:

- **Screen Inventory** table (UI-XXX, route, description, FR Ref, priority)
- **Screen Specifications** — one sub-section per screen with:
  - Purpose
  - Layout Zones
  - Components (with shadcn/ui names)
  - API Endpoints Consumed (API-XXX references)
  - User Actions
  - Empty State
  - Error State
- **UX Flow** — numbered navigation walkthrough
- Component Inventory (if shared components exist)
- Design Tokens (if deviating from default)

---

## Special Instructions

- Default design system: dark theme (bg=#0F0F1A), shadcn/ui components, Inter font — unless `design_system_notes` overrides
- Every screen must have a UI-XXX ID and reference at least one FR-XXX
- Every API endpoint (API-XXX) from the API Specification must appear in at least one screen's "API Endpoints Consumed" section
- Describe layouts in prose and tables only — no HTML, CSS, or JSX
- Empty State and Error State are required for every screen — do not skip them
