import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X, Bot, Save, CheckCircle2, Loader2, XCircle, Clock,
  FileText, Settings, Pencil, RotateCcw, LayoutDashboard,
  ScrollText, AlertCircle,
} from "lucide-react";
import { agentApi } from "@/services/agentApi";
import type { Agent, ModelProvider } from "@/types/agent";
import { cn } from "@/lib/utils";

// ── Static maps ───────────────────────────────────────────────────────────────

const STEP_MAP: Record<string, number> = {
  "requirement-agent":        1,
  "gap-analysis-agent":       2,
  "ba-agent":                 3,
  "architect-agent":          4,
  "ux-agent":                 5,
  "technical-design-agent":   6,
  "developer-agent":          7,
  "developer-agent-backend":  7,
  "developer-agent-frontend": 7,
  "developer-agent-platform": 7,
  "code-review-agent":        8,
  "qa-agent":                 9,
  "devops-agent":            10,
  "monitoring-agent":        11,
  "change-impact-agent":     12,
};

const LAYER_MAP: Record<string, { label: string; cls: string }> = {
  "requirement-agent":        { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "gap-analysis-agent":       { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "ba-agent":                 { label: "Business",  cls: "bg-amber-100 text-amber-700" },
  "architect-agent":          { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "ux-agent":                 { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "technical-design-agent":   { label: "Design",    cls: "bg-blue-100 text-blue-700" },
  "developer-agent":          { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-backend":  { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-frontend": { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "developer-agent-platform": { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "code-review-agent":        { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "qa-agent":                 { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "devops-agent":             { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "monitoring-agent":         { label: "Delivery",  cls: "bg-green-100 text-green-700" },
  "change-impact-agent":      { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
  "documentation-agent":      { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
  "pm-agent":                 { label: "On-demand", cls: "bg-purple-100 text-purple-700" },
};

const STATUS_BADGE: Record<string, { label: string; cls: string; spin?: boolean; Icon: React.ElementType }> = {
  idle:    { label: "Waiting", cls: "text-gray-600 bg-gray-100",   Icon: Clock },
  working: { label: "Running", cls: "text-blue-700 bg-blue-100",   Icon: Loader2, spin: true },
  done:    { label: "Done",    cls: "text-green-700 bg-green-100", Icon: CheckCircle2 },
  error:   { label: "Failed",  cls: "text-red-700 bg-red-100",     Icon: XCircle },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatBytes(bytes: number | null) {
  if (!bytes) return null;
  return `${(bytes / 1e9).toFixed(1)} GB`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString([], {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

// ── Minimal Markdown renderer ─────────────────────────────────────────────────

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
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) { tableLines.push(lines[i]); i++; }
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
      while (i < lines.length && !lines[i].startsWith("```")) { codeLines.push(lines[i]); i++; }
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

// ── Tab types ─────────────────────────────────────────────────────────────────

type Tab = "overview" | "model" | "skill" | "logs";

const TABS: { key: Tab; label: string; Icon: React.ElementType }[] = [
  { key: "overview", label: "Overview",     Icon: LayoutDashboard },
  { key: "model",    label: "Model Config", Icon: Settings },
  { key: "skill",    label: "Prompt / Skill", Icon: FileText },
  { key: "logs",     label: "Logs",         Icon: ScrollText },
];

// ── Props ─────────────────────────────────────────────────────────────────────

interface AgentDetailPanelProps {
  agent: Agent;
  onClose: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function AgentDetailPanel({ agent, onClose }: AgentDetailPanelProps) {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>("overview");

  const [provider, setProvider]   = useState<ModelProvider>(agent.model_provider);
  const [modelName, setModelName] = useState(agent.model_name);
  const [savedModel, setSavedModel] = useState(false);

  const [editingSkill, setEditingSkill] = useState(false);
  const [skillDraft, setSkillDraft]     = useState(agent.skill_markdown ?? "");
  const [savedSkill, setSavedSkill]     = useState(false);

  useEffect(() => {
    setProvider(agent.model_provider);
    setModelName(agent.model_name);
    setSkillDraft(agent.skill_markdown ?? "");
    setSavedModel(false);
    setSavedSkill(false);
    setEditingSkill(false);
    setTab("overview");
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

  const stepNumber = STEP_MAP[agent.name] ?? null;
  const layer      = LAYER_MAP[agent.name];
  const badge      = STATUS_BADGE[agent.status];

  return (
    <div className="rounded-lg border bg-white shadow-sm overflow-hidden flex flex-col">
      {/* ── Agent Header ── */}
      <div className="border-b px-4 py-3 flex-shrink-0">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 flex-shrink-0">
            <Bot className="h-5 w-5 text-primary" />
          </div>

          <div className="flex-1 min-w-0">
            {/* Name */}
            <p className="text-sm font-semibold break-all leading-snug">{agent.name}</p>

            {/* Meta badges */}
            <div className="flex flex-wrap items-center gap-1.5 mt-1">
              <span className="text-xs text-muted-foreground">{agent.role}</span>
              {stepNumber && (
                <span className="text-[10px] text-muted-foreground border rounded px-1.5 py-0.5">Step {stepNumber}</span>
              )}
              {layer && (
                <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium", layer.cls)}>
                  {layer.label}
                </span>
              )}
              <span className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold", badge.cls)}>
                <badge.Icon className={cn("h-3 w-3", badge.spin && "animate-spin")} />
                {badge.label}
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={tab === "model" ? saveModel : tab === "skill" && editingSkill ? saveSkill : undefined}
              disabled={
                updateMutation.isPending ||
                (tab === "model" && provider === agent.model_provider && modelName === agent.model_name) ||
                (tab === "skill" && !editingSkill)
              }
              className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {savedModel || savedSkill ? (
                <><CheckCircle2 className="h-3.5 w-3.5" /> Saved</>
              ) : updateMutation.isPending ? (
                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Saving…</>
              ) : (
                <><Save className="h-3.5 w-3.5" /> Save Changes</>
              )}
            </button>
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground p-1">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex border-b flex-shrink-0 overflow-x-auto">
        {TABS.map(({ key, label, Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={cn(
              "flex items-center gap-1.5 whitespace-nowrap px-4 py-2.5 text-xs font-medium border-b-2 transition-colors",
              tab === key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* ── Tab: Overview ── */}
      {tab === "overview" && (
        <div className="p-4 space-y-4 overflow-y-auto">
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-xs">
            <div>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Agent Name</p>
              <p className="font-medium break-all">{agent.name}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Role</p>
              <p className="font-medium">{agent.role}</p>
            </div>
            {stepNumber && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Pipeline Step</p>
                <p className="font-medium">Step {stepNumber}</p>
              </div>
            )}
            {layer && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Category</p>
                <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium", layer.cls)}>
                  {layer.label}
                </span>
              </div>
            )}
            <div>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Status</p>
              <span className={cn("flex items-center gap-1 w-fit rounded-full px-2 py-0.5 text-[10px] font-semibold", badge.cls)}>
                <badge.Icon className={cn("h-3 w-3", badge.spin && "animate-spin")} />
                {badge.label}
              </span>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Model</p>
              <p className="font-mono text-[11px]">{agent.model_name}</p>
            </div>
            {agent.home_zone && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Home Zone</p>
                <p className="font-medium">{agent.home_zone}</p>
              </div>
            )}
            {agent.current_zone && agent.current_zone !== agent.home_zone && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Current Zone</p>
                <p className="font-medium text-blue-600">{agent.current_zone}</p>
              </div>
            )}
            <div className="col-span-2">
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-0.5">Last Updated</p>
              <p className="font-medium">{formatDate(agent.updated_at)}</p>
            </div>
          </div>

          {agent.description && (
            <div>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Description</p>
              <p className="text-xs text-muted-foreground leading-relaxed">{agent.description}</p>
            </div>
          )}

          {/* Status-specific notice */}
          {agent.status === "error" && (
            <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 p-3">
              <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-red-700">Agent Failed</p>
                <p className="text-xs text-red-600 mt-0.5">
                  Check the Logs tab for execution history, or open the Pipeline Console for details.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Model Config ── */}
      {tab === "model" && (
        <div className="p-4 space-y-4 overflow-y-auto">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">LLM Configuration</p>

          <div>
            <label className="block text-xs font-medium mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as ModelProvider)}
              className="w-full rounded-md border bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="ollama">Ollama (local)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic / Claude</option>
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
                placeholder={
                  provider === "openai" ? "e.g. gpt-4o"
                  : provider === "anthropic" ? "e.g. claude-sonnet-4-6"
                  : "model name"
                }
                className="w-full rounded-md border px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            )}
            {provider !== "ollama" && (
              <p className="text-[11px] text-muted-foreground mt-1">
                {provider === "openai"
                  ? "Requires OPENAI_API_KEY in environment"
                  : "Requires ANTHROPIC_API_KEY in environment"}
              </p>
            )}
          </div>

          <div className="flex gap-2 pt-1">
            <button
              onClick={saveModel}
              disabled={
                updateMutation.isPending ||
                (provider === agent.model_provider && modelName === agent.model_name)
              }
              className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {savedModel ? (
                <><CheckCircle2 className="h-3.5 w-3.5" /> Saved!</>
              ) : (
                <><Save className="h-3.5 w-3.5" /> {updateMutation.isPending ? "Saving…" : "Save Model Config"}</>
              )}
            </button>
            <button
              onClick={() => { setProvider(agent.model_provider); setModelName(agent.model_name); }}
              className="flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
          </div>
        </div>
      )}

      {/* ── Tab: Prompt / Skill ── */}
      {tab === "skill" && (
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50 flex-shrink-0">
            <span className="text-xs text-muted-foreground">
              {editingSkill ? "Editing skill.md" : "skill.md"}
            </span>
            <div className="flex items-center gap-2">
              {editingSkill ? (
                <>
                  <button
                    onClick={() => { setSkillDraft(agent.skill_markdown ?? ""); setEditingSkill(false); }}
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
                        : <><Save className="h-3 w-3" /> Save Skill</>
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

      {/* ── Tab: Logs ── */}
      {tab === "logs" && (
        <div className="p-4 space-y-3 overflow-y-auto">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Execution History</p>

          <div className="rounded-lg border bg-muted/30 p-4 text-center space-y-2">
            <ScrollText className="mx-auto h-8 w-8 text-muted-foreground/30" />
            <p className="text-sm text-muted-foreground">
              Per-agent execution logs are available in the Pipeline Console.
            </p>
            <p className="text-xs text-muted-foreground">
              Open a project → Pipeline tab to see detailed step logs and duration for this agent.
            </p>
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Status</span>
              <span className={cn(
                "font-medium",
                agent.status === "done"    ? "text-green-600"
                : agent.status === "error" ? "text-red-600"
                : agent.status === "working"? "text-blue-600"
                : "text-muted-foreground"
              )}>
                {({ idle: "Waiting", working: "Running", done: "Done", error: "Failed" } as Record<string, string>)[agent.status] ?? agent.status}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Last Updated</span>
              <span>{formatDate(agent.updated_at)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
