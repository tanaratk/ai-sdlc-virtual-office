import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X, Bot, Save, CheckCircle2, Loader2, XCircle, Clock,
  FileText, Settings, Pencil, RotateCcw,
} from "lucide-react";
import { agentApi } from "@/services/agentApi";
import type { Agent, ModelProvider } from "@/types/agent";
import { cn } from "@/lib/utils";

const STATUS_BADGES = {
  idle:    { icon: Clock,        cls: "text-muted-foreground bg-muted" },
  working: { icon: Loader2,      cls: "text-blue-700 bg-blue-100", spin: true },
  done:    { icon: CheckCircle2, cls: "text-green-700 bg-green-100" },
  error:   { icon: XCircle,      cls: "text-red-700 bg-red-100" },
} as const;

const STEP_MAP: Record<string, number> = {
  "requirement-agent":       1,
  "gap-analysis-agent":      2,
  "ba-agent":                3,
  "architect-agent":         4,
  "ux-agent":                5,
  "technical-design-agent":  6,
  "developer-agent":         7,
  "developer-agent-backend":  7,
  "developer-agent-frontend": 7,
  "developer-agent-platform": 7,
  "code-review-agent":       8,
  "qa-agent":                9,
  "devops-agent":           10,
  "monitoring-agent":       11,
  "change-impact-agent":    12,
};

