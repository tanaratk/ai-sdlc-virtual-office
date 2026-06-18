import type { PaginatedResponse } from "@/types/workflow";
import type { RequirementInput, RequirementInputCreate } from "@/types/requirement";
import apiClient from "./apiClient";

export const sourceApi = {
  list: (projectId: string, page = 1, pageSize = 20) =>
    apiClient
      .get<PaginatedResponse<RequirementInput>>(`/projects/${projectId}/inputs`, {
        params: { page, page_size: pageSize },
      })
      .then((r) => r.data),

  get: (projectId: string, inputId: string) =>
    apiClient
      .get<RequirementInput>(`/projects/${projectId}/inputs/${inputId}`)
      .then((r) => r.data),

  create: (projectId: string, data: RequirementInputCreate) =>
    apiClient
      .post<RequirementInput>(`/projects/${projectId}/inputs`, data)
      .then((r) => r.data),

  delete: (projectId: string, inputId: string) =>
    apiClient.delete(`/projects/${projectId}/inputs/${inputId}`),
};
