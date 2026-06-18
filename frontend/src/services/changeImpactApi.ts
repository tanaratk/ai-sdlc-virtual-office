import { API_BASE_URL } from "./api";

export interface ChangeImpactRequest {
  change_description: string;
  changed_requirement_ids: string[];
  context_notes?: string;
}

export interface ChangeImpactResponse {
  document_id: string;
  title: string;
  status: string;
  message: string;
}

export async function runChangeImpact(
  projectId: string,
  body: ChangeImpactRequest,
): Promise<ChangeImpactResponse> {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/change-impact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<ChangeImpactResponse>;
}
