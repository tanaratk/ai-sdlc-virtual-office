import { API_BASE_URL } from "./api";

export interface IngestResponse {
  project_id: string;
  chunks_created: number;
  message: string;
}

export interface ChunkResult {
  chunk_id: string;
  document_id: string;
  document_type: string;
  chunk_index: number;
  chunk_text: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: ChunkResult[];
}

export interface ChunkStats {
  project_id: string;
  total_chunks: number;
  document_types: string[];
}

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

export const ragApi = {
  ingest: (projectId: string): Promise<IngestResponse> =>
    apiFetch(`${API_BASE_URL}/projects/${projectId}/rag/ingest`, { method: "POST" }),

  search: (projectId: string, query: string, topK = 5): Promise<SearchResponse> =>
    apiFetch(`${API_BASE_URL}/projects/${projectId}/rag/search`, {
      method: "POST",
      body: JSON.stringify({ query, top_k: topK }),
    }),

  stats: (projectId: string): Promise<ChunkStats> =>
    apiFetch(`${API_BASE_URL}/projects/${projectId}/rag/chunks`),
};
