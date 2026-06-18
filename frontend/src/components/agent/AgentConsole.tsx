import { useState } from "react";
import { Play } from "lucide-react";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import { AgentRunStatus } from "./AgentRunStatus";

interface AgentConsoleProps {
  projectId: string;
  activeRun: PipelineRun | null;
  steps: PipelineStep[];
  onStart: () => void;
  onApprove: (stepId: string) => void;
  onReject: (stepId: string) => void;
  isStarting: boolean;
}

export function AgentConsole({
  activeRun,
  steps,
  onStart,
  onApprove,
  onReject,
  isStarting,
}: AgentConsoleProps) {
  const canStart = !activeRun || ["completed", "failed", "cancelled"].includes(activeRun.status);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Agent Pipeline</h3>
        <button
          onClick={onStart}
          disabled={!canStart || isStarting}
          className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="h-3 w-3" />
          {isStarting ? "Starting…" : "Run Pipeline"}
        </button>
      </div>

      {activeRun ? (
        <AgentRunStatus
          run={activeRun}
          steps={steps}
          onApprove={onApprove}
          onReject={onReject}
        />
      ) : (
        <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
          No pipeline runs yet. Click Run Pipeline to start.
        </div>
      )}
    </div>
  );
}
