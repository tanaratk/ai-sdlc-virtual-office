import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { agentApi } from "@/services/agentApi";
import { AgentCard } from "@/components/agent/AgentCard";
import { AgentConsole } from "@/components/agent/AgentConsole";
import { DocumentPreviewPanel } from "@/components/agent/DocumentPreviewPanel";

export default function AgentConsolePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();

  const { data: agents = [] } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    refetchInterval: 4000,
  });

  const { data: runs = [] } = useQuery({
    queryKey: ["pipeline-runs", projectId],
    queryFn: () => agentApi.listRuns(projectId!),
    enabled: !!projectId,
    refetchInterval: 4000,
  });

  const activeRun = runs.find(
    (r) => r.status === "running" || r.status === "waiting_for_user"
  ) ?? runs[0] ?? null;

  const { data: steps = [] } = useQuery({
    queryKey: ["pipeline-steps", projectId, activeRun?.id],
    queryFn: () => agentApi.getSteps(projectId!, activeRun!.id),
    enabled: !!projectId && !!activeRun,
    refetchInterval:
      activeRun?.status === "running" || activeRun?.status === "waiting_for_user"
        ? 3000
        : false,
  });

  const startMutation = useMutation({
    mutationFn: () => agentApi.startRun(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.approveStep(projectId!, activeRun!.id, stepId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-steps", projectId, activeRun?.id] });
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (stepId: string) =>
      agentApi.rejectStep(projectId!, activeRun!.id, stepId, "Rejected by user"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipeline-runs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["pipeline-steps", projectId, activeRun?.id] });
    },
  });

  const pendingReviewStep =
    activeRun?.status === "waiting_for_user"
      ? steps.find(
          (s) =>
            s.status === "completed" &&
            s.step_name === activeRun.current_step &&
            s.output_document_id
        )
      : null;

  return (
    <div className="grid gap-6 lg:grid-cols-[200px_1fr]">
      {/* Agent status sidebar — read-only, shows live status */}
      <aside className="space-y-2">
        <h3 className="text-sm font-semibold">Agent Status</h3>
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </aside>

      <main className="space-y-4">
        <AgentConsole
          projectId={projectId ?? ""}
          activeRun={activeRun}
          steps={steps}
          onStart={startMutation.mutate}
          isStarting={startMutation.isPending}
        />

        {pendingReviewStep && (
          <DocumentPreviewPanel
            projectId={projectId ?? ""}
            documentId={pendingReviewStep.output_document_id!}
            stepName={pendingReviewStep.step_name}
            onApprove={() => approveMutation.mutate(pendingReviewStep.id)}
            onReject={() => rejectMutation.mutate(pendingReviewStep.id)}
            isApproving={approveMutation.isPending}
            isRejecting={rejectMutation.isPending}
          />
        )}
      </main>
    </div>
  );
}
