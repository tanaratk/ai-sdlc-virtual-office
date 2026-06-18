import { useNavigate } from "react-router-dom";
import { PauseCircle, Loader2, CheckCircle2, XCircle, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Agent } from "@/types/agent";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import { AgentAvatar } from "./AgentAvatar";

export interface RoomConfig {
  zone: string;
  label: string;
  stepNames: string[];   // pipeline step names that belong to this room
  navPath: string;       // relative path under /projects/:id/...
}

interface RoomCardProps {
  room: RoomConfig;
  agents: Agent[];
  projectId?: string;
  activeRun?: PipelineRun | null;
  steps?: PipelineStep[];
  onAgentClick?: (agent: Agent) => void;
}

type StepState = "idle" | "running" | "awaiting" | "completed" | "failed";

function getRoomState(
  room: RoomConfig,
  activeRun: PipelineRun | null | undefined,
  steps: PipelineStep[] | undefined,
): StepState {
  if (!activeRun || !steps) return "idle";

  const roomSteps = steps.filter((s) => room.stepNames.includes(s.step_name));
  if (roomSteps.length === 0) return "idle";

  if (roomSteps.some((s) => s.status === "running")) return "running";

  const isGateHere =
    activeRun.status === "waiting_for_user" &&
    room.stepNames.includes(activeRun.current_step ?? "");
  if (isGateHere) return "awaiting";

  if (roomSteps.some((s) => s.status === "failed")) return "failed";

  if (roomSteps.every((s) => s.status === "completed")) return "completed";

  return "idle";
}

const STATE_STYLES: Record<StepState, string> = {
  idle:      "border-border bg-accent/30",
  running:   "border-blue-400 bg-blue-50",
  awaiting:  "border-yellow-400 bg-yellow-50",
  completed: "border-green-400 bg-green-50",
  failed:    "border-destructive bg-red-50",
};

const STATE_BADGE: Record<StepState, { label: string; icon: LucideIcon | null; color: string }> = {
  idle:      { label: "", icon: null, color: "" },
  running:   { label: "Running", icon: Loader2, color: "text-blue-600" },
  awaiting:  { label: "Awaiting Review", icon: PauseCircle, color: "text-yellow-600" },
  completed: { label: "Done", icon: CheckCircle2, color: "text-green-600" },
  failed:    { label: "Failed", icon: XCircle, color: "text-destructive" },
};

export function RoomCard({
  room,
  agents,
  projectId,
  activeRun,
  steps,
  onAgentClick,
}: RoomCardProps) {
  const navigate = useNavigate();
  const state = getRoomState(room, activeRun, steps);
  const badge = STATE_BADGE[state];

  const handleRoomClick = () => {
    if (!projectId) return;
    navigate(`/projects/${projectId}/${room.navPath}`);
  };

  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-lg border-2 p-3 min-h-[96px] transition-colors",
        STATE_STYLES[state],
        projectId && "cursor-pointer hover:brightness-95",
      )}
      onClick={handleRoomClick}
      role={projectId ? "button" : undefined}
      tabIndex={projectId ? 0 : undefined}
      onKeyDown={(e) => e.key === "Enter" && handleRoomClick()}
    >
      {/* Room header */}
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-foreground">{room.label}</p>
        {badge.icon && (
          <span className={cn("flex items-center gap-1 text-[10px] font-medium", badge.color)}>
            <badge.icon
              className={cn("h-3 w-3", state === "running" && "animate-spin")}
            />
            {badge.label}
          </span>
        )}
      </div>

      {/* Agents */}
      <div
        className="flex flex-wrap gap-1.5"
        onClick={(e) => e.stopPropagation()}
      >
        {agents.length === 0 ? (
          <p className="text-[10px] text-muted-foreground">No agents</p>
        ) : (
          agents.map((agent) => (
            <AgentAvatar
              key={agent.id}
              agent={agent}
              size="sm"
              onClick={onAgentClick ? () => onAgentClick(agent) : undefined}
            />
          ))
        )}
      </div>
    </div>
  );
}
