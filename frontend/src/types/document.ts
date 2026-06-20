export type DocumentType =
  | "requirement_summary"
  | "gap_analysis_report"
  | "brd"
  | "fsd"
  | "user_story"
  | "architecture_design"
  | "database_design"
  | "api_spec"
  | "screen_spec"
  | "code_task_list"
  | "technical_design"
  | "code_review"
  | "devops_config"
  | "build_report"
  | "monitoring_report"
  | "test_report"
  | "test_cases"
  | "uat_script"
  | "change_impact_report"
  | "compiled_documents"
  | "project_summary"
  | "delivery_report";

export type DocumentStatus = "draft" | "review" | "approved" | "rejected" | "superseded";

export interface DocumentSummary {
  id: string;
  project_id: string;
  document_type: DocumentType;
  title: string;
  version: number;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
}

export interface Document extends DocumentSummary {
  content_markdown: string;
  created_by_agent_id: string | null;
  approved_by: string | null;
}
