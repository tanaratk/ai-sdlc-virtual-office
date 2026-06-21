import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2, RefreshCw, Zap, AlertCircle,
  Eye, EyeOff, Key, ChevronDown, ChevronRight,
} from "lucide-react";
import { agentApi } from "@/services/agentApi";
import { settingsApi } from "@/services/settingsApi";
import { cn } from "@/lib/utils";
import type { LlmSetting, ModelProvider } from "@/types/agent";

// ── Model catalogues ──────────────────────────────────────────────────────────

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

// ── API Key input ─────────────────────────────────────────────────────────────

function ApiKeyField({
  hasKey,
  onSave,
  isPending,
}: {
  hasKey: boolean;
  onSave: (key: string) => void;
  isPending: boolean;
}) {
  const [editing, setEditing] = useState(!hasKey);
  const [value, setValue] = useState("");
  const [show, setShow] = useState(false);

  if (!editing && hasKey) {
    return (
      <div className="flex items-center gap-2">
        <Key className="h-3.5 w-3.5 text-green-600" />
        <span className="text-xs text-green-700 font-medium">API key configured</span>
        <button
          onClick={() => { setEditing(true); setValue(""); }}
          className="text-xs text-muted-foreground hover:text-foreground underline"
        >
          Change
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Key className="h-3.5 w-3.5 text-muted-foreground" />
      <div className="relative flex-1 max-w-xs">
        <input
          type={show ? "text" : "password"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="sk-..."
          className="w-full rounded border px-3 py-1.5 text-xs font-mono pr-8 focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          {show ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
        </button>
      </div>
      <button
        onClick={() => { if (value.trim()) { onSave(value.trim()); setEditing(false); } }}
        disabled={!value.trim() || isPending}
        className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40"
      >
        {isPending ? "Saving…" : "Save Key"}
      </button>
      {hasKey && (
        <button onClick={() => setEditing(false)} className="text-xs text-muted-foreground hover:text-foreground">
          Cancel
        </button>
      )}
    </div>
  );
}

// ── Ollama section ────────────────────────────────────────────────────────────

function OllamaSection() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(true);

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
        agents.map((a) => agentApi.update(a.id, { model_provider: "ollama", model_name: modelName }))
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agents"] }),
  });

  const allSameOllama = agents.length > 0 && agents.every(
    (a) => a.model_provider === "ollama" && a.model_name === agents[0].model_name
  );
  const activeModel = allSameOllama ? agents[0]?.model_name : null;

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-accent/30"
      >
        <div className="flex items-center gap-3">
          {open ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
          <span className="text-sm font-semibold">Ollama (Local)</span>
          {ollamaData && (
            <span className="flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-700">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500" /> Connected · {ollamaData.models.length} models
            </span>
          )}
          {isError && (
            <span className="flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700">
              <AlertCircle className="h-3 w-3" /> Offline
            </span>
          )}
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); refetch(); }}
          disabled={isFetching}
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", isFetching && "animate-spin")} />
          Refresh
        </button>
      </button>

      {open && (
        <div className="border-t">
          {isLoading && <p className="px-4 py-3 text-sm text-muted-foreground">Connecting…</p>}
          {isError && (
            <div className="px-4 py-3 text-sm text-destructive">
              Cannot reach Ollama at <code className="font-mono text-xs">http://localhost:11434</code>
            </div>
          )}
          {ollamaData && ollamaData.models.length === 0 && (
            <p className="px-4 py-3 text-sm text-muted-foreground">
              No models installed. Run <code className="font-mono text-xs">ollama pull qwen3:8b</code>
            </p>
          )}
          {ollamaData && ollamaData.models.length > 0 && (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted/20 text-xs font-semibold text-muted-foreground">
                  <th className="px-4 py-2 text-left">Model</th>
                  <th className="px-4 py-2 text-left">Size</th>
                  <th className="px-4 py-2 text-left">Updated</th>
                  <th className="px-4 py-2 text-left">Status</th>
                  <th className="px-4 py-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {ollamaData.models.map((model) => (
                  <tr key={model.name} className="hover:bg-accent/20">
                    <td className="px-4 py-2.5 font-mono text-xs font-medium">{model.name}</td>
                    <td className="px-4 py-2.5 text-xs text-muted-foreground">{formatBytes(model.size) || "—"}</td>
                    <td className="px-4 py-2.5 text-xs text-muted-foreground">{formatDate(model.modified_at) || "—"}</td>
                    <td className="px-4 py-2.5">
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-700">
                        <span className="h-1.5 w-1.5 rounded-full bg-green-500" /> Ready
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      {model.name === activeModel ? (
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
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

// ── Claude / OpenAI section ───────────────────────────────────────────────────

function CloudProviderSection({
  provider,
  models: modelCatalogue,
  existingSettings,
}: {
  provider: "anthropic" | "openai";
  models: string[];
  existingSettings: LlmSetting[];
}) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(true);

  const providerSettings = existingSettings.filter((s) => s.provider === provider);
  const hasApiKey = providerSettings.some((s) => s.has_api_key);

  // Find setting row for a given model name
  const settingFor = (modelName: string) =>
    providerSettings.find((s) => s.model_name === modelName);

  const saveKeyMutation = useMutation({
    mutationFn: async (apiKey: string) => {
      const results = [];
      for (const modelName of modelCatalogue) {
        const existing = settingFor(modelName);
        if (existing) {
          results.push(await settingsApi.patchLlm(existing.id, { api_key: apiKey }));
        } else {
          results.push(await settingsApi.createLlm({ provider, model_name: modelName, api_key: apiKey, is_active: false }));
        }
      }
      return results;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["llm-settings"] }),
  });

  const toggleMutation = useMutation({
    mutationFn: async ({ modelName, active }: { modelName: string; active: boolean }) => {
      const existing = settingFor(modelName);
      if (existing) {
        return settingsApi.patchLlm(existing.id, { is_active: active });
      }
      // Create row if doesn't exist (shouldn't happen if API key was saved first)
      return settingsApi.createLlm({ provider, model_name: modelName, is_active: active });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["llm-settings"] }),
  });

  const label = PROVIDER_LABELS[provider];
  const enabledCount = providerSettings.filter((s) => s.is_active).length;

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-accent/30"
      >
        <div className="flex items-center gap-3">
          {open ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
          <span className="text-sm font-semibold">{label}</span>
          {hasApiKey && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700">
              {enabledCount} / {modelCatalogue.length} enabled
            </span>
          )}
          {!hasApiKey && (
            <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
              No API key
            </span>
          )}
        </div>
      </button>

      {open && (
        <div className="border-t divide-y">
          {/* API Key section */}
          <div className="px-4 py-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">API Key</p>
            <ApiKeyField
              hasKey={hasApiKey}
              onSave={(key) => saveKeyMutation.mutate(key)}
              isPending={saveKeyMutation.isPending}
            />
            {saveKeyMutation.isError && (
              <p className="mt-1 text-xs text-destructive">Failed to save API key.</p>
            )}
          </div>

          {/* Model list */}
          <div className="px-4 py-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">
              Models {!hasApiKey && <span className="font-normal">— save API key first to enable models</span>}
            </p>
            <div className="space-y-2">
              {modelCatalogue.map((modelName) => {
                const setting = settingFor(modelName);
                const isEnabled = setting?.is_active ?? false;
                const canToggle = hasApiKey;

                return (
                  <div key={modelName} className="flex items-center justify-between rounded-md border px-3 py-2">
                    <span className="text-xs font-mono font-medium">{modelName}</span>
                    <label className={cn("relative inline-flex items-center cursor-pointer", !canToggle && "opacity-40 cursor-not-allowed")}>
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={isEnabled}
                        disabled={!canToggle || toggleMutation.isPending}
                        onChange={(e) => {
                          if (!canToggle) return;
                          toggleMutation.mutate({ modelName, active: e.target.checked });
                        }}
                      />
                      <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary transition-colors" />
                      <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4" />
                    </label>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Tab 1: Available Models ───────────────────────────────────────────────────

function AvailableModelsTab() {
  const { data: llmSettings = [] } = useQuery({
    queryKey: ["llm-settings"],
    queryFn: settingsApi.listLlm,
    staleTime: 10_000,
  });

  return (
    <div className="space-y-3">
      <OllamaSection />
      <CloudProviderSection provider="anthropic" models={CLAUDE_MODELS} existingSettings={llmSettings} />
      <CloudProviderSection provider="openai"    models={OPENAI_MODELS} existingSettings={llmSettings} />
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

  const { data: llmSettings = [] } = useQuery({
    queryKey: ["llm-settings"],
    queryFn: settingsApi.listLlm,
    staleTime: 10_000,
  });

  const [pending, setPending] = useState<Record<string, { provider: ModelProvider; model: string }>>({});

  const getVal = (agentId: string, field: "provider" | "model", agent: { model_provider: ModelProvider; model_name: string }) => {
    const p = pending[agentId];
    return field === "provider" ? (p?.provider ?? agent.model_provider) : (p?.model ?? agent.model_name);
  };

  const modelOptions = (provider: ModelProvider): string[] => {
    if (provider === "anthropic") {
      const enabled = llmSettings.filter((s) => s.provider === "anthropic" && s.is_active).map((s) => s.model_name);
      return enabled.length > 0 ? enabled : CLAUDE_MODELS;
    }
    if (provider === "openai") {
      const enabled = llmSettings.filter((s) => s.provider === "openai" && s.is_active).map((s) => s.model_name);
      return enabled.length > 0 ? enabled : OPENAI_MODELS;
    }
    return ollamaData?.models.map((m) => m.name) ?? [];
  };

  const setField = (agentId: string, field: "provider" | "model", value: string, agent: { model_provider: ModelProvider; model_name: string }) => {
    setPending((prev) => {
      const current = prev[agentId] ?? { provider: agent.model_provider, model: agent.model_name };
      const next = { ...current };
      if (field === "provider") {
        next.provider = value as ModelProvider;
        const opts = modelOptions(value as ModelProvider);
        next.model = opts[0] ?? "";
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
      setPending((prev) => { const n = { ...prev }; delete n[vars.agentId]; return n; });
    },
  });

  const saveAll = () =>
    Object.entries(pending).forEach(([agentId, { provider, model }]) =>
      saveMutation.mutate({ agentId, provider, model })
    );

  const hasPending = Object.keys(pending).length > 0;

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading agents…</p>;
  if (agents.length === 0) return <p className="text-sm text-muted-foreground">No agents found.</p>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border bg-white overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/20 text-xs font-semibold text-muted-foreground">
              <th className="px-4 py-2.5 text-left">Agent</th>
              <th className="px-4 py-2.5 text-left">Role</th>
              <th className="px-4 py-2.5 text-left">Provider</th>
              <th className="px-4 py-2.5 text-left">Model</th>
              <th className="px-4 py-2.5 text-left">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {agents.map((agent) => {
              const provider = getVal(agent.id, "provider", agent) as ModelProvider;
              const model    = getVal(agent.id, "model", agent);
              const isDirty  = !!pending[agent.id];
              const opts     = modelOptions(provider);

              return (
                <tr key={agent.id} className={cn("hover:bg-accent/20", isDirty && "bg-amber-50/60")}>
                  <td className="px-4 py-2.5 text-xs font-medium">{agent.name}</td>
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
                    {isDirty
                      ? <span className="text-xs text-amber-600 font-medium">Unsaved</span>
                      : <span className="text-xs text-green-700">Saved</span>
                    }
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={saveAll}
          disabled={!hasPending || saveMutation.isPending}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {saveMutation.isPending ? "Saving…" : "Save Configuration"}
        </button>
        <button
          onClick={() => setPending({})}
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

type Tab = "models" | "per-agent";

export default function Settings() {
  const [activeTab, setActiveTab] = useState<Tab>("models");

  const tabs: Array<{ id: Tab; label: string; icon: React.ElementType }> = [
    { id: "models",    label: "Available Models", icon: CheckCircle2 },
    { id: "per-agent", label: "Per-Agent Model",  icon: Zap },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <h2 className="text-lg font-semibold">AI Model Settings</h2>

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

      {activeTab === "models"    && <AvailableModelsTab />}
      {activeTab === "per-agent" && <PerAgentModelTab />}
    </div>
  );
}
