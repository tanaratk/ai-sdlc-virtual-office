import { useParams, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  FileText,
  Loader2,
} from "lucide-react";
import { compileDocs } from "@/services/documentationApi";

const COMPILED_SECTIONS = [
  "Requirement Summary",
  "Gap Analysis Report",
  "Business Requirements Document (BRD)",
  "Functional Specification Document (FSD)",
  "User Stories",
  "Architecture Design",
  "Database Design",
  "API Specification",
  "Screen Specification",
  "Code Task List",
  "Test Cases",
  "UAT Script",
  "Change Impact Report (if any)",
];

export default function DocumentationPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: () => compileDocs(projectId!),
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
            <BookOpen className="h-5 w-5" />
            Compile Documentation
          </h2>
          <p className="text-sm text-muted-foreground">
            Bundle all AI-generated project documents into one Compiled Document Set
            with an executive summary and table of contents.
          </p>
        </div>
      </div>

      {mutation.isSuccess && mutation.data ? (
        <div className="rounded-lg border border-green-300 bg-green-50 p-5 space-y-3">
          <div className="flex items-center gap-2 text-green-700 font-medium">
            <CheckCircle2 className="h-5 w-5" />
            Compiled Document Set created
          </div>
          <p className="text-sm text-green-800">{mutation.data.title}</p>
          <p className="text-xs text-muted-foreground">{mutation.data.message}</p>
          <div className="flex gap-3 pt-1">
            <button
              onClick={() => navigate(`/projects/${projectId}/documents`)}
              className="rounded-md bg-green-700 px-4 py-1.5 text-sm text-white hover:bg-green-800"
            >
              View in Documents
            </button>
            <button
              onClick={() => mutation.reset()}
              className="rounded-md border px-4 py-1.5 text-sm hover:bg-accent"
            >
              Compile Again
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {/* What will be compiled */}
          <div className="rounded-lg border bg-white p-5 space-y-3">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Documents That Will Be Compiled
            </h3>
            <p className="text-xs text-muted-foreground">
              The agent collects whichever of these documents exist for this project.
              Missing documents are noted in the index but do not block compilation.
            </p>
            <ul className="space-y-1">
              {COMPILED_SECTIONS.map((section, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="w-5 text-right text-xs">{i + 1}.</span>
                  {section}
                </li>
              ))}
            </ul>
          </div>

          {/* What the agent does */}
          <div className="rounded-lg border bg-accent/30 p-4 space-y-2 text-sm">
            <p className="font-medium text-foreground">What the agent produces</p>
            <ul className="space-y-1 text-muted-foreground list-disc pl-4">
              <li>Cover page with project metadata</li>
              <li>Table of contents for all included sections</li>
              <li>LLM-generated executive summary (3–5 sentences)</li>
              <li>Document index table with status and IDs</li>
              <li>Full content of every compiled document in order</li>
            </ul>
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
            {mutation.isPending ? "Compiling documents…" : "Compile All Documents"}
          </button>

          <p className="text-xs text-muted-foreground">
            Compilation reads existing documents — no pipeline agents will be re-run.
            This may take 30–60 seconds while the executive summary is generated.
          </p>
        </div>
      )}
    </div>
  );
}
