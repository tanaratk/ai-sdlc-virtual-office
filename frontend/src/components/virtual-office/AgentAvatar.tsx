import { cn } from "@/lib/utils";
import type { Agent } from "@/types/agent";

const STATUS_DOT: Record<Agent["status"], string> = {
  idle: "bg-muted-foreground",
  working: "bg-blue-500 animate-pulse",
  done: "bg-green-500",
  error: "bg-destructive",
};

interface AgentAvatarProps {
  agent: Agent;
  size?: "sm" | "md";
}

export function AgentAvatar({ agent, size = "md" }: AgentAvatarProps) {
  const initials = agent.name
    .split("-")
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 2);

  return (
    <div
      className={cn(
        "relative flex items-center justify-center rounded-full bg-accent font-semibold text-primary",
        size === "md" ? "h-10 w-10 text-sm" : "h-7 w-7 text-xs"
      )}
      title={agent.name}
    >
      {initials}
      <span
        className={cn(
          "absolute bottom-0 right-0 rounded-full ring-2 ring-white",
          size === "md" ? "h-2.5 w-2.5" : "h-2 w-2",
          STATUS_DOT[agent.status]
        )}
      />
    </div>
  );
}
