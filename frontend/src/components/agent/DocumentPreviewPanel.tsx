import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, FileText, XCircle } from "lucide-react";
import { documentApi } from "@/services/documentApi";

const STEP_LABELS: Record<string, string> = {
  requirement_summary: "Requirement Summary",
  gap_analysis: "Gap Analysis Report",
  ba_documents: "BA Documents (BRD + FSD + User Stories)",
  sa_documents: "Architecture + DB Design + API Spec",
  ux_documents: "Screen Specification + UX Flows",
  dev_documents: "Code Task List + Skeleton Plan",
  test_cases: "Test Cases + UAT Scripts",
  change_impact: "Change Impact Report",
  documentation: "Compiled Documentation",
  pm_summary: "PM Delivery Report",
};

interface DocumentPreviewPanelProps {
  projectId: string;
  documentId: string;
  stepName: string;
  onApprove: () => void;
  onReject: () => void;
  isApproving?: boolean;
  isRejecting?: boolean;
}

export function DocumentPreviewPanel({
  projectId,
  documentId,
  stepName,
  onApprove,
  onReject,
  isApproving = false,
  isRejecting = false,
}: DocumentPreviewPanelProps) {
  const { data: doc, isLoading } = useQuery({
    queryKey: ["document", projectId, documentId],
    queryFn: () => documentApi.get(projectId, documentId),
    enabled: !!projectId && !!documentId,
  });

  const label = STEP_LABELS[stepName] ?? stepName;

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b bg-yellow-50 px-4 py-3">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-yellow-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-yellow-900">Awaiting Review</p>
            <p className="text-xs text-yellow-700">{label}</p>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={onReject}
            disabled={isRejecting || isApproving}
            className="flex items-center gap-1.5 rounded-md border border-destructive px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <XCircle className="h-3.5 w-3.5" />
            {isRejecting ? "Rejecting…" : "Reject"}
          </button>
          <button
            onClick={onApprove}
            disabled={isApproving || isRejecting}
            className="flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            {isApproving ? "Approving…" : "Approve"}
          </button>
        </div>
      </div>

      {/* Document content */}
      <div className="max-h-[60vh] overflow-y-auto p-4">
        {isLoading && (
          <p className="text-sm text-muted-foreground text-center py-8">Loading document…</p>
        )}
        {!isLoading && doc && (
          <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-foreground">
            {doc.content_markdown}
          </pre>
        )}
        {!isLoading && !doc && (
          <p className="text-sm text-destructive text-center py-8">
            Could not load document content.
          </p>
        )}
      </div>
    </div>
  );
}
