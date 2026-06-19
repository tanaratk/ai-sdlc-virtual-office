import apiClient from "./apiClient";

export interface ActivityLog {
  id: string;
  project_id: string;
  agent_id: string | null;
  event_type: string;
  message: string;
  created_at: string;
}

export interface ActivityLogList {
  total: number;
  items: ActivityLog[];
}

export const activityApi = {
  list: (projectId: string, params?: { limit?: number; offset?: number; event_type?: string }) =>
    apiClient
      .get<ActivityLogList>(`/projects/${projectId}/activity`, { params })
      .then((r) => r.data),
};
