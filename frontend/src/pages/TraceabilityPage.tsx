import { useParams } from "react-router-dom";
import { TraceabilityMatrix } from "@/components/traceability/TraceabilityMatrix";

export default function TraceabilityPage() {
  const { projectId } = useParams<{ projectId: string }>();
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Traceability Matrix</h2>
      <TraceabilityMatrix projectId={projectId ?? ""} />
    </div>
  );
}
