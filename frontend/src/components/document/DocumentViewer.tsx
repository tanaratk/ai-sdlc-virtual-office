import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CheckCircle2, XCircle, Code } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Document } from "@/types/document";
import { ScreenSpecViewer } from "./ScreenSpecViewer";
import { useState } from "react";

const STATUS_COLORS: Record<Document["status"], string> = {
  draft: "bg-muted text-muted-foreground",
  review: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  superseded: "bg-gray-100 text-gray-500",
};

interface DocumentViewerProps {
  document: Document;
  onApprove?: () => void;
  onReject?: () => void;
}

export function DocumentViewer({ document, onApprove, onReject }: DocumentViewerProps) {
  const canReview = document.status === "review";
  const isScreenSpec = document.document_type === "screen_spec";
  const [rawMode, setRawMode] = useState(false);

  return (
    <div className="flex h-full flex-col rounded-lg border bg-white overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold">{document.title}</span>
          <span className="text-xs text-muted-foreground">v{document.version}</span>
          <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", STATUS_COLORS[document.status])}>
            {document.status}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isScreenSpec && (
            <button
              onClick={() => setRawMode((r) => !r)}
              className={cn(
                "flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                rawMode ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted"
              )}
            >
              <Code className="h-3 w-3" />
              {rawMode ? "Card View" : "Raw"}
            </button>
          )}
          {canReview && (
            <>
              <button
                onClick={onApprove}
                className="flex items-center gap-1 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
              >
                <CheckCircle2 className="h-3.5 w-3.5" />
                Approve
              </button>
              <button
                onClick={onReject}
                className="flex items-center gap-1 rounded-md border border-destructive px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10"
              >
                <XCircle className="h-3.5 w-3.5" />
                Reject
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {isScreenSpec && !rawMode ? (
          <ScreenSpecViewer markdown={document.content_markdown} />
        ) : (
          <div className="prose prose-sm max-w-none
            prose-headings:font-semibold prose-headings:text-foreground
            prose-h1:text-lg prose-h2:text-base prose-h3:text-sm
            prose-p:text-muted-foreground prose-p:leading-relaxed
            prose-code:rounded prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:text-xs prose-code:font-mono prose-code:text-foreground prose-code:before:content-none prose-code:after:content-none
            prose-pre:bg-muted prose-pre:rounded-lg prose-pre:p-3 prose-pre:text-xs
            prose-table:text-xs prose-th:font-medium prose-th:text-left prose-td:align-top
            prose-blockquote:border-l-2 prose-blockquote:border-muted prose-blockquote:text-muted-foreground
            prose-li:text-muted-foreground prose-li:leading-relaxed
            prose-strong:text-foreground prose-strong:font-semibold
            prose-a:text-primary prose-a:no-underline hover:prose-a:underline
          ">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {document.content_markdown}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
