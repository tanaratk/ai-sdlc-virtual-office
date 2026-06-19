import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { X, Bot, Save, CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";
import { agentApi } from "@/services/agentApi";
import type { Agent, ModelProvider } from "@/types/agent";

const STATUS_BADGES = {
  idle: { icon: Clock, cls: "text-muted-foreground bg-muted" },
  working: { icon: Loader2, cls: "text-blue-700 bg-blue-100", spin: true },
  done: { icon: CheckCircle2, cls: "text-green-700 bg-green-100" },
  error: { icon: XCircle, cls: "text-red-700 bg-red-100" },
} as const;

const STEP_MAP: Record<string, number> = {
  "Requirement Agent": 1, "Gap Analysis Agent": 2, "BA Agent": 3,
  "Solution Architect Agent": 4, "UX Agent": 5, "Developer Agent": 6,
  "QA Agent": 7, "Change Impact Agent": 8, "Documentation Agent": 9, "PM Agent": 10,
};

interface AgentDetailPanelProps {
  agent: Agent;
  onClose: () => void;
}

function formatBytes(bytes: number | null) {
  if (!bytes) return null;
  return `${(bytes / 1e9).toFixed(1)} GB`;
}

export function AgentDetailPanel({ agent, onClose }: AgentDetailPanelProps) {
  const queryClient = useQueryClient();
  const [provider, setProvider] = useState<ModelProvider>(agent.model_provider);
  const [modelName, setModelName] = useState(agent.model_name);
  const [saved, setSaved] = useState(false);

  // Reset when agent changes
  useEffect(() => {
    setProvider(agent.model_provider);
    setModelName(agent.model_name);
    setSaved(false);
  }, [agent.id]);

  const { data: ollamaData } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: agentApi.listOllamaModels,
    staleTime: 60_000,
  });

  const updateMutation = useMutation({
    mutationFn: (data: { model_provider: ModelProvider; model_name: string }) =>
      agentApi.update(agent.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const stepNumber = STEP_MAP[agent.name] ?? null;
  const badge = STATUS_BADGES[agent.status];
  const BadgeIcon = badge.icon;

  return (
    <div className="rounded-lg border bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 border-b px-4 py-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 flex-shrink-0">
          <Bot className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold">{agent.name}</h3>
            {stepNumber && (
              <span className="text-xs text-muted-foreground">Step {stepNumber}</span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">{agent.role}</p>
        </div>
        <div className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${badge.cls}`}>
          <BadgeIcon className={`h-3 w-3 ${"spin" in badge && badge.spin ? "animate-spin" : ""}`} />
          <span className="capitalize">{agent.status}</span>
        </div>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground flex-shrink-0"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Description */}
        {agent.description && (
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
              Description
            </p>
            <p className="text-sm text-foreground">{agent.description}</p>
          </div>
        )}

        {/* Goal */}
        {agent.goal && (
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
              Goal
            </p>
            <p className="text-sm text-foreground">{agent.goal}</p>
          </div>
        )}

        {/* Location */}
        {agent.home_zone && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>Home: <span className="text-foreground">{agent.home_zone}</span></span>
            {agent.current_zone && agent.current_zone !== agent.home_zone && (
              <span>Now: <span className="text-blue-600">{agent.current_zone}</span></span>
            )}
          </div>
        )}

        <hr />

        {/* LLM Config */}
        <div className="space-y-3">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            LLM Configuration
          </p>

          <div>
            <label className="block text-xs font-medium mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as ModelProvider)}
              className="w-full rounded-md border bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="ollama">Ollama (local)</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium mb-1">Model</label>
            {provider === "ollama" && ollamaData ? (
              <select
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="w-full rounded-md border bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {ollamaData.models.map((m) => (
                  <option key={m.name} value={m.name}>
                    {m.name}{m.size ? ` (${formatBytes(m.size)})` : ""}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="e.g. gpt-4o"
                className="w-full rounded-md border px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            )}
          </div>

          <button
            onClick={() => updateMutation.mutate({ model_provider: provider, model_name: modelName })}
            disabled={updateMutation.isPending || (provider === agent.model_provider && modelName === agent.model_name)}
            className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saved ? (
              <><CheckCircle2 className="h-3.5 w-3.5" /> Saved!</>
            ) : (
              <><Save className="h-3.5 w-3.5" /> {updateMutation.isPending ? "Saving…" : "Save Model"}</>
            )}
          </button>

          {updateMutation.isError && (
            <p className="text-xs text-destructive">
              {(updateMutation.error as Error)?.message ?? "Failed to save."}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
