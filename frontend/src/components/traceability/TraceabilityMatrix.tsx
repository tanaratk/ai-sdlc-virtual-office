interface TraceabilityMatrixProps {
  projectId: string;
}

export function TraceabilityMatrix({ projectId: _projectId }: TraceabilityMatrixProps) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center">
      <p className="text-sm font-medium">Traceability Matrix</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Available in Sprint 15 — after all agent documents are generated.
      </p>
    </div>
  );
}
