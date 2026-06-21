import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, FolderOpen } from "lucide-react";
import { projectApi } from "@/services/projectApi";
import type { ProjectCreate, TechStackConfig } from "@/types/project";

const FRONTEND_OPTIONS = ["React", "ASPX", "ASP.NET Web Forms", "ASP.NET MVC / Razor", "Other / Custom"];
const BACKEND_OPTIONS  = ["Node.js", ".NET / ASP.NET Core", "ASP.NET Framework", "Other / Custom"];
const DATABASE_OPTIONS = ["PostgreSQL", "Microsoft SQL Server", "MySQL"];
const APP_TYPE_OPTIONS = ["Web App", "Mobile App", "Web + Mobile App"];

function SelectField({
  label, value, onChange, options, placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  placeholder?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring bg-background"
      >
        <option value="">{placeholder ?? "— Select —"}</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}

export default function NewProject() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [workspacePath, setWorkspacePath] = useState("D:\\workspace");

  const [techStack, setTechStack] = useState<TechStackConfig>({
    frontend: "",
    backend: "",
    database: "",
    app_type: "",
  });

  const setTech = (key: keyof TechStackConfig) => (v: string) =>
    setTechStack((prev) => ({ ...prev, [key]: v }));

  const createMutation = useMutation({
    mutationFn: (data: ProjectCreate) => projectApi.create(data),
    onSuccess: (project) => navigate(`/projects/${project.id}`),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const cleanStack: TechStackConfig = Object.fromEntries(
      Object.entries(techStack).filter(([, v]) => v && v.length > 0)
    );

    createMutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      created_by: "user",
      workspace_path: workspacePath.trim() || "D:\\workspace",
      tech_stack: Object.keys(cleanStack).length > 0 ? cleanStack : undefined,
    });
  };

  const safeProjectName = name.trim().replace(/[^\w\-]/g, "_") || "project_name";
  const effectivePath = `${workspacePath.trim() || "D:\\workspace"}\\${safeProjectName}`;

  return (
    <div className="max-w-lg">
      <Link
        to="/projects"
        className="mb-6 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to Projects
      </Link>

      <h2 className="text-lg font-semibold mb-6">New Project</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Project Name <span className="text-destructive">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. HR System Upgrade 2026"
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            required
            autoFocus
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="Brief description of the project scope or objective…"
            className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            <FolderOpen className="inline h-3.5 w-3.5 mr-1" />
            Workspace Output Path
          </label>
          <input
            type="text"
            value={workspacePath}
            onChange={(e) => setWorkspacePath(e.target.value)}
            placeholder="D:\workspace"
            className="w-full rounded-md border px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <p className="mt-1 text-xs text-muted-foreground">
            Dev Agent output will be written to:{" "}
            <span className="font-mono text-foreground">{effectivePath}</span>
          </p>
        </div>

        {/* Tech Stack Configuration */}
        <div className="rounded-lg border p-4 space-y-3">
          <p className="text-sm font-medium">Tech Stack Configuration</p>
          <p className="text-xs text-muted-foreground -mt-1">
            Agents use this to generate code, test cases, and documents tailored to your stack.
          </p>

          <div className="grid grid-cols-2 gap-3">
            <SelectField
              label="Frontend"
              value={techStack.frontend ?? ""}
              onChange={setTech("frontend")}
              options={FRONTEND_OPTIONS}
            />
            <SelectField
              label="Backend"
              value={techStack.backend ?? ""}
              onChange={setTech("backend")}
              options={BACKEND_OPTIONS}
            />
            <SelectField
              label="Database"
              value={techStack.database ?? ""}
              onChange={setTech("database")}
              options={DATABASE_OPTIONS}
            />
            <SelectField
              label="Application Type"
              value={techStack.app_type ?? ""}
              onChange={setTech("app_type")}
              options={APP_TYPE_OPTIONS}
            />
          </div>
        </div>

        {createMutation.isError && (
          <p className="text-sm text-destructive">
            {(createMutation.error as Error)?.message ?? "Failed to create project."}
          </p>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={createMutation.isPending || !name.trim()}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? "Creating…" : "Create Project"}
          </button>
          <Link
            to="/projects"
            className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
