"""Developer Agent -- Pipeline Step 7 (Delivery Layer).

Reads the Technical Design task list (dev_tasks.md) and approved design documents
to generate real source code files for the project.

Generation strategy:
  Phase 1 -- File plan: parse TASK-XXX items from Technical Design Agent output.
             Falls back to LLM planning if no technical_design doc exists.
  Phase 2 -- Per-file generation with cross-file context:
             Each file receives already-generated files as import reference.

Essential config files (requirements.txt, package.json, vite.config.ts,
.env.example, README.md) are always appended to the plan.

Files are written to: {workspace}/{project_name}/generated_app/{file_path}
A summary document (code_task_list type) is saved to the DB.
"""
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.models import (
    ActivityLog,
    Agent,
    AgentStatus,
    Document,
    DocumentStatus,
    DocumentType,
    EventType,
    PipelineRun,
    PipelineRunStatus,
    PipelineStep,
    PipelineStepStatus,
    Project,
)
from app.llm import client as _llm

logger = logging.getLogger(__name__)

AGENT_NAME = "developer-agent"
STEP_NAME = "dev_tasks"

PLAN_TIMEOUT = 120.0
FILE_TIMEOUT = 150.0
MAX_FILES = 20          # max files from tech-design plan (essential files added on top)
MIN_FILE_CHARS = 100    # minimum chars to accept a generated file as valid
MAX_DEVELOPER_LANES = 3


def _esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


def _trunc(s: str, n: int) -> str:
    return s[:n] + "\n...(truncated)" if len(s) > n else s


# -- File plan schema ----------------------------------------------------------

class _FileSpec(BaseModel):
    path: str = ""
    lang: str = "python"
    purpose: str = ""
    context_hint: str = "backend_route"

    class Config:
        extra = "ignore"


class _FilePlan(BaseModel):
    files: list[_FileSpec] = Field(default_factory=list)

    class Config:
        extra = "ignore"


@dataclass
class _DeveloperLane:
    name: str
    label: str
    focus: str
    files: list[_FileSpec] = field(default_factory=list)


# -- Essential config files always added to every project ----------------------

_ESSENTIAL_SPECS_DEFAULT: list[_FileSpec] = [
    _FileSpec(path="requirements.txt", lang="text",
              purpose="Python dependencies: FastAPI, SQLModel, psycopg2, alembic, httpx, pydantic",
              context_hint="backend_model"),
    _FileSpec(path="frontend/package.json", lang="json",
              purpose="Node.js package manifest with react, vite, tailwind, react-router, tanstack-query",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/vite.config.ts", lang="typescript",
              purpose="Vite build configuration for React + TypeScript with path alias @/",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/tsconfig.json", lang="json",
              purpose="TypeScript compiler configuration for React + Vite project",
              context_hint="frontend_type"),
    _FileSpec(path=".env.example", lang="text",
              purpose="Environment variables template: DATABASE_URL, SECRET_KEY, CORS_ORIGINS",
              context_hint="readme"),
    _FileSpec(path="README.md", lang="markdown",
              purpose="Project overview, setup instructions, and how to run locally",
              context_hint="readme"),
]

_ESSENTIAL_SPECS_DOTNET: list[_FileSpec] = [
    _FileSpec(path="App.csproj", lang="xml",
              purpose=".NET 8 project file (Sdk='Microsoft.NET.Sdk.Web'). TargetFramework net8.0, ImplicitUsings enable, Nullable enable. NuGet packages: Npgsql.EntityFrameworkCore.PostgreSQL 8.0.x, Swashbuckle.AspNetCore 6.x.",
              context_hint="backend_model"),
    _FileSpec(path="Program.cs", lang="csharp",
              purpose="ASP.NET Core entry point. AddControllersWithViews() + AddSwaggerGen(). DbContext registered with Npgsql. Retry loop (up to 10 times, 2s sleep) before EnsureCreated() to wait for Postgres. UseStaticFiles(), UseSwagger(), UseSwaggerUI(c => { c.RoutePrefix='swagger'; c.SwaggerEndpoint('/swagger/v1/swagger.json','API v1'); }). MapControllerRoute default pattern {controller=Home}/{action=Index}/{id?}. MapControllers().",
              context_hint="backend_route"),
    _FileSpec(path="Views/_ViewImports.cshtml", lang="csharp",
              purpose="Razor view imports: @using <RootNamespace>.Models and @addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers",
              context_hint="frontend_page"),
    _FileSpec(path="Views/_ViewStart.cshtml", lang="csharp",
              purpose="Razor view start: sets Layout = \"_Layout\"",
              context_hint="frontend_page"),
    _FileSpec(path="Views/Shared/_Layout.cshtml", lang="csharp",
              purpose="Bootstrap 5 main layout with sidebar navigation. Links to all main sections of the app. @RenderBody() in main content area. Bootstrap 5 CDN + Bootstrap Icons CDN in <head>.",
              context_hint="frontend_page"),
    _FileSpec(path="appsettings.json", lang="json",
              purpose="ASP.NET Core app settings: Logging levels and AllowedHosts. No connection string here — connection string built from env vars in Program.cs.",
              context_hint="backend_model"),
    _FileSpec(path=".env.example", lang="text",
              purpose="Environment variables template: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD",
              context_hint="readme"),
    _FileSpec(path="README.md", lang="markdown",
              purpose="Project overview, setup instructions: docker compose up, then open http://localhost",
              context_hint="readme"),
]

