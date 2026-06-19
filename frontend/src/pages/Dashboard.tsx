import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FolderOpen, Bot, Building2, Plus, GitBranch } from "lucide-react";
import { projectApi } from "@/services/projectApi";

const QUICK_LINKS = [
  { to: "/projects", icon: FolderOpen, label: "Projects", desc: "Manage all your SDLC projects" },
  { to: "/agents", icon: Bot, label: "Agent Console", desc: "Monitor AI agent activity" },
  { to: "/office", icon: Building2, label: "Virtual Office", desc: "2D office map with live agents" },
  { to: "/traceability", icon: GitBranch, label: "Traceability", desc: "Requirement → Document coverage" },
];

export default function Dashboard() {
  const { data } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list(),
  });

  const total = data?.total ?? 0;
  const active = data?.items.filter((p) => p.status === "active").length ?? 0;
  const completed = data?.items.filter((p) => p.status === "completed").length ?? 0;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold">Welcome to AI-SDLC Working Office</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Agentic Software Factory — AI agents collaborate through the full SDLC pipeline.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-muted-foreground">Total Projects</p>
          <p className="text-3xl font-semibold mt-1">{total}</p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-muted-foreground">Active</p>
          <p className="text-3xl font-semibold mt-1 text-green-600">{active}</p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-muted-foreground">Completed</p>
          <p className="text-3xl font-semibold mt-1 text-blue-600">{completed}</p>
        </div>
      </div>

      <div>
        <p className="text-sm font-medium mb-3">Quick Access</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_LINKS.map(({ to, icon: Icon, label, desc }) => (
            <Link
              key={to}
              to={to}
              className="flex gap-3 items-start rounded-lg border bg-white p-4 hover:border-primary transition-colors"
            >
              <Icon className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium">{label}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {total === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <FolderOpen className="mx-auto h-10 w-10 text-muted-foreground" />
          <p className="mt-3 text-sm font-medium">No projects yet</p>
          <p className="text-xs text-muted-foreground mt-1">
            Start by creating your first project and running the SDLC pipeline.
          </p>
          <Link
            to="/projects/new"
            className="mt-4 inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Plus className="h-4 w-4" />
            New Project
          </Link>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-medium">Recent Projects</p>
            <Link to="/projects" className="text-xs text-primary hover:underline">
              View all
            </Link>
          </div>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.slice(0, 6).map((project) => (
              <li key={project.id}>
                <Link
                  to={`/projects/${project.id}`}
                  className="block rounded-lg border bg-white p-4 hover:border-primary transition-colors"
                >
                  <p className="text-sm font-semibold truncate">{project.name}</p>
                  {project.description && (
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-1">
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
        </div>
      )}
    </div>
  );
}
