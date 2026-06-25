import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, FolderOpen, ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";
import { projectApi } from "@/services/projectApi";
import type { ProjectCreate, TechStackConfig } from "@/types/project";

// ── Preset definitions (FR-01, FR-06, FR-07) ──────────────────────────────────

interface Preset {
  id: string;
  label: string;
  description: string;
  stack: Partial<TechStackConfig>;
}

const PRESETS: Preset[] = [
  {
    id: "react-dotnet",
    label: "React + .NET Core",
    description: "SPA frontend with .NET 9 Web API backend",
    stack: { frontend: "React", frontend_version: "19", backend: "ASP.NET Core", backend_version: "9", language: "TypeScript / C#", database: "SQL Server", database_version: "2022", app_type: "Web Application", cloud: "Azure", auth: "JWT", orm: "Entity Framework Core", container: "Docker", testing: "xUnit / Vitest", api_docs: "Swagger / OpenAPI" },
  },
  {
    id: "react-nodejs",
    label: "React + Node.js",
    description: "SPA frontend with Node.js / Express backend",
    stack: { frontend: "React", frontend_version: "19", backend: "Node.js / Express", backend_version: "22", language: "TypeScript", database: "PostgreSQL", database_version: "17", app_type: "Web Application", cloud: "AWS", auth: "JWT", orm: "Prisma", container: "Docker", testing: "Jest / Vitest", api_docs: "Swagger / OpenAPI" },
  },
  {
    id: "angular-dotnet",
    label: "Angular + .NET Core",
    description: "Angular SPA with .NET 9 Web API backend",
    stack: { frontend: "Angular", frontend_version: "19", backend: "ASP.NET Core", backend_version: "9", language: "TypeScript / C#", database: "SQL Server", database_version: "2022", app_type: "Web Application", cloud: "Azure", auth: "JWT", orm: "Entity Framework Core", container: "Docker", testing: "xUnit / Jasmine", api_docs: "Swagger / OpenAPI" },
  },
  {
    id: "vue-nodejs",
    label: "Vue + Node.js",
    description: "Vue 3 SPA with Node.js backend",
    stack: { frontend: "Vue", frontend_version: "3", backend: "Node.js / Express", backend_version: "22", language: "TypeScript", database: "PostgreSQL", database_version: "17", app_type: "Web Application", cloud: "AWS", auth: "JWT", orm: "Prisma", container: "Docker", testing: "Jest / Vitest", api_docs: "Swagger / OpenAPI" },
  },
  {
    id: "aspnet-mvc",
    label: "ASP.NET MVC",
    description: "Server-side rendered app with Razor Pages",
    stack: { frontend: "ASP.NET Core MVC / Razor Pages", frontend_version: "9", backend: "ASP.NET Core", backend_version: "9", language: "C#", database: "SQL Server", database_version: "2022", app_type: "Web Application", cloud: "Azure", auth: "ASP.NET Identity", orm: "Entity Framework Core", container: "Docker", testing: "xUnit", api_docs: "Swagger / OpenAPI" },
  },
  {
    id: "aspnet-webforms",
    label: "ASP.NET Web Forms",
    description: "Classic .NET Framework Web Forms (ASPX pages)",
    stack: { frontend: "ASP.NET Web Forms", frontend_version: "4.8", backend: "ASP.NET Framework", backend_version: "4.8", language: "C#", database: "SQL Server", database_version: "2022", app_type: "Web Application", cloud: "Azure", auth: "ASP.NET Identity", orm: "Entity Framework 6", container: "Docker (Windows Container)", testing: "MSTest", api_docs: "None" },
  },
  {
    id: "custom",
    label: "Custom Stack",
    description: "Define your own technology combination",
    stack: {},
  },
];

// ── Smart recommendations (FR-04, FR-05) ─────────────────────────────────────

const BACKEND_FOR_FRONTEND: Record<string, string[]> = {
  "React":                            ["ASP.NET Core", "Node.js / Express", "FastAPI", "NestJS"],
  "Angular":                          ["ASP.NET Core", "Node.js / Express", "NestJS"],
  "Vue":                              ["Node.js / Express", "ASP.NET Core", "NestJS"],
  "ASP.NET Core MVC / Razor Pages":   ["ASP.NET Core"],
  "ASP.NET Web Forms":                ["ASP.NET Framework"],
};

const DATABASE_FOR_BACKEND: Record<string, string[]> = {
  "ASP.NET Core":      ["SQL Server", "PostgreSQL", "MySQL"],
  "ASP.NET Framework": ["SQL Server"],
  "Node.js / Express": ["PostgreSQL", "MySQL", "MongoDB"],
  "FastAPI":           ["PostgreSQL", "MySQL"],
  "NestJS":            ["PostgreSQL", "MySQL", "MongoDB"],
};

