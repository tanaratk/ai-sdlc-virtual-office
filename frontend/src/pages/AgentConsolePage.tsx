import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  Play, StopCircle, FileText, ScrollText,
  ChevronDown, ChevronUp, Users, AlertCircle, CheckCircle2,
  Loader2, Clock, XCircle, Circle, ExternalLink,
} from "lucide-react";
import { agentApi } from "@/services/agentApi";
import { DocumentPreviewPanel } from "@/components/agent/DocumentPreviewPanel";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import type { Agent } from "@/types/agent";
import { cn } from "@/lib/utils";

// ── Pipeline step definitions ─────────────────────────────────────────────────

const PIPELINE = [
  { key: "requirement_summary", label: "Requirement Summary",      agent: "Requirement Agent",       num: 1 },
  { key: "gap_analysis",        label: "Gap Analysis",             agent: "Gap Analysis Agent",      num: 2 },
  { key: "ba_documents",        label: "BRD + FSD + User Stories", agent: "BA Agent",                num: 3 },
  { key: "sa_documents",        label: "Architecture + DB + API",  agent: "Solution Architect Agent",num: 4 },
  { key: "ux_documents",        label: "Screen Spec + UX Flows",   agent: "UX Agent",                num: 5 },
  { key: "technical_design",    label: "Technical Design",         agent: "Technical Design Agent",  num: 6 },
  { key: "dev_tasks",           label: "Generated Code + Fan-out", agent: "Developer Agents",        num: 7 },
  { key: "code_review",         label: "Code Review",              agent: "Code Review Agent",       num: 8 },
  { key: "test_cases",          label: "Generated Tests + Report", agent: "QA Agent",                num: 9 },
  { key: "devops_tasks",        label: "Build + Deploy Package",   agent: "DevOps Agent",            num: 10 },
  { key: "monitoring",          label: "Monitoring Report",        agent: "Monitoring Agent",        num: 11 },
] as const;


// ── Helpers ───────────────────────────────────────────────────────────────────

function formatDuration(start: string | null, end?: string | null): string | null {
  if (!start) return null;
  const ms = (end ? new Date(end) : new Date()).getTime() - new Date(start).getTime();
  if (ms < 0) return null;
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  if (m > 0) return `${m}m ${s % 60}s`;
  return `${s}s`;
}

function formatTime(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

// ── Status badge ──────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    running:          "bg-blue-100 text-blue-700",
    working:          "bg-blue-100 text-blue-700",
    completed:        "bg-green-100 text-green-700",
    done:             "bg-green-100 text-green-700",
    failed:           "bg-red-100 text-red-700",
    error:            "bg-red-100 text-red-700",
    waiting_for_user: "bg-amber-100 text-amber-700",
    pending:          "bg-gray-100 text-gray-500",
    idle:             "bg-gray-100 text-gray-500",
    not_started:      "bg-gray-100 text-gray-400",
    skipped:          "bg-gray-100 text-gray-400",
  };
  const labels: Record<string, string> = {
    waiting_for_user: "Need Review",
    not_started:      "Waiting",
    idle:             "Waiting",
    pending:          "Waiting",
    completed:        "Done",
    done:             "Done",
    failed:           "Failed",
    error:            "Failed",
    running:          "Running",
    working:          "Running",
    skipped:          "Skipped",
  };
  const cls = map[status] ?? "bg-gray-100 text-gray-400";
  const lbl = labels[status] ?? status;
  return (
    <span className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide", cls)}>
      {lbl}
    </span>
  );
}

// ── Agent Summary ─────────────────────────────────────────────────────────────

