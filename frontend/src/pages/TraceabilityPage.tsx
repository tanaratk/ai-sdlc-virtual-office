import { Link, useParams } from "react-router-dom";
import { FolderOpen } from "lucide-react";
import { TraceabilityMatrix } from "@/components/traceability/TraceabilityMatrix";

export default function TraceabilityPage() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Traceability Matrix</h2>
        <p className="text-sm text-muted-foreground">
          Requirement → Document coverage across the pipeline.
        </p>
      </div>

      {!projectId ? (
        <div className="rounded-lg border border-dashed p-10 text-center">
          <FolderOpen className="mx-auto h-8 w-8 text-muted-foreground" />
          <p className="mt-2 text-sm font-medium">No project selected</p>
          <p className="text-xs text-muted-foreground mt-1">
            Open a project first, then navigate to its Traceability tab.
          </p>
          <Link
            to="/projects"
            className="mt-4 inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-accent"
          >
            Go to Projects
          </Link>
        </div>
      ) : (
        <TraceabilityMatrix projectId={projectId} />
      )}
    </div>
  );
}
