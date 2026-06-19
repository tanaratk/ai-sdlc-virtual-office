import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FolderOpen, Trash2, ExternalLink, AlertTriangle } from "lucide-react";
import { projectApi } from "@/services/projectApi";
import type { Project } from "@/types/project";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<Project["status"], string> = {
  active:    "bg-green-100 text-green-700",
  archived:  "bg-gray-100 text-gray-500",
  completed: "bg-blue-100 text-blue-700",
};

export default function AdminProjectsPage() {
  const queryClient = useQueryClient();
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list(1, 100),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => projectApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setConfirmId(null);
    },
  });

  const projects = (data?.items ?? []).filter((p) =>
    search === "" ||
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    (p.description ?? "").toLowerCase().includes(search.toLowerCase())
  );

  const confirmProject = data?.items.find((p) => p.id === confirmId);

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Project Management</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Admin only — delete projects and all associated data</p>
        </div>
        <Link
          to="/projects/new"
          className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
        >
          + New Project
        </Link>
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="Search projects…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full rounded-md border px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
      />

      {/* Table */}
      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!isLoading && projects.length === 0 && (
        <div className="rounded-lg border border-dashed p-10 text-center">
          <FolderOpen className="mx-auto h-8 w-8 text-muted-foreground" />
          <p className="mt-2 text-sm font-medium text-muted-foreground">No projects found</p>
        </div>
      )}

      {projects.length > 0 && (
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Project</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Created</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {projects.map((project) => (
                <tr key={project.id} className="bg-white hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-start gap-2">
                      <FolderOpen className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
                      <div className="min-w-0">
                        <p className="font-medium truncate max-w-xs">{project.name}</p>
                        {project.description && (
                          <p className="text-xs text-muted-foreground truncate max-w-xs mt-0.5">
                            {project.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", STATUS_COLORS[project.status])}>
                      {project.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                    {new Date(project.created_at).toLocaleDateString("en-GB", {
                      day: "2-digit", month: "short", year: "numeric",
                    })}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        to={`/projects/${project.id}`}
                        className="flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs text-muted-foreground hover:bg-accent transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Open
                      </Link>
                      <button
                        onClick={() => setConfirmId(project.id)}
                        className="flex items-center gap-1 rounded-md border border-destructive/40 px-2.5 py-1 text-xs text-destructive hover:bg-destructive/10 transition-colors"
                      >
                        <Trash2 className="h-3 w-3" />
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="border-t bg-muted/20 px-4 py-2 text-xs text-muted-foreground">
            {projects.length} project{projects.length !== 1 ? "s" : ""}
          </div>
        </div>
      )}

      {/* Confirm dialog */}
      {confirmId && confirmProject && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-sm rounded-xl border bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-destructive/10">
                <AlertTriangle className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <p className="text-sm font-semibold">Delete project?</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">{confirmProject.name}</span> and all its
                  documents, pipeline runs, and requirement inputs will be permanently deleted.
                  This cannot be undone.
                </p>
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <button
                onClick={() => setConfirmId(null)}
                disabled={deleteMutation.isPending}
                className="rounded-md border px-4 py-1.5 text-xs font-medium hover:bg-muted disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate(confirmId)}
                disabled={deleteMutation.isPending}
                className="flex items-center gap-1.5 rounded-md bg-destructive px-4 py-1.5 text-xs font-medium text-white hover:bg-destructive/90 disabled:opacity-50"
              >
                <Trash2 className="h-3 w-3" />
                {deleteMutation.isPending ? "Deleting…" : "Delete permanently"}
              </button>
            </div>
            {deleteMutation.isError && (
              <p className="mt-3 text-xs text-destructive">{(deleteMutation.error as Error).message}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