_ESSENTIAL_SPECS_NODE: list[_FileSpec] = [
    _FileSpec(path="backend/package.json", lang="json",
              purpose="Node.js/Express backend package manifest. Dependencies: express, pg, dotenv, jsonwebtoken, bcryptjs, cors. DevDependencies: typescript, ts-node, @types/express, @types/node, nodemon.",
              context_hint="backend_model"),
    _FileSpec(path="backend/tsconfig.json", lang="json",
              purpose="TypeScript compiler config for Node.js backend: target ES2020, module commonjs, outDir dist, strict true",
              context_hint="backend_model"),
    _FileSpec(path="frontend/package.json", lang="json",
              purpose="Frontend package manifest matching the frontend framework (React: react+vite+tailwindcss; Vue: vue+vite; Angular: @angular/core+@angular/cli)",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/vite.config.ts", lang="typescript",
              purpose="Vite build configuration for React or Vue frontend with path alias @/ and proxy /api/ to backend",
              context_hint="frontend_type"),
    _FileSpec(path=".env.example", lang="text",
              purpose="Environment variables template: DATABASE_URL, PORT=3000, JWT_SECRET, NODE_ENV",
              context_hint="readme"),
    _FileSpec(path="README.md", lang="markdown",
              purpose="Project overview, setup instructions, and how to run locally with docker compose",
              context_hint="readme"),
]

_ESSENTIAL_SPECS_ANGULAR: list[_FileSpec] = [
    _FileSpec(path="backend/package.json", lang="json",
              purpose="Node.js/Express backend package manifest with express, pg, dotenv, jsonwebtoken, cors, typescript",
              context_hint="backend_model"),
    _FileSpec(path="backend/tsconfig.json", lang="json",
              purpose="TypeScript compiler config for Node.js backend: target ES2020, module commonjs, outDir dist",
              context_hint="backend_model"),
    _FileSpec(path="frontend/angular.json", lang="json",
              purpose="Angular CLI workspace configuration. Projects: one app named after project. Build target: browser. Assets: src/assets. Styles: src/styles.scss.",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/package.json", lang="json",
              purpose="Angular project package manifest. Dependencies: @angular/core, @angular/common, @angular/forms, @angular/router, @angular/material. DevDependencies: @angular/cli, typescript.",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/tsconfig.json", lang="json",
              purpose="TypeScript config for Angular project: strict true, target ES2022, module ES2022",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/src/main.ts", lang="typescript",
              purpose="Angular app bootstrap entry point: bootstrapApplication(AppComponent, appConfig)",
              context_hint="frontend_page"),
    _FileSpec(path=".env.example", lang="text",
              purpose="Environment variables template: DATABASE_URL, PORT=3000, JWT_SECRET, NODE_ENV",
              context_hint="readme"),
    _FileSpec(path="README.md", lang="markdown",
              purpose="Project overview and setup instructions for Angular + Node.js project",
              context_hint="readme"),
]

_ESSENTIAL_SPECS_VUE: list[_FileSpec] = [
    _FileSpec(path="backend/package.json", lang="json",
              purpose="Node.js/Express backend package manifest with express, pg, dotenv, jsonwebtoken, cors, typescript",
              context_hint="backend_model"),
    _FileSpec(path="backend/tsconfig.json", lang="json",
              purpose="TypeScript compiler config for Node.js backend: target ES2020, module commonjs, outDir dist",
              context_hint="backend_model"),
    _FileSpec(path="frontend/package.json", lang="json",
              purpose="Vue 3 frontend package manifest. Dependencies: vue, vue-router, pinia, @vueuse/core. DevDependencies: vite, @vitejs/plugin-vue, typescript, tailwindcss.",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/vite.config.ts", lang="typescript",
              purpose="Vite config for Vue 3 project: @vitejs/plugin-vue(), resolve alias @/ → src/, proxy /api/ to backend",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/tsconfig.json", lang="json",
              purpose="TypeScript config for Vue 3 project: target ESNext, module ESNext, strict true, include vue files",
              context_hint="frontend_type"),
    _FileSpec(path="frontend/src/main.ts", lang="typescript",
              purpose="Vue 3 app entry point: createApp(App).use(router).use(pinia).mount('#app')",
              context_hint="frontend_page"),
    _FileSpec(path=".env.example", lang="text",
              purpose="Environment variables template: DATABASE_URL, PORT=3000, JWT_SECRET, VITE_API_URL",
              context_hint="readme"),
    _FileSpec(path="README.md", lang="markdown",
              purpose="Project overview and setup instructions for Vue 3 + Node.js project",
              context_hint="readme"),
]


