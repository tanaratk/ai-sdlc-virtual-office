import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { documentApi } from "@/services/documentApi";
import { DocumentViewer } from "@/components/document/DocumentViewer";
import type { DocumentSummary, DocumentType } from "@/types/document";

const QA_DOC_TYPES: DocumentType[] = ["test_cases", "test_report", "code_review", "uat_script"];

const DOC_LABELS: Record<DocumentType, string> = {
  test_cases:         "Test Cases",
  test_report:        "Test Report",
  code_review:        "Code Review",
  uat_script:         "UAT Script",
  requirement_summary:  "Req Summary",
  gap_analysis_report:  "Gap Analysis",
  brd:                  "BRD",
  fsd:                  "FSD",
  user_story:           "User Stories",
  architecture_design:  "Architecture",
  database_design:      "DB Design",
  api_spec:             "API Spec",
  screen_spec:          "Screen Spec",
  code_task_list:       "Task List",
  technical_design:     "Technical Design",
  devops_config:        "DevOps Config",
  build_report:         "Build Report",
  monitoring_report:    "Monitoring Report",
  change_impact_report: "Change Impact",
  compiled_documents:   "Compiled",
  project_summary:      "Project Summary",
  delivery_report:      "Delivery Report",
};

const STATUS_COLORS: Record<string, string> = {
  approved: "bg-green-100 text-green-700",
  review:   "bg-yellow-100 text-yellow-700",
  draft:    "bg-gray-100 text-gray-500",
  rejected: "bg-red-100 text-red-600",
};

function DocCard({
  doc,
  selected,
  onClick,
}: {
  doc: DocumentSummary;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-xl border p-4 text-left transition-all hover:shadow-md ${
        selected ? "border-primary bg-primary/5 shadow-sm" : "border-border bg-white"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="text-sm font-medium leading-tight">{DOC_LABELS[doc.document_type] ?? doc.document_type}</span>
        <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${STATUS_COLORS[doc.status] ?? "bg-gray-100 text-gray-500"}`}>
          {doc.status}
        </span>
      </div>
      <p className="mt-1 text-xs text-muted-foreground line-clamp-1">{doc.title}</p>
      <p className="mt-1 text-[10px] text-muted-foreground/60">
        v{doc.version} · {new Date(doc.updated_at).toLocaleDateString()}
      </p>
    </button>
  );
}

export default function QAPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["documents", projectId],
    queryFn: () => documentApi.list(projectId!, 1, 100),
    enabled: !!projectId,
  });

  const { data: selectedDoc, isLoading: isDocLoading } = useQuery({
    queryKey: ["document", projectId, selectedId],
    queryFn: () => documentApi.get(projectId!, selectedId!),
    enabled: !!projectId && !!selectedId,
  });

  const qaDocs = (data?.items ?? []).filter((d) =>
    QA_DOC_TYPES.includes(d.document_type)
  );

  if (isLoading) {
    return <div className="py-12 text-center text-sm text-muted-foreground">Loading…</div>;
  }

  if (qaDocs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-muted">
          <span className="text-2xl">🧪</span>
        </div>
        <h3 className="text-base font-semibold">No QA Documents Yet</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Run the full pipeline to generate Test Cases, Test Report, and Code Review documents.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full gap-6">
      {/* Left panel — doc list */}
      <div className="w-64 shrink-0 space-y-2 overflow-y-auto">
        <h3 className="mb-3 text-sm font-semibold text-foreground">QA Documents</h3>
        {QA_DOC_TYPES.map((type) => {
          const docs = qaDocs.filter((d) => d.document_type === type);
          if (docs.length === 0) {
            return (
              <div key={type} className="rounded-xl border border-dashed border-border p-4 opacity-40">
                <p className="text-sm font-medium text-muted-foreground">{DOC_LABELS[type]}</p>
                <p className="mt-0.5 text-[10px] text-muted-foreground">Not generated yet</p>
              </div>
            );
          }
          return docs.map((doc) => (
            <DocCard
              key={doc.id}
              doc={doc}
              selected={selectedId === doc.id}
              onClick={() => setSelectedId(doc.id)}
            />
          ));
        })}
      </div>

      {/* Right panel — viewer */}
      <div className="flex-1 min-w-0 overflow-y-auto">
        {!selectedId && (
          <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground">
            <p className="text-sm">Select a document on the left to view its content</p>
          </div>
        )}
        {selectedId && (
          <div className="rounded-xl border border-border bg-white p-6">
            {isDocLoading ? (
              <p className="text-sm text-muted-foreground">Loading document…</p>
            ) : selectedDoc ? (
              <DocumentViewer document={selectedDoc} />
            ) : (
              <p className="text-sm text-destructive">Failed to load document.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
