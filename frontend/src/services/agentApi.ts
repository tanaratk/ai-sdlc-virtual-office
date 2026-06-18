import type { Agent } from "@/types/agent";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import apiClient from "./apiClient";

export const agentApi = {
  list: () =>
    apiClient.get<Agent[]>("/agents").then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Agent>(`/agents/${id}`).then((r) => r.data),

  startRun: (projectId: string) =>
    apiClient
      .post<PipelineRun>(`/projects/${projectId}/pipeline/runs`)
      .then((r) => r.data),

  getRun: (projectId: string, runId: string) =>
    apiClient
      .get<PipelineRun>(`/projects/${projectId}/pipeline/runs/${runId}`)
      .then((r) => r.data),

  listRuns: (projectId: string) =>
    apiClient
      .get<PipelineRun[]>(`/projects/${projectId}/pipeline/runs`)
      .then((r) => r.data),

  getSteps: (projectId: string, runId: string) =>
    apiClient
      .get<PipelineStep[]>(`/projects/${projectId}/pipeline/runs/${runId}/steps`)
      .then((r) => r.data),

  approveStep: (projectId: string, runId: string, stepId: string) =>
    apiClient
      .post(`/projects/${projectId}/pipeline/runs/${runId}/steps/${stepId}/approve`)
      .then((r) => r.data),

  rejectStep: (projectId: string, runId: string, stepId: string, reason: string) =>
    apiClient
      .post(`/projects/${projectId}/pipeline/runs/${runId}/steps/${stepId}/reject`, { reason })
      .then((r) => r.data),
};