def _detect_stack_type(tech_stack: dict | None) -> str:
    """Return 'dotnet' | 'angular' | 'vue' | 'node' | 'python' based on project tech_stack."""
    if not tech_stack:
        return "python"
    backend = (tech_stack.get("backend") or "").lower()
    frontend = (tech_stack.get("frontend") or "").lower()
    if any(k in backend or k in frontend for k in [".net", "asp.net", "aspnet", "blazor", "razor", "c#"]):
        return "dotnet"
    if "angular" in frontend:
        return "angular"
    if "vue" in frontend:
        return "vue"
    if any(k in backend for k in ["node", "express", "nest", "javascript", "typescript"]):
        return "node"
    return "python"


def _essential_specs_for_stack(tech_stack: dict | None) -> list[_FileSpec]:
    t = _detect_stack_type(tech_stack)
    if t == "dotnet":
        return _ESSENTIAL_SPECS_DOTNET
    if t == "angular":
        return _ESSENTIAL_SPECS_ANGULAR
    if t == "vue":
        return _ESSENTIAL_SPECS_VUE
    if t == "node":
        return _ESSENTIAL_SPECS_NODE
    return _ESSENTIAL_SPECS_DEFAULT


def _tech_stack_description(tech_stack: dict | None) -> str:
    """Convert tech_stack JSON to a human-readable description for LLM prompts."""
    if not tech_stack:
        return "FastAPI + SQLModel + PostgreSQL for backend; React + TypeScript + Vite + Tailwind for frontend."
    parts = []
    for key, label in [
        ("backend", "Backend"), ("backend_version", "Backend version"),
        ("frontend", "Frontend"), ("frontend_version", "Frontend version"),
        ("database", "Database"), ("database_version", "Database version"),
        ("language", "Language"), ("app_type", "App type"),
        ("orm", "ORM"), ("auth", "Auth"), ("testing", "Testing"),
        ("cloud", "Cloud"), ("api_docs", "API docs"),
        ("cache", "Cache"), ("queue", "Queue"),
    ]:
        if tech_stack.get(key):
            parts.append(f"{label}: {tech_stack[key]}")
    return "; ".join(parts) + "." if parts else "FastAPI + React + PostgreSQL."


def _lang_options_for_stack(tech_stack: dict | None) -> str:
    t = _detect_stack_type(tech_stack)
    if t == "dotnet":
        return '"csharp", "aspx", "xml", "json", "sql", "markdown", "text"'
    if t in ("node", "angular", "vue"):
        return '"typescript", "javascript", "json", "sql", "yaml", "markdown", "text"'
    return '"python", "typescript", "json", "sql", "yaml", "markdown", "text"'

# -- Prompts: fallback LLM planning -------------------------------------------

_PLAN_SYSTEM_PROMPT = """\
You are a senior software architect in an AI-powered software factory.
Given technical specification documents, decide which source code files
to generate for the project.

PROJECT TECH STACK: {tech_stack_info}

RULES:
- Produce a JSON object with a "files" array only.
- Each file must have: path, lang, purpose, context_hint.
- path: relative path inside the project matching the tech stack above.
- lang: one of {lang_options}
- purpose: one sentence describing what this file does
- context_hint: one of "backend_model", "backend_route", "backend_schema",
  "backend_migration", "frontend_type", "frontend_service",
  "frontend_component", "frontend_page", "readme"
- Generate at most {max_files} files. Focus on the most critical files first.
- Match the file extensions and structure to the PROJECT TECH STACK above.
- Do NOT include config/setup files (*.csproj, requirements.txt, package.json,
  appsettings.json, .env.example, README.md) — those are added automatically.
- Return ONLY valid JSON. No markdown fences, no explanation.
"""

_PLAN_TEMPLATE = """\
Generate the file plan for this project. Return JSON only.

FUNCTIONAL SPECIFICATION (excerpt):
{fsd}

ARCHITECTURE DESIGN (excerpt):
{architecture}

DATABASE DESIGN (excerpt):
{database}

API SPECIFICATION (excerpt):
{api_spec}

SCREEN SPECIFICATION (excerpt):
{screen_spec}

Schema:
{{
  "files": [
    {{
      "path": "backend/app/models/user.py",
      "lang": "python",
      "purpose": "SQLModel User table definition",
      "context_hint": "backend_model"
    }}
  ]
}}
"""

# -- Prompts: file generation -------------------------------------------------

