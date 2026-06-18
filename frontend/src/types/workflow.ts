export type PipelineRunStatus =
  | "pending"
  | "running"
  | "waiting_for_user"
  | "completed"
  | "failed"
  | "cancelled";

export type PipelineStepStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export interface PipelineRun {
  id: string;
  project_id: string;
  status: PipelineRunStatus;
  current_step: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface PipelineStep {
  id: string;
  pipeline_run_id: string;
  step_name: string;
  agent_id: string | null;
  status: PipelineStepStatus;
  output_document_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  retry_count: number;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}
