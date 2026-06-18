import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { documentApi } from "@/services/documentApi";
import { DocumentViewer } from "@/components/document/DocumentViewer";
import type { DocumentType } from "@/types/document";

const DOC_TYPE_LABELS: Record<DocumentType, string> = {
  requirement_summary: "Req Summary",
  gap_analysis_report: "Gap Analysis",
  brd: "BRD",
  fsd: "FSD",
  user_story: "User Stories",
  architecture_design: "Architecture",
  database_design: "DB Design",
  api_spec: "API Spec",
  screen_spec: "Screen Spec",
  code_task_list: "Task List",
  test_cases: "Test Cases",
  uat_script: "UAT Script",
  change_impact_report: "Change Impact",
  compiled_documents: "Compiled",
  project_summary: "Project Summary",
  delivery_report: "Delivery Report",
};

export default function DocumentReview() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["documents", projectId],
    queryFn: () => documentApi.list(projectId!),
    enabled: !!projectId,
  });

  // Fetch full document (with content_markdown) separately when selected
  const { data: selectedDoc, isLoading: isDocLoading } = useQuery({
    queryKey: ["document", projectId, selectedId],
    queryFn: () => documentApi.get(projectId!, selectedId!),
    enabled: !!projectId && !!selectedId,
  });

  const approveMutation = useMutation({
    mutationFn: () => documentApi.approve(projectId!, selectedId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
      queryClient.invalidateQueries({ queryKey: ["document", projectId, selectedId] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => documentApi.reject(projectId!, selectedId!, "Rejected by reviewer"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
      queryClient.invalidateQueries({ queryKey: ["document", projectId, selectedId] });
    },
  });

  return (
    <div className="flex h-full gap-4">
      <aside className="w-48 flex-shrink-0 space-y-1 overflow-y-auto">
        <h3 className="mb-2 text-sm font-semibold">Documents</h3>
        {isLoading && <p className="text-xs text-muted-foreground">Loading…</p>}
        {data?.items.map((doc) => (
          <button
            key={doc.id}
            onClick={() => setSelectedId(doc.id)}
            className={`w-full rounded-md px-2 py-1.5 text-left text-xs transition-colors hover:bg-accent ${
              selectedId === doc.id ? "bg-accent font-medium" : ""
            }`}
          >
            {DOC_TYPE_LABELS[doc.document_type] ?? doc.document_type}
          </button>
        ))}
        {data?.items.length === 0 && (
          <p className="text-xs text-muted-foreground">No documents yet.</p>
        )}
      </aside>

      <div className="flex-1 min-h-0">
        {selectedId && isDocLoading && (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-muted-foreground">Loading document…</p>
          </div>
        )}
        {selectedDoc && !isDocLoading && (
          <DocumentViewer
            document={selectedDoc}
            onApprove={approveMutation.mutate}
            onReject={rejectMutation.mutate}
          />
        )}
        {!selectedId && (
          <div className="flex h-full items-center justify-center rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">Select a document to review</p>
          </div>
        )}
      </div>
    </div>
  );
}
