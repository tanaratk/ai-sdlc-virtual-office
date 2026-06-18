import { useParams } from "react-router-dom";
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
      <TraceabilityMatrix projectId={projectId ?? ""} />
    </div>
  );
}
