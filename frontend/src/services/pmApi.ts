import { API_BASE_URL } from "./api";

export interface PMSummaryResponse {
  project_summary_id: string;
  delivery_report_id: string;
  project_summary_title: string;
  delivery_report_title: string;
  message: string;
}

export async function runPMSummary(projectId: string): Promise<PMSummaryResponse> {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/pm-summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<PMSummaryResponse>;
}
