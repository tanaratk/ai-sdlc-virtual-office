import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { agentApi } from "@/services/agentApi";
import { VirtualOfficeMap } from "@/components/virtual-office/VirtualOfficeMap";
import type { Agent } from "@/types/agent";
import type { PipelineRun } from "@/types/workflow";

export default function VirtualOfficePage() {
  const { projectId } = useParams<{ projectId?: string }>();
  const navigate = useNavigate();

  const { data: agents = [], isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    refetchInterval: 5000,
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["pipeline-runs", projectId],
    queryFn: () => agentApi.listRuns(projectId!),
    enabled: !!projectId,
    refetchInterval: 4000,
  });

  const activeRun: PipelineRun | null =
    runs.find((r) => r.status === "running" || r.status === "waiting_for_user") ??
    runs[0] ??
    null;

  const { data: steps = [] } = useQuery({
    queryKey: ["pipeline-steps", projectId, activeRun?.id],
    queryFn: () => agentApi.getSteps(projectId!, activeRun!.id),
    enabled: !!projectId && !!activeRun,
    refetchInterval: activeRun?.status === "running" ? 3000 : false,
  });

  const handleAgentClick = (agent: Agent) => {
    if (projectId) {
      navigate(`/projects/${projectId}/agents`);
    } else {
      navigate("/agents");
    }
    // Pass agent name as hint via query param for future use
    void agent;
  };

  const runStatusLabel: Record<string, string> = {
    running:          "Pipeline running",
    waiting_for_user: "Awaiting your review",
    completed:        "Pipeline complete",
    failed:           "Pipeline failed",
    pending:          "Pipeline pending",
    cancelled:        "Pipeline cancelled",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Virtual Office</h2>
          <p className="text-sm text-muted-foreground">
            {projectId
              ? "Live agent status for this project. Click a room to navigate, click an agent to open the console."
              : "Global agent status. Open a project to see pipeline state."}
          </p>
        </div>

        {activeRun && (
          <div
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              activeRun.status === "waiting_for_user"
                ? "bg-yellow-100 text-yellow-700"
                : activeRun.status === "running"
                ? "bg-blue-100 text-blue-700"
                : activeRun.status === "completed"
                ? "bg-green-100 text-green-700"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {runStatusLabel[activeRun.status] ?? activeRun.status}
          </div>
        )}
      </div>

      {agentsLoading ? (
        <p className="text-sm text-muted-foreground">Loading agents…</p>
      ) : (
        <VirtualOfficeMap
          agents={agents}
          projectId={projectId}
          activeRun={activeRun}
          steps={steps}
          onAgentClick={handleAgentClick}
        />
      )}

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-muted-foreground" /> Idle
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-blue-500" /> Running
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-yellow-400" /> Awaiting Review
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-green-500" /> Done
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-destructive" /> Failed / Error
        </span>
      </div>
    </div>
  );
}
