import apiClient from "./apiClient";

export interface FileEntry {
  path: string;
  size: number;
  lang: string;
}

export interface FileTreeResponse {
  base_dir: string;
  files: FileEntry[];
  exists: boolean;
}

export interface FileContentResponse {
  path: string;
  lang: string;
  content: string;
  size: number;
}

export const generatedCodeApi = {
  getTree: (projectId: string) =>
    apiClient
      .get<FileTreeResponse>(`/projects/${projectId}/generated-code/tree`)
      .then((r) => r.data),

  getFile: (projectId: string, path: string) =>
    apiClient
      .get<FileContentResponse>(`/projects/${projectId}/generated-code/file`, {
        params: { path },
      })
      .then((r) => r.data),

  getDownloadUrl: (projectId: string) =>
    `/api/v1/projects/${projectId}/generated-code/download`,
};