_FILE_SYSTEM_PROMPT = """\
You are an expert code generator. You write clean, production-ready code.

PROJECT TECH STACK: {tech_stack_info}

RULES:
- Output ONLY the file content. No markdown fences. No explanation.
- Write complete, runnable code -- not stubs or placeholders.
- Strictly follow the PROJECT TECH STACK above. Use the correct language,
  frameworks, and file conventions for that stack.
- For ASP.NET Web Forms: use .aspx + code-behind .aspx.cs pattern.
- For ASP.NET Core MVC or Razor Pages:
    * Controllers inherit ControllerBase (API) or Controller (web views).
    * Web UI controllers return View(model) and live under Controllers/.
    * Views use .cshtml Razor syntax with Bootstrap 5.
    * File-scoped namespaces (namespace App.Controllers;) for .NET 6+.
    * ImplicitUsings enabled — no need to add 'using System;' or 'using System.Threading.Tasks;'.
    * Models live under Models/ with file-scoped namespace App.Models;
    * ApplicationDbContext uses DbSet<T> for each entity, extends DbContext.
    * Program.cs MUST use AddControllersWithViews() not AddControllers() when Views exist.
    * Program.cs MUST retry DB connection before EnsureCreated() — use a loop with Thread.Sleep(2000).
- For Blazor: use .razor components.
- For React/TypeScript: use functional components, hooks, Tailwind CSS, shadcn/ui components.
- For Angular: use @Component decorator, standalone components, HttpClient for API calls, Angular Material for UI components, @angular/forms for reactive forms.
- For Vue 3: use Composition API (<script setup lang="ts">), Pinia for state management, vue-router for routing, PrimeVue or Vuetify for UI components.
- For Node.js/Express: use TypeScript, async/await, express.Router(), pg or Prisma for DB access.
- For FastAPI: use Pydantic models, SQLModel tables, APIRouter.
- When "ALREADY GENERATED FILES" are provided, use the EXACT same class/function
  names and import paths shown there.
- Never output TODO or pass-only stubs unless the file is intentionally minimal.
"""

_FILE_TEMPLATE = """\
Generate the complete content of this file:

FILE PATH: {path}
LANGUAGE: {lang}
PURPOSE: {purpose}

RELEVANT SPECIFICATION:
{context}
{cross_context}
Output the file content directly. No fences, no explanation.
"""

# Context snippet sizes per hint type (doc_key, max_chars)
_CONTEXT_CHARS: dict[str, tuple[str, int]] = {
    "backend_model":      ("database",    4000),
    "backend_schema":     ("api_spec",    3000),
    "backend_route":      ("api_spec",    4000),
    "backend_migration":  ("database",    3000),
    "frontend_type":      ("api_spec",    3000),
    "frontend_service":   ("api_spec",    3500),
    "frontend_component": ("screen_spec", 3500),
    "frontend_page":      ("screen_spec", 4000),
    "readme":             ("fsd",         2000),
}

# Which previously generated context_hints are useful as cross-file context
_CROSS_WANT: dict[str, set[str]] = {
    "backend_route":      {"backend_model", "backend_schema"},
    "backend_schema":     {"backend_model"},
    "frontend_service":   {"frontend_type"},
    "frontend_component": {"frontend_type", "frontend_service"},
    "frontend_page":      {"frontend_type", "frontend_service", "frontend_component"},
}

MAX_CROSS_CHARS = 2500


# -- Tech Design output parser ------------------------------------------------

_TASK_ROW_RE = re.compile(
    r"\|\s*TASK-\d+\s*\|\s*(\w+)\s*\|\s*`([^`]+)`\s*\|([^|]+)\|"
)


def _lang_from_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".py": "python", ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript", ".json": "json",
        ".yaml": "yaml", ".yml": "yaml", ".sql": "sql",
        ".html": "html", ".css": "css", ".md": "markdown",
        ".cs": "csharp", ".aspx": "aspx", ".cshtml": "csharp",
        ".razor": "csharp", ".csproj": "xml", ".sln": "text",
        ".config": "xml", ".resx": "xml", ".vb": "vb",
        ".sh": "text", ".txt": "text", ".toml": "text",
    }.get(ext, "text")


def _hint_from_domain_and_path(domain: str, path: str) -> str:
    p = path.lower()
    if domain == "backend":
        if any(x in p for x in ("model", "table", "entity")):
            return "backend_model"
        if any(x in p for x in ("schema", "dto", "request", "response")):
            return "backend_schema"
        if any(x in p for x in ("migration", "alembic", "version")):
            return "backend_migration"
        return "backend_route"
    if domain == "frontend":
        if any(x in p for x in ("type", "interface", "interface")):
            return "frontend_type"
        if any(x in p for x in ("service", "api", "client")):
            return "frontend_service"
        if any(x in p for x in ("component", "components", "widget", "ui/")):
            return "frontend_component"
        return "frontend_page"
    if domain == "database":
        return "backend_migration"
    return "readme"


def _parse_tech_design_tasks(markdown: str) -> list[_FileSpec]:
    """Extract file specs from Technical Design markdown task table."""
    specs: list[_FileSpec] = []
    seen: set[str] = set()
    for m in _TASK_ROW_RE.finditer(markdown):
        domain = m.group(1).strip()
        path = m.group(2).strip()
        description = m.group(3).strip()
        if not path or path in seen:
            continue
        seen.add(path)
        specs.append(_FileSpec(
            path=path,
            lang=_lang_from_path(path),
            purpose=description[:120],
            context_hint=_hint_from_domain_and_path(domain, path),
        ))
    return specs


