import { API_BASE_URL } from "./api";

export interface GitHubSettingResponse {
  id: string;
  project_id: string;
  repo_owner: string;
  repo_name: string;
  default_branch: string;
  repo_url: string;
  created_at: string;
  updated_at: string;
}

export interface GitHubIssueResponse {
  id: string;
  project_id: string;
  issue_number: number;
  issue_url: string;
  title: string;
  requirement_ids: string | null;
  state: string;
  created_at: string;
}

export interface CreateIssuesResponse {
  created: number;
  issues: GitHubIssueResponse[];
  skipped: number;
  errors: string[];
}

export interface GitHubVerifyResponse {
  ok: boolean;
  full_name: string;
  private: boolean;
  html_url: string;
}

export interface GitHubSettingUpsert {
  repo_owner: string;
  repo_name: string;
  access_token: string;
  default_branch?: string;
}

export interface PushAppRequest {
  repo_name?: string;
  private?: boolean;
}

export interface PushAppResponse {
  repo_url: string;
  repo_full_name: string;
  files_pushed: number;
  errors: string[];
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

const base = (id: string) => `${API_BASE_URL}/projects/${id}/github`;

export const githubApi = {
  getSettings: (projectId: string) =>
    apiFetch<GitHubSettingResponse>(`${base(projectId)}/settings`),

  saveSettings: (projectId: string, body: GitHubSettingUpsert) =>
    apiFetch<GitHubSettingResponse>(`${base(projectId)}/settings`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),

  verify: (projectId: string) =>
    apiFetch<GitHubVerifyResponse>(`${base(projectId)}/verify`, { method: "POST" }),

  listIssues: (projectId: string) =>
    apiFetch<GitHubIssueResponse[]>(`${base(projectId)}/issues`),

  createIssues: (projectId: string) =>
    apiFetch<CreateIssuesResponse>(`${base(projectId)}/issues`, { method: "POST" }),

  createBranch: (projectId: string, branchName: string, fromBranch?: string) =>
    apiFetch<{ branch: string; sha: string }>(`${base(projectId)}/branches`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ branch_name: branchName, from_branch: fromBranch ?? null }),
    }),

  pushApp: (projectId: string, body?: PushAppRequest) =>
    apiFetch<PushAppResponse>(`${base(projectId)}/push-app`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body ?? {}),
    }),
};
