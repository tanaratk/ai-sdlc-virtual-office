import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { agentApi } from "@/services/agentApi";
import { AgentCard } from "@/components/agent/AgentCard";
import { AgentConsole } from "@/components/agent/AgentConsole";

export default function AgentConsolePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();

  const { data: agents = [] } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["pipeline-runs", projectId],
    queryFn: () => agentApi.listRuns(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  });

  const activeRun = runs.find(
    (r) => r.status === "running" || r.status === "waiting_for_user"
  ) ?? runs[0] ?? null;

  const { data: steps = [] } = useQuery({
    queryKey: ["pipeline-steps", projectId, activeRun?.id],
    queryFn: () => agentApi.getSteps(projectId!, activeRun!.id),
    enabled: !!projectId && !!activeRun,
    refetchInterval: activeRun?.status === "running" ? 3000 : false,
  });

  const startMutation = useMutation({
    mutationFn: () => agentApi.startRun(projectId!),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] }),
  });

  const approveMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.approveStep(projectId!, activeRun!.id, stepId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] }),
  });

  const rejectMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.rejectStep(projectId!, activeRun!.id, stepId, "Rejected by user"),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] }),
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
      <aside className="space-y-2">
        <h3 className="text-sm font-semibold">Agents</h3>
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </aside>

      <main>
        <AgentConsole
          projectId={projectId ?? ""}
          activeRun={activeRun}
          steps={steps}
          onStart={startMutation.mutate}
          onApprove={approveMutation.mutate}
          onReject={rejectMutation.mutate}
          isStarting={startMutation.isPending}
        />
      </main>
    </div>
  );
}
