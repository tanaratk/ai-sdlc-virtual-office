import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bot,
  Building2,
  CheckCircle2,
  Clock3,
  FileText,
  FolderOpen,
  GitBranch,
  Plus,
  Radio,
  Settings,
} from "lucide-react";
import { projectApi } from "@/services/projectApi";
import { cn } from "@/lib/utils";

const PIPELINE_STEPS = [
  "Req",
  "Gap",
  "BA",
  "SA",
  "UX",
  "Tech",
  "Dev",
  "Review",
  "QA",
  "DevOps",
  "Monitor",
  "Impact",
];

const ACTIONS = [
  {
    to: "/projects/new",
    icon: Plus,
    label: "Create project",
    desc: "Start a new workspace with tech stack presets.",
  },
  {
    to: "/pipeline-runs",
    icon: Radio,
    label: "Open pipeline control",
    desc: "Review running jobs, approvals, and stuck steps.",
  },
  {
    to: "/office",
    icon: Building2,
    label: "View virtual office",
    desc: "Watch agents move through live SDLC work.",
  },
  {
    to: "/settings",
    icon: Settings,
    label: "Tune AI models",
    desc: "Configure providers, models, and connectors.",
  },
];

function StatCard({
  label,
  value,
  helper,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: number | string;
  helper: string;
  icon: React.ElementType;
  tone?: "default" | "success" | "warning" | "info";
}) {
  const color = {
    default: "bg-slate-100 text-slate-700",
    success: "bg-emerald-100 text-emerald-700",
    warning: "bg-amber-100 text-amber-700",
    info: "bg-blue-100 text-blue-700",
  }[tone];

  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-muted-foreground">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
        </div>
        <div className={cn("rounded-md p-2", color)}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">{helper}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const tone =
    status === "active"
      ? "bg-emerald-100 text-emerald-700"
      : status === "completed"
        ? "bg-blue-100 text-blue-700"
        : "bg-slate-100 text-slate-600";

  return (
    <span className={cn("rounded-full px-2 py-0.5 text-[11px] font-medium", tone)}>
      {status}
    </span>
  );
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list(),
  });

  const projects = data?.items ?? [];
  const total = data?.total ?? 0;
  const active = projects.filter((p) => p.status === "active").length;
  const completed = projects.filter((p) => p.status === "completed").length;
  const draft = Math.max(total - active - completed, 0);
  const latestProject = projects[0];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="overflow-hidden rounded-lg border bg-white">
        <div className="grid gap-0 lg:grid-cols-[1.6fr_1fr]">
          <div className="p-6 lg:p-7">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
              <Activity className="h-3.5 w-3.5" />
              Enterprise AI operations dashboard
            </div>
            <h2 className="mt-4 max-w-2xl text-2xl font-semibold tracking-tight">
              Control the SDLC pipeline from requirement intake to deploy-ready output.
            </h2>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Track projects, agent work, approvals, generated documents, and delivery health from one workspace.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                to="/projects/new"
                className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                <Plus className="h-4 w-4" />
                New project
              </Link>
              <Link
                to="/pipeline-runs"
                className="inline-flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent"
              >
                Open control center
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="border-t bg-slate-950 p-6 text-white lg:border-l lg:border-t-0">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">12-agent workflow</p>
            <div className="mt-4 grid grid-cols-4 gap-2">
              {PIPELINE_STEPS.map((step, idx) => (
                <div key={step} className="rounded-md border border-white/10 bg-white/5 p-2">
                  <p className="text-[10px] text-slate-400">Step {idx + 1}</p>
                  <p className="mt-1 text-xs font-semibold">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total projects" value={isLoading ? "-" : total} helper="All SDLC workspaces in the system." icon={FolderOpen} />
        <StatCard label="Active projects" value={isLoading ? "-" : active} helper="Projects currently moving through delivery." icon={Clock3} tone="success" />
        <StatCard label="Completed" value={isLoading ? "-" : completed} helper="Projects with finished pipeline output." icon={CheckCircle2} tone="info" />
        <StatCard label="Needs setup" value={isLoading ? "-" : draft} helper="Draft or inactive projects to prepare." icon={AlertTriangle} tone="warning" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="rounded-lg border bg-white">
          <div className="flex items-center justify-between border-b px-5 py-4">
            <div>
              <h3 className="text-sm font-semibold">Recent Projects</h3>
              <p className="text-xs text-muted-foreground">Open a project workspace to run intake, pipeline, QA, deploy, and integrations.</p>
            </div>
            <Link to="/projects" className="text-xs font-medium text-primary hover:underline">
              View all
            </Link>
          </div>

          {projects.length === 0 && (
            <div className="flex flex-col items-center gap-2 px-6 py-12 text-center">
              <FolderOpen className="h-10 w-10 text-muted-foreground/50" />
              <p className="text-sm font-medium">No projects yet</p>
              <p className="max-w-sm text-xs text-muted-foreground">
                Create a project, add requirement inputs, then run the agent pipeline.
              </p>
            </div>
          )}

          {projects.length > 0 && (
            <div className="divide-y">
              {projects.slice(0, 6).map((project) => (
                <Link
                  key={project.id}
                  to={`/projects/${project.id}`}
                  className="grid gap-3 px-5 py-4 transition-colors hover:bg-accent/60 sm:grid-cols-[1fr_auto]"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-semibold">{project.name}</p>
                      <StatusBadge status={project.status} />
                    </div>
                    <p className="mt-1 line-clamp-1 text-xs text-muted-foreground">
                      {project.description || "No project description provided."}
                    </p>
                  </div>
                  <div className="text-left text-xs text-muted-foreground sm:text-right">
                    <p>Created</p>
                    <p className="mt-1 font-medium text-foreground">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-5">
          <div className="rounded-lg border bg-white p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-md bg-emerald-100 p-2 text-emerald-700">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold">Current focus</h3>
                <p className="text-xs text-muted-foreground">Harden Phase 3 delivery flow</p>
              </div>
            </div>
            <div className="mt-4 space-y-3 text-sm">
              {[
                "Verify MCP, GitHub, Figma, and Diagram integrations.",
                "Sync backlog statuses with completed sprint work.",
                "Test approval gates before developer and after QA.",
              ].map((item) => (
                <div key={item} className="flex gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                  <span className="text-muted-foreground">{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border bg-white p-5">
            <h3 className="text-sm font-semibold">Quick actions</h3>
            <div className="mt-3 space-y-2">
              {ACTIONS.map(({ to, icon: Icon, label, desc }) => (
                <Link key={to} to={to} className="flex gap-3 rounded-md border p-3 transition-colors hover:bg-accent">
                  <Icon className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
                  <div>
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-xs text-muted-foreground">{desc}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {latestProject && (
        <section className="grid gap-4 lg:grid-cols-3">
          {[
            { to: `/projects/${latestProject.id}/documents`, icon: FileText, label: "Review documents", desc: "Open generated BRD, FSD, architecture, QA, and deploy reports." },
            { to: `/projects/${latestProject.id}/traceability`, icon: GitBranch, label: "Check traceability", desc: "Inspect coverage from requirement through tests." },
            { to: `/projects/${latestProject.id}/agents`, icon: Radio, label: "Run project pipeline", desc: "Approve, reject, rerun, or monitor agent execution." },
          ].map(({ to, icon: Icon, label, desc }) => (
            <Link key={to} to={to} className="rounded-lg border bg-white p-4 transition-colors hover:border-primary">
              <Icon className="h-5 w-5 text-primary" />
              <p className="mt-3 text-sm font-semibold">{label}</p>
              <p className="mt-1 text-xs text-muted-foreground">{desc}</p>
            </Link>
          ))}
        </section>
      )}
    </div>
  );
}
