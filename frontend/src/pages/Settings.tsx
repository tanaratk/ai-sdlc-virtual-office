import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Cpu, RefreshCw, Zap, AlertCircle } from "lucide-react";
import { agentApi } from "@/services/agentApi";
import { cn } from "@/lib/utils";
import type { ModelProvider } from "@/types/agent";

// ── Model catalogue ───────────────────────────────────────────────────────────

const CLAUDE_MODELS = [
  "claude-sonnet-4-6",
  "claude-haiku-4-5-20251001",
  "claude-opus-4-8",
];

const OPENAI_MODELS = [
  "gpt-4o",
  "gpt-4o-mini",
  "gpt-4-turbo",
  "gpt-3.5-turbo",
];

const PROVIDER_LABELS: Record<ModelProvider, string> = {
  ollama:    "Ollama (Local)",
  anthropic: "Claude (Anthropic)",
  openai:    "OpenAI ChatGPT",
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatBytes(bytes: number | null) {
  if (!bytes) return "";
  return `${(bytes / 1e9).toFixed(1)} GB`;
}

function formatDate(iso: string | null) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString();
}

// ── Tab 1: Available Ollama Models ───────────────────────────────────────────

function OllamaModelsTab() {
  const queryClient = useQueryClient();

  const { data: ollamaData, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: agentApi.listOllamaModels,
    staleTime: 30_000,
    retry: false,
  });

  const { data: agents = [] } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    staleTime: 10_000,
  });

  const updateAllMutation = useMutation({
    mutationFn: (modelName: string) =>
      Promise.all(
        agents.map((a) =>
          agentApi.update(a.id, { model_provider: "ollama", model_name: modelName })
        )
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agents"] }),
  });

  const defaultModel = agents.length > 0 ? agents[0].model_name : null;
  const allSameModel = agents.length > 0 && agents.every((a) => a.model_name === agents[0].model_name && a.model_provider === "ollama");
  const activeOllama = allSameModel ? defaultModel : null;

  return (
    <div className="space-y-4">
      {/* Connection status bar */}
      <div className="flex items-center justify-between rounded-lg border bg-white px-4 py-3">
        <div>
          {isLoading && <p className="text-sm text-muted-foreground">Connecting to Ollama…</p>}
          {isError && (
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <div>
                <p className="text-sm text-destructive font-medium">Cannot reach Ollama</p>
                <p className="text-xs text-muted-foreground">
                  Make sure Ollama is running at{" "}
                  <code className="font-mono">http://localhost:11434</code>
                </p>
              </div>
            </div>
          )}
          {ollamaData && (
            <div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                <p className="text-sm font-medium">Connected</p>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                <code className="font-mono">{ollamaData.base_url}</code>
                {" "}· {ollamaData.models.length} model{ollamaData.models.length !== 1 ? "s" : ""} available
              </p>
            </div>
          )}
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", isFetching && "animate-spin")} />
          Refresh
        </button>
      </div>

      {/* Model list */}
      {ollamaData && ollamaData.models.length > 0 && (
        <div className="rounded-lg border bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/30">
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Model Name</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Size</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Last Updated</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Status</th>
                <th className="px-4 py-2.5 text-right text-xs font-semibold text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {ollamaData.models.map((model) => {
                const isDefault = model.name === activeOllama;
                return (
                  <tr key={model.name} className="hover:bg-accent/30">
                    <td className="px-4 py-3 font-mono text-xs font-medium">{model.name}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{formatBytes(model.size) || "—"}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{formatDate(model.modified_at) || "—"}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                        <span className="h-1.5 w-1.5 rounded-full bg-green-500" /> Ready
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {isDefault ? (
                        <span className="flex items-center justify-end gap-1 text-xs text-green-700">
                          <CheckCircle2 className="h-3.5 w-3.5" /> Default
                        </span>
                      ) : (
                        <button
                          onClick={() => updateAllMutation.mutate(model.name)}
                          disabled={updateAllMutation.isPending}
                          className="text-xs text-primary hover:underline disabled:opacity-50"
                        >
                          Set as default
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {ollamaData && ollamaData.models.length === 0 && (
        <div className="rounded-lg border bg-white p-6 text-center">
          <p className="text-sm text-muted-foreground">No models installed in Ollama.</p>
          <p className="text-xs text-muted-foreground mt-1">
            Run <code className="font-mono">ollama pull qwen3:8b</code> to get started.
          </p>
        </div>
      )}
    </div>
  );
}

// ── Tab 2: Per-Agent Model ────────────────────────────────────────────────────

function PerAgentModelTab() {
  const queryClient = useQueryClient();

  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    staleTime: 10_000,
  });

  const { data: ollamaData } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: agentApi.listOllamaModels,
    staleTime: 30_000,
    retry: false,
  });

  const [pending, setPending] = useState<Record<string, { provider: ModelProvider; model: string }>>({});

  const getVal = (agentId: string, field: "provider" | "model", agent: { model_provider: ModelProvider; model_name: string }) => {
    const p = pending[agentId];
    if (field === "provider") return p?.provider ?? agent.model_provider;
    return p?.model ?? agent.model_name;
  };

  const setField = (agentId: string, field: "provider" | "model", value: string, agent: { model_provider: ModelProvider; model_name: string }) => {
    setPending((prev) => {
      const current = prev[agentId] ?? { provider: agent.model_provider, model: agent.model_name };
      const next = { ...current };
      if (field === "provider") {
        next.provider = value as ModelProvider;
        // Reset model to first option for that provider
        if (value === "anthropic") next.model = CLAUDE_MODELS[0];
        else if (value === "openai") next.model = OPENAI_MODELS[0];
        else next.model = ollamaData?.models[0]?.name ?? agent.model_name;
      } else {
        next.model = value;
      }
      return { ...prev, [agentId]: next };
    });
  };

  const saveMutation = useMutation({
    mutationFn: ({ agentId, provider, model }: { agentId: string; provider: ModelProvider; model: string }) =>
      agentApi.update(agentId, { model_provider: provider, model_name: model }),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      setPending((prev) => {
        const next = { ...prev };
        delete next[vars.agentId];
        return next;
      });
    },
  });

  const saveAll = () => {
    Object.entries(pending).forEach(([agentId, { provider, model }]) => {
      saveMutation.mutate({ agentId, provider, model });
    });
  };

  const resetAll = () => setPending({});

  const hasPending = Object.keys(pending).length > 0;

  const modelOptions = (provider: ModelProvider): string[] => {
    if (provider === "anthropic") return CLAUDE_MODELS;
    if (provider === "openai") return OPENAI_MODELS;
    return ollamaData?.models.map((m) => m.name) ?? [];
  };

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading agents…</p>;
  if (agents.length === 0) return <p className="text-sm text-muted-foreground">No agents found.</p>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border bg-white overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/30">
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Agent</th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Role</th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Provider</th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Model</th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {agents.map((agent) => {
              const provider = getVal(agent.id, "provider", agent) as ModelProvider;
              const model    = getVal(agent.id, "model",    agent);
              const isDirty  = !!pending[agent.id];
              const opts     = modelOptions(provider);

              return (
                <tr key={agent.id} className={cn("hover:bg-accent/30", isDirty && "bg-amber-50/60")}>
                  <td className="px-4 py-2.5 font-medium text-xs">{agent.name}</td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground capitalize">{agent.role}</td>
                  <td className="px-4 py-2.5">
                    <select
                      value={provider}
                      onChange={(e) => setField(agent.id, "provider", e.target.value, agent)}
                      className="rounded border bg-white px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      {(Object.keys(PROVIDER_LABELS) as ModelProvider[]).map((p) => (
                        <option key={p} value={p}>{PROVIDER_LABELS[p]}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-2.5">
                    {opts.length > 0 ? (
                      <select
                        value={model}
                        onChange={(e) => setField(agent.id, "model", e.target.value, agent)}
                        className="rounded border bg-white px-2 py-1 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-ring"
                      >
                        {opts.map((m) => <option key={m} value={m}>{m}</option>)}
                      </select>
                    ) : (
                      <input
                        value={model}
                        onChange={(e) => setField(agent.id, "model", e.target.value, agent)}
                        placeholder="model name"
                        className="rounded border bg-white px-2 py-1 text-xs font-mono w-40 focus:outline-none focus:ring-1 focus:ring-ring"
                      />
                    )}
                  </td>
                  <td className="px-4 py-2.5">
                    {isDirty ? (
                      <span className="text-xs text-amber-600 font-medium">Unsaved</span>
                    ) : (
                      <span className="text-xs text-green-700">Saved</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Save / Reset bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={saveAll}
          disabled={!hasPending || saveMutation.isPending}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {saveMutation.isPending ? "Saving…" : "Save Configuration"}
        </button>
        <button
          onClick={resetAll}
          disabled={!hasPending}
          className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Reset Changes
        </button>
        {hasPending && (
          <p className="text-xs text-muted-foreground">
            {Object.keys(pending).length} agent{Object.keys(pending).length !== 1 ? "s" : ""} with unsaved changes
          </p>
        )}
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

type Tab = "ollama" | "per-agent";

export default function Settings() {
  const [activeTab, setActiveTab] = useState<Tab>("ollama");

  const tabs: Array<{ id: Tab; label: string; icon: React.ElementType }> = [
    { id: "ollama",     label: "Available Ollama Models", icon: Cpu  },
    { id: "per-agent",  label: "Per-Agent Model",         icon: Zap  },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <h2 className="text-lg font-semibold">AI Model Settings</h2>

      {/* Tab bar */}
      <div className="flex gap-1 rounded-lg border bg-muted/30 p-1 w-fit">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
              activeTab === id
                ? "bg-white shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "ollama"    && <OllamaModelsTab />}
      {activeTab === "per-agent" && <PerAgentModelTab />}
    </div>
  );
}
