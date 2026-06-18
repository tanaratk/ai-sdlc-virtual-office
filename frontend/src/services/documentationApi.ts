import { API_BASE_URL } from "./api";

export interface CompileDocsResponse {
  document_id: string;
  title: string;
  status: string;
  message: string;
}

export async function compileDocs(projectId: string): Promise<CompileDocsResponse> {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/compile-docs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<CompileDocsResponse>;
}