const ALL_BACKENDS  = ["ASP.NET Core", "ASP.NET Framework", "Node.js / Express", "FastAPI", "NestJS", "Other / Custom"];
const ALL_DATABASES = ["SQL Server", "PostgreSQL", "MySQL", "MongoDB", "Other / Custom"];
const ALL_FRONTENDS = PRESETS.filter(p => p.id !== "custom").map(p => p.stack.frontend as string).filter(Boolean);

// FR-07 version options
const VERSIONS: Record<string, string[]> = {
  "React":                          ["19", "18"],
  "Angular":                        ["19", "18", "17"],
  "Vue":                            ["3", "2"],
  "ASP.NET Core MVC / Razor Pages": ["9", "8"],
  "ASP.NET Web Forms":              ["4.8", "4.7"],
  "ASP.NET Core":                   ["9", "8"],
  "ASP.NET Framework":              ["4.8", "4.7", "4.6"],
  "Node.js / Express":              ["22", "20"],
  "FastAPI":                        ["0.115", "0.110"],
  "NestJS":                         ["10", "9"],
  "SQL Server":                     ["2022", "2019"],
  "PostgreSQL":                     ["17", "16"],
  "MySQL":                          ["8.4", "8.0"],
  "MongoDB":                        ["7", "6"],
};

// FR-08 incompatibility rules
interface CompatWarning { condition: (s: TechStackConfig) => boolean; message: string; suggestion: string; }
const COMPAT_WARNINGS: CompatWarning[] = [
  {
    condition: s => s.frontend === "React" && s.backend === "ASP.NET Framework",
    message: "React + ASP.NET Framework is not recommended.",
    suggestion: "Consider React + ASP.NET Core instead.",
  },
  {
    condition: s => s.frontend === "ASP.NET Web Forms" && s.backend !== "ASP.NET Framework",
    message: "ASP.NET Web Forms requires ASP.NET Framework backend.",
    suggestion: "Change backend to ASP.NET Framework 4.8.",
  },
  {
    condition: s => s.frontend === "Angular" && s.backend === "ASP.NET Framework",
    message: "Angular + ASP.NET Framework is not recommended.",
    suggestion: "Consider Angular + ASP.NET Core instead.",
  },
];

// ── Stack Preview (FR-02) ─────────────────────────────────────────────────────

