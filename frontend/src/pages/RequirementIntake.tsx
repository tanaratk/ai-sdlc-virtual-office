import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { sourceApi } from "@/services/sourceApi";
import { RequirementUpload } from "@/components/requirement/RequirementUpload";
import { RequirementList } from "@/components/requirement/RequirementList";
import type { RequirementInputCreate } from "@/types/requirement";

export default function RequirementIntake() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const [resetKey, setResetKey] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ["inputs", projectId],
    queryFn: () => sourceApi.list(projectId!),
    enabled: !!projectId,
  });

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
    <div className="grid gap-6 lg:grid-cols-2">
      <section>
        <h3 className="mb-4 text-sm font-semibold">Upload / Paste Requirement</h3>
        <RequirementUpload
          key={resetKey}
          onSubmit={createMutation.mutate}
          isLoading={createMutation.isPending}
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
  );
}
