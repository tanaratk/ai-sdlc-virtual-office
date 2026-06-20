import { Link, Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const PAGE_TITLES: Record<string, string> = {
  "/":              "Dashboard",
  "/projects":      "Projects",
  "/intake":        "Requirements",
  "/agents":        "Agents",
  "/documents":     "Documents",
  "/pipeline-runs": "Pipeline Runs",
  "/code-workspace":"Code Workspace",
  "/traceability":  "Traceability",
  "/office":        "Virtual Office",
  "/monitoring":    "Monitoring",
  "/settings":      "AI Model Settings",
  "/rag":           "RAG Knowledge Base",
  "/mcp":           "Tool Registry",
  "/profile":       "Profile",
  "/users":         "User Management",
};

export function AppLayout() {
  const { pathname } = useLocation();
  const parts = pathname.split("/").filter(Boolean);

  const isNewProject = parts[0] === "projects" && parts[1] === "new";
  const isProjectRoute =
    parts[0] === "projects" && parts.length >= 2 && parts[1] !== "new";

  const base = "/" + (parts[0] ?? "");
  const title = PAGE_TITLES[base] ?? "AI-SDLC Working Office";

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar title={isProjectRoute ? "Project Workspace" : title} />

        {/* Breadcrumb — only for New Project */}
        {isNewProject && (
          <div className="flex items-center gap-2 border-b bg-muted/30 px-6 py-2 text-xs text-muted-foreground">
            <Link to="/projects" className="hover:text-foreground">
              Projects
            </Link>
            <span>/</span>
            <span className="text-foreground font-medium">New Project</span>
          </div>
        )}

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
