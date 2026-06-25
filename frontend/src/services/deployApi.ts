import apiClient from "./apiClient";

export interface DeployStatus {
  status: "not_deployed" | "deploying" | "running" | "stopped" | "failed";
  port: number | null;
  app_url: string | null;
  project_name: string | null;
  last_deployed_at: string | null;
  error: string | null;
  has_compose_file: boolean;
  docker_available: boolean;
  services: Record<string, unknown>[];
}

export interface DeployLogsResponse {
  logs: string;
}

export const deployApi = {
  getStatus: (projectId: string) =>
    apiClient
      .get<DeployStatus>(`/projects/${projectId}/deploy/status`)
      .then((r) => r.data),

  start: (projectId: string) =>
    apiClient
      .post<DeployStatus>(`/projects/${projectId}/deploy/start`)
      .then((r) => r.data),

  stop: (projectId: string) =>
    apiClient
      .post<DeployStatus>(`/projects/${projectId}/deploy/stop`)
      .then((r) => r.data),

  getLogs: (projectId: string) =>
    apiClient
      .get<DeployLogsResponse>(`/projects/${projectId}/deploy/logs`)
      .then((r) => r.data),
};
