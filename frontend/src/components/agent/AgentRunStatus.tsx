import {
  CheckCircle2,
  Loader2,
  XCircle,
  Clock,
  PauseCircle,
  AlertCircle,
  Circle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { PipelineRun, PipelineStep } from "@/types/workflow";

const PIPELINE = [
  { key: "requirement_summary", label: "Requirement Summary",       agent: "Requirement Agent",         num: 1 },
  { key: "gap_analysis",        label: "Gap Analysis",              agent: "Gap Analysis Agent",         num: 2 },
  { key: "ba_documents",        label: "BRD + FSD + User Stories",  agent: "BA Agent",                   num: 3 },
  { key: "sa_documents",        label: "Architecture + DB + API",   agent: "Solution Architect Agent",   num: 4 },
  { key: "ux_documents",        label: "Screen Spec + UX Flows",    agent: "UX Agent",                   num: 5 },
  { key: "technical_design",    label: "Technical Design",          agent: "Technical Design Agent",     num: 6 },
  { key: "dev_tasks",           label: "Generated Code + Fan-out",  agent: "Developer Agents",           num: 7 },
  { key: "code_review",         label: "Code Review",               agent: "Code Review Agent",          num: 8 },
  { key: "test_cases",          label: "Generated Tests + Report",  agent: "QA Agent",                   num: 9 },
  { key: "devops_tasks",        label: "Build + Deploy Package",    agent: "DevOps Agent",               num: 10 },
  { key: "monitoring",          label: "Monitoring Report",         agent: "Monitoring Agent",           num: 11 },
] as const;

type StepKey = (typeof PIPELINE)[number]["key"];

const RUN_STATUS_CONFIG = {
  pending:          { icon: Clock,         color: "text-muted-foreground", label: "Pending" },
  running:          { icon: Loader2,       color: "text-blue-500",         label: "Running",         spin: true },
  waiting_for_user: { icon: PauseCircle,   color: "text-yellow-500",       label: "Awaiting Review" },
  completed:        { icon: CheckCircle2,  color: "text-green-600",        label: "Completed" },
  failed:           { icon: XCircle,       color: "text-destructive",      label: "Failed" },
  cancelled:        { icon: XCircle,       color: "text-muted-foreground", label: "Cancelled" },
} as const;

function formatDuration(start: string | null, end: string | null) {
  if (!start || !end) return null;
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (ms < 60_000) return `${Math.round(ms / 1000)}s`;
  return `${Math.round(ms / 60_000)}m`;
}

interface StepIconProps {
  status: PipelineStep["status"] | "not_started";
  isWaiting: boolean;
}

function StepIcon({ status, isWaiting }: StepIconProps) {
  if (isWaiting)
    return <PauseCircle className="h-5 w-5 text-yellow-500 flex-shrink-0" />;
  if (status === "completed")
    return <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0" />;
  if (status === "running")
    return <Loader2 className="h-5 w-5 text-blue-500 animate-spin flex-shrink-0" />;
  if (status === "failed")
    return <XCircle className="h-5 w-5 text-destructive flex-shrink-0" />;
  return <Circle className="h-5 w-5 text-muted-foreground/40 flex-shrink-0" />;
}

interface AgentRunStatusProps {
  run: PipelineRun;
  steps?: PipelineStep[];
}

export function AgentRunStatus({ run, steps = [] }: AgentRunStatusProps) {
  const cfg = RUN_STATUS_CONFIG[run.status];
  const RunIcon = cfg.icon;

  const stepByKey = Object.fromEntries(steps.map((s) => [s.step_name, s])) as Record<StepKey, PipelineStep | undefined>;

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const progressPct = Math.round((completedCount / PIPELINE.length) * 100);

  // Find which pipeline index is the "next" upcoming step
  const currentPipelineIdx = PIPELINE.findIndex((p) => p.key === run.current_step);

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      {/* ── Header ── */}
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <RunIcon
            className={cn(
              "h-4 w-4",
              cfg.color,
              "spin" in cfg && cfg.spin && "animate-spin"
            )}
          />
          <span className={cn("text-sm font-semibold", cfg.color)}>{cfg.label}</span>
        </div>
        <span className="text-xs text-muted-foreground">
          {completedCount} / {PIPELINE.length} steps complete
        </span>
      </div>

      {/* ── Progress bar ── */}
      <div className="h-1.5 bg-muted">
        <div
          className={cn(
            "h-full transition-all duration-500",
            run.status === "completed" ? "bg-green-500" :
            run.status === "failed"    ? "bg-destructive" :
                                         "bg-blue-500"
          )}
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* ── Pipeline stepper ── */}
      <div className="divide-y">
        {PIPELINE.map((def, idx) => {
          const step = stepByKey[def.key];
          const status: PipelineStep["status"] | "not_started" = step?.status ?? "not_started";
          const isCurrentStep = run.current_step === def.key;
          const isWaiting = isCurrentStep && run.status === "waiting_for_user";
          const isNext =
            !step &&
            run.status === "running" &&
            currentPipelineIdx !== -1 &&
            idx === currentPipelineIdx + 1;
          const duration = step ? formatDuration(step.started_at, step.completed_at) : null;

          return (
            <div
              key={def.key}
              className={cn(
                "flex gap-3 px-4 py-3 transition-colors",
                status === "running" && "bg-blue-50",
                isWaiting           && "bg-yellow-50",
                status === "failed" && "bg-red-50/40",
                isNext              && "bg-muted/30"
              )}
            >
              {/* Icon + connector line */}
              <div className="flex flex-col items-center gap-0.5 pt-0.5">
                <StepIcon status={status} isWaiting={isWaiting} />
                {idx < PIPELINE.length - 1 && (
                  <div
                    className={cn(
                      "w-0.5 flex-1 min-h-[16px] rounded-full mt-0.5",
                      status === "completed" ? "bg-green-400" : "bg-muted"
                    )}
                  />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pb-1">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className={cn(
                      "text-xs font-medium leading-tight",
                      status === "not_started" || status === "pending" ? "text-muted-foreground" : "text-foreground",
                      isNext && "text-foreground/70"
                    )}>
                      <span className="font-mono text-[10px] text-muted-foreground mr-1.5">{def.num}.</span>
                      {def.label}
                    </p>
                    <p className={cn(
                      "text-[11px] mt-0.5",
                      status === "running" ? "text-blue-600 font-medium" :
                      isWaiting            ? "text-yellow-700 font-medium" :
                                             "text-muted-foreground"
                    )}>
                      {def.agent}
                      {isNext && (
                        <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                          next
                        </span>
                      )}
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    {duration && (
                      <span className="text-[10px] text-muted-foreground">{duration}</span>
                    )}
                    {status === "completed" && (
                      <span className="rounded-full bg-green-100 px-1.5 py-0.5 text-[10px] font-medium text-green-700">done</span>
                    )}
                    {status === "running" && (
                      <span className="rounded-full bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 animate-pulse">running</span>
                    )}
                    {isWaiting && (
                      <span className="rounded-full bg-yellow-100 px-1.5 py-0.5 text-[10px] font-medium text-yellow-700">review</span>
                    )}
                    {status === "failed" && (
                      <span className="rounded-full bg-red-100 px-1.5 py-0.5 text-[10px] font-medium text-red-700">failed</span>
                    )}
                  </div>
                </div>

                {/* Error message */}
                {status === "failed" && step?.error_message && (
                  <div className="mt-1.5 flex items-start gap-1.5 rounded bg-destructive/10 px-2 py-1.5">
                    <AlertCircle className="h-3 w-3 text-destructive flex-shrink-0 mt-0.5" />
                    <p className="text-[11px] text-destructive break-all">{step.error_message}</p>
                  </div>
                )}

                {/* Review hint */}
                {isWaiting && (
                  <p className="mt-1 text-[11px] text-yellow-700">
                    Review the document below to approve or reject.
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