function StackPreview({ stack }: { stack: TechStackConfig }) {
  const items: [string, string | undefined][] = [
    ["Frontend",   stack.frontend ? `${stack.frontend}${stack.frontend_version ? ` ${stack.frontend_version}` : ""}` : undefined],
    ["Backend",    stack.backend  ? `${stack.backend}${stack.backend_version   ? ` ${stack.backend_version}`  : ""}` : undefined],
    ["Language",   stack.language],
    ["Database",   stack.database ? `${stack.database}${stack.database_version ? ` ${stack.database_version}` : ""}` : undefined],
    ["App Type",   stack.app_type],
    ["Cloud",      stack.cloud],
    ["Auth",       stack.auth],
    ["ORM",        stack.orm],
    ["Container",  stack.container],
    ["Testing",    stack.testing],
    ["API Docs",   stack.api_docs],
  ];
  const filled = items.filter(([, v]) => v);
  if (filled.length === 0) return null;

  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">Stack Preview</p>
      <div className="grid grid-cols-2 gap-x-6 gap-y-1.5">
        {filled.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-2 text-sm">
            <span className="text-muted-foreground shrink-0">{label}</span>
            <span className="font-medium text-right">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Compatibility Warning (FR-08) ─────────────────────────────────────────────

function CompatWarning({ stack, onProceed }: { stack: TechStackConfig; onProceed: () => void }) {
  const warning = COMPAT_WARNINGS.find(w => w.condition(stack));
  if (!warning) return null;
  return (
    <div className="rounded-lg border border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 p-3 text-sm">
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-yellow-600 shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-medium text-yellow-800 dark:text-yellow-300">⚠ {warning.message}</p>
          <p className="text-yellow-700 dark:text-yellow-400 mt-0.5">Recommended: {warning.suggestion}</p>
        </div>
      </div>
      <button onClick={onProceed} className="mt-2 text-xs text-yellow-700 dark:text-yellow-400 underline hover:no-underline">
        Proceed Anyway
      </button>
    </div>
  );
}

// ── Helper select ─────────────────────────────────────────────────────────────

function Field({ label, value, onChange, options, placeholder, disabled }: {
  label: string; value: string; onChange: (v: string) => void;
  options: string[]; placeholder?: string; disabled?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1 text-muted-foreground">{label}</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        className="w-full rounded-md border px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring bg-background disabled:opacity-50"
      >
        <option value="">{placeholder ?? "— Select —"}</option>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function NewProject() {
  const navigate = useNavigate();
  const [name, setName]               = useState("");
  const [description, setDescription] = useState("");
  const [workspacePath, setWorkspacePath] = useState("D:\\workspace");
  const [selectedPreset, setSelectedPreset] = useState<string>("react-dotnet");
  const [showCustomize, setShowCustomize]   = useState(false);
  const [warningDismissed, setWarningDismissed] = useState(false);

  // Start with React + .NET Core preset
  const defaultStack = PRESETS.find(p => p.id === "react-dotnet")!.stack;
  const [stack, setStack] = useState<TechStackConfig>({ ...defaultStack });

  const setField = (key: keyof TechStackConfig) => (v: string) =>
    setStack(prev => ({ ...prev, [key]: v || undefined }));

  function applyPreset(id: string) {
    setSelectedPreset(id);
    setWarningDismissed(false);
    const preset = PRESETS.find(p => p.id === id)!;
    setStack({ preset: id, ...preset.stack });
    if (id === "custom") setShowCustomize(true);
  }

  // Smart recommendations
  const recommendedBackends  = stack.frontend ? (BACKEND_FOR_FRONTEND[stack.frontend]  ?? ALL_BACKENDS)  : ALL_BACKENDS;
  const recommendedDatabases = stack.backend  ? (DATABASE_FOR_BACKEND[stack.backend]   ?? ALL_DATABASES) : ALL_DATABASES;
  const frontendVersions     = stack.frontend ? (VERSIONS[stack.frontend] ?? []) : [];
  const backendVersions      = stack.backend  ? (VERSIONS[stack.backend]  ?? []) : [];
  const databaseVersions     = stack.database ? (VERSIONS[stack.database] ?? []) : [];

  const hasWarning = !warningDismissed && COMPAT_WARNINGS.some(w => w.condition(stack));

  const createMutation = useMutation({
    mutationFn: (data: ProjectCreate) => projectApi.create(data),
    onSuccess: (project) => navigate(`/projects/${project.id}`),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    const cleanStack = Object.fromEntries(Object.entries(stack).filter(([, v]) => v));
    createMutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      created_by: "user",
      workspace_path: workspacePath.trim() || "D:\\workspace",
      tech_stack: Object.keys(cleanStack).length > 0 ? cleanStack : undefined,
    });
  }

  const safeProjectName = name.trim().replace(/[^\w\-]/g, "_") || "project_name";
  const effectivePath   = `${workspacePath.trim() || "D:\\workspace"}\\${safeProjectName}`;

  return (
    <div className="max-w-2xl">
      <Link to="/projects" className="mb-6 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Projects
      </Link>
      <h2 className="text-lg font-semibold mb-6">New Project</h2>

      <form onSubmit={handleSubmit} className="space-y-5">

        {/* ── Project Info ── */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Project Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text" value={name} onChange={e => setName(e.target.value)}
              placeholder="e.g. HR System Upgrade 2026"
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              required autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description} onChange={e => setDescription(e.target.value)}
              rows={2} placeholder="Brief description of the project scope or objective…"
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-y"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              <FolderOpen className="inline h-3.5 w-3.5 mr-1" />Workspace Output Path
            </label>
            <input
              type="text" value={workspacePath} onChange={e => setWorkspacePath(e.target.value)}
              placeholder="D:\workspace"
              className="w-full rounded-md border px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Output path: <span className="font-mono text-foreground">{effectivePath}</span>
            </p>
          </div>
        </div>

        {/* ── Tech Stack Preset (FR-01) ── */}
        <div className="rounded-lg border p-4 space-y-4">
          <div>
            <p className="text-sm font-semibold">Tech Stack Preset</p>
            <p className="text-xs text-muted-foreground mt-0.5">Choose a preset to auto-fill the stack. Agents use this context to generate accurate code and documents.</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {PRESETS.map(preset => (
              <label
                key={preset.id}
                className={`flex items-start gap-2.5 rounded-lg border p-3 cursor-pointer transition-colors ${
                  selectedPreset === preset.id
                    ? "border-primary bg-primary/5"
                    : "hover:bg-accent"
                }`}
              >
                <input
                  type="radio" name="preset" value={preset.id}
                  checked={selectedPreset === preset.id}
                  onChange={() => applyPreset(preset.id)}
                  className="mt-0.5 accent-primary"
                />
                <div>
                  <p className="text-sm font-medium leading-tight">{preset.label}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{preset.description}</p>
                </div>
              </label>
            ))}
          </div>

          {/* ── Stack Preview (FR-02) ── */}
          {selectedPreset !== "custom" && <StackPreview stack={stack} />}

          {/* ── Compatibility Warning (FR-08) ── */}
          {hasWarning && <CompatWarning stack={stack} onProceed={() => setWarningDismissed(true)} />}

          {/* ── Customize Stack (FR-03) ── */}
          <div className="border-t pt-3">
            <button
              type="button"
              onClick={() => setShowCustomize(v => !v)}
              className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              {showCustomize ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              Customize Stack
            </button>

            {showCustomize && (
              <div className="mt-4 space-y-4">
                {/* Core (FR-04, FR-05, FR-07) */}
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Core Stack</p>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Frontend" value={stack.frontend ?? ""} onChange={v => { setField("frontend")(v); setField("backend")(""); setField("database")(""); setWarningDismissed(false); }} options={ALL_FRONTENDS} />
                    {frontendVersions.length > 0 && <Field label="Frontend Version" value={stack.frontend_version ?? ""} onChange={setField("frontend_version")} options={frontendVersions} />}
                    <Field label="Backend" value={stack.backend ?? ""} onChange={v => { setField("backend")(v); setField("database")(""); setWarningDismissed(false); }} options={recommendedBackends} />
                    {backendVersions.length > 0 && <Field label="Backend Version" value={stack.backend_version ?? ""} onChange={setField("backend_version")} options={backendVersions} />}
                    <Field label="Database" value={stack.database ?? ""} onChange={setField("database")} options={recommendedDatabases} />
                    {databaseVersions.length > 0 && <Field label="Database Version" value={stack.database_version ?? ""} onChange={setField("database_version")} options={databaseVersions} />}
                    <Field label="Application Type" value={stack.app_type ?? ""} onChange={setField("app_type")} options={["Web Application", "Mobile App", "Web + Mobile App", "Desktop App", "API Only"]} />
                    <div>
                      <label className="block text-xs font-medium mb-1 text-muted-foreground">Language</label>
                      <input
                        type="text" value={stack.language ?? ""} onChange={e => setField("language")(e.target.value)}
                        placeholder="Auto-filled from preset"
                        className="w-full rounded-md border px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                      />
                    </div>
                  </div>
                </div>

                {/* Infrastructure (FR-09) */}
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Infrastructure & Tooling</p>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Cloud Provider" value={stack.cloud ?? ""} onChange={setField("cloud")} options={["Azure", "AWS", "GCP", "On-Premise", "None"]} />
                    <Field label="Authentication" value={stack.auth ?? ""} onChange={setField("auth")} options={["JWT", "ASP.NET Identity", "OAuth2 / OIDC", "API Key", "None"]} />
                    <Field label="ORM" value={stack.orm ?? ""} onChange={setField("orm")} options={["Entity Framework Core", "Entity Framework 6", "Prisma", "TypeORM", "SQLAlchemy", "None"]} />
                    <Field label="Container" value={stack.container ?? ""} onChange={setField("container")} options={["Docker", "Docker (Windows Container)", "Kubernetes", "None"]} />
                    <Field label="Testing Framework" value={stack.testing ?? ""} onChange={setField("testing")} options={["xUnit / Vitest", "xUnit / Jest", "MSTest", "NUnit", "Jest / Vitest", "None"]} />
                    <Field label="API Documentation" value={stack.api_docs ?? ""} onChange={setField("api_docs")} options={["Swagger / OpenAPI", "Redoc", "None"]} />
                    <Field label="Cache" value={stack.cache ?? ""} onChange={setField("cache")} options={["Redis", "Memcached", "In-Memory", "None"]} />
                    <Field label="Queue" value={stack.queue ?? ""} onChange={setField("queue")} options={["RabbitMQ", "Azure Service Bus", "AWS SQS", "None"]} />
                    <Field label="Logging" value={stack.logging ?? ""} onChange={setField("logging")} options={["Serilog", "NLog", "Winston", "Pino", "None"]} />
                    <Field label="Monitoring" value={stack.monitoring ?? ""} onChange={setField("monitoring")} options={["Azure Monitor", "Prometheus + Grafana", "Datadog", "None"]} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Errors ── */}
        {createMutation.isError && (
          <p className="text-sm text-destructive">
            {(createMutation.error as Error)?.message ?? "Failed to create project."}
          </p>
        )}

        {/* ── Actions ── */}
        <div className="flex gap-3 pt-1">
          <button
            type="submit"
            disabled={createMutation.isPending || !name.trim() || hasWarning}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? "Creating…" : "Create Project"}
          </button>
          <Link to="/projects" className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
