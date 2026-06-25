import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ExternalLink,
  PauseCircle,
  PlayCircle,
  Radio,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import apiClient from "@/services/apiClient";
import { cn } from "@/lib/utils";

interface ActiveRun {
  run_id: string;
  project_id: string;
  project_name: string;
  status: "running" | "waiting_for_user";
  current_step: string | null;
  active_step: string | null;
  active_step_status: string | null;
  started_at: string | null;
  step_count: number;
}

function fetchActiveRuns(): Promise<{ active_runs: ActiveRun[]; total: number }> {
  return apiClient.get("/admin/pipeline/active").then((r) => r.data);
}

function cancelRun(runId: string): Promise<void> {
  return apiClient.post(`/admin/pipeline/runs/${runId}/cancel`).then((r) => r.data);
}

const STATUS_LABEL: Record<ActiveRun["status"], string> = {
  running: "Running",
  waiting_for_user: "Waiting for approval",
};

const STEP_LABELS: Record<string, string> = {
  requirement_summary: "Requirement Summary",
  gap_analysis: "Gap Analysis",
  ba_documents: "BRD + FSD + User Stories",
  sa_documents: "Architecture + DB + API",
  ux_documents: "Screen Spec + UX Flows",
  technical_design: "Technical Design",
  dev_tasks: "Generated Code",
  code_review: "Code Review",
  test_cases: "Generated Tests + Report",
  devops_tasks: "Build + Deploy Package",
  monitoring: "Monitoring Report",
};

function stepLabel(step: string | null) {
  if (!step) return "No active step";
  return STEP_LABELS[step] ?? step;
}

function elapsed(iso: string | null): string {
  if (!iso) return "-";
  const diff = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
  return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
}

