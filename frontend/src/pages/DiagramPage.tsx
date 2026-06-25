import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Copy,
  ExternalLink,
  Loader2,
  RefreshCw,
  Shapes,
  Wand2,
} from "lucide-react";
import { diagramApi, type DiagramResponse } from "@/services/diagramApi";
import MermaidChart from "@/components/diagram/MermaidChart";

// ── Diagram card ──────────────────────────────────────────────────────────────

function DiagramCard({ diagram }: { diagram: DiagramResponse }) {
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(diagram.mermaid_code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      {/* Card header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/20">
        <div className="flex items-center gap-2">
          <Shapes className="h-4 w-4 text-indigo-500" />
          <h3 className="text-sm font-semibold">{diagram.title}</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={copy}
            title="Copy Mermaid code"
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            <Copy className="h-3.5 w-3.5" />
            {copied ? "Copied!" : "Copy"}
          </button>
          <a
            href={diagram.drawio_url}
            target="_blank"
            rel="noreferrer"
            title="Open in Mermaid Live Editor"
            className="flex items-center gap-1 text-xs text-indigo-600 hover:underline"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Open in Mermaid Live
          </a>
        </div>
      </div>

      {/* Rendered diagram */}
      <div className="p-4 bg-white min-h-[200px] flex items-center justify-center overflow-x-auto">
        <MermaidChart code={diagram.mermaid_code} className="max-w-full" />
      </div>

      {/* Collapsible Mermaid code */}
      <div className="border-t">
        <button
          onClick={() => setShowCode((v) => !v)}
          className="flex items-center gap-2 w-full px-4 py-2 text-xs text-muted-foreground hover:text-foreground hover:bg-muted/20"
        >
          {showCode ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          {showCode ? "Hide" : "Show"} Mermaid code
        </button>
        {showCode && (
          <pre className="px-4 pb-4 text-xs font-mono text-muted-foreground whitespace-pre-wrap bg-muted/10 border-t">
            {diagram.mermaid_code}
          </pre>
        )}
      </div>

      {/* Draw.io import hint */}
      <div className="px-4 py-2 bg-muted/10 border-t text-xs text-muted-foreground">
        To use in Draw.io: open <strong>app.diagrams.net</strong> → Extras → Edit Diagram → paste Mermaid code
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function DiagramPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const qc = useQueryClient();

  const { data: diagrams = [], isLoading, isError } = useQuery({
    queryKey: ["diagrams", projectId],
    queryFn: () => diagramApi.list(projectId!),
    enabled: !!projectId,
  });

  const generateMutation = useMutation({
    mutationFn: () => diagramApi.generate(projectId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["diagrams", projectId] }),
  });

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Shapes className="h-5 w-5 text-indigo-500" /> Diagrams
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Auto-generate architecture and ERD diagrams from the Solution Architect Agent's output.
            Diagrams are rendered with Mermaid.js and can be exported to Draw.io.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => qc.invalidateQueries({ queryKey: ["diagrams", projectId] })}
            className="text-muted-foreground hover:text-foreground"
            title="Refresh"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {generateMutation.isPending
              ? <><Loader2 className="h-4 w-4 animate-spin" /> Generating…</>
              : <><Wand2 className="h-4 w-4" /> Generate Diagrams</>}
          </button>
        </div>
      </div>

      {/* Generate result */}
      {generateMutation.isSuccess && generateMutation.data && (
        <div className="rounded-md border border-green-300 bg-green-50 p-3 text-sm text-green-800">
          {generateMutation.data.generated} diagram(s) generated successfully.
        </div>
      )}
      {generateMutation.isError && (
        <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-red-50 p-3 text-sm text-destructive">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          {generateMutation.error instanceof Error
            ? generateMutation.error.message
            : "Generation failed."}
        </div>
      )}

      {/* Draw.io info banner */}
      <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-xs text-blue-800 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-blue-500" />
        <span>
          <strong>Draw.io tip:</strong> Click "Open in Mermaid Live" to edit the diagram online,
          or click "Copy" and paste into <strong>app.diagrams.net</strong> via Extras → Edit Diagram.
          Draw.io natively supports Mermaid syntax.
        </span>
      </div>

      {/* Diagram list */}
      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground py-12 justify-center">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading diagrams…
        </div>
      ) : isError ? (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertTriangle className="h-4 w-4" /> Failed to load diagrams.
        </div>
      ) : diagrams.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center space-y-3">
          <Shapes className="h-8 w-8 text-muted-foreground mx-auto" />
          <p className="text-sm text-muted-foreground">
            No diagrams yet. Click <strong>Generate Diagrams</strong> above to create
            architecture and ERD diagrams from the Solution Architect Agent's output.
          </p>
          <p className="text-xs text-muted-foreground">
            Requires the <em>Solution Architect Agent</em> pipeline step to have completed.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {diagrams.map((d) => (
            <DiagramCard key={d.id} diagram={d} />
          ))}
        </div>
      )}
    </div>
  );
}