def _parse_developer_instances(markdown: str) -> int:
    match = re.search(r"Recommended Developer Agent instances:\*\*\s*(\d+)", markdown)
    if not match:
        match = re.search(r"Developer Agent instances[^0-9]*(\d+)", markdown, re.IGNORECASE)
    if not match:
        return 1
    try:
        return max(1, min(MAX_DEVELOPER_LANES, int(match.group(1))))
    except ValueError:
        return 1


def _lane_key_for_file(spec: _FileSpec) -> str:
    path = spec.path.lower()
    hint = spec.context_hint.lower()
    if hint.startswith("frontend") or "/frontend/" in path or path.startswith("frontend/"):
        return "frontend"
    if hint in {"backend_model", "backend_route", "backend_schema"} or "/backend/" in path or path.startswith("backend/"):
        return "backend"
    return "platform"


def _backend_focus_for_stack(tech_stack: dict | None) -> str:
    t = _detect_stack_type(tech_stack)
    if t == "dotnet":
        return "ASP.NET Core Controllers, EF Core models and DbContext, Razor Views (.cshtml), service classes, and Program.cs configuration."
    if t in ("angular", "vue", "node"):
        backend = (tech_stack or {}).get("backend", "Node.js/Express")
        return f"{backend} routes, TypeScript models, database queries, middleware, and REST API implementation."
    return "FastAPI routes, SQLModel models, Pydantic schemas, Alembic migrations, and backend integration."


def _frontend_focus_for_stack(tech_stack: dict | None) -> str:
    t = _detect_stack_type(tech_stack)
    if t == "angular":
        return "Angular components, services, modules, routing, Angular Material forms, and API client (HttpClient)."
    if t == "vue":
        return "Vue 3 components (Composition API), Pinia stores, vue-router routes, and API client code."
    if t in ("node", "dotnet"):
        return "React/Vite pages, TypeScript components, hooks, API client, and Tailwind CSS styling."
    return "React/Vite pages, TypeScript components, hooks, API client code, and Tailwind CSS styling."


def _build_developer_lanes(files: list[_FileSpec], requested_instances: int, tech_stack: dict | None = None) -> list[_DeveloperLane]:
    requested_instances = max(1, min(MAX_DEVELOPER_LANES, requested_instances))
    if requested_instances == 1:
        return [_DeveloperLane(
            name="developer-agent",
            label="Full-stack Developer",
            focus="Generate all application files with end-to-end consistency.",
            files=list(files),
        )]

    lane_defs = [
        _DeveloperLane(
            name="developer-agent-backend",
            label="Backend Developer",
            focus=_backend_focus_for_stack(tech_stack),
        ),
        _DeveloperLane(
            name="developer-agent-frontend",
            label="Frontend Developer",
            focus=_frontend_focus_for_stack(tech_stack),
        ),
    ]
    if requested_instances >= 3:
        lane_defs.append(_DeveloperLane(
            name="developer-agent-platform",
            label="Platform Developer",
            focus="Project configuration, README, environment files, tests, infra, and cross-cutting glue.",
        ))

    by_name = {lane.name: lane for lane in lane_defs}
    for spec in files:
        key = _lane_key_for_file(spec)
        if key == "frontend":
            lane = by_name["developer-agent-frontend"]
        elif key == "backend":
            lane = by_name["developer-agent-backend"]
        elif "developer-agent-platform" in by_name:
            lane = by_name["developer-agent-platform"]
        else:
            lane = min(lane_defs, key=lambda item: len(item.files))
        lane.files.append(spec)

    return [lane for lane in lane_defs if lane.files]


# -- Markdown renderer for summary document -----------------------------------

def _render_summary(
    files: list[_FileSpec],
    results: list[tuple[str, bool]],
    project_id: str,
    doc_id: str,
    used_tech_design: bool,
    lanes: list[_DeveloperLane],
) -> str:
    ok = sum(1 for _, success in results if success)
    fail = len(results) - ok
    source = "Technical Design Agent" if used_tech_design else "LLM planning (fallback)"

    rows = ""
    status_by_path = {path: success for path, success in results}
    for spec in files:
        success = status_by_path.get(spec.path, False)
        status = "OK" if success else "FAILED"
        rows += f"| `{spec.path}` | {spec.lang} | {spec.purpose[:60]} | {status} |\n"

    lane_rows = "\n".join(
        f"| {idx} | {lane.name} | {lane.label} | {len(lane.files)} | {lane.focus} |"
        for idx, lane in enumerate(lanes, start=1)
    )

    return f"""\
# Generated Code Summary

**Project ID:** `{project_id}`
**Document ID:** `{doc_id}`
**Generated By:** Developer Agent
**Pipeline Step:** 7 of 12
**File Plan Source:** {source}
**Developer Fan-out:** {len(lanes)} lane{'s' if len(lanes) != 1 else ''}
**Status:** Draft -- Awaiting Code Review

---

## Generation Results

| Files OK | Files Failed | Total |
|---|---|---|
| {ok} | {fail} | {len(results)} |

## Developer Fan-out Plan

| Lane | Agent | Role | Files | Focus |
|---:|---|---|---:|---|
{lane_rows}

## File List

| Path | Language | Purpose | Status |
|---|---|---|---|
{rows}

---

## Output Location

Files are written to: `generated_app/` inside the project workspace.

{"**Warning:** Some files failed to generate. Review and regenerate manually." if fail else "All files generated successfully."}
"""


