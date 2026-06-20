import { Play } from "lucide-react";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import { AgentRunStatus } from "./AgentRunStatus";

const EMPTY_RUN: PipelineRun = {
  id: "__empty__",
  project_id: "",
  status: "pending",
  current_step: null,
  started_at: null,
  completed_at: null,
  created_at: new Date().toISOString(),
};

interface AgentConsoleProps {
  projectId: string;
  activeRun: PipelineRun | null;
  steps: PipelineStep[];
  onStart: () => void;
  isStarting: boolean;
}

export function AgentConsole({
  activeRun,
  steps,
  onStart,
  isStarting,
}: AgentConsoleProps) {
  const canStart = !activeRun || ["completed", "failed", "cancelled"].includes(activeRun.status);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Agent Pipeline (11-step auto-chain)</h3>
        <button
          onClick={onStart}
          disabled={!canStart || isStarting}
          className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="h-3 w-3" />
          {isStarting ? "Starting…" : canStart ? "Run Pipeline" : "Running…"}
        </button>
      </div>

      {/* Always show the pipeline stepper — empty state uses a pending run placeholder */}
      <AgentRunStatus
        run={activeRun ?? EMPTY_RUN}
        steps={steps}
      />
    </div>
  );
}
