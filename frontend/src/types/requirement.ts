export type InputType =
  | "manual_text"
  | "meeting_transcript"
  | "chat_log"
  | "markdown_document"
  | "email_content"
  | "audio_transcript";

export interface RequirementInput {
  id: string;
  project_id: string;
  input_type: InputType;
  title: string | null;
  content: string;
  file_url: string | null;
  source_owner: string | null;
  source_date: string | null;
  created_at: string;
}

export interface RequirementInputCreate {
  input_type: InputType;
  title?: string;
  content: string;
  file_url?: string;
  source_owner?: string;
  source_date?: string;
}
