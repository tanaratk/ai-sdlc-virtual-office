import { Link, Outlet, useLocation } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/projects": "Projects",
  "/intake": "Requirement Intake",
  "/agents": "Agent Manager",
  "/documents": "Documents",
  "/traceability": "Traceability",
  "/office": "Virtual Office",
  "/monitoring": "Monitoring",
  "/settings": "LLM Management",
  "/profile": "Profile",
  "/users": "User Management",
};

const SUB_PAGE_LABELS: Record<string, string> = {
  intake: "Requirement Intake",
  agents: "Pipeline Console",
  documents: "Documents",
  traceability: "Traceability",
  office: "Virtual Office",
  "change-impact": "Change Impact",
  documentation: "Compile Docs",
  pm: "PM Summary",
  github: "GitHub",
  mcp: "MCP Tools",
  rag: "Knowledge Base",
};

export function AppLayout() {
  const { pathname } = useLocation();
  const parts = pathname.split("/").filter(Boolean);

  // Detect /projects/:projectId/:subpage
  const isProjectSubPage =
    parts[0] === "projects" &&
    parts.length >= 3 &&
    parts[1] !== "new";

  const isNewProject = parts[0] === "projects" && parts[1] === "new";

  const projectId = isProjectSubPage ? parts[1] : null;
  const subPage = isProjectSubPage ? parts[2] : null;

  const base = "/" + parts[0];
  let title = PAGE_TITLES[base] ?? "AI-SDLC Working Office";
  if (isProjectSubPage && subPage) {
    title = SUB_PAGE_LABELS[subPage] ?? subPage;
  } else if (isNewProject) {
    title = "New Project";
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar title={title} />

        {/* Project sub-page breadcrumb */}
        {(isProjectSubPage || isNewProject) && (
          <div className="flex items-center gap-2 border-b bg-muted/30 px-6 py-2 text-xs text-muted-foreground">
            <Link to="/projects" className="hover:text-foreground">
              Projects
            </Link>
            <span>/</span>
            {isProjectSubPage ? (
              <>
                <Link
                  to={`/projects/${projectId}`}
                  className="flex items-center gap-1 hover:text-foreground"
                >
                  <ArrowLeft className="h-3 w-3" />
                  Project
                </Link>
                <span>/</span>
                <span className="text-foreground font-medium">{title}</span>
              </>
            ) : (
              <span className="text-foreground font-medium">New Project</span>
            )}
          </div>
        )}

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
