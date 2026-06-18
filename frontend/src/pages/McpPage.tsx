import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Loader2,
  Play,
  Shield,
  ShieldAlert,
  XCircle,
  Zap,
} from "lucide-react";
import { mcpApi, type McpTool, type McpToolCall } from "@/services/mcpApi";
import { cn } from "@/lib/utils";

const CATEGORY_LABELS: Record<string, string> = {
  github: "GitHub",
  filesystem: "Filesystem",
  database: "Database",
  design: "Design",
  browser: "Browser",
  document: "Document",
  testing: "Testing",
};

const STATUS_STYLES: Record<McpToolCall["status"], string> = {
  pending:   "bg-yellow-100 text-yellow-700",
  approved:  "bg-blue-100 text-blue-700",
  rejected:  "bg-gray-100 text-gray-600",
  running:   "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  failed:    "bg-red-100 text-red-700",
};

export default function McpPage() {
  const { projectId } = useParams<{ projectId?: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [invokeTarget, setInvokeTarget] = useState<McpTool | null>(null);
  const [invokeInput, setInvokeInput] = useState("{}");
  const [invokeInputError, setInvokeInputError] = useState<string | null>(null);
  const [expandedCall, setExpandedCall] = useState<string | null>(null);

  // ── Queries ──────────────────────────────────────────────────────────────────
  const { data: tools = [], isLoading: toolsLoading } = useQuery({
    queryKey: ["mcp-tools"],
    queryFn: mcpApi.listTools,
  });

  const { data: calls = [], isLoading: callsLoading } = useQuery({
    queryKey: ["mcp-calls", projectId],
    queryFn: () => mcpApi.listCalls(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  });

  // ── Mutations ────────────────────────────────────────────────────────────────
  const toggleMutation = useMutation({
    mutationFn: ({ name, enabled }: { name: string; enabled: boolean }) =>
      mcpApi.updateTool(name, enabled),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mcp-tools"] }),
  });

  const invokeMutation = useMutation({
    mutationFn: () => {
      let parsed: Record<string, unknown> = {};
      try {
        parsed = JSON.parse(invokeInput) as Record<string, unknown>;
      } catch {
        throw new Error("Input is not valid JSON. Please fix it before submitting.");
      }
      return mcpApi.invoke(projectId!, {
        tool_name: invokeTarget!.tool_name,
        input_json: parsed,
        requested_by: "user",
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mcp-calls", projectId] });
      setInvokeTarget(null);
      setInvokeInput("{}");
      setInvokeInputError(null);
    },
  });

  const approveMutation = useMutation({
    mutationFn: (callId: string) => mcpApi.approve(projectId!, callId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mcp-calls", projectId] }),
  });

  const rejectMutation = useMutation({
    mutationFn: (callId: string) => mcpApi.reject(projectId!, callId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mcp-calls", projectId] }),
  });

  // ── Derived ──────────────────────────────────────────────────────────────────
  const toolsByCategory = tools.reduce<Record<string, McpTool[]>>((acc, t) => {
    acc[t.category] = acc[t.category] ?? [];
    acc[t.category].push(t);
    return acc;
  }, {});

  const pendingCalls = calls.filter((c) => c.status === "pending");

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="h-5 w-5" /> MCP Tool Registry
          </h2>
          <p className="text-sm text-muted-foreground">
            Manage external tools agents can invoke. Tools marked as dangerous require
            human approval before execution.
          </p>
        </div>
      </div>

      {/* ── Pending approvals ────────────────────────────────────────────────── */}
      {projectId && pendingCalls.length > 0 && (
        <section className="rounded-lg border border-yellow-300 bg-yellow-50 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-yellow-800 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4" />
            {pendingCalls.length} Pending Approval{pendingCalls.length > 1 ? "s" : ""}
          </h3>
          <ul className="space-y-2">
            {pendingCalls.map((call) => (
              <li key={call.id} className="flex items-center justify-between rounded-md bg-white border p-3">
                <div>
                  <p className="text-sm font-medium">{call.tool_name}</p>
                  <p className="text-xs text-muted-foreground">
                    Requested by {call.requested_by ?? "system"} ·{" "}
                    {new Date(call.requested_at).toLocaleTimeString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => approveMutation.mutate(call.id)}
                    disabled={approveMutation.isPending}
                    className="flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                  </button>
                  <button
                    onClick={() => rejectMutation.mutate(call.id)}
                    disabled={rejectMutation.isPending}
                    className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50"
                  >
                    <XCircle className="h-3.5 w-3.5" /> Reject
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ── Tool Registry ────────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h3 className="text-sm font-semibold">Available Tools</h3>
        {toolsLoading ? (
          <p className="text-sm text-muted-foreground">Loading tools…</p>
        ) : (
          Object.entries(toolsByCategory).map(([category, categoryTools]) => (
            <div key={category}>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {CATEGORY_LABELS[category] ?? category}
              </p>
              <ul className="space-y-1.5">
                {categoryTools.map((tool) => (
                  <li
                    key={tool.tool_name}
                    className={cn(
                      "flex items-center justify-between rounded-md border p-3",
                      !tool.is_enabled && "opacity-50",
                    )}
                  >
                    <div className="flex items-start gap-2 min-w-0">
                      {tool.is_dangerous ? (
                        <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                      ) : tool.requires_approval ? (
                        <Shield className="mt-0.5 h-4 w-4 shrink-0 text-yellow-500" />
                      ) : (
                        <Zap className="mt-0.5 h-4 w-4 shrink-0 text-green-500" />
                      )}
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">{tool.display_name}</p>
                        <p className="text-xs text-muted-foreground">{tool.description}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          <code className="font-mono">{tool.tool_name}</code>
                          {" · "}
                          {tool.requires_approval ? "Requires approval" : "Auto-execute"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-3 shrink-0">
                      {projectId && tool.is_enabled && (
                        <button
                          onClick={() => { setInvokeTarget(tool); setInvokeInput("{}"); }}
                          className="flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs hover:bg-accent"
                        >
                          <Play className="h-3 w-3" /> Invoke
                        </button>
                      )}
                      <button
                        onClick={() =>
                          toggleMutation.mutate({
                            name: tool.tool_name,
                            enabled: !tool.is_enabled,
                          })
                        }
                        className={cn(
                          "h-5 w-9 rounded-full transition-colors focus:outline-none",
                          tool.is_enabled ? "bg-primary" : "bg-muted",
                        )}
                        title={tool.is_enabled ? "Disable" : "Enable"}
                      >
                        <span
                          className={cn(
                            "block h-4 w-4 rounded-full bg-white shadow transition-transform mx-0.5",
                            tool.is_enabled ? "translate-x-4" : "translate-x-0",
                          )}
                        />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
        <div className="flex gap-4 text-xs text-muted-foreground pt-1">
          <span className="flex items-center gap-1"><Zap className="h-3 w-3 text-green-500" /> Auto-execute</span>
          <span className="flex items-center gap-1"><Shield className="h-3 w-3 text-yellow-500" /> Requires approval</span>
          <span className="flex items-center gap-1"><ShieldAlert className="h-3 w-3 text-destructive" /> Dangerous</span>
        </div>
      </section>

      {/* ── Invoke modal ─────────────────────────────────────────────────────── */}
      {invokeTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl space-y-4">
            <h3 className="font-semibold">Invoke: {invokeTarget.display_name}</h3>
            <p className="text-xs text-muted-foreground">
              <code className="font-mono">{invokeTarget.tool_name}</code>
              {invokeTarget.requires_approval
                ? " — will create a pending call for your approval."
                : " — will execute immediately."}
            </p>
            <div className="space-y-1">
              <label className="text-xs font-medium">Input JSON</label>
              <textarea
                value={invokeInput}
                onChange={(e) => {
                  setInvokeInput(e.target.value);
                  try {
                    JSON.parse(e.target.value);
                    setInvokeInputError(null);
                  } catch {
                    setInvokeInputError("Invalid JSON syntax");
                  }
                }}
                rows={5}
                className={`w-full rounded-md border px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring resize-none ${
                  invokeInputError ? "border-destructive" : ""
                }`}
              />
              {invokeInputError && (
                <p className="text-xs text-destructive">{invokeInputError}</p>
              )}
            </div>
            {invokeMutation.isError && (
              <div className="flex items-start gap-2 text-sm text-destructive">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                {invokeMutation.error instanceof Error
                  ? invokeMutation.error.message
                  : "Failed to invoke tool."}
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setInvokeTarget(null);
                  setInvokeInputError(null);
                  invokeMutation.reset();
                }}
                className="rounded-md border px-4 py-1.5 text-sm hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={() => invokeMutation.mutate()}
                disabled={invokeMutation.isPending || !!invokeInputError}
                className="flex items-center gap-2 rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {invokeMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                {invokeTarget.requires_approval ? "Submit for Approval" : "Execute Now"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Call history ─────────────────────────────────────────────────────── */}
      {projectId && (
        <section className="space-y-3 border-t pt-6">
          <h3 className="text-sm font-semibold">
            Tool Call History ({calls.length})
          </h3>
          {callsLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : calls.length === 0 ? (
            <p className="text-sm text-muted-foreground">No tool calls yet.</p>
          ) : (
            <ul className="space-y-1.5">
              {calls.map((call) => (
                <li key={call.id} className="rounded-md border">
                  <button
                    className="w-full flex items-center justify-between p-3 text-left hover:bg-accent/30"
                    onClick={() => setExpandedCall(expandedCall === call.id ? null : call.id)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedCall === call.id
                        ? <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
                        : <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />}
                      <div>
                        <p className="text-sm font-medium">{call.tool_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(call.requested_at).toLocaleString()}
                          {call.requested_by && ` · by ${call.requested_by}`}
                        </p>
                      </div>
                    </div>
                    <span className={cn(
                      "rounded-full px-2 py-0.5 text-[10px] font-medium",
                      STATUS_STYLES[call.status],
                    )}>
                      {call.status}
                    </span>
                  </button>
                  {expandedCall === call.id && (
                    <div className="border-t px-4 py-3 space-y-2 text-xs">
                      {call.input_json && (
                        <div>
                          <p className="font-semibold text-muted-foreground mb-1">Input</p>
                          <pre className="rounded bg-muted p-2 overflow-x-auto text-[11px]">
                            {JSON.stringify(call.input_json, null, 2)}
                          </pre>
                        </div>
                      )}
                      {call.output_json && (
                        <div>
                          <p className="font-semibold text-muted-foreground mb-1">Output</p>
                          <pre className="rounded bg-muted p-2 overflow-x-auto text-[11px]">
                            {JSON.stringify(call.output_json, null, 2)}
                          </pre>
                        </div>
                      )}
                      {call.error_message && (
                        <p className="text-destructive">{call.error_message}</p>
                      )}
                      {call.status === "pending" && (
                        <div className="flex gap-2 pt-1">
                          <button
                            onClick={() => approveMutation.mutate(call.id)}
                            className="flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
                          >
                            <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                          </button>
                          <button
                            onClick={() => rejectMutation.mutate(call.id)}
                            className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent"
                          >
                            <XCircle className="h-3.5 w-3.5" /> Reject
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}
