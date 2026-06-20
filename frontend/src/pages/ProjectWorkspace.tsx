import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  Upload, Bot, FileText, GitBranch, Building2, Zap,
  Github, Wrench, BookOpen, ClipboardList, Database, Code2,
  CheckCircle2, Circle, ArrowRight, AlertCircle, RotateCcw,
  ScrollText, FolderGit2,
} from "lucide-react";
import { projectApi } from "@/services/projectApi";
import { sourceApi } from "@/services/sourceApi";
import { agentApi } from "@/services/agentApi";
import { cn } from "@/lib/utils";

// ── Project Output groups ─────────────────────────────────────────────────────

type OutputItem = { label: string; icon: React.ElementType; sub: string; href: (id: string) => string };

const OUTPUT_GROUPS: Array<{ group: string; items: OutputItem[] }> = [
  {
    group: "Documents",
    items: [
      { label: "Document Package", icon: BookOpen,     sub: "Bundle all pipeline docs",      href: (id) => `/projects/${id}/documentation` },
      { label: "Delivery Summary", icon: ClipboardList, sub: "PM / delivery report",          href: (id) => `/projects/${id}/pm` },
    ],
  },
  {
    group: "Development",
    items: [
      { label: "Code Workspace",   icon: Code2,    sub: "View & download code files",  href: (id) => `/projects/${id}/generated-code` },
      { label: "GitHub Issues",    icon: Github,   sub: "Push tasks as issues",         href: (id) => `/projects/${id}/github` },
    ],
  },
  {
    group: "Quality",
    items: [
      { label: "Traceability",     icon: GitBranch, sub: "Coverage matrix",             href: (id) => `/projects/${id}/traceability` },
      { label: "Change Impact",    icon: Zap,       sub: "Analyse requirement changes",  href: (id) => `/projects/${id}/change-impact` },
    ],
  },
  {
    group: "Knowledge & Tools",
    items: [
      { label: "RAG Knowledge Base", icon: Database,  sub: "Semantic search (RAG)",       href: (id) => `/projects/${id}/rag` },
      { label: "Tool Registry",      icon: Wrench,    sub: "MCP tools & approvals",       href: (id) => `/projects/${id}/mcp` },
      { label: "Virtual Office",     icon: Building2, sub: "Live agent status",            href: (id) => `/projects/${id}/office` },
    ],
  },
];

// ── Step labels ───────────────────────────────────────────────────────────────

const STEP_LABELS: Record<string, string> = {
  requirement_summary: "Requirement Summary",
  gap_analysis:        "Gap Analysis",
  ba_documents:        "BRD + FSD + User Stories",
  sa_documents:        "Architecture + DB + API",
  ux_documents:        "Screen Spec + UX Flows",
  technical_design:    "Technical Design",
  dev_tasks:           "Generated Code",
  code_review:         "Code Review",
  test_cases:          "Generated Tests + Report",
  devops_tasks:        "Build + Deploy Package",
  monitoring:          "Monitoring Report",
};

function stepLabel(step: string | null | undefined) {
  if (!step) return "starting";
  return STEP_LABELS[step] ?? step;
}

// ── Status helpers ────────────────────────────────────────────────────────────

