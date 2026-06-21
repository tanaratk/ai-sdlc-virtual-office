# AI-SDLC Virtual Office — Progress Tracker

**Last Updated:** 2026-06-21 (Sprint 43 done — AI Model Settings redesigned: 2-tab layout + Claude/OpenAI providers)  
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
| 6 | Gap Analysis Agent System Prompt | `docs/prompts/gap-analysis-agent.system.md` | ✅ Done |
| 7a | Template — Requirement Summary | `docs/templates/requirement-summary.template.md` | ✅ Done |
| 7b | Template — Gap Analysis Report | `docs/templates/gap-analysis-report.template.md` | ✅ Done |
| 8 | Database Schema Design | `docs/database/schema.md` | ✅ Done |
| 9 | UI Design ใน Figma | https://www.figma.com/design/fwTNT7ztQLI1Hj0Bj0EaJb | ✅ Done |
| 10 | README.md | `README.md` | ✅ Done |

---

## Sprint Progress (ai-dlc-development-sprint-skill.md)

| Sprint | Title | Status |
|---|---|---|
| 0 | Requirement Intake & Baseline Review | ✅ Done |
| 1 | Agent Contract Design | ✅ Done |
| 2 | Prompt & Template Design | ✅ Done |
| 3 | Database Design | ✅ Done |
| 4 | API Design | ✅ Done |
| 5 | Workflow Design | ✅ Done |
| 6 | Backend Skeleton | ✅ Done |
| 7 | Frontend Skeleton | ✅ Done |
| 8 | Requirement Agent MVP | ✅ Done |
| 9 | Gap Analysis Agent MVP | ✅ Done |
| 10 | BA Agent MVP | ✅ Done |
| 11 | Solution Architect Agent MVP | ✅ Done |
| 12 | UX Agent MVP | ✅ Done |
| 13 | Developer Agent MVP | ✅ Done |
| 14 | QA Agent MVP | ✅ Done |
| 15 | Traceability MVP | ✅ Done |
| 16 | Virtual Office MVP | ✅ Done |
| 17 | RAG MVP | ✅ Done |
| 18 | GitHub Integration MVP | ✅ Done |
| 19 | MCP MVP | ✅ Done |
| 20 | Change Impact Agent MVP | ✅ Done |
| 21 | Documentation Agent MVP | ✅ Done |
| 22 | PM Agent MVP | ✅ Done |
| 23 | Docker + CI/CD | ✅ Done |
| **Phase 2** | **Code Generation Factory** | ✅ Done |
| 24 | Per-Agent LLM Selection | ✅ Done |
| 25 | Developer Agent — Real Code Generation | ✅ Done |
| 26 | Code Output Viewer + ZIP Download | ✅ Done |
| 27 | DevOps Agent (Dockerfile + CI/CD gen) | ✅ Done |
| 28 | Pipeline Steps 8–10 Completion | ✅ Done |
| 29 | GitHub Push of Generated Application | ✅ Done |
| **Phase 3** | **Enterprise Pipeline (3-Layer Architecture)** | 🔲 Next |
| 30-pre | Agent Skill Document (skill.md per agent, editable in UI) | ✅ Done |
| 30 | Pipeline Rewire — 3-Layer Architecture | ✅ Done |
| 31 | Agent File Output — write docs to workspace | ✅ Done |
| 32 | Technical Design Agent (NEW) | ✅ Done |
| 33 | Code Review Agent (NEW) | ✅ Done |
| 33-fix | Developer Agent code review — 5 bugs fixed | ✅ Done |
| 34 | QA Agent Rewrite — gen test files + run | ✅ Done |
| 35 | DevOps Agent — build + deploy + health check | ✅ Done |
| 36 | Monitoring Agent (NEW) | ✅ Done |
| 37 | Multi-Developer Agent fan-out | ✅ Done |
| 38 | Agent Contract Refactor | ✅ Done |
| 39 | Change Impact On-demand Trigger | ✅ Done |
| 39-fix | UI Redesign (sidebar groups, pipeline control center, agent console) | ✅ Done |
| 39-bugfix | Backend: 6 bugs fixed (SA validation, change_impact doctype, BOM removal) | ✅ Done |
| 40 | Wire Documentation + PM Agent into pipeline (auto-chain after monitoring) | ✅ Done |
| 41 | Tech Stack Config — backend model + schema + migration + frontend UI (FR-005) | ✅ Done |
| 42 | Left Menu Restructure — remove project-level items, reorder per CR spec (FR-008) | ✅ Done |
| 43 | AI Model Settings Redesign — 2-tab layout (Ollama Models + Per-Agent) + Claude/OpenAI providers (FR-006, FR-007) | ✅ Done |

## Project Status

**Phase 1 COMPLETE (Sprint 0–23)** — SDLC Document Pipeline ครบทุก agent

**Phase 2 COMPLETE (Sprint 24–29)** — Code Generation Factory

**Phase 3 IN PROGRESS** — Enterprise 3-Layer Pipeline Architecture
- Architecture decision: 2026-06-19
- Spec: `Requirement Spec/AI-SDLC-Working-Office-Spec.md` Section 37
- 12 agents: Requirement → Gap → BA → SA → UX → Technical Design → Dev(N) → Code Review → QA → DevOps → Monitor → Change Impact
- 3 layers: Business / Design / Delivery
- 2 hard gates: BA Approved, Technical Design Approved
- Multi-Developer Agent fan-out for large projects

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
