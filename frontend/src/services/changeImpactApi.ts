import { API_BASE_URL } from "./api";
import type { DocumentSummary } from "@/types/document";

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

export interface ChangeImpactReportListResponse {
  items: DocumentSummary[];
}

async function parseError(res: Response): Promise<string> {
  const err = await res.json().catch(() => ({}));
  const detail = (err as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object" && "message" in detail) {
    return String((detail as { message: unknown }).message);
  }
  return `HTTP ${res.status}`;
}

export async function listChangeImpactReports(
  projectId: string,
): Promise<DocumentSummary[]> {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/change-impact/reports`);
  if (!res.ok) throw new Error(await parseError(res));
  const data = (await res.json()) as ChangeImpactReportListResponse;
  return data.items;
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
    throw new Error(await parseError(res));
  }
  return res.json() as Promise<ChangeImpactResponse>;
}