function pipelineStatusBadge(status: string | undefined) {
  switch (status) {
    case "running":          return <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">Running</span>;
    case "waiting_for_user": return <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">Need Review</span>;
    case "completed":        return <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">Completed</span>;
    case "failed":           return <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700">Failed</span>;
    default:                 return <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-500">No Pipeline Run</span>;
  }
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function ProjectWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: inputs } = useQuery({
    queryKey: ["inputs", projectId],
    queryFn: () => sourceApi.list(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["pipeline-runs", projectId],
    queryFn: () => agentApi.listRuns(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  });

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!project)  return <p className="text-sm text-destructive">Project not found.</p>;

  const inputCount    = inputs?.total ?? 0;
  const activeRun     = runs.find((r) => r.status === "running" || r.status === "waiting_for_user");
  const latestRun     = activeRun ?? runs[0] ?? null;
  const pipelineDone  = latestRun?.status === "completed";
  const pipelineFailed = latestRun?.status === "failed";

  const hasInputs      = inputCount > 0;
  const canRunPipeline = hasInputs;

  // Compute progress fraction
  const totalSteps = 11;
  const completedSteps = pipelineDone ? totalSteps : (latestRun?.current_step ? 1 : 0);

  const steps: Array<{
    num: number; label: string; desc: string; href: string;
    icon: React.ElementType; done: boolean; locked: boolean; actionLabel: string;
  }> = [
    {
      num: 1,
      label: "Upload Requirements",
      desc: hasInputs
        ? `${inputCount} input${inputCount !== 1 ? "s" : ""} uploaded — add more or proceed`
        : "Upload meeting transcripts, documents, or text as requirements",
      href: `/projects/${projectId}/intake`,
      icon: Upload,
      done: hasInputs,
      locked: false,
      actionLabel: "Upload",
    },
    {
      num: 2,
      label: "Run AI Pipeline",
      desc: !hasInputs
        ? "Complete Step 1 first — upload at least one requirement"
        : activeRun?.status === "waiting_for_user"
        ? `Waiting for your approval — ${stepLabel(activeRun.current_step)}`
        : activeRun?.status === "running"
        ? `Running… current step: ${stepLabel(activeRun.current_step)}`
        : pipelineDone
        ? "Pipeline completed — 11-step auto-chain finished"
        : pipelineFailed
        ? "Last run failed — check the console or retry"
        : "Start the 11-step SDLC pipeline",
      href: `/projects/${projectId}/agents`,
      icon: Bot,
      done: pipelineDone,
      locked: !canRunPipeline,
      actionLabel: activeRun
        ? (activeRun.status === "waiting_for_user" ? "Review & Approve" : "View Progress")
        : pipelineFailed ? "Retry Pipeline" : "Run Pipeline",
    },
    {
      num: 3,
      label: "Review Documents",
      desc: !latestRun
        ? "Documents will appear here after the pipeline runs"
        : "Review BRD, FSD, Architecture, Screen Spec and more",
      href: `/projects/${projectId}/documents`,
      icon: FileText,
      done: false,
      locked: !latestRun,
      actionLabel: "Review",
    },
  ];

  const activeStepNum = steps.find((s) => !s.done && !s.locked)?.num ?? 3;

  return (
    <div className="space-y-6 max-w-3xl">
      {/* ── Project status bar ── */}
      <div className="rounded-xl border bg-white p-4 flex flex-wrap gap-6">
        <div>
          <p className="text-xs text-muted-foreground">Pipeline Status</p>
          <div className="mt-1">{pipelineStatusBadge(latestRun?.status)}</div>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Current Step</p>
          <p className="mt-1 text-sm font-medium">{latestRun ? stepLabel(latestRun.current_step) : "—"}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Progress</p>
          <p className="mt-1 text-sm font-medium">{pipelineDone ? totalSteps : completedSteps} / {totalSteps} steps</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Requirement Files</p>
          <p className="mt-1 text-sm font-medium">{inputCount}</p>
        </div>

        {/* Quick actions */}
        {(pipelineFailed || activeRun?.status === "waiting_for_user") && (
          <div className="w-full flex gap-2 pt-1">
            {pipelineFailed && (
              <Link
                to={`/projects/${projectId}/agents`}
                className="inline-flex items-center gap-1.5 rounded-md bg-red-50 border border-red-200 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Retry Failed Step
              </Link>
            )}
            {activeRun?.status === "waiting_for_user" && (
              <Link
                to={`/projects/${projectId}/agents`}
                className="inline-flex items-center gap-1.5 rounded-md bg-amber-50 border border-amber-200 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-100"
              >
                <AlertCircle className="h-3.5 w-3.5" />
                Review & Approve
              </Link>
            )}
            <Link
              to={`/projects/${projectId}/agents`}
              className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent"
            >
              <ScrollText className="h-3.5 w-3.5" />
              Open Pipeline Console
            </Link>
          </div>
        )}
      </div>

      {/* ── Guided steps ── */}
      <section>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Pipeline Workflow
        </h3>
        <div className="space-y-2">
          {steps.map((step) => {
            const Icon = step.icon;
            const active = step.num === activeStepNum;
            return (
              <div
                key={step.num}
                className={cn(
                  "flex items-start gap-3 rounded-xl border p-4 transition-all",
                  step.done     && "border-green-200 bg-green-50",
                  !step.done && active  && "border-primary/30 bg-primary/5 shadow-sm",
                  !step.done && !active && !step.locked && "border-muted bg-white",
                  step.locked   && "border-muted bg-muted/30 opacity-60 cursor-not-allowed",
                )}
              >
                <div className={cn(
                  "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold",
                  step.done  && "bg-green-500 text-white",
                  !step.done && active  && "bg-primary text-primary-foreground",
                  !step.done && !active && "bg-muted text-muted-foreground",
                )}>
                  {step.done ? <CheckCircle2 className="h-4 w-4" /> : step.num}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Icon className={cn("h-4 w-4", step.done ? "text-green-600" : active ? "text-primary" : "text-muted-foreground")} />
                    <p className={cn("text-sm font-semibold", step.done ? "text-green-700" : active ? "text-foreground" : "text-muted-foreground")}>
                      {step.label}
                    </p>
                    {active && !step.done && (
                      <span className="rounded-full bg-primary px-2 py-0.5 text-[10px] font-medium text-primary-foreground">
                        Next
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">{step.desc}</p>
                </div>

                {!step.locked ? (
                  <Link
                    to={step.href}
                    className={cn(
                      "flex-shrink-0 flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                      step.done   && "bg-green-100 text-green-700 hover:bg-green-200",
                      !step.done && active  && "bg-primary text-primary-foreground hover:bg-primary/90",
                      !step.done && !active && "border text-muted-foreground hover:bg-accent",
                    )}
                  >
                    {step.done ? "View" : step.actionLabel}
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                ) : (
                  <span className="flex-shrink-0 flex items-center gap-1 rounded-md border px-3 py-1.5 text-xs text-muted-foreground">
                    <Circle className="h-3 w-3" /> Locked
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Project Outputs ── */}
      <div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground mb-4">
          <div className="flex-1 border-t" />
          <span className="font-medium flex items-center gap-1.5">
            <FolderGit2 className="h-3.5 w-3.5" />
            Project Outputs
          </span>
          <div className="flex-1 border-t" />
        </div>

        <div className="space-y-4">
          {OUTPUT_GROUPS.map(({ group, items }) => (
            <div key={group}>
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                {group}
              </p>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {items.map(({ label, icon: Icon, sub, href }) => (
                  <Link
                    key={label}
                    to={href(projectId!)}
                    className="flex items-start gap-3 rounded-lg border bg-white p-3 hover:border-primary/40 hover:bg-accent/30 transition-colors"
                  >
                    <Icon className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs font-medium">{label}</p>
                      <p className="text-[10px] text-muted-foreground leading-tight">{sub}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
