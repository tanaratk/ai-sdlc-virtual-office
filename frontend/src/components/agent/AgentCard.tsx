import { Bot, CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Agent } from "@/types/agent";

const STATUS_CONFIG = {
  idle:    { icon: Clock,        label: "Waiting", cls: "text-gray-500 bg-gray-100" },
  working: { icon: Loader2,      label: "Running", cls: "text-blue-700 bg-blue-100", spin: true },
  done:    { icon: CheckCircle2, label: "Done",    cls: "text-green-700 bg-green-100" },
  error:   { icon: XCircle,      label: "Failed",  cls: "text-red-700 bg-red-100" },
} as const;

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

interface AgentCardProps {
  agent: Agent;
  isSelected?: boolean;
  onClick?: () => void;
}

export function AgentCard({ agent, isSelected, onClick }: AgentCardProps) {
  const cfg = STATUS_CONFIG[agent.status];
  const Icon = cfg.icon;
  const step = STEP_MAP[agent.name];

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-start gap-3 rounded-lg border p-3 text-left transition-colors",
        isSelected
          ? "border-primary bg-primary/5 shadow-sm"
          : "bg-white hover:bg-accent/50"
      )}
    >
      <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-accent mt-0.5">
        <Bot className="h-4 w-4 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        {/* Name — allow wrap, no truncation */}
        <p className="text-xs font-semibold leading-snug break-all">{agent.name}</p>

        {/* Role + Step */}
        <p className="text-[11px] text-muted-foreground mt-0.5">
          {agent.role}
          {step ? <span className="ml-1 text-muted-foreground/60">· Step {step}</span> : null}
        </p>

        {/* Model */}
        <p className="text-[10px] text-muted-foreground/70 mt-0.5 font-mono">{agent.model_name}</p>
      </div>

      {/* Status badge */}
      <div className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold flex-shrink-0 mt-0.5", cfg.cls)}>
        <Icon className={cn("h-3 w-3", "spin" in cfg && cfg.spin && "animate-spin")} />
        {cfg.label}
      </div>
    </button>
  );
}
