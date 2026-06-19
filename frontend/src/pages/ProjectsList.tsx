import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FolderOpen, Plus } from "lucide-react";
import { projectApi } from "@/services/projectApi";
import type { Project } from "@/types/project";

const STATUS_COLORS: Record<Project["status"], string> = {
  active: "bg-green-100 text-green-700",
  archived: "bg-muted text-muted-foreground",
  completed: "bg-blue-100 text-blue-700",
};

export default function ProjectsList() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Projects</h2>
        <Link
          to="/projects/new"
          className="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Project
        </Link>
      </div>

      {isLoading && (
        <p className="text-sm text-muted-foreground">Loading projects…</p>
      )}

      {isError && (
        <p className="text-sm text-destructive">Failed to load projects.</p>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded-lg border border-dashed p-10 text-center">
          <FolderOpen className="mx-auto h-8 w-8 text-muted-foreground" />
          <p className="mt-2 text-sm font-medium">No projects yet</p>
          <p className="text-xs text-muted-foreground">
            Create a project to begin the SDLC pipeline.
          </p>
          <Link
            to="/projects/new"
            className="mt-4 inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Plus className="h-3.5 w-3.5" />
            New Project
          </Link>
        </div>
      )}

      {data && data.items.length > 0 && (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((project) => (
            <li key={project.id}>
              <Link
                to={`/projects/${project.id}`}
                className="block rounded-lg border bg-white p-4 hover:border-primary transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-semibold truncate">{project.name}</p>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium flex-shrink-0 ${STATUS_COLORS[project.status]}`}
                  >
                    {project.status}
                  </span>
                </div>
                {project.description && (
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                    {project.description}
                  </p>
                )}
                <p className="mt-2 text-xs text-muted-foreground">
                  {new Date(project.created_at).toLocaleDateString()}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
