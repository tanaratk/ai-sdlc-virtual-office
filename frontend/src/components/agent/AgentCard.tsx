import { Bot, CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Agent } from "@/types/agent";

const statusConfig = {
  idle: { icon: Clock, color: "text-muted-foreground", label: "Idle" },
  working: { icon: Loader2, color: "text-blue-500", label: "Working", spin: true },
  done: { icon: CheckCircle2, color: "text-green-500", label: "Done" },
  error: { icon: XCircle, color: "text-destructive", label: "Error" },
} as const;

interface AgentCardProps {
  agent: Agent;
}

export function AgentCard({ agent }: AgentCardProps) {
  const cfg = statusConfig[agent.status];
  const Icon = cfg.icon;

  return (
    <div className="flex items-center gap-3 rounded-lg border p-3 bg-white">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent">
        <Bot className="h-4 w-4 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{agent.name}</p>
        <p className="text-xs text-muted-foreground truncate">{agent.role}</p>
      </div>
      <div className={cn("flex items-center gap-1 text-xs", cfg.color)}>
        <Icon className={cn("h-3.5 w-3.5", "spin" in cfg && cfg.spin && "animate-spin")} />
        <span>{cfg.label}</span>
      </div>
    </div>
  );
}
