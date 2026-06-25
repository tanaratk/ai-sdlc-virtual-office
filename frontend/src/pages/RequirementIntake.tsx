import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { sourceApi } from "@/services/sourceApi";
import { RequirementUpload } from "@/components/requirement/RequirementUpload";
import { RequirementList } from "@/components/requirement/RequirementList";
import type { RequirementInputCreate } from "@/types/requirement";

export default function RequirementIntake() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [resetKey, setResetKey] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ["inputs", projectId],
    queryFn: () => sourceApi.list(projectId!),
    enabled: !!projectId,
  });

  const hasInputs = (data?.total ?? 0) > 0;

  const createMutation = useMutation({
    mutationFn: (body: RequirementInputCreate) =>
      sourceApi.create(projectId!, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inputs", projectId] });
      setResetKey((k) => k + 1);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (inputId: string) => sourceApi.delete(projectId!, inputId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["inputs", projectId] }),
  });

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <section>
          <h3 className="mb-4 text-sm font-semibold">Upload / Paste Requirement</h3>
          <RequirementUpload
            key={resetKey}
            onSubmit={createMutation.mutate}
            isLoading={createMutation.isPending}
            onNext={hasInputs ? () => navigate(`/projects/${projectId}/agents`) : undefined}
          />
          {createMutation.isError && (
            <p className="mt-2 text-xs text-destructive">{createMutation.error?.message}</p>
          )}
        </section>

        <section>
          <h3 className="mb-4 text-sm font-semibold">
            Saved Requirements ({data?.total ?? 0})
          </h3>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : (
            <RequirementList
              inputs={data?.items ?? []}
              onDelete={deleteMutation.mutate}
            />
          )}
        </section>
      </div>

      {/* Next step call-to-action */}
      {hasInputs && (
        <div className="flex items-center justify-between rounded-xl border border-primary/20 bg-primary/5 px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-foreground">Ready to run the AI Pipeline?</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {data!.total} requirement{data!.total !== 1 ? "s" : ""} saved — proceed to start the 11-step SDLC pipeline.
            </p>
          </div>
          <button
            onClick={() => navigate(`/projects/${projectId}/agents`)}
            className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Next: Run Pipeline
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
