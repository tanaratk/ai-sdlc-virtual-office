import type { Document } from "@/types/document";
import type { PaginatedResponse } from "@/types/workflow";
import apiClient from "./apiClient";

export const documentApi = {
  list: (projectId: string, page = 1, pageSize = 20) =>
    apiClient
      .get<PaginatedResponse<Document>>(`/projects/${projectId}/documents`, {
        params: { page, page_size: pageSize },
      })
      .then((r) => r.data),

  get: (projectId: string, documentId: string) =>
    apiClient
      .get<Document>(`/projects/${projectId}/documents/${documentId}`)
      .then((r) => r.data),

  approve: (projectId: string, documentId: string) =>
    apiClient
      .post(`/projects/${projectId}/documents/${documentId}/approve`)
      .then((r) => r.data),

  reject: (projectId: string, documentId: string, reason: string) =>
    apiClient
      .post(`/projects/${projectId}/documents/${documentId}/reject`, { reason })
      .then((r) => r.data),
};
