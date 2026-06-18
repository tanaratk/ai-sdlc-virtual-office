import { useParams, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ClipboardList,
  FileCheck,
  Loader2,
} from "lucide-react";
import { runPMSummary } from "@/services/pmApi";

export default function PMPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: () => runPMSummary(projectId!),
  });

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
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <ClipboardList className="h-5 w-5" />
            PM Summary — Pipeline Final Step
          </h2>
          <p className="text-sm text-muted-foreground">
            Generate the Project Summary and Delivery Report — the final step (10 of 10)
            in the AI-SDLC pipeline.
          </p>
        </div>
      </div>

      {mutation.isSuccess && mutation.data ? (
        <div className="rounded-lg border border-green-300 bg-green-50 p-5 space-y-4">
          <div className="flex items-center gap-2 text-green-700 font-medium">
            <CheckCircle2 className="h-5 w-5" />
            Pipeline Step 10 complete — two documents created
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 rounded-md border bg-white p-3">
              <FileCheck className="h-4 w-4 text-green-600 shrink-0" />
              <div>
                <p className="text-sm font-medium">{mutation.data.project_summary_title}</p>
                <p className="text-xs text-muted-foreground">
                  ID: {mutation.data.project_summary_id}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-md border bg-white p-3">
              <FileCheck className="h-4 w-4 text-green-600 shrink-0" />
              <div>
                <p className="text-sm font-medium">{mutation.data.delivery_report_title}</p>
                <p className="text-xs text-muted-foreground">
                  ID: {mutation.data.delivery_report_id}
                </p>
              </div>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">{mutation.data.message}</p>

          <div className="flex gap-3 pt-1">
            <button
              onClick={() => navigate(`/projects/${projectId}/documents`)}
              className="rounded-md bg-green-700 px-4 py-1.5 text-sm text-white hover:bg-green-800"
            >
              View Documents
            </button>
            <button
              onClick={() => mutation.reset()}
              className="rounded-md border px-4 py-1.5 text-sm hover:bg-accent"
            >
              Regenerate
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Pipeline badge */}
          <div className="flex items-center gap-2 rounded-lg border bg-primary/5 px-4 py-3">
            <span className="rounded-full bg-primary px-2.5 py-0.5 text-xs font-semibold text-primary-foreground">
              Step 10 / 10
            </span>
            <span className="text-sm text-foreground font-medium">Final Pipeline Step</span>
          </div>

          {/* What the agent produces */}
          <div className="rounded-lg border bg-white p-5 space-y-4">
            <h3 className="text-sm font-semibold">Two Documents Will Be Created</h3>

            <div className="space-y-3">
              <div className="rounded-md border-l-4 border-l-primary bg-accent/20 p-3 space-y-1">
                <p className="text-sm font-medium">Project Summary</p>
                <ul className="text-xs text-muted-foreground space-y-0.5 list-disc pl-4">
                  <li>LLM-generated executive summary (2–3 paragraphs)</li>
                  <li>Scope delivered — major deliverables with status</li>
                  <li>Risk register derived from project context</li>
                  <li>Recommended next steps for the team</li>
                  <li>Full artifact inventory table</li>
                </ul>
              </div>

              <div className="rounded-md border-l-4 border-l-muted-foreground bg-accent/20 p-3 space-y-1">
                <p className="text-sm font-medium">Delivery Report</p>
                <ul className="text-xs text-muted-foreground space-y-0.5 list-disc pl-4">
                  <li>Pipeline execution log (all steps with timestamps)</li>
                  <li>Complete document inventory with approval status</li>
                  <li>Quality metrics (traceability links, retries, approvals)</li>
                  <li>Sign-off table for PM, BA, Architect, QA, Sponsor</li>
                </ul>
              </div>
            </div>
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
            onClick={() => { if (projectId) mutation.mutate(); }}
            disabled={!projectId || mutation.isPending}
            className="flex items-center gap-2 rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {mutation.isPending ? "Generating reports…" : "Generate PM Summary"}
          </button>

          <p className="text-xs text-muted-foreground">
            Requires at least one project document to exist. The LLM generates the
            executive summary from the Requirement Summary. This may take 30–90 seconds.
          </p>
        </div>
      )}
    </div>
  );
}
