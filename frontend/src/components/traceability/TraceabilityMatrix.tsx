import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link2, RefreshCw, CheckCircle2, XCircle } from "lucide-react";
import { traceabilityApi } from "@/services/traceabilityApi";
import type { DocumentType } from "@/types/document";

interface TraceabilityMatrixProps {
  projectId: string;
}

const DOC_TYPE_SHORT: Partial<Record<DocumentType, string>> = {
  requirement_summary: "Req Sum",
  gap_analysis_report: "Gap",
  brd: "BRD",
  fsd: "FSD",
  user_story: "Stories",
  architecture_design: "Arch",
  database_design: "DB",
  api_spec: "API",
  screen_spec: "Screen",
  code_task_list: "Tasks",
  test_cases: "Tests",
  uat_script: "UAT",
};

const PIPELINE_DOC_TYPES: DocumentType[] = [
  "requirement_summary",
  "gap_analysis_report",
  "brd",
  "fsd",
  "user_story",
  "architecture_design",
  "database_design",
  "api_spec",
  "screen_spec",
  "code_task_list",
  "test_cases",
  "uat_script",
];

export function TraceabilityMatrix({ projectId }: TraceabilityMatrixProps) {
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["traceability", projectId],
    queryFn: () => traceabilityApi.getMatrix(projectId),
    enabled: !!projectId,
  });

  const autoLinkMutation = useMutation({
    mutationFn: () => traceabilityApi.autoLink(projectId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["traceability", projectId] }),
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading traceability matrix…</p>;
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-destructive">Failed to load traceability data.</p>
    );
  }

  const { coverage, requirement_inputs, documents } = data;

  // Build lookup: doc_type → document
  const docByType = new Map(documents.map((d) => [d.document_type, d]));

  // Build lookup: req_id → Set of linked target_ids
  const linkedTargets = new Map<string, Set<string>>();
  for (const lnk of data.links) {
    if (lnk.source_type === "requirement_input") {
      if (!linkedTargets.has(lnk.source_id)) {
        linkedTargets.set(lnk.source_id, new Set());
      }
      linkedTargets.get(lnk.source_id)!.add(lnk.target_id);
    }
  }

  return (
    <div className="space-y-6">
      {/* Coverage summary */}
      <div className="grid gap-3 sm:grid-cols-4">
        <div className="rounded-lg border bg-white p-3">
          <p className="text-xs text-muted-foreground">Requirements</p>
          <p className="text-2xl font-semibold">{coverage.total_requirement_inputs}</p>
        </div>
        <div className="rounded-lg border bg-white p-3">
          <p className="text-xs text-muted-foreground">Documents Generated</p>
          <p className="text-2xl font-semibold">{coverage.total_documents}</p>
          <p className="text-xs text-muted-foreground">of {PIPELINE_DOC_TYPES.length} expected</p>
        </div>
        <div className="rounded-lg border bg-white p-3">
          <p className="text-xs text-muted-foreground">Linked Requirements</p>
          <p className="text-2xl font-semibold">{coverage.linked_requirement_inputs}</p>
          <p className="text-xs text-muted-foreground">of {coverage.total_requirement_inputs}</p>
        </div>
        <div className="rounded-lg border bg-white p-3">
          <p className="text-xs text-muted-foreground">Pipeline Coverage</p>
          <p
            className={`text-2xl font-semibold ${
              coverage.coverage_pct >= 80
                ? "text-green-600"
                : coverage.coverage_pct >= 50
                ? "text-yellow-600"
                : "text-destructive"
            }`}
          >
            {coverage.coverage_pct}%
          </p>
        </div>
      </div>

      {/* Auto-link action */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">Requirement → Document Links</p>
          <p className="text-xs text-muted-foreground">
            {data.links.length} explicit link{data.links.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => autoLinkMutation.mutate()}
          disabled={autoLinkMutation.isPending}
          className="flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {autoLinkMutation.isPending ? (
            <RefreshCw className="h-3 w-3 animate-spin" />
          ) : (
            <Link2 className="h-3 w-3" />
          )}
          {autoLinkMutation.isPending ? "Linking…" : "Auto-Link All"}
        </button>
      </div>

      {autoLinkMutation.isSuccess && autoLinkMutation.data && (
        <p className="text-xs text-green-600">{autoLinkMutation.data.message}</p>
      )}

      {/* Matrix table */}
      {requirement_inputs.length > 0 ? (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-3 py-2 text-left font-medium w-40">Requirement Input</th>
                {PIPELINE_DOC_TYPES.map((dt) => (
                  <th
                    key={dt}
                    className="px-2 py-2 text-center font-medium min-w-[52px]"
                    title={dt}
                  >
                    {DOC_TYPE_SHORT[dt] ?? dt}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {requirement_inputs.map((req, idx) => {
                const targets = linkedTargets.get(req.id) ?? new Set<string>();
                return (
                  <tr
                    key={req.id}
                    className={idx % 2 === 0 ? "bg-white" : "bg-muted/10"}
                  >
                    <td className="px-3 py-2 font-medium max-w-[160px] truncate" title={req.title ?? req.input_type}>
                      {req.title ?? req.input_type}
                    </td>
                    {PIPELINE_DOC_TYPES.map((dt) => {
                      const doc = docByType.get(dt);
                      const linked = doc ? targets.has(doc.id) : false;
                      return (
                        <td key={dt} className="px-2 py-2 text-center">
                          {doc ? (
                            linked ? (
                              <span title={`Linked to ${doc.title}`}>
                                <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mx-auto" />
                              </span>
                            ) : (
                              <span
                                className="inline-block h-2 w-2 rounded-full bg-yellow-400 mx-auto"
                                title="Document exists but not linked"
                              />
                            )
                          ) : (
                            <span title="No document generated yet">
                              <XCircle className="h-3 w-3 text-muted-foreground/30 mx-auto" />
                            </span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            No requirement inputs found. Upload requirements and run the pipeline first.
          </p>
        </div>
      )}

      {/* Missing document types */}
      {coverage.document_types_missing.length > 0 && (
        <div className="rounded-lg border bg-yellow-50 p-3">
          <p className="text-xs font-medium text-yellow-800">Missing document types:</p>
          <p className="text-xs text-yellow-700 mt-1">
            {coverage.document_types_missing
              .map((dt) => DOC_TYPE_SHORT[dt] ?? dt)
              .join(", ")}
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3 text-green-500" /> Linked
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-yellow-400" /> Document exists, not linked
        </span>
        <span className="flex items-center gap-1">
          <XCircle className="h-3 w-3 text-muted-foreground/30" /> Not generated
        </span>
      </div>
    </div>
  );
}