function AgentSummary({ agents }: { agents: Agent[] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const active  = agents.filter((a) => a.status === "working").length;
  const done    = agents.filter((a) => a.status === "done").length;
  const failed  = agents.filter((a) => a.status === "error").length;
  const waiting = agents.filter((a) => a.status === "idle").length;

  const grouped = {
    Running: agents.filter((a) => a.status === "working"),
    Done:    agents.filter((a) => a.status === "done"),
    Failed:  agents.filter((a) => a.status === "error"),
    Waiting: agents.filter((a) => a.status === "idle"),
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-md border bg-white px-3 py-1.5 text-xs hover:bg-accent"
      >
        <Users className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="text-blue-600 font-medium">Active {active}</span>
        <span className="text-muted-foreground">|</span>
        <span className="text-green-600 font-medium">Done {done}</span>
        <span className="text-muted-foreground">|</span>
        <span className="text-red-600 font-medium">Failed {failed}</span>
        <span className="text-muted-foreground">|</span>
        <span className="text-gray-500 font-medium">Waiting {waiting}</span>
        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 z-50 w-72 rounded-lg border bg-white shadow-lg">
          <div className="border-b px-4 py-2.5">
            <p className="text-sm font-semibold">All Agents</p>
          </div>
          <div className="max-h-72 overflow-y-auto divide-y">
            {Object.entries(grouped).map(([group, items]) =>
              items.length === 0 ? null : (
                <div key={group} className="px-4 py-2">
                  <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{group}</p>
                  {items.map((a) => (
                    <div key={a.id} className="flex items-center justify-between py-1">
                      <p className="text-xs">{a.name}</p>
                      <StatusBadge status={a.status} />
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Pipeline Summary Bar ──────────────────────────────────────────────────────

interface SummaryBarProps {
  run: PipelineRun | null;
  completedCount: number;
  totalSteps: number;
  agents: Agent[];
  onStart: () => void;
  isStarting: boolean;
}

function PipelineSummaryBar({ run, completedCount, totalSteps, agents, onStart, isStarting }: SummaryBarProps) {
  const canStart = !run || ["completed", "failed", "cancelled"].includes(run.status);
  const runStatus = run?.status ?? "pending";
  const currentPipelineDef = PIPELINE.find((p) => p.key === run?.current_step);
  const duration = run?.status === "running"
    ? formatDuration(run.started_at)
    : run?.completed_at ? formatDuration(run.started_at, run.completed_at) : null;

  const failedStep = run?.status === "failed"
    ? PIPELINE.find((p) => p.key === run.current_step)
    : null;

  return (
    <div className="rounded-xl border bg-white p-4 space-y-3">
      {/* Row 1: status + metrics */}
      <div className="flex flex-wrap items-center gap-6">
        <div>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Status</p>
          <StatusBadge status={runStatus} />
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Progress</p>
          <p className="text-sm font-semibold">{completedCount} / {totalSteps}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">
            {run?.status === "failed" ? "Failed Step" : "Current Step"}
          </p>
          <p className="text-sm font-medium">
            {currentPipelineDef?.label ?? (run ? "—" : "Not started")}
          </p>
        </div>
        {duration && (
          <div>
            <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Duration</p>
            <p className="text-sm font-medium">{duration}</p>
          </div>
        )}
        <div className="ml-auto">
          <AgentSummary agents={agents} />
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div
          className={cn("h-full transition-all duration-500 rounded-full", {
            "bg-green-500": run?.status === "completed",
            "bg-red-500":   run?.status === "failed",
            "bg-blue-500":  run?.status === "running" || run?.status === "waiting_for_user",
            "bg-gray-300":  !run || run.status === "pending",
          })}
          style={{ width: `${Math.round((completedCount / totalSteps) * 100)}%` }}
        />
      </div>

      {/* Row 2: actions */}
      <div className="flex flex-wrap gap-2">
        {canStart && (
          <button
            onClick={onStart}
            disabled={isStarting}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isStarting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            {isStarting ? "Starting…" : run?.status === "failed" ? "Retry Failed Step" : "Run Pipeline"}
          </button>
        )}
        {run?.status === "running" && (
          <button disabled className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium text-muted-foreground opacity-50 cursor-not-allowed">
            <StopCircle className="h-3.5 w-3.5" />
            Stop
          </button>
        )}
        {failedStep && (
          <span className="inline-flex items-center gap-1.5 rounded-md bg-red-50 border border-red-200 px-3 py-1.5 text-xs text-red-700">
            <AlertCircle className="h-3.5 w-3.5" />
            Failed: {failedStep.label}
          </span>
        )}
      </div>
    </div>
  );
}

// ── Step Detail Panel ─────────────────────────────────────────────────────────

interface StepDetailPanelProps {
  projectId: string;
  run: PipelineRun | null;
  stepKey: string | null;
  stepData: PipelineStep | undefined;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  isApproving: boolean;
  isRejecting: boolean;
}

function StepDetailPanel({
  projectId, run, stepKey, stepData, onApprove, onReject, isApproving, isRejecting,
}: StepDetailPanelProps) {
  const def = PIPELINE.find((p) => p.key === stepKey);

  if (!def) {
    return (
      <div className="rounded-xl border bg-white p-4 flex items-center justify-center h-40">
        <p className="text-sm text-muted-foreground">Select a step to view details</p>
      </div>
    );
  }

  const status = stepData?.status ?? "not_started";
  const isWaiting = stepKey === run?.current_step && run?.status === "waiting_for_user";
  const duration = stepData ? formatDuration(stepData.started_at, stepData.completed_at) : null;

  return (
    <div className="rounded-xl border bg-white overflow-hidden">
      <div className="border-b px-4 py-3 bg-muted/20">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Step {def.num}</p>
            <p className="text-sm font-semibold mt-0.5">{def.label}</p>
          </div>
          <StatusBadge status={isWaiting ? "waiting_for_user" : status} />
        </div>
        <p className="text-xs text-muted-foreground mt-1">{def.agent}</p>
      </div>

      <div className="p-4 space-y-3">
        {/* Timing */}
        {stepData?.started_at && (
          <div className="space-y-1">
            <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Timing</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-muted-foreground">Started: </span>
                {formatTime(stepData.started_at)}
              </div>
              {duration && (
                <div>
                  <span className="text-muted-foreground">Duration: </span>
                  {duration}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error */}
        {status === "failed" && stepData?.error_message && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-3">
            <p className="text-[10px] uppercase tracking-wide text-red-600 font-semibold mb-1">Error</p>
            <p className="text-xs text-red-700 break-all">{stepData.error_message}</p>
          </div>
        )}

        {/* Review hint */}
        {isWaiting && (
          <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
            <p className="text-xs text-amber-700">
              This step is waiting for your review. Check the document below then Approve or Reject.
            </p>
          </div>
        )}

        {/* Retry count */}
        {stepData && stepData.retry_count > 0 && (
          <p className="text-[10px] text-muted-foreground">Retry count: {stepData.retry_count}</p>
        )}

        {/* Actions */}
        <div className="space-y-2 pt-1">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Actions</p>

          {stepData?.output_document_id && (
            <Link
              to={`/projects/${projectId}/documents`}
              className="flex w-full items-center gap-2 rounded-md border px-3 py-2 text-xs font-medium hover:bg-accent"
            >
              <FileText className="h-3.5 w-3.5 text-muted-foreground" />
              View Output Document
              <ExternalLink className="h-3 w-3 ml-auto text-muted-foreground" />
            </Link>
          )}

          {isWaiting && (
            <>
              <button
                onClick={() => stepData && onApprove(stepData.id)}
                disabled={isApproving}
                className="flex w-full items-center gap-2 rounded-md bg-green-600 px-3 py-2 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                <CheckCircle2 className="h-3.5 w-3.5" />
                {isApproving ? "Approving…" : "Approve"}
              </button>
              <button
                onClick={() => stepData && onReject(stepData.id)}
                disabled={isRejecting}
                className="flex w-full items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
              >
                <XCircle className="h-3.5 w-3.5" />
                {isRejecting ? "Rejecting…" : "Reject"}
              </button>
            </>
          )}

          {status === "not_started" && (
            <p className="text-xs text-muted-foreground italic">Step has not run yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Execution Logs ────────────────────────────────────────────────────────────

function ExecutionLogs({ steps, run }: { steps: PipelineStep[]; run: PipelineRun | null }) {
  const events = [
    ...(run?.started_at ? [{ time: run.started_at, msg: "Pipeline started", type: "info" }] : []),
    ...steps.flatMap((s) => {
      const def = PIPELINE.find((p) => p.key === s.step_name);
      const label = def?.label ?? s.step_name;
      const items = [];
      if (s.started_at) items.push({ time: s.started_at, msg: `${label} — started`, type: "info" });
      if (s.completed_at && s.status === "completed") items.push({ time: s.completed_at, msg: `${label} — completed`, type: "success" });
      if (s.completed_at && s.status === "failed") items.push({ time: s.completed_at, msg: `${label} — failed${s.error_message ? `: ${s.error_message}` : ""}`, type: "error" });
      return items;
    }),
    ...(run?.completed_at ? [{ time: run.completed_at, msg: `Pipeline ${run.status}`, type: run.status === "completed" ? "success" : "error" }] : []),
  ].sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());

  return (
    <div className="rounded-xl border bg-white overflow-hidden">
      <div className="border-b px-4 py-2.5 flex items-center justify-between">
        <p className="text-sm font-semibold flex items-center gap-2">
          <ScrollText className="h-4 w-4 text-muted-foreground" />
          Execution Logs
        </p>
      </div>
      <div className="divide-y max-h-48 overflow-y-auto font-mono text-xs">
        {events.length === 0 && (
          <p className="px-4 py-6 text-center text-muted-foreground">No logs yet</p>
        )}
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 px-4 py-2">
            <span className="text-muted-foreground/60 flex-shrink-0">[{formatTime(e.time)}]</span>
            <span className={cn(
              e.type === "success" && "text-green-700",
              e.type === "error"   && "text-red-700",
              e.type === "info"    && "text-foreground",
            )}>
              {e.msg}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Pipeline Steps List ───────────────────────────────────────────────────────

interface PipelineStepsListProps {
  run: PipelineRun | null;
  steps: PipelineStep[];
  selectedKey: string | null;
  onSelect: (key: string) => void;
}

function PipelineStepsList({ run, steps, selectedKey, onSelect }: PipelineStepsListProps) {
  const stepByKey = Object.fromEntries(steps.map((s) => [s.step_name, s])) as Record<string, PipelineStep>;
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const totalSteps = PIPELINE.length;
  const currentPipelineIdx = PIPELINE.findIndex((p) => p.key === run?.current_step);

  return (
    <div className="rounded-xl border bg-white overflow-hidden">
      {/* header */}
      <div className="border-b px-4 py-2.5 flex items-center justify-between">
        <p className="text-sm font-semibold">Pipeline Steps</p>
        <span className="text-xs text-muted-foreground">{completedCount}/{totalSteps} done</span>
      </div>

      {/* progress bar */}
      <div className="h-1 bg-muted">
        <div
          className={cn("h-full transition-all", {
            "bg-green-500": run?.status === "completed",
            "bg-red-500":   run?.status === "failed",
            "bg-blue-500":  run?.status === "running" || run?.status === "waiting_for_user",
          })}
          style={{ width: `${Math.round((completedCount / totalSteps) * 100)}%` }}
        />
      </div>

      {/* steps */}
      <div className="divide-y">
        {PIPELINE.map((def, idx) => {
          const step = stepByKey[def.key];
          const rawStatus = step?.status;
          const isCurrentStep = run?.current_step === def.key;
          const isWaiting = isCurrentStep && run?.status === "waiting_for_user";
          const isActive = isCurrentStep && run?.status === "running";
          const isNext = !step && run?.status === "running" && currentPipelineIdx !== -1 && idx === currentPipelineIdx + 1;
          const displayStatus = isWaiting ? "waiting_for_user" : (rawStatus ?? "not_started");
          const isSelected = selectedKey === def.key;

          return (
            <button
              key={def.key}
              onClick={() => onSelect(def.key)}
              className={cn(
                "w-full text-left flex gap-3 px-4 py-3 transition-colors",
                isSelected  && "bg-primary/5 border-l-2 border-primary",
                !isSelected && isActive  && "bg-blue-50",
                !isSelected && isWaiting && "bg-amber-50",
                !isSelected && step?.status === "failed" && "bg-red-50/40",
                !isSelected && isNext    && "bg-muted/20",
                !isSelected && !isActive && !isWaiting && !isNext && "hover:bg-muted/10",
              )}
            >
              {/* connector */}
              <div className="flex flex-col items-center gap-0.5 pt-0.5 flex-shrink-0">
                {/* icon */}
                <div className="h-5 w-5 flex items-center justify-center">
                  {rawStatus === "completed" ? <CheckCircle2 className="h-5 w-5 text-green-500" />
                  : rawStatus === "running"  ? <Loader2      className="h-5 w-5 text-blue-500 animate-spin" />
                  : isWaiting               ? <Clock         className="h-5 w-5 text-amber-500" />
                  : rawStatus === "failed"   ? <XCircle      className="h-5 w-5 text-red-500" />
                  :                            <Circle       className="h-5 w-5 text-muted-foreground/30" />}
                </div>
                {idx < PIPELINE.length - 1 && (
                  <div className={cn("w-0.5 flex-1 min-h-[12px] rounded-full", rawStatus === "completed" ? "bg-green-300" : "bg-muted/60")} />
                )}
              </div>

              {/* content */}
              <div className="flex-1 min-w-0 pb-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-muted-foreground">{def.num}.</span>
                  <p className={cn(
                    "text-xs font-medium",
                    !step ? "text-muted-foreground" : "text-foreground"
                  )}>
                    {def.label}
                  </p>
                  {isNext && <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">next</span>}
                </div>

                <div className="flex items-center gap-2 mt-0.5">
                  <p className="text-[11px] text-muted-foreground">{def.agent}</p>
                  <StatusBadge status={displayStatus} />
                </div>

                {step?.error_message && (
                  <p className="mt-1 text-[10px] text-red-600 truncate">{step.error_message}</p>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function AgentConsolePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(false);

  const { data: agents = [] } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    refetchInterval: 4000,
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["pipeline-runs", projectId],
    queryFn: () => agentApi.listRuns(projectId!),
    enabled: !!projectId,
    refetchInterval: 4000,
  });

  const activeRun =
    runs.find((r) => r.status === "running" || r.status === "waiting_for_user") ??
    runs[0] ?? null;

  const { data: steps = [] } = useQuery({
    queryKey: ["pipeline-steps", projectId, activeRun?.id],
    queryFn: () => agentApi.getSteps(projectId!, activeRun!.id),
    enabled: !!projectId && !!activeRun,
    refetchInterval:
      activeRun?.status === "running" || activeRun?.status === "waiting_for_user" ? 3000 : false,
  });

  // Force-refetch steps once when run transitions to failed so error_message is picked up
  const prevRunStatus = useRef(activeRun?.status);
  useEffect(() => {
    if (
      prevRunStatus.current !== activeRun?.status &&
      activeRun?.status === "failed"
    ) {
      queryClient.invalidateQueries({
        queryKey: ["pipeline-steps", projectId, activeRun.id],
      });
    }
    prevRunStatus.current = activeRun?.status;
  }, [activeRun?.status, activeRun?.id, projectId, queryClient]);

  // Auto-select the current/failed/waiting step
  useEffect(() => {
    if (activeRun?.current_step) setSelectedStep(activeRun.current_step);
  }, [activeRun?.current_step]);

  const startMutation = useMutation({
    mutationFn: () => agentApi.startRun(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.approveStep(projectId!, activeRun!.id, stepId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-steps", projectId, activeRun?.id] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.rejectStep(projectId!, activeRun!.id, stepId, "Rejected by user"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-steps", projectId, activeRun?.id] });
    },
  });

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const selectedStepData = steps.find((s) => s.step_name === selectedStep);

  const pendingReviewStep =
    activeRun?.status === "waiting_for_user"
      ? steps.find(
          (s) =>
            s.status === "completed" &&
            s.step_name === activeRun.current_step &&
            s.output_document_id
        )
      : null;

  return (
    <div className="space-y-4">
      {/* ── Summary bar ── */}
      <PipelineSummaryBar
        run={activeRun}
        completedCount={completedCount}
        totalSteps={PIPELINE.length}
        agents={agents}
        onStart={startMutation.mutate}
        isStarting={startMutation.isPending}
      />

      {/* ── Main 70/30 grid ── */}
      <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
        <PipelineStepsList
          run={activeRun}
          steps={steps}
          selectedKey={selectedStep}
          onSelect={setSelectedStep}
        />
        <div className="space-y-4">
          <StepDetailPanel
            projectId={projectId ?? ""}
            run={activeRun}
            stepKey={selectedStep}
            stepData={selectedStepData}
            onApprove={(id) => approveMutation.mutate(id)}
            onReject={(id) => rejectMutation.mutate(id)}
            isApproving={approveMutation.isPending}
            isRejecting={rejectMutation.isPending}
          />

          {/* Document preview for review step */}
          {pendingReviewStep && (
            <DocumentPreviewPanel
              projectId={projectId ?? ""}
              documentId={pendingReviewStep.output_document_id!}
              stepName={pendingReviewStep.step_name}
              onApprove={() => approveMutation.mutate(pendingReviewStep.id)}
              onReject={() => rejectMutation.mutate(pendingReviewStep.id)}
              isApproving={approveMutation.isPending}
              isRejecting={rejectMutation.isPending}
            />
          )}
        </div>
      </div>

      {/* ── Execution Logs toggle ── */}
      <div>
        <button
          onClick={() => setShowLogs((v) => !v)}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ScrollText className="h-3.5 w-3.5" />
          Execution Logs
          {showLogs ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
        {showLogs && <div className="mt-2"><ExecutionLogs steps={steps} run={activeRun} /></div>}
      </div>
    </div>
  );
}
