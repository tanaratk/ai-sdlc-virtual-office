import { CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Document } from "@/types/document";

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

  return (
    <div className="flex h-full flex-col rounded-lg border bg-white overflow-hidden">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold">{document.title}</span>
          <span className="text-xs text-muted-foreground">v{document.version}</span>
          <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", STATUS_COLORS[document.status])}>
            {document.status}
          </span>
        </div>
        {canReview && (
          <div className="flex gap-2">
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
          </div>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <pre className="whitespace-pre-wrap text-sm font-mono text-foreground leading-relaxed">
          {document.content_markdown}
        </pre>
      </div>
    </div>
  );
}
