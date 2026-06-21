export type ProjectStatus = "active" | "archived" | "completed";

export interface TechStackConfig {
  frontend?: string;
  backend?: string;
  database?: string;
  app_type?: string;
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
