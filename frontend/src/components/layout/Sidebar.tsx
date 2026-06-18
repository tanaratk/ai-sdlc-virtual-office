import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FolderOpen,
  Upload,
  Bot,
  FileText,
  GitBranch,
  Building2,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/projects", icon: FolderOpen, label: "Projects" },
  { to: "/intake", icon: Upload, label: "Requirement Intake" },
  { to: "/agents", icon: Bot, label: "Agent Console" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/traceability", icon: GitBranch, label: "Traceability" },
  { to: "/office", icon: Building2, label: "Virtual Office" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const { pathname } = useLocation();

  return (
    <aside className="flex h-full w-56 flex-col border-r bg-white">
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-sm font-semibold text-primary">AI-SDLC Office</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            className={cn(
              "flex items-center gap-3 px-4 py-2 text-sm transition-colors hover:bg-accent",
              pathname === to
                ? "bg-accent font-medium text-primary"
                : "text-muted-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
