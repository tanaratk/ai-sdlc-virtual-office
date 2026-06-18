import { CheckCircle2, Loader2, XCircle, Clock, PauseCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PipelineRun, PipelineStep } from "@/types/workflow";

const RUN_STATUS_CONFIG = {
  pending: { icon: Clock, color: "text-muted-foreground", label: "Pending" },
  running: { icon: Loader2, color: "text-blue-500", label: "Running", spin: true },
  waiting_for_user: { icon: PauseCircle, color: "text-yellow-500", label: "Awaiting Review" },
  completed: { icon: CheckCircle2, color: "text-green-500", label: "Completed" },
  failed: { icon: XCircle, color: "text-destructive", label: "Failed" },
  cancelled: { icon: XCircle, color: "text-muted-foreground", label: "Cancelled" },
} as const;

const STEP_STATUS_CONFIG = {
  pending: { color: "bg-muted" },
  running: { color: "bg-blue-500 animate-pulse" },
  completed: { color: "bg-green-500" },
  failed: { color: "bg-destructive" },
  skipped: { color: "bg-muted" },
} as const;

interface AgentRunStatusProps {
  run: PipelineRun;
  steps?: PipelineStep[];
  onApprove?: (stepId: string) => void;
  onReject?: (stepId: string) => void;
}

export function AgentRunStatus({ run, steps = [], onApprove, onReject }: AgentRunStatusProps) {
  const cfg = RUN_STATUS_CONFIG[run.status];
  const Icon = cfg.icon;

  return (
    <div className="rounded-lg border bg-white p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon
            className={cn(
              "h-4 w-4",
              cfg.color,
              "spin" in cfg && cfg.spin && "animate-spin"
            )}
          />
          <span className={cn("text-sm font-medium", cfg.color)}>{cfg.label}</span>
        </div>
        {run.current_step && (
          <span className="text-xs text-muted-foreground">
            Current: {run.current_step}
          </span>
        )}
      </div>

      {steps.length > 0 && (
        <div className="space-y-2">
          {steps.map((step) => (
            <div key={step.id} className="flex items-center gap-3">
              <div
                className={cn(
                  "h-2 w-2 rounded-full flex-shrink-0",
                  STEP_STATUS_CONFIG[step.status].color
                )}
              />
              <span className="flex-1 text-xs">{step.step_name}</span>
              {step.status === "completed" &&
                run.status === "waiting_for_user" &&
                run.current_step === step.step_name && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => onApprove?.(step.id)}
                      className="text-xs text-green-600 hover:underline"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => onReject?.(step.id)}
                      className="text-xs text-destructive hover:underline"
                    >
                      Reject
                    </button>
                  </div>
                )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
