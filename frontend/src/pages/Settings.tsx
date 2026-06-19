import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Cpu, RefreshCw, Zap } from "lucide-react";
import { agentApi } from "@/services/agentApi";
import { settingsApi } from "@/services/settingsApi";

function formatBytes(bytes: number | null) {
  if (!bytes) return "";
  return ` · ${(bytes / 1e9).toFixed(1)} GB`;
}

function formatDate(iso: string | null) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString();
}

export default function Settings() {
  const queryClient = useQueryClient();

  const { data: ollamaData, isLoading: modelsLoading, isError: modelsError, refetch: refetchModels } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: agentApi.listOllamaModels,
    staleTime: 30_000,
    retry: false,
  });

  const { data: llmSettings = [] } = useQuery({
    queryKey: ["llm-settings"],
    queryFn: settingsApi.listLlm,
  });

  const { data: agents = [] } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    staleTime: 10_000,
  });

  const activateMutation = useMutation({
    mutationFn: (settingId: string) => settingsApi.activateLlm(settingId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["llm-settings"] }),
  });

  const updateAgentModelMutation = useMutation({
    mutationFn: ({ agentId, modelName }: { agentId: string; modelName: string }) =>
      agentApi.update(agentId, { model_name: modelName }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["agents"] }),
  });

  const activeModel = agents[0]?.model_name ?? "qwen3:8b";

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-lg font-semibold">Settings</h2>

      {/* Ollama Models */}
      <section className="rounded-lg border bg-white overflow-hidden">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold">Available Ollama Models</h3>
          </div>
          <button
            onClick={() => refetchModels()}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>

        {modelsLoading && (
          <p className="p-4 text-sm text-muted-foreground">Connecting to Ollama…</p>
        )}
        {modelsError && (
          <div className="p-4">
            <p className="text-sm text-destructive">
              Cannot reach Ollama. Make sure it is running on your machine.
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Expected URL: <code className="font-mono">http://localhost:11434</code>
            </p>
          </div>
        )}
        {ollamaData && (
          <div>
            <p className="px-4 py-2 text-xs text-muted-foreground border-b">
              Connected to <code className="font-mono">{ollamaData.base_url}</code>
              {" "}· {ollamaData.models.length} model{ollamaData.models.length !== 1 ? "s" : ""} available
            </p>
            <ul className="divide-y">
              {ollamaData.models.map((model) => {
                const isActive = model.name === activeModel;
                return (
                  <li
                    key={model.name}
                    className="flex items-center gap-3 px-4 py-3 hover:bg-accent/40"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-mono font-medium">{model.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatBytes(model.size)}{model.modified_at ? ` · updated ${formatDate(model.modified_at)}` : ""}
                      </p>
                    </div>
                    {isActive ? (
                      <span className="flex items-center gap-1 text-xs text-green-700 bg-green-100 rounded-full px-2 py-0.5">
                        <CheckCircle2 className="h-3 w-3" /> Active
                      </span>
                    ) : (
                      <button
                        onClick={() => {
                          // Update ALL agents to use this model
                          agents.forEach((a) =>
                            updateAgentModelMutation.mutate({ agentId: a.id, modelName: model.name })
                          );
                        }}
                        disabled={updateAgentModelMutation.isPending}
                        className="text-xs text-primary hover:underline disabled:opacity-50"
                      >
                        Set as default
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </section>

      {/* Per-Agent LLM */}
      <section className="rounded-lg border bg-white overflow-hidden">
        <div className="flex items-center gap-2 border-b px-4 py-3">
          <Zap className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold">Per-Agent Model</h3>
        </div>
        {agents.length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground">No agents found.</p>
        ) : (
          <ul className="divide-y">
            {agents.map((agent) => (
              <li key={agent.id} className="flex items-center gap-3 px-4 py-2.5">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{agent.name}</p>
                  <p className="text-xs text-muted-foreground">{agent.role}</p>
                </div>
                {ollamaData ? (
                  <select
                    value={agent.model_name}
                    onChange={(e) =>
                      updateAgentModelMutation.mutate({ agentId: agent.id, modelName: e.target.value })
                    }
                    className="rounded-md border bg-white px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    {ollamaData.models.map((m) => (
                      <option key={m.name} value={m.name}>{m.name}</option>
                    ))}
                  </select>
                ) : (
                  <span className="text-xs font-mono text-muted-foreground">{agent.model_name}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* LLM Presets from DB */}
      {llmSettings.length > 0 && (
        <section className="rounded-lg border bg-white overflow-hidden">
          <div className="border-b px-4 py-3">
            <h3 className="text-sm font-semibold">Saved LLM Presets</h3>
          </div>
          <ul className="divide-y">
            {llmSettings.map((s) => (
              <li key={s.id} className="flex items-center gap-3 px-4 py-2.5">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-mono">{s.model_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{s.provider}</p>
                </div>
                {s.is_active ? (
                  <span className="text-xs text-green-700 bg-green-100 rounded-full px-2 py-0.5">Active</span>
                ) : (
                  <button
                    onClick={() => activateMutation.mutate(s.id)}
                    className="text-xs text-primary hover:underline"
                  >
                    Activate
                  </button>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Backend Info */}
      <section className="rounded-lg border bg-white p-4 space-y-2">
        <h3 className="text-sm font-semibold">Backend</h3>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">API Base URL</span>
          <code className="font-mono text-xs">/api/v1</code>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Ollama URL (in container)</span>
          <code className="font-mono text-xs">http://host.docker.internal:11434</code>
        </div>
      </section>
    </div>
  );
}
