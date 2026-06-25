import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { ExternalLink, Play, Square, RefreshCw, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { deployApi, type DeployStatus } from "@/services/deployApi";
import { documentApi } from "@/services/documentApi";
import { DocumentViewer } from "@/components/document/DocumentViewer";
import type { DocumentType } from "@/types/document";

const DEPLOY_DOC_TYPES: DocumentType[] = ["devops_config", "build_report", "monitoring_report"];
const DOC_LABELS: Record<string, string> = {
  devops_config:    "DevOps Config",
  build_report:     "Build Report",
  monitoring_report: "Monitoring Report",
};

// ── Status badge ───────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: DeployStatus["status"] }) {
  const map: Record<DeployStatus["status"], { label: string; cls: string; dot: string }> = {
    not_deployed: { label: "Not Deployed", cls: "bg-gray-100 text-gray-500",  dot: "bg-gray-400" },
    deploying:    { label: "Deploying…",   cls: "bg-blue-100 text-blue-600",  dot: "bg-blue-500 animate-ping" },
    running:      { label: "Running",      cls: "bg-green-100 text-green-700", dot: "bg-green-500" },
    stopped:      { label: "Stopped",      cls: "bg-yellow-100 text-yellow-700", dot: "bg-yellow-500" },
    failed:       { label: "Failed",       cls: "bg-red-100 text-red-600",    dot: "bg-red-500" },
  };
  const { label, cls, dot } = map[status] ?? map.not_deployed;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${cls}`}>
      <span className={`inline-block h-2 w-2 rounded-full ${dot}`} />
      {label}
    </span>
  );
}

// ── Deploy control panel ───────────────────────────────────────────────────────

function DeployPanel({ projectId }: { projectId: string }) {
  const qc = useQueryClient();
  const [showLogs, setShowLogs] = useState(false);

  const { data: status, isLoading } = useQuery({
    queryKey: ["deploy-status", projectId],
    queryFn: () => deployApi.getStatus(projectId),
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "deploying" ? 3000 : 10000;
    },
  });

  const { data: logsData, refetch: refetchLogs, isFetching: isLogsFetching } = useQuery({
    queryKey: ["deploy-logs", projectId],
    queryFn: () => deployApi.getLogs(projectId),
    enabled: showLogs,
    refetchOnWindowFocus: false,
  });

  const startMutation = useMutation({
    mutationFn: () => deployApi.start(projectId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["deploy-status", projectId] }),
  });

  const stopMutation = useMutation({
    mutationFn: () => deployApi.stop(projectId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["deploy-status", projectId] }),
  });

  if (isLoading) {
    return <div className="rounded-xl border border-border bg-white p-6 text-sm text-muted-foreground">Loading…</div>;
  }

  const s = status!;
  const isDeploying = s.status === "deploying" || startMutation.isPending;
  const isStopping = stopMutation.isPending;
  const canDeploy = s.has_compose_file && !isDeploying && s.status !== "running";
  const canStop   = s.status === "running" && !isStopping;

  return (
    <div className="space-y-4">
      {/* Main control card */}
      <div className="rounded-xl border border-border bg-white p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="mb-2 text-sm font-semibold text-foreground">Deploy Environment</h3>
            <StatusBadge status={s.status} />

            {s.app_url && s.status === "running" && (
              <p className="mt-2 text-xs text-muted-foreground">
                App URL:{" "}
                <a href={s.app_url} target="_blank" rel="noopener noreferrer"
                  className="font-medium text-primary underline underline-offset-2">
                  {s.app_url}
                </a>
                {s.port && <span className="ml-1 text-muted-foreground/60">(port {s.port})</span>}
              </p>
            )}

            {s.last_deployed_at && (
              <p className="mt-1 text-[10px] text-muted-foreground/60">
                Last deployed: {new Date(s.last_deployed_at).toLocaleString()}
              </p>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2">
            {s.status === "running" && s.app_url && (
              <a href={s.app_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                <ExternalLink className="h-4 w-4" />
                Open App
              </a>
            )}

            {canDeploy && (
              <button
                onClick={() => startMutation.mutate()}
                disabled={isDeploying}
                className="flex items-center gap-1.5 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                {isDeploying ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                {isDeploying ? "Deploying…" : s.status === "stopped" ? "Redeploy" : "Deploy"}
              </button>
            )}

            {canStop && (
              <button
                onClick={() => stopMutation.mutate()}
                disabled={isStopping}
                className="flex items-center gap-1.5 rounded-md border border-destructive/40 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/5 disabled:opacity-50"
              >
                <Square className="h-4 w-4" />
                {isStopping ? "Stopping…" : "Stop"}
              </button>
            )}

            {isDeploying && (
              <button
                onClick={() => qc.invalidateQueries({ queryKey: ["deploy-status", projectId] })}
                className="flex items-center gap-1 rounded-md border px-3 py-2 text-xs text-muted-foreground hover:bg-accent"
              >
                <RefreshCw className="h-3 w-3" />
                Refresh
              </button>
            )}
          </div>
        </div>

        {/* Error message */}
        {s.status === "failed" && s.error && (
          <div className="mt-4 flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <div>
              <p className="text-xs font-medium text-destructive">Deploy failed</p>
              <pre className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap text-[11px] text-destructive/80">
                {s.error}
              </pre>
            </div>
          </div>
        )}

        {/* docker not available warning */}
        {!s.docker_available && (
          <div className="mt-4 flex items-start gap-2 rounded-lg border border-yellow-300 bg-yellow-50 p-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-yellow-600" />
            <p className="text-xs text-yellow-700">
              Docker is not available inside this container. Rebuild the backend image and ensure
              <code className="mx-1 rounded bg-yellow-100 px-1 font-mono">/var/run/docker.sock</code>
              is mounted.
            </p>
          </div>
        )}

        {/* No compose file warning */}
        {!s.has_compose_file && (
          <div className="mt-4 rounded-lg border border-dashed border-border bg-muted/30 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              No <code className="font-mono">docker-compose.yml</code> found. Run the DevOps agent in the Pipeline to generate it.
            </p>
          </div>
        )}

        {/* Running services table */}
        {s.status === "running" && s.services.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-xs font-medium text-muted-foreground">Running Containers</p>
            <div className="overflow-x-auto rounded-lg border border-border text-xs">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium">Service</th>
                    <th className="px-3 py-2 text-left font-medium">State</th>
                    <th className="px-3 py-2 text-left font-medium">Ports</th>
                  </tr>
                </thead>
                <tbody>
                  {s.services.map((svc, i) => (
                    <tr key={i} className="border-t border-border">
                      <td className="px-3 py-2 font-mono">{String(svc.Service ?? svc.Name ?? "—")}</td>
                      <td className="px-3 py-2">
                        <span className={`rounded px-1.5 py-0.5 ${String(svc.State).toLowerCase() === "running" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                          {String(svc.State ?? "—")}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-mono text-muted-foreground">
                        {typeof svc.Ports === "string"
                          ? [...new Set(
                              (svc.Ports as string)
                                .split(", ")
                                .filter(s => s.startsWith("0.0.0.0:"))
                                .map(s => s.replace("0.0.0.0:", "").replace("->", "→"))
                            )].join(", ") || "—"
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Logs panel */}
      <div className="rounded-xl border border-border bg-white">
        <button
          onClick={() => setShowLogs((v) => !v)}
          className="flex w-full items-center justify-between px-6 py-4 text-sm font-medium"
        >
          <span>Container Logs</span>
          <div className="flex items-center gap-2">
            {showLogs && (
              <button
                onClick={(e) => { e.stopPropagation(); refetchLogs(); }}
                className="flex items-center gap-1 rounded border px-2 py-0.5 text-xs text-muted-foreground hover:bg-accent"
              >
                <RefreshCw className={`h-3 w-3 ${isLogsFetching ? "animate-spin" : ""}`} />
                Refresh
              </button>
            )}
            {showLogs ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
          </div>
        </button>
        {showLogs && (
          <div className="border-t border-border">
            <pre className="max-h-80 overflow-y-auto px-6 py-4 font-mono text-[11px] leading-relaxed text-foreground/80 whitespace-pre-wrap">
              {logsData?.logs ?? "(Click Refresh to load logs)"}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// ── DevOps documents section ───────────────────────────────────────────────────

function DeployDocs({ projectId }: { projectId: string }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["documents", projectId],
    queryFn: () => documentApi.list(projectId, 1, 100),
    enabled: !!projectId,
  });

  const { data: selectedDoc, isLoading: isDocLoading } = useQuery({
    queryKey: ["document", projectId, selectedId],
    queryFn: () => documentApi.get(projectId, selectedId!),
    enabled: !!selectedId,
  });

  const deployDocs = (data?.items ?? []).filter((d) => DEPLOY_DOC_TYPES.includes(d.document_type));

  if (deployDocs.length === 0) return null;

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold text-foreground">DevOps Documents</h3>
      <div className="flex gap-4">
        {/* Doc selector */}
        <div className="w-48 shrink-0 space-y-2">
          {DEPLOY_DOC_TYPES.map((type) => {
            const docs = deployDocs.filter((d) => d.document_type === type);
            if (docs.length === 0) {
              return (
                <div key={type} className="rounded-lg border border-dashed border-border p-3 opacity-40">
                  <p className="text-xs font-medium text-muted-foreground">{DOC_LABELS[type]}</p>
                </div>
              );
            }
            return docs.map((doc) => (
              <button
                key={doc.id}
                onClick={() => setSelectedId(doc.id)}
                className={`w-full rounded-lg border p-3 text-left text-xs transition-colors hover:bg-accent ${
                  selectedId === doc.id ? "border-primary bg-primary/5 font-medium" : "border-border"
                }`}
              >
                {DOC_LABELS[type]}
                <span className={`mt-1 block text-[10px] ${doc.status === "approved" ? "text-green-600" : "text-muted-foreground/60"}`}>
                  {doc.status} · v{doc.version}
                </span>
              </button>
            ));
          })}
        </div>

        {/* Doc viewer */}
        <div className="flex-1 min-w-0">
          {!selectedId ? (
            <div className="flex h-40 items-center justify-center rounded-xl border border-dashed border-border text-sm text-muted-foreground">
              Select a document to view
            </div>
          ) : (
            <div className="rounded-xl border border-border bg-white p-6">
              {isDocLoading ? (
                <p className="text-sm text-muted-foreground">Loading…</p>
              ) : selectedDoc ? (
                <DocumentViewer document={selectedDoc} />
              ) : (
                <p className="text-sm text-destructive">Failed to load document.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function DeployPage() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <div className="space-y-8">
      <DeployPanel projectId={projectId!} />
      <DeployDocs projectId={projectId!} />
    </div>
  );
}
