# AI-SDLC Virtual Office — Progress Tracker

**Last Updated:** 2026-06-19 (Phase 2 planning — Code Generation Factory)  
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
| **Phase 2** | **Code Generation Factory** | **In Progress** |
| 24 | Per-Agent LLM Selection | 🔲 Next |
| 25 | Developer Agent — Real Code Generation | 🔲 Planned |
| 26 | Code Output Viewer + ZIP Download | 🔲 Planned |
| 27 | DevOps Agent (Dockerfile + CI/CD gen) | 🔲 Planned |
| 28 | Pipeline Steps 8–10 Completion | 🔲 Planned |
| 29 | GitHub Push of Generated Application | 🔲 Planned |

## Project Status

**Phase 1 COMPLETE (Sprint 0–23)** — SDLC Document Pipeline ครบทุก agent, infra, UI, RAG, GitHub, MCP

**Phase 2 IN PROGRESS** — Code Generation Factory (Sprint 24–29)
- Sprint 24: Per-Agent LLM Selection — **NEXT**
- Sprint 25: Developer Agent Rewrite — Real Code Generation
- Sprint 26: Code Output Viewer + ZIP Download
- Sprint 27: DevOps Agent (Dockerfile + CI/CD)
- Sprint 28: Pipeline Steps 8–10 Completion
- Sprint 29: GitHub Push of Generated Application

**Goal shift:** Developer Agent ต้องสร้างไฟล์ code จริง (`.py`, `.tsx`, `.sql`) ไม่ใช่แค่ task list
Spec อัปเดตแล้วใน `Requirement Spec/AI-SDLC-Working-Office-Spec.md`

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
