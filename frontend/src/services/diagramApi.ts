import apiClient from "./apiClient";

export interface DiagramResponse {
  id: string;
  title: string;
  document_type: string;
  content_markdown: string;
  mermaid_code: string;
  drawio_url: string;
  created_at: string;
  updated_at: string;
}

export interface GenerateDiagramsResponse {
  generated: number;
  diagrams: DiagramResponse[];
}

const base = (projectId: string) => `/projects/${projectId}/diagrams`;

export const diagramApi = {
  list: (projectId: string) =>
    apiClient.get<DiagramResponse[]>(base(projectId)).then((r) => r.data),

  generate: (projectId: string) =>
    apiClient.post<GenerateDiagramsResponse>(`${base(projectId)}/generate`).then((r) => r.data),
};
