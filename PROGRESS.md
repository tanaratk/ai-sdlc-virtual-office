# AI-SDLC Virtual Office — Progress Tracker

**Last Updated:** 2026-06-18  
**Project:** ai-sdlc-virtual-office  
**Repo:** https://github.com/tanaratk/ai-sdlc-virtual-office  
**Working Directory:** D:\AI_Office

---

## Completed Tasks

| # | Task | Output | Status |
|---|------|--------|--------|
| 1 | สร้าง GitHub repo | https://github.com/tanaratk/ai-sdlc-virtual-office (public) | ✅ Done |
| 2 | สร้างโครง folder structure | `/docs/contracts`, `/docs/prompts`, `/docs/templates`, `/docs/database`, `/backend`, `/frontend`, `/infra` | ✅ Done |
| 3 | Requirement Agent Contract | `docs/contracts/requirement-agent.contract.json` | ✅ Done |
| 4 | Gap Analysis Agent Contract | `docs/contracts/gap-analysis-agent.contract.json` | ✅ Done |
| 5 | Requirement Agent System Prompt | `docs/prompts/requirement-agent.system.md` | ✅ Done |

---

## Next Task

**Task 6 — Gap Analysis Agent System Prompt**

- File to create: `docs/prompts/gap-analysis-agent.system.md`
- Base content: Spec Section 16.2 + Gap Analysis Agent Contract (`docs/contracts/gap-analysis-agent.contract.json`)
- Must cover: role definition, per-section instructions for all 14 output sections, 12 gap categories, severity levels, Approval Gap trigger rule, quality checklist, handoff message to BA Agent

---

## Remaining Tasks

| # | Task | Output |
|---|------|--------|
| 6 | Gap Analysis Agent System Prompt | `docs/prompts/gap-analysis-agent.system.md` |
| 7a | Template — Requirement Summary | `docs/templates/requirement-summary.template.md` |
| 7b | Template — Gap Analysis Report | `docs/templates/gap-analysis-report.template.md` |
| 8 | Database Schema Design | `docs/database/schema.md` |
| 9 | UI Design ใน Figma | Dashboard, Upload, Agent Console, Document Viewer |
| 10 | README.md | Project overview + how to run |

---

## Important Context

### Git / GitHub
- Remote: `origin` → `https://github.com/tanaratk/ai-sdlc-virtual-office.git`
- Branch: `master`
- GitHub user: `tanaratk`
- Git email: `tanarat.kit@gmail.com`
- gh CLI: installed at `C:\Program Files\GitHub CLI\gh.exe`
- gh auth: authenticated via Personal Access Token

### PowerShell PATH Note
- gh CLI requires PATH refresh in each new PowerShell session:
  ```powershell
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  ```

### Spec Reference
- Full spec: `Requirement Spec/AI-SDLC-Working-Office-Spec.md`
- Agent system prompts base: Spec Section 16
- DB schema base: Spec Section 12
- API design base: Spec Section 13
- Tech stack: React + Vite + TypeScript + Tailwind + Phaser.js (frontend), FastAPI + SQLAlchemy + PostgreSQL (backend)

### Contract Design Decisions
- All agent contracts follow the same JSON structure: agent → input → output → responsibilities → handoff → pipeline_step → office_behaviour
- Output document types: `requirement_summary`, `gap_analysis_report`, (BA: `brd`, `fsd`, `user_story`), etc.
- Pipeline has 10 steps total; Requirement Agent = step 1, Gap Analysis = step 2
- Database table `requirement_inputs` (not `source_documents`) per spec Section 12.2
- Default LLM: Ollama with model `qwen3:8b`

### Task List Agreed Additions (vs original)
- Added Task 7b (Gap Analysis Report template) — was missing from original list
- Added Task 10 (README.md)
- Renamed `source_documents` → `requirement_inputs` to match spec
- Repo name corrected: `ai-sdlc-virtual-office` (original had `ai-dlc-virtual-office`, missing 's')
