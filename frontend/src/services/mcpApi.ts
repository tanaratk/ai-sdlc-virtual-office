import { API_BASE_URL } from "./api";

export interface McpTool {
  id: string;
  tool_name: string;
  display_name: string;
  description: string;
  category: string;
  requires_approval: boolean;
  is_enabled: boolean;
  is_dangerous: boolean;
}

export interface McpToolCall {
  id: string;
  project_id: string;
  tool_name: string;
  agent_id: string | null;
  status: "pending" | "approved" | "rejected" | "running" | "completed" | "failed";
  input_json: Record<string, unknown> | null;
  output_json: Record<string, unknown> | null;
  error_message: string | null;
  requested_by: string | null;
  resolved_by: string | null;
  requested_at: string;
  resolved_at: string | null;
}

export interface InvokeRequest {
  tool_name: string;
  input_json?: Record<string, unknown>;
  requested_by?: string;
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const mcpApi = {
  listTools: () =>
    apiFetch<McpTool[]>(`${API_BASE_URL}/mcp/tools`),

  updateTool: (toolName: string, isEnabled: boolean) =>
    apiFetch<McpTool>(`${API_BASE_URL}/mcp/tools/${toolName}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_enabled: isEnabled }),
    }),

  listCalls: (projectId: string, statusFilter?: string) => {
    const url = new URL(`${API_BASE_URL}/projects/${projectId}/mcp/calls`);
    if (statusFilter) url.searchParams.set("status_filter", statusFilter);
    return apiFetch<McpToolCall[]>(url.toString());
  },

  invoke: (projectId: string, body: InvokeRequest) =>
    apiFetch<McpToolCall>(`${API_BASE_URL}/projects/${projectId}/mcp/invoke`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),

  approve: (projectId: string, callId: string) =>
    apiFetch<McpToolCall>(
      `${API_BASE_URL}/projects/${projectId}/mcp/calls/${callId}/approve`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resolved_by: "user" }),
      },
    ),

  reject: (projectId: string, callId: string) =>
    apiFetch<McpToolCall>(
      `${API_BASE_URL}/projects/${projectId}/mcp/calls/${callId}/reject`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resolved_by: "user" }),
      },
    ),
};
