import type { AutoLinkResult, TraceabilityMatrix } from "@/types/traceability";
import apiClient from "./apiClient";

export const traceabilityApi = {
  getMatrix: (projectId: string) =>
    apiClient
      .get<TraceabilityMatrix>(`/projects/${projectId}/traceability`)
      .then((r) => r.data),

  autoLink: (projectId: string) =>
    apiClient
      .post<AutoLinkResult>(`/projects/${projectId}/traceability/auto-link`)
      .then((r) => r.data),

  deleteLink: (projectId: string, linkId: string) =>
    apiClient
      .delete(`/projects/${projectId}/traceability/links/${linkId}`)
      .then((r) => r.data),
};
