import type { PaginatedResponse } from "@/types/workflow";
import type { Project, ProjectCreate, ProjectUpdate } from "@/types/project";
import apiClient from "./apiClient";

export const projectApi = {
  list: (page = 1, pageSize = 20, status?: string) =>
    apiClient
      .get<PaginatedResponse<Project>>("/projects", {
        params: { page, page_size: pageSize, status },
      })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Project>(`/projects/${id}`).then((r) => r.data),

  create: (data: ProjectCreate) =>
    apiClient.post<Project>("/projects", data).then((r) => r.data),

  update: (id: string, data: ProjectUpdate) =>
    apiClient.patch<Project>(`/projects/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/projects/${id}`),
};
