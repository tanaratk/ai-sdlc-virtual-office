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
  | "test_cases"
  | "uat_script"
  | "change_impact_report"
  | "compiled_documents"
  | "project_summary"
  | "delivery_report";

export type DocumentStatus = "draft" | "review" | "approved" | "rejected" | "superseded";

export interface Document {
  id: string;
  project_id: string;
  document_type: DocumentType;
  title: string;
  content_markdown: string;
  version: number;
  status: DocumentStatus;
  created_by_agent_id: string | null;
  approved_by: string | null;
  created_at: string;
  updated_at: string;
}
