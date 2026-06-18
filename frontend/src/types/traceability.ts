import type { DocumentType } from "./document";

export type ArtifactType = "requirement_input" | "document" | "task" | "pipeline_step";
export type LinkType = "derived_from" | "implements" | "tests" | "conflicts_with";

export interface TraceabilityLink {
  id: string;
  project_id: string;
  source_type: ArtifactType;
  source_id: string;
  target_type: ArtifactType;
  target_id: string;
  link_type: LinkType;
  created_at: string;
}

export interface RequirementInputSummary {
  id: string;
  title: string | null;
  input_type: string;
  created_at: string;
}

export interface DocumentCoverage {
  id: string;
  document_type: DocumentType;
  title: string;
  status: string;
  created_at: string;
}

export interface CoverageStats {
  total_requirement_inputs: number;
  total_documents: number;
  linked_requirement_inputs: number;
  document_types_present: DocumentType[];
  document_types_missing: DocumentType[];
  coverage_pct: number;
}

export interface TraceabilityMatrix {
  project_id: string;
  requirement_inputs: RequirementInputSummary[];
  documents: DocumentCoverage[];
  links: TraceabilityLink[];
  coverage: CoverageStats;
}

export interface AutoLinkResult {
  links_created: number;
  links_skipped: number;
  message: string;
}
