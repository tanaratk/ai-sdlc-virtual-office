import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Bot, CheckCircle2, Loader2, XCircle, Clock, SlidersHorizontal } from "lucide-react";
import { agentApi } from "@/services/agentApi";
import { AgentCard } from "@/components/agent/AgentCard";
import { AgentDetailPanel } from "@/components/agent/AgentDetailPanel";
import { cn } from "@/lib/utils";
import type { Agent } from "@/types/agent";

// ── Category mapping ──────────────────────────────────────────────────────────

const CATEGORY_MAP: Record<string, string> = {
  "requirement-agent":        "Business",
  "gap-analysis-agent":       "Business",
  "ba-agent":                 "Business",
  "architect-agent":          "Design",
  "ux-agent":                 "Design",
  "technical-design-agent":   "Design",
  "developer-agent":          "Delivery",
  "developer-agent-backend":  "Delivery",
  "developer-agent-frontend": "Delivery",
  "developer-agent-platform": "Delivery",
  "code-review-agent":        "Delivery",
  "qa-agent":                 "Delivery",
  "devops-agent":             "Delivery",
  "monitoring-agent":         "Delivery",
  "change-impact-agent":      "On-demand",
  "documentation-agent":      "On-demand",
  "pm-agent":                 "On-demand",
};

const STATUS_DISPLAY: Record<string, string> = {
  idle: "Waiting", working: "Running", done: "Done", error: "Failed",
};

// ── Summary Cards ─────────────────────────────────────────────────────────────

function SummaryCards({ agents }: { agents: Agent[] }) {
  const cards = [
    {
      label: "Total Agents",
      value: agents.length,
      icon: Bot,
      cls: "text-primary bg-primary/10",
    },
    {
      label: "Running",
      value: agents.filter((a) => a.status === "working").length,
      icon: Loader2,
      cls: "text-blue-700 bg-blue-100",
    },
    {
      label: "Done",
      value: agents.filter((a) => a.status === "done").length,
      icon: CheckCircle2,
      cls: "text-green-700 bg-green-100",
    },
    {
      label: "Waiting",
      value: agents.filter((a) => a.status === "idle").length,
      icon: Clock,
      cls: "text-gray-600 bg-gray-100",
    },
    {
      label: "Failed",
      value: agents.filter((a) => a.status === "error").length,
      icon: XCircle,
      cls: "text-red-700 bg-red-100",
    },
  ];

  return (
    <div className="grid grid-cols-5 gap-3">
      {cards.map(({ label, value, icon: Icon, cls }) => (
        <div key={label} className="rounded-lg border bg-white p-3 flex items-center gap-3">
          <div className={cn("flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0", cls)}>
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <p className="text-lg font-bold leading-none">{value}</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">{label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

type StatusFilter = "all" | "working" | "done" | "idle" | "error";
type CategoryFilter = "all" | "Business" | "Design" | "Delivery" | "On-demand";

export default function AgentManagerPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");

  const { data: agents = [], isLoading, isError } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    staleTime: 10_000,
    refetchInterval: 8_000,
  });

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return agents.filter((a) => {
      const matchesSearch =
        !q ||
        a.name.toLowerCase().includes(q) ||
        a.role.toLowerCase().includes(q) ||
        STATUS_DISPLAY[a.status]?.toLowerCase().includes(q);
      const matchesStatus = statusFilter === "all" || a.status === statusFilter;
      const category = CATEGORY_MAP[a.name] ?? "Other";
      const matchesCategory = categoryFilter === "all" || category === categoryFilter;
      return matchesSearch && matchesStatus && matchesCategory;
    });
  }, [agents, search, statusFilter, categoryFilter]);

  const selectedAgent = agents.find((a) => a.id === selectedAgentId) ?? null;

  return (
    <div className="space-y-4">
      {/* ── Header ── */}
      <div>
        <h2 className="text-lg font-semibold">Agents</h2>
        <p className="text-sm text-muted-foreground">
          Manage AI agents, model configuration, skills, tools, and execution behaviour.
        </p>
      </div>

      {/* ── Summary Cards ── */}
      {!isLoading && <SummaryCards agents={agents} />}

      {/* ── Search + Filters ── */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
          <input
            type="text"
            placeholder="Search agent name, role, status…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-md border bg-white py-1.5 pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Status filter */}
        <div className="flex items-center gap-1.5">
          <SlidersHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
            className="rounded-md border bg-white px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="all">All Status</option>
            <option value="working">Running</option>
            <option value="done">Done</option>
            <option value="idle">Waiting</option>
            <option value="error">Failed</option>
          </select>
        </div>

        {/* Category filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as CategoryFilter)}
          className="rounded-md border bg-white px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="all">All Categories</option>
          <option value="Business">Business</option>
          <option value="Design">Design</option>
          <option value="Delivery">Delivery</option>
          <option value="On-demand">On-demand</option>
        </select>

        <span className="text-xs text-muted-foreground ml-auto">
          {filtered.length} / {agents.length} agents
        </span>
      </div>

      {/* ── 30 / 70 grid ── */}
      <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
        {/* Agent List */}
        <aside className="space-y-1.5 max-h-[calc(100vh-320px)] overflow-y-auto pr-1">
          {isLoading && (
            <p className="text-sm text-muted-foreground py-4 text-center">Loading…</p>
          )}
          {isError && (
            <p className="text-sm text-destructive py-4 text-center">Cannot reach backend API. Start the server and refresh.</p>
          )}
          {!isLoading && !isError && filtered.length === 0 && (
            <p className="text-sm text-muted-foreground py-4 text-center">No agents match</p>
          )}
          {filtered.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              isSelected={agent.id === selectedAgentId}
              onClick={() =>
                setSelectedAgentId(agent.id === selectedAgentId ? null : agent.id)
              }
            />
          ))}
        </aside>

        {/* Detail Panel */}
        <main className="min-h-[400px]">
          {selectedAgent ? (
            <AgentDetailPanel
              agent={selectedAgent}
              onClose={() => setSelectedAgentId(null)}
            />
          ) : (
            <div className="flex h-full items-center justify-center rounded-lg border border-dashed">
              <div className="text-center">
                <Bot className="mx-auto h-8 w-8 text-muted-foreground/30 mb-2" />
                <p className="text-sm text-muted-foreground">
                  Select an agent to view details and configure
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