function SummaryCard({
  label,
  value,
  helper,
  icon: Icon,
  tone,
}: {
  label: string;
  value: number | string;
  helper: string;
  icon: React.ElementType;
  tone: "blue" | "amber" | "emerald" | "slate";
}) {
  const color = {
    blue: "bg-blue-100 text-blue-700",
    amber: "bg-amber-100 text-amber-700",
    emerald: "bg-emerald-100 text-emerald-700",
    slate: "bg-slate-100 text-slate-700",
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

function StatusPill({ status }: { status: ActiveRun["status"] }) {
  const className =
    status === "running"
      ? "bg-blue-100 text-blue-700"
      : "bg-amber-100 text-amber-700";

  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium", className)}>
      {status === "running" ? <PlayCircle className="h-3.5 w-3.5" /> : <PauseCircle className="h-3.5 w-3.5" />}
      {STATUS_LABEL[status]}
    </span>
  );
}

export default function PipelineMonitorPage() {
  const queryClient = useQueryClient();
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const { data, isLoading, isError, dataUpdatedAt } = useQuery({
    queryKey: ["admin-pipeline-active"],
    queryFn: fetchActiveRuns,
    refetchInterval: 5000,
  });

  const cancelMutation = useMutation({
    mutationFn: cancelRun,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-pipeline-active"] });
      setConfirmId(null);
    },
  });

  const runs = data?.active_runs ?? [];
  const waitingRuns = runs.filter((r) => r.status === "waiting_for_user");
  const runningRuns = runs.filter((r) => r.status === "running");
  const confirmRun = runs.find((r) => r.run_id === confirmId);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="flex flex-col gap-4 rounded-lg border bg-white p-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            <Radio className="h-3.5 w-3.5" />
            Live pipeline control center
          </div>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight">Control active agent runs</h2>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            Monitor every running project, catch approval gates, and stop failed or incorrect runs before downstream agents continue.
          </p>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ["admin-pipeline-active"] })}
          className="inline-flex items-center justify-center gap-2 rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh now
        </button>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Active runs" value={isLoading ? "-" : runs.length} helper="All projects currently in pipeline execution." icon={Activity} tone="blue" />
        <SummaryCard label="Running" value={isLoading ? "-" : runningRuns.length} helper="Agents actively producing outputs." icon={PlayCircle} tone="emerald" />
        <SummaryCard label="Waiting approval" value={isLoading ? "-" : waitingRuns.length} helper="Human gates that need attention." icon={ShieldCheck} tone="amber" />
        <SummaryCard
          label="Last refresh"
          value={dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-"}
          helper="Automatically refreshes every 5 seconds."
          icon={Clock3}
          tone="slate"
        />
      </section>

      {waitingRuns.length > 0 && (
        <section className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-700" />
              <div>
                <p className="text-sm font-semibold text-amber-900">Approval required</p>
                <p className="text-xs text-amber-800">
                  {waitingRuns.length} run{waitingRuns.length !== 1 ? "s" : ""} paused at a human review gate.
                </p>
              </div>
            </div>
            <Link
              to={`/projects/${waitingRuns[0].project_id}/agents`}
              className="inline-flex items-center justify-center gap-2 rounded-md bg-amber-700 px-3 py-2 text-xs font-medium text-white hover:bg-amber-800"
            >
              Review first gate
              <ExternalLink className="h-3.5 w-3.5" />
            </Link>
          </div>
        </section>
      )}

      <section className="rounded-lg border bg-white">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <div>
            <h3 className="text-sm font-semibold">Active Run Queue</h3>
            <p className="text-xs text-muted-foreground">Project, status, current agent step, elapsed time, and run controls.</p>
          </div>
          <div className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Worker connected
          </div>
        </div>

        {isLoading && (
          <div className="px-5 py-10 text-sm text-muted-foreground">Loading active runs...</div>
        )}

        {isError && (
          <div className="px-5 py-10 text-sm text-destructive">
            Cannot connect to backend API. Start the server to monitor pipeline runs.
          </div>
        )}

        {!isLoading && !isError && runs.length === 0 && (
          <div className="flex flex-col items-center gap-2 px-6 py-14 text-center">
            <CheckCircle2 className="h-10 w-10 text-emerald-500" />
            <p className="text-sm font-medium">No active pipeline runs</p>
            <p className="max-w-sm text-xs text-muted-foreground">
              All pipelines are idle or completed. Start a run from a project workspace.
            </p>
            <Link
              to="/projects"
              className="mt-2 inline-flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-medium hover:bg-accent"
            >
              Open projects
              <ExternalLink className="h-3.5 w-3.5" />
            </Link>
          </div>
        )}

        {runs.length > 0 && (
          <div className="divide-y">
            {runs.map((run) => (
              <div key={run.run_id} className="grid gap-4 px-5 py-4 transition-colors hover:bg-accent/50 xl:grid-cols-[1.25fr_0.75fr_1fr_0.5fr_auto] xl:items-center">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{run.project_name}</p>
                  <p className="mt-1 font-mono text-xs text-muted-foreground">{run.run_id}</p>
                </div>

                <div>
                  <StatusPill status={run.status} />
                </div>

                <div className="min-w-0">
                  <p className="text-xs font-medium text-muted-foreground">Current step</p>
                  <p className="mt-1 truncate text-sm font-medium">{stepLabel(run.active_step)}</p>
                  {run.active_step_status && (
                    <p className="mt-1 text-xs text-muted-foreground">Step status: {run.active_step_status}</p>
                  )}
                </div>

                <div>
                  <p className="text-xs font-medium text-muted-foreground">Elapsed</p>
                  <p className="mt-1 text-sm font-semibold tabular-nums">{elapsed(run.started_at)}</p>
                </div>

                <div className="flex flex-wrap justify-start gap-2 xl:justify-end">
                  <Link
                    to={`/projects/${run.project_id}/agents`}
                    className="inline-flex items-center gap-1.5 rounded-md border px-3 py-2 text-xs font-medium hover:bg-white"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Open
                  </Link>
                  <button
                    onClick={() => setConfirmId(run.run_id)}
                    className="inline-flex items-center gap-1.5 rounded-md border border-destructive/40 px-3 py-2 text-xs font-medium text-destructive hover:bg-destructive/10"
                  >
                    <XCircle className="h-3.5 w-3.5" />
                    Cancel
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {confirmId && confirmRun && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-sm rounded-lg border bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-md bg-destructive/10">
                <AlertTriangle className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <p className="text-sm font-semibold">Cancel pipeline run?</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">{confirmRun.project_name}</span> will be stopped at the next worker checkpoint and marked as failed.
                </p>
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <button
                onClick={() => setConfirmId(null)}
                disabled={cancelMutation.isPending}
                className="rounded-md border px-4 py-2 text-xs font-medium hover:bg-muted disabled:opacity-50"
              >
                Keep running
              </button>
              <button
                onClick={() => cancelMutation.mutate(confirmId)}
                disabled={cancelMutation.isPending}
                className="inline-flex items-center gap-1.5 rounded-md bg-destructive px-4 py-2 text-xs font-medium text-white hover:bg-destructive/90 disabled:opacity-50"
              >
                <XCircle className="h-3.5 w-3.5" />
                {cancelMutation.isPending ? "Cancelling..." : "Cancel run"}
              </button>
            </div>
            {cancelMutation.isError && (
              <p className="mt-3 text-xs text-destructive">{(cancelMutation.error as Error).message}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
