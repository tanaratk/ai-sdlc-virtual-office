import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import { Activity, ExternalLink, XCircle, RefreshCw, AlertTriangle, CheckCircle2 } from "lucide-react";
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
  running:          "Running",
  waiting_for_user: "Waiting for approval",
};
const STATUS_COLOR: Record<ActiveRun["status"], string> = {
  running:          "bg-blue-100 text-blue-700",
  waiting_for_user: "bg-yellow-100 text-yellow-700",
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
  if (!step) return null;
  return STEP_LABELS[step] ?? step;
}

function elapsed(iso: string | null): string {
  if (!iso) return "—";
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60)  return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
  return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
}

export default function PipelineMonitorPage() {
  const queryClient = useQueryClient();
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const { data, isLoading, dataUpdatedAt } = useQuery({
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
  const confirmRun = runs.find((r) => r.run_id === confirmId);

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Pipeline Monitor</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Active runs across all projects · refreshes every 5s
            {dataUpdatedAt ? ` · updated ${new Date(dataUpdatedAt).toLocaleTimeString()}` : ""}
          </p>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ["admin-pipeline-active"] })}
          className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>

      {/* Worker status bar */}
      <div className="flex items-center gap-2 rounded-lg border bg-muted/30 px-4 py-3 text-xs">
        <div className="flex h-2 w-2 rounded-full bg-green-500" />
        <span className="text-muted-foreground">Celery worker connected</span>
        <span className="mx-2 text-muted-foreground/40">·</span>
        <Activity className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-medium">{data?.total ?? "—"} active run{data?.total !== 1 ? "s" : ""}</span>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!isLoading && runs.length === 0 && (
        <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed py-14 text-center">
          <CheckCircle2 className="h-8 w-8 text-muted-foreground/50" />
          <p className="text-sm font-medium text-muted-foreground">No active pipeline runs</p>
          <p className="text-xs text-muted-foreground">All pipelines are idle or completed.</p>
        </div>
      )}

      {runs.length > 0 && (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Project</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Current Step</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Elapsed</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {runs.map((run) => (
                <tr key={run.run_id} className="bg-white hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium">{run.project_name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{run.run_id.slice(0, 8)}…</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", STATUS_COLOR[run.status])}>
                      {STATUS_LABEL[run.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {run.active_step ? (
                      <span className="font-mono bg-muted px-1.5 py-0.5 rounded">
                        {stepLabel(run.active_step)}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                    {run.active_step_status && (
                      <span className="ml-2 text-muted-foreground">({run.active_step_status})</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground tabular-nums">
                    {elapsed(run.started_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        to={`/projects/${run.project_id}/agents`}
                        className="flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs text-muted-foreground hover:bg-accent"
                      >
                        <ExternalLink className="h-3 w-3" />
                        View
                      </Link>
                      <button
                        onClick={() => setConfirmId(run.run_id)}
                        className="flex items-center gap-1 rounded-md border border-destructive/40 px-2.5 py-1 text-xs text-destructive hover:bg-destructive/10"
                      >
                        <XCircle className="h-3 w-3" />
                        Cancel
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirm dialog */}
      {confirmId && confirmRun && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-sm rounded-xl border bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-destructive/10">
                <AlertTriangle className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <p className="text-sm font-semibold">Cancel pipeline run?</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">{confirmRun.project_name}</span> — the
                  run will be marked as failed. The Celery worker will stop at its next checkpoint.
                </p>
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <button
                onClick={() => setConfirmId(null)}
                disabled={cancelMutation.isPending}
                className="rounded-md border px-4 py-1.5 text-xs font-medium hover:bg-muted disabled:opacity-50"
              >
                Keep running
              </button>
              <button
                onClick={() => cancelMutation.mutate(confirmId)}
                disabled={cancelMutation.isPending}
                className="flex items-center gap-1.5 rounded-md bg-destructive px-4 py-1.5 text-xs font-medium text-white hover:bg-destructive/90 disabled:opacity-50"
              >
                <XCircle className="h-3 w-3" />
                {cancelMutation.isPending ? "Cancelling…" : "Cancel run"}
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
