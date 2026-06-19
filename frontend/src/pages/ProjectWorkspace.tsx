import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  Upload, Bot, FileText, GitBranch, Building2, Zap,
  Github, Wrench, BookOpen, ClipboardList, Database,
  CheckCircle2, Circle, ArrowRight,
} from "lucide-react";
import { projectApi } from "@/services/projectApi";
import { sourceApi } from "@/services/sourceApi";
import { agentApi } from "@/services/agentApi";
import { cn } from "@/lib/utils";

// ── Tool links grid ───────────────────────────────────────────────────────────

const TOOLS = [
  { label: "Traceability",   icon: GitBranch,    sub: "Coverage matrix",          href: (id: string) => `/projects/${id}/traceability` },
  { label: "Virtual Office", icon: Building2,    sub: "Live agent status",        href: (id: string) => `/projects/${id}/office` },
  { label: "Change Impact",  icon: Zap,          sub: "Analyse requirement changes", href: (id: string) => `/projects/${id}/change-impact` },
  { label: "GitHub",         icon: Github,       sub: "Push tasks as issues",     href: (id: string) => `/projects/${id}/github` },
  { label: "MCP Tools",      icon: Wrench,       sub: "Tool registry & approvals", href: (id: string) => `/projects/${id}/mcp` },
  { label: "Compile Docs",   icon: BookOpen,     sub: "Bundle all pipeline docs", href: (id: string) => `/projects/${id}/documentation` },
  { label: "PM Summary",     icon: ClipboardList, sub: "Final delivery report",   href: (id: string) => `/projects/${id}/pm` },
  { label: "Knowledge Base", icon: Database,     sub: "Semantic search (RAG)",    href: (id: string) => `/projects/${id}/rag` },
];

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
  if (!project) return <p className="text-sm text-destructive">Project not found.</p>;

  const inputCount  = inputs?.total ?? 0;
  const activeRun   = runs.find((r) => r.status === "running" || r.status === "waiting_for_user");
  const latestRun   = activeRun ?? runs[0] ?? null;
  const pipelineDone = latestRun?.status === "completed";
  const pipelineStarted = !!latestRun;

  // Derive guided step states
  const hasInputs   = inputCount > 0;
  const canRunPipeline = hasInputs;
  const steps: Array<{ num: number; label: string; desc: string; href: string; icon: React.ElementType; done: boolean; locked: boolean; actionLabel: string }> = [
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
        ? `Waiting for your approval — step: ${activeRun.current_step}`
        : activeRun?.status === "running"
        ? `Running… current step: ${activeRun.current_step ?? "starting"}`
        : pipelineDone
        ? "Pipeline completed — all 10 agents finished"
        : latestRun?.status === "failed"
        ? "Last run failed — check the console or retry"
        : "Start the 10-agent SDLC pipeline",
      href: `/projects/${projectId}/agents`,
      icon: Bot,
      done: pipelineDone,
      locked: !canRunPipeline,
      actionLabel: activeRun ? (activeRun.status === "waiting_for_user" ? "Review & Approve" : "View Progress") : "Run Pipeline",
    },
    {
      num: 3,
      label: "Review Documents",
      desc: !pipelineStarted
        ? "Documents will appear here after the pipeline runs"
        : "Review BRD, FSD, Architecture, Screen Spec and more",
      href: `/projects/${projectId}/documents`,
      icon: FileText,
      done: false,
      locked: !pipelineStarted,
      actionLabel: "Review",
    },
  ];

  // Find the first active (not done, not locked) step
  const activeStepNum = steps.find((s) => !s.done && !s.locked)?.num ?? 3;

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold">{project.name}</h2>
        {project.description && (
          <p className="text-sm text-muted-foreground mt-0.5">{project.description}</p>
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
                  step.done    && "border-green-200 bg-green-50",
                  !step.done && active  && "border-primary/30 bg-primary/5 shadow-sm",
                  !step.done && !active && !step.locked && "border-muted bg-white",
                  step.locked  && "border-muted bg-muted/30 opacity-60 cursor-not-allowed",
                )}
              >
                {/* circle */}
                <div className={cn(
                  "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold",
                  step.done   && "bg-green-500 text-white",
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

      {/* ── Divider ── */}
      <div className="flex items-center gap-3 text-xs text-muted-foreground">
        <div className="flex-1 border-t" />
        <span>Additional tools</span>
        <div className="flex-1 border-t" />
      </div>

      {/* ── Tools grid ── */}
      <div className="grid gap-3 sm:grid-cols-4">
        {TOOLS.map(({ label, icon: Icon, sub, href }) => (
          <Link
            key={label}
            to={href(projectId!)}
            className="flex flex-col items-center gap-1.5 rounded-lg border bg-white px-3 py-4 text-center hover:border-primary/40 hover:bg-accent/30 transition-colors"
          >
            <Icon className="h-5 w-5 text-muted-foreground" />
            <span className="text-xs font-medium">{label}</span>
            <span className="text-[10px] text-muted-foreground leading-tight">{sub}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
