import apiClient from "./apiClient";

export interface FigmaSettingResponse {
  id: string;
  project_id: string;
  file_key: string;
  file_url: string;
  file_name: string | null;
  embed_url: string;
  created_at: string;
  updated_at: string;
}

export interface FigmaScreen {
  screen_id: string;
  name: string;
  description: string;
  components: string[];
}

export interface PushScreensResponse {
  pushed: number;
  skipped: number;
  errors: string[];
}

const base = (projectId: string) => `/projects/${projectId}/figma`;

export const figmaApi = {
  getSetting: (projectId: string) =>
    apiClient.get<FigmaSettingResponse | null>(base(projectId)).then((r) => r.data),

  linkFile: (projectId: string, fileUrl: string) =>
    apiClient.put<FigmaSettingResponse>(base(projectId), { file_url: fileUrl }).then((r) => r.data),

  unlink: (projectId: string) =>
    apiClient.delete(base(projectId)),

  listScreens: (projectId: string) =>
    apiClient.get<FigmaScreen[]>(`${base(projectId)}/screens`).then((r) => r.data),

  pushScreens: (projectId: string) =>
    apiClient.post<PushScreensResponse>(`${base(projectId)}/push-screens`).then((r) => r.data),
};
