import { Link, Outlet, useParams, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectApi } from "@/services/projectApi";
import { cn } from "@/lib/utils";

const TABS = [
  { label: "Overview",     path: "" },
  { label: "Requirements", path: "intake" },
  { label: "Pipeline",     path: "agents" },
  { label: "Documents",    path: "documents" },
  { label: "Code",         path: "generated-code" },
  { label: "QA",           path: "qa",          disabled: true },
  { label: "Traceability", path: "traceability" },
  { label: "Deploy",       path: "deploy",       disabled: true },
  { label: "Monitoring",   path: "office" },
];

export default function ProjectLayout() {
  const { projectId } = useParams<{ projectId: string }>();
  const { pathname } = useLocation();

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const base = `/projects/${projectId}`;

  const activeLabel = (() => {
    for (const tab of [...TABS].reverse()) {
      const fullPath = tab.path ? `${base}/${tab.path}` : base;
      if (tab.path ? pathname.startsWith(fullPath) : pathname === base) {
        return tab.label;
      }
    }
    return "Overview";
  })();

  return (
    // -mx-6 -mt-6 breaks out of AppLayout's p-6 so the header/tabs are flush with the edge
    <div className="flex flex-col min-h-full -mx-6 -mt-6">
      {/* Project header */}
      <div className="border-b bg-white px-6 pt-4 pb-0">
        <p className="text-xs text-muted-foreground mb-0.5">Project</p>
        <h2 className="text-base font-semibold">{project?.name ?? "Loading…"}</h2>

        {/* Tab bar */}
        <div className="flex gap-0 mt-3 -mb-px overflow-x-auto">
          {TABS.map((tab) => {
            const fullPath = tab.path ? `${base}/${tab.path}` : base;
            const isActive = activeLabel === tab.label;

            if (tab.disabled) {
              return (
                <span
                  key={tab.label}
                  className="whitespace-nowrap px-4 py-2.5 text-sm text-muted-foreground/40 cursor-not-allowed border-b-2 border-transparent"
                >
                  {tab.label}
                </span>
              );
            }

            return (
              <Link
                key={tab.label}
                to={fullPath}
                className={cn(
                  "whitespace-nowrap px-4 py-2.5 text-sm transition-colors border-b-2",
                  isActive
                    ? "border-primary text-primary font-medium"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Tab content */}
      <div className="flex-1 p-6">
        <Outlet />
      </div>
    </div>
  );
}
