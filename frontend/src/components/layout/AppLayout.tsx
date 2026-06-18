import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/projects": "Projects",
  "/intake": "Requirement Intake",
  "/agents": "Agent Console",
  "/documents": "Documents",
  "/traceability": "Traceability",
  "/office": "Virtual Office",
  "/settings": "Settings",
};

export function AppLayout() {
  const { pathname } = useLocation();
  const base = "/" + pathname.split("/")[1];
  const title = PAGE_TITLES[base] ?? "AI-SDLC Working Office";

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