# -- Agent runner -------------------------------------------------------------

class DevAgentRunner:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, run_id: uuid.UUID) -> None:
        step: Optional[PipelineStep] = None
        agent_row: Optional[Agent] = None
        lane_agent_rows: list[Agent] = []

        try:
            run = self._get_run(run_id)

            if run.status == PipelineRunStatus.failed:
                logger.info("DevAgent skipped -- run %s already failed", run_id)
                return

            step = self._get_step(run_id)
            agent_row = self._get_agent_row()
            model = agent_row.model_name if agent_row else None

            run.status = PipelineRunStatus.running
            run.current_step = STEP_NAME
            step.status = PipelineStepStatus.running
            step.started_at = datetime.now(UTC)
            if agent_row:
                agent_row.status = AgentStatus.working
                agent_row.updated_at = datetime.now(UTC)
            self.session.commit()

            fsd_doc, arch_doc, db_doc, api_doc, screen_doc = \
                self._load_source_documents(run.project_id)

            docs = {
                "fsd":          fsd_doc.content_markdown,
                "architecture": arch_doc.content_markdown,
                "database":     db_doc.content_markdown,
                "api_spec":     api_doc.content_markdown,
                "screen_spec":  screen_doc.content_markdown,
            }

            # Load project tech stack for stack-aware code generation
            project = self.session.get(Project, run.project_id)
            tech_stack: dict | None = project.tech_stack if project else None
            logger.info("DevAgent tech_stack=%s run=%s", tech_stack, run_id)

            # Phase 1: resolve file plan (Tech Design output or LLM fallback)
            files, used_tech_design = self._resolve_file_plan(docs, model, run.project_id, tech_stack)
            logger.info(
                "DevAgent file plan: %d files (tech_design=%s) run=%s",
                len(files), used_tech_design, run_id,
            )
            lanes = _build_developer_lanes(files, self._recommended_instances(run.project_id), tech_stack)
            lane_agent_rows = self._get_lane_agent_rows([lane.name for lane in lanes])
            for lane_agent in lane_agent_rows:
                lane_agent.status = AgentStatus.working
                lane_agent.updated_at = datetime.now(UTC)
            self.session.commit()

            # Phase 2: generate each file with cross-file context
            out_dir = self._get_output_dir(run.project_id)
            results: list[tuple[str, bool]] = []
            generated: list[tuple[_FileSpec, str]] = []

            for lane in lanes:
                logger.info(
                    "DevAgent lane %s generating %d file(s) run=%s",
                    lane.name, len(lane.files), run_id,
                )
                for spec in lane.files:
                    content = self._generate_file(spec, docs, model, generated, lane, tech_stack)
                    if content:
                        self._write_file(out_dir, spec.path, content)
                        generated.append((spec, content))
                        results.append((spec.path, True))
                        logger.info("DevAgent lane %s generated %s (%d chars)", lane.name, spec.path, len(content))
                    else:
                        results.append((spec.path, False))
                        logger.warning("DevAgent lane %s failed to generate %s", lane.name, spec.path)

            # Save summary document
            doc_id = uuid.uuid4()
            pid = str(run.project_id)
            summary_md = _render_summary(files, results, pid, str(doc_id), used_tech_design, lanes)

            summary_doc = Document(
                id=doc_id,
                project_id=run.project_id,
                document_type=DocumentType.code_task_list,
                title="Generated Code Summary",
                content_markdown=summary_md,
                version=1,
                status=DocumentStatus.review,
                created_by_agent_id=agent_row.id if agent_row else None,
            )
            self.session.add(summary_doc)
            self.session.flush()

            step.status = PipelineStepStatus.completed
            step.agent_id = agent_row.id if agent_row else None
            step.output_document_id = summary_doc.id
            step.completed_at = datetime.now(UTC)

            run.status = PipelineRunStatus.waiting_for_user
            run.current_step = STEP_NAME

            if agent_row:
                agent_row.status = AgentStatus.done
                agent_row.updated_at = datetime.now(UTC)
            for lane_agent in lane_agent_rows:
                lane_agent.status = AgentStatus.done
                lane_agent.updated_at = datetime.now(UTC)

            ok_count = sum(1 for _, s in results if s)
            self._log_activity(
                run.project_id, agent_row,
                f"Code generation complete: {ok_count}/{len(files)} files generated "
                f"to generated_app/. Plan source: {'TechDesign' if used_tech_design else 'LLM fallback'}. "
                f"Developer fan-out lanes: {len(lanes)}. Awaiting code review.",
            )
            self.session.commit()
            logger.info(
                "DevAgent completed run=%s files=%d/%d tech_design=%s",
                run_id, ok_count, len(files), used_tech_design,
            )

        except Exception as exc:
            logger.exception("DevAgent failed run=%s: %s", run_id, exc)
            self.session.rollback()
            try:
                run = self.session.get(PipelineRun, run_id)
                if run:
                    run.status = PipelineRunStatus.failed
                if step:
                    step.status = PipelineStepStatus.failed
                    step.error_message = str(exc)[:2000]
                if agent_row:
                    agent_row.status = AgentStatus.error
                    agent_row.updated_at = datetime.now(UTC)
                for lane_agent in lane_agent_rows:
                    lane_agent.status = AgentStatus.error
                    lane_agent.updated_at = datetime.now(UTC)
                self.session.commit()
            except Exception:
                logger.exception("Failed to persist failure state for run=%s", run_id)

    # -- Phase 1: file plan resolution ----------------------------------------

    def _resolve_file_plan(
        self,
        docs: dict[str, str],
        model: str | None,
        project_id: uuid.UUID,
        tech_stack: dict | None = None,
    ) -> tuple[list[_FileSpec], bool]:
        """Return (file_list, used_tech_design_flag).

        Prefers Technical Design Agent output; falls back to LLM planning.
        Essential config files are always appended.
        """
        tech_doc = self._load_tech_design(project_id)
        used_tech = False
        files: list[_FileSpec] = []

        if tech_doc:
            parsed = _parse_tech_design_tasks(tech_doc.content_markdown)
            if parsed:
                files = parsed[:MAX_FILES]
                used_tech = True
                logger.info(
                    "DevAgent parsed %d tasks from Technical Design doc", len(parsed)
                )

        if not files:
            logger.info("DevAgent falling back to LLM file planning")
            plan = self._plan_files_llm(docs, model, tech_stack)
            files = plan.files[:MAX_FILES]

        # Always add essential config files (stack-aware)
        existing_paths = {f.path for f in files}
        for ess in _essential_specs_for_stack(tech_stack):
            if ess.path not in existing_paths:
                files.append(ess)

        return files, used_tech

    def _plan_files_llm(
        self,
        docs: dict[str, str],
        model: str | None,
        tech_stack: dict | None = None,
    ) -> _FilePlan:
        """Fallback: ask LLM to produce the file plan."""
        prompt = _PLAN_TEMPLATE.format(
            fsd=_esc(_trunc(docs["fsd"], 2500)),
            architecture=_esc(_trunc(docs["architecture"], 2000)),
            database=_esc(_trunc(docs["database"], 2500)),
            api_spec=_esc(_trunc(docs["api_spec"], 2500)),
            screen_spec=_esc(_trunc(docs["screen_spec"], 1500)),
        )
        raw = _llm.call_ollama(
            system_prompt=_PLAN_SYSTEM_PROMPT.format(
                max_files=MAX_FILES,
                tech_stack_info=_tech_stack_description(tech_stack),
                lang_options=_lang_options_for_stack(tech_stack),
            ),
            user_prompt=prompt,
            model=model,
            timeout=PLAN_TIMEOUT,
            response_format="json",
        )
        data = _llm.extract_json(raw)
        return _FilePlan.model_validate(data)

    # -- Phase 2: file generation ---------------------------------------------

    def _generate_file(
        self,
        spec: _FileSpec,
        docs: dict[str, str],
        model: str | None,
        generated: list[tuple["_FileSpec", str]],
        lane: _DeveloperLane,
        tech_stack: dict | None = None,
    ) -> str | None:
        context = self._build_context(spec, docs)
        cross = self._build_cross_context(spec, generated)
        cross_section = (
            f"\nALREADY GENERATED FILES (use these exact import paths and class names):\n{cross}\n"
            if cross else ""
        )
        lane_context = (
            f"\nDEVELOPER LANE:\n"
            f"- Agent: {lane.name}\n"
            f"- Role: {lane.label}\n"
            f"- Focus: {lane.focus}\n"
        )

        prompt = _FILE_TEMPLATE.format(
            path=spec.path,
            lang=spec.lang,
            purpose=spec.purpose,
            context=context + lane_context,
            cross_context=cross_section,
        )

        for attempt in range(2):
            try:
                raw = _llm.call_ollama(
                    system_prompt=_FILE_SYSTEM_PROMPT.format(
                        tech_stack_info=_tech_stack_description(tech_stack),
                    ),
                    user_prompt=prompt,
                    model=model,
                    timeout=FILE_TIMEOUT,
                    response_format=None,
                )
                content = _llm.strip_code_fences(raw)
                if len(content) >= MIN_FILE_CHARS:
                    return content
                logger.warning(
                    "File %s: content too short (%d chars), attempt %d",
                    spec.path, len(content), attempt + 1,
                )
            except Exception as exc:
                logger.warning(
                    "File %s generation error (attempt %d): %s",
                    spec.path, attempt + 1, exc,
                )
        return None

    def _build_context(self, spec: _FileSpec, docs: dict[str, str]) -> str:
        mapping = _CONTEXT_CHARS.get(spec.context_hint, ("fsd", 2000))
        primary_key, primary_chars = mapping
        primary = _trunc(docs.get(primary_key, ""), primary_chars)
        secondary = ""
        if spec.context_hint not in ("readme",) and primary_key != "fsd":
            secondary = f"\n\nFSD EXCERPT:\n{_trunc(docs['fsd'], 1200)}"
        return primary + secondary

    def _build_cross_context(
        self,
        spec: _FileSpec,
        generated: list[tuple["_FileSpec", str]],
    ) -> str:
        """Return snippets of already-generated files relevant to this file."""
        want = _CROSS_WANT.get(spec.context_hint, set())
        if not want:
            return ""

        parts: list[str] = []
        total = 0
        for prev_spec, prev_content in generated:
            if prev_spec.context_hint not in want:
                continue
            snippet = f"--- {prev_spec.path} ---\n{prev_content[:800]}\n"
            if total + len(snippet) > MAX_CROSS_CHARS:
                break
            parts.append(snippet)
            total += len(snippet)

        return "\n".join(parts)

    # -- File writing ---------------------------------------------------------

    def _write_file(self, out_dir: str, rel_path: str, content: str) -> None:
        safe_rel = re.sub(r"\.\.+[/\\]", "", rel_path).lstrip("/\\")
        full_path = os.path.join(out_dir, safe_rel)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _get_output_dir(self, project_id: uuid.UUID) -> str:
        project = self.session.get(Project, project_id)
        raw_path = (project.workspace_path if project else None) or "/workspace"
        container_path = re.sub(
            r"^[A-Za-z]:[/\\]workspace", "/workspace", raw_path, flags=re.IGNORECASE
        )
        if not container_path.startswith("/workspace"):
            container_path = "/workspace"
        safe_name = re.sub(r"[^\w\-]", "_", project.name if project else "project")
        return os.path.join(container_path, safe_name, "generated_app")

    # -- DB helpers -----------------------------------------------------------

    def _get_run(self, run_id: uuid.UUID) -> PipelineRun:
        run = self.session.get(PipelineRun, run_id)
        if not run:
            raise ValueError(f"PipelineRun {run_id} not found")
        return run

    def _get_step(self, run_id: uuid.UUID) -> PipelineStep:
        step = self.session.exec(
            select(PipelineStep).where(
                PipelineStep.pipeline_run_id == run_id,
                PipelineStep.step_name == STEP_NAME,
            )
        ).first()
        if not step:
            raise ValueError(f"PipelineStep {STEP_NAME} not found for run {run_id}")
        return step

    def _get_agent_row(self) -> Optional[Agent]:
        return self.session.exec(
            select(Agent).where(Agent.name == AGENT_NAME)
        ).first()

    def _get_lane_agent_rows(self, names: list[str]) -> list[Agent]:
        if not names:
            return []
        return list(self.session.exec(select(Agent).where(Agent.name.in_(names))).all())  # type: ignore[union-attr]

    def _load_tech_design(self, project_id: uuid.UUID) -> Optional[Document]:
        return self.session.exec(
            select(Document)
            .where(
                Document.project_id == project_id,
                Document.document_type == DocumentType.technical_design,
            )
            .order_by(Document.created_at.desc())  # type: ignore[union-attr]
        ).first()

    def _recommended_instances(self, project_id: uuid.UUID) -> int:
        tech_doc = self._load_tech_design(project_id)
        if not tech_doc:
            return 1
        return _parse_developer_instances(tech_doc.content_markdown)

    def _load_source_documents(
        self, project_id: uuid.UUID
    ) -> tuple[Document, Document, Document, Document, Document]:
        def _latest(doc_type: DocumentType) -> Optional[Document]:
            return self.session.exec(
                select(Document)
                .where(
                    Document.project_id == project_id,
                    Document.document_type == doc_type,
                )
                .order_by(Document.created_at.desc())  # type: ignore[union-attr]
            ).first()

        fsd    = _latest(DocumentType.fsd)
        arch   = _latest(DocumentType.architecture_design)
        db     = _latest(DocumentType.database_design)
        api    = _latest(DocumentType.api_spec)
        screen = _latest(DocumentType.screen_spec)

        missing = [
            name for name, doc in [
                ("FSD", fsd), ("Architecture", arch), ("Database", db),
                ("API Spec", api), ("Screen Spec", screen),
            ] if not doc
        ]
        if missing:
            raise ValueError(f"Missing source documents: {', '.join(missing)}")

        return fsd, arch, db, api, screen  # type: ignore[return-value]

    def _log_activity(
        self, project_id: uuid.UUID, agent_row: Optional[Agent], message: str
    ) -> None:
        self.session.add(ActivityLog(
            project_id=project_id,
            agent_id=agent_row.id if agent_row else None,
            event_type=EventType.document_created,
            message=message,
        ))
