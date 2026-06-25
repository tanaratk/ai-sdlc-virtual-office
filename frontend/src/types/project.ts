export type ProjectStatus = "active" | "archived" | "completed";

export interface TechStackConfig {
  // Core
  preset?: string;
  frontend?: string;
  backend?: string;
  database?: string;
  app_type?: string;
  // Language & versions (FR-06, FR-07)
  language?: string;
  frontend_version?: string;
  backend_version?: string;
  database_version?: string;
  // Infrastructure (FR-09)
  cloud?: string;
  auth?: string;
  orm?: string;
  container?: string;
  testing?: string;
  logging?: string;
  monitoring?: string;
  api_docs?: string;
  cache?: string;
  queue?: string;
  deployment_target?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  created_by: string;
  workspace_path: string | null;
  tech_stack?: TechStackConfig | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  created_by: string;
  workspace_path?: string;
  tech_stack?: TechStackConfig;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  workspace_path?: string;
  tech_stack?: TechStackConfig;
}
