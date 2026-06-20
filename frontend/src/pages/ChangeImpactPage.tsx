import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, CheckCircle2, FileText, Loader2 } from "lucide-react";
import { listChangeImpactReports, runChangeImpact } from "@/services/changeImpactApi";

export default function ChangeImpactPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [changeDescription, setChangeDescription] = useState("");
  const [reqIdsRaw, setReqIdsRaw] = useState("");
  const [contextNotes, setContextNotes] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      runChangeImpact(projectId!, {
        change_description: changeDescription,
        changed_requirement_ids: reqIdsRaw
          .split(/[,\n]+/)
          .map((s) => s.trim())
          .filter(Boolean),
        context_notes: contextNotes,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["change-impact-reports", projectId] });
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });

  const reportsQuery = useQuery({
    queryKey: ["change-impact-reports", projectId],
    queryFn: () => listChangeImpactReports(projectId!),
    enabled: !!projectId,
  });

  const canSubmit =
    !!projectId &&
    changeDescription.trim().length >= 10 &&
    reqIdsRaw.trim().length > 0 &&
    !mutation.isPending;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-lg font-semibold">Change Impact Analysis</h2>
          <p className="text-sm text-muted-foreground">
            Describe what changed and which requirements are affected. The agent will
            analyse all available project documents and produce an impact report.
          </p>
        </div>
      </div>

      {mutation.isSuccess && mutation.data ? (
        <div className="rounded-lg border border-green-300 bg-green-50 p-5 space-y-3">
          <div className="flex items-center gap-2 text-green-700 font-medium">
            <CheckCircle2 className="h-5 w-5" />
            Impact report created
          </div>
          <p className="text-sm text-green-800">{mutation.data.title}</p>
          <p className="text-xs text-muted-foreground">{mutation.data.message}</p>
          <div className="flex gap-3 pt-1">
            <button
              onClick={() => navigate(`/projects/${projectId}/documents`)}
              className="rounded-md bg-green-700 px-4 py-1.5 text-sm text-white hover:bg-green-800"
            >
              View Report in Documents
            </button>
            <button
              onClick={() => {
                mutation.reset();
                setChangeDescription("");
                setReqIdsRaw("");
                setContextNotes("");
              }}
              className="rounded-md border px-4 py-1.5 text-sm hover:bg-accent"
            >
              Run Another Analysis
            </button>
          </div>
        </div>
      ) : (
        <form
          className="space-y-5"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) mutation.mutate();
          }}
        >
          {/* Change description */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">
              Change Description <span className="text-destructive">*</span>
            </label>
            <textarea
              value={changeDescription}
              onChange={(e) => setChangeDescription(e.target.value)}
              rows={4}
              placeholder="Describe what changed and why. Be specific — e.g. 'FR-003 now requires email verification before first login. Previously there was no verification step.'"
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              disabled={mutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              Min 10 characters. Include old vs new behaviour where possible.
            </p>
          </div>

          {/* Requirement IDs */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">
              Changed Requirement IDs <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={reqIdsRaw}
              onChange={(e) => setReqIdsRaw(e.target.value)}
              placeholder="FR-003, FR-011, NFR-002"
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              disabled={mutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated. Use the same IDs as in the Requirement Summary (FR-XXX,
              NFR-XXX, BR-XXX).
            </p>
          </div>

          {/* Context notes */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">
              Context Notes{" "}
              <span className="text-xs text-muted-foreground">(optional)</span>
            </label>
            <textarea
              value={contextNotes}
              onChange={(e) => setContextNotes(e.target.value)}
              rows={2}
              placeholder="Any additional context — e.g. 'Requested by client on 2026-06-18 following PDPA review.'"
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              disabled={mutation.isPending}
            />
          </div>

          {mutation.isError && (
            <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-red-50 p-3 text-sm text-destructive">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              {mutation.error instanceof Error
                ? mutation.error.message
                : "An unexpected error occurred."}
            </div>
          )}

          <button
            type="submit"
            disabled={!canSubmit}
            className="flex items-center gap-2 rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {mutation.isPending ? "Analysing impact…" : "Run Change Impact Analysis"}
          </button>

          <p className="text-xs text-muted-foreground">
            The agent reads all available project documents (Requirement Summary, FSD,
            API Spec, DB Design, Screen Spec, Test Cases) and produces a Change Impact
            Report. This may take 1–3 minutes.
          </p>
        </form>
      )}

      <section className="rounded-lg border bg-white">
        <div className="border-b px-4 py-3">
          <h3 className="text-sm font-semibold">Recent Impact Reports</h3>
        </div>
        <div className="divide-y">
          {reportsQuery.isLoading ? (
            <p className="px-4 py-3 text-sm text-muted-foreground">Loading reports...</p>
          ) : !reportsQuery.data?.length ? (
            <p className="px-4 py-3 text-sm text-muted-foreground">No impact reports yet.</p>
          ) : (
            reportsQuery.data.slice(0, 5).map((report) => (
              <button
                key={report.id}
                type="button"
                onClick={() => navigate(`/projects/${projectId}/documents`)}
                className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-accent"
              >
                <FileText className="h-4 w-4 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{report.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(report.created_at).toLocaleString()} - {report.status}
                  </p>
                </div>
              </button>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