const LAYER_MAP: Record<string, { label: string; cls: string }> = {
  "requirement-agent":       { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "gap-analysis-agent":      { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "ba-agent":                { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "architect-agent":         { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "ux-agent":                { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "technical-design-agent":  { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "developer-agent":         { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-backend":  { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-frontend": { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-platform": { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "code-review-agent":       { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "qa-agent":                { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "devops-agent":            { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "monitoring-agent":        { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "change-impact-agent":     { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
  "documentation-agent":     { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
  "pm-agent":                { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
};

type Tab = "info" | "skill";

interface AgentDetailPanelProps {
  agent: Agent;
  onClose: () => void;
}

function formatBytes(bytes: number | null) {
  if (!bytes) return null;
  return `${(bytes / 1e9).toFixed(1)} GB`;
}

// Minimal markdown renderer — headers, bold, lists, tables, code blocks
function MarkdownView({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("### ")) {
      elements.push(<h3 key={i} className="text-sm font-semibold mt-3 mb-1">{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i} className="text-sm font-bold mt-4 mb-1 border-b pb-1">{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i} className="text-base font-bold mt-2 mb-2">{line.slice(2)}</h1>);
    } else if (line.startsWith("| ")) {
      // collect table rows
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const rows = tableLines.filter(l => !l.match(/^\|[-| ]+\|$/));
      elements.push(
        <div key={`table-${i}`} className="overflow-x-auto my-2">
          <table className="text-xs border-collapse w-full">
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri} className={ri === 0 ? "bg-muted font-medium" : "border-t"}>
                  {r.split("|").filter((_, ci) => ci > 0 && ci < r.split("|").length - 1)
                    .map((cell, ci) => (
                      <td key={ci} className="px-2 py-1 border border-border">{cell.trim()}</td>
                    ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    } else if (line.startsWith("- ")) {
      elements.push(
        <li key={i} className="text-xs ml-3 list-disc text-foreground">
          {line.slice(2).replace(/\*\*(.+?)\*\*/g, "$1")}
        </li>
      );
    } else if (line.trim() === "") {
      elements.push(<div key={i} className="h-1" />);
    } else if (line.startsWith("```")) {
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      elements.push(
        <pre key={`code-${i}`} className="bg-muted rounded p-2 text-xs font-mono overflow-x-auto my-1">
          {codeLines.join("\n")}
        </pre>
      );
    } else {
      const html = line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      elements.push(
        <p key={i} className="text-xs text-foreground leading-relaxed"
          dangerouslySetInnerHTML={{ __html: html }} />
      );
    }
    i++;
  }

  return <div className="space-y-0.5">{elements}</div>;
}

export function AgentDetailPanel({ agent, onClose }: AgentDetailPanelProps) {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>("info");

  // Info tab state
  const [provider, setProvider] = useState<ModelProvider>(agent.model_provider);
  const [modelName, setModelName] = useState(agent.model_name);
  const [savedModel, setSavedModel] = useState(false);

  // Skill tab state
  const [editingSkill, setEditingSkill] = useState(false);
  const [skillDraft, setSkillDraft] = useState(agent.skill_markdown ?? "");
  const [savedSkill, setSavedSkill] = useState(false);

  useEffect(() => {
    setProvider(agent.model_provider);
    setModelName(agent.model_name);
    setSkillDraft(agent.skill_markdown ?? "");
    setSavedModel(false);
    setSavedSkill(false);
    setEditingSkill(false);
    setTab("info");
  }, [agent.id]);

  const { data: ollamaData } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: agentApi.listOllamaModels,
    staleTime: 60_000,
  });

  const updateMutation = useMutation({
    mutationFn: (data: Parameters<typeof agentApi.update>[1]) =>
      agentApi.update(agent.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const saveModel = () => {
    updateMutation.mutate(
      { model_provider: provider, model_name: modelName },
      { onSuccess: () => { setSavedModel(true); setTimeout(() => setSavedModel(false), 2000); } }
    );
  };

  const saveSkill = () => {
    updateMutation.mutate(
      { skill_markdown: skillDraft },
      {
        onSuccess: () => {
          setSavedSkill(true);
          setEditingSkill(false);
          setTimeout(() => setSavedSkill(false), 2000);
        },
      }
    );
  };

  const resetSkill = () => {
    setSkillDraft(agent.skill_markdown ?? "");
    setEditingSkill(false);
  };

  const stepNumber = STEP_MAP[agent.name] ?? null;
  const layer = LAYER_MAP[agent.name];
  const badge = STATUS_BADGES[agent.status];
  const BadgeIcon = badge.icon;

  return (
    <div className="rounded-lg border bg-white shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b px-4 py-3 flex-shrink-0">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 flex-shrink-0">
          <Bot className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-sm font-semibold">{agent.name}</h3>
            {stepNumber && (
              <span className="text-xs text-muted-foreground">Step {stepNumber}</span>
            )}
            {layer && (
              <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium", layer.cls)}>
                {layer.label}
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">{agent.role}</p>
        </div>
        <div className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium flex-shrink-0", badge.cls)}>
          <BadgeIcon className={cn("h-3 w-3", "spin" in badge && badge.spin && "animate-spin")} />
          <span className="capitalize">{agent.status}</span>
        </div>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground flex-shrink-0">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b flex-shrink-0">
        {(["info", "skill"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "flex items-center gap-1.5 px-4 py-2 text-xs font-medium border-b-2 transition-colors",
              tab === t
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t === "info" ? <Settings className="h-3.5 w-3.5" /> : <FileText className="h-3.5 w-3.5" />}
            {t === "info" ? "Configuration" : "Skill Document"}
          </button>
        ))}
      </div>

      {/* Tab: Configuration */}
      {tab === "info" && (
        <div className="p-4 space-y-4 overflow-y-auto">
          {agent.description && (
            <div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Description</p>
              <p className="text-sm">{agent.description}</p>
            </div>
          )}
          {agent.home_zone && (
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>Home: <span className="text-foreground">{agent.home_zone}</span></span>
              {agent.current_zone && agent.current_zone !== agent.home_zone && (
                <span>Now: <span className="text-blue-600">{agent.current_zone}</span></span>
              )}
            </div>
          )}
          <hr />
          <div className="space-y-3">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">LLM Configuration</p>
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
              onClick={saveModel}
              disabled={updateMutation.isPending || (provider === agent.model_provider && modelName === agent.model_name)}
              className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {savedModel ? (
                <><CheckCircle2 className="h-3.5 w-3.5" /> Saved!</>
              ) : (
                <><Save className="h-3.5 w-3.5" /> {updateMutation.isPending ? "Saving…" : "Save Model"}</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Tab: Skill Document */}
      {tab === "skill" && (
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          {/* Skill toolbar */}
          <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50 flex-shrink-0">
            <span className="text-xs text-muted-foreground">
              {editingSkill ? "Editing skill.md" : "skill.md"}
            </span>
            <div className="flex items-center gap-2">
              {editingSkill ? (
                <>
                  <button
                    onClick={resetSkill}
                    className="flex items-center gap-1 rounded px-2 py-1 text-xs text-muted-foreground hover:bg-accent"
                  >
                    <RotateCcw className="h-3 w-3" /> Cancel
                  </button>
                  <button
                    onClick={saveSkill}
                    disabled={updateMutation.isPending}
                    className="flex items-center gap-1 rounded-md bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  >
                    {updateMutation.isPending
                      ? <><Loader2 className="h-3 w-3 animate-spin" /> Saving…</>
                      : savedSkill
                        ? <><CheckCircle2 className="h-3 w-3" /> Saved!</>
                        : <><Save className="h-3 w-3" /> Save</>
                    }
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setEditingSkill(true)}
                  className="flex items-center gap-1 rounded px-2 py-1 text-xs text-muted-foreground hover:bg-accent"
                >
                  <Pencil className="h-3 w-3" /> Edit
                </button>
              )}
            </div>
          </div>

          {/* Content area */}
          <div className="flex-1 overflow-y-auto">
            {editingSkill ? (
              <textarea
                value={skillDraft}
                onChange={(e) => setSkillDraft(e.target.value)}
                className="w-full h-full min-h-[400px] resize-none border-0 p-4 font-mono text-xs focus:outline-none"
                spellCheck={false}
              />
            ) : agent.skill_markdown ? (
              <div className="p-4">
                <MarkdownView content={agent.skill_markdown} />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 gap-2 text-muted-foreground">
                <FileText className="h-8 w-8 opacity-30" />
                <p className="text-xs">No skill document yet.</p>
                <button
                  onClick={() => setEditingSkill(true)}
                  className="text-xs text-primary underline"
                >
                  Create one
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
