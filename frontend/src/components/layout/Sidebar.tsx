import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FolderOpen,
  Upload,
  Bot,
  FileText,
  GitBranch,
  Building2,
  Activity,
  Users,
  Cpu,
  Radio,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const baseNavItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/projects", icon: FolderOpen, label: "Projects" },
  { to: "/intake", icon: Upload, label: "Requirement Intake" },
  { to: "/agents", icon: Bot, label: "Agent Manager" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/traceability", icon: GitBranch, label: "Traceability" },
  { to: "/office", icon: Building2, label: "Virtual Office" },
  { to: "/monitoring", icon: Activity, label: "Monitoring" },
  { to: "/settings", icon: Cpu, label: "LLM Management" },
];

const adminNavItems = [
  { to: "/users", icon: Users, label: "User Management" },
  { to: "/admin/projects", icon: FolderOpen, label: "Project Management" },
  { to: "/admin/pipeline", icon: Radio, label: "Pipeline Monitor" },
];

const bottomNavItems: { to: string; icon: React.ElementType; label: string }[] = [];

export function Sidebar() {
  const { pathname } = useLocation();
  const { user } = useAuth();

  const isActive = (to: string) =>
    to === "/" ? pathname === "/" : pathname.startsWith(to);

  const navLink = ({ to, icon: Icon, label }: { to: string; icon: React.ElementType; label: string }) => (
    <Link
      key={to}
      to={to}
      className={cn(
        "flex items-center gap-3 px-4 py-2 text-sm transition-colors hover:bg-accent",
        isActive(to)
          ? "bg-accent font-medium text-primary"
          : "text-muted-foreground"
      )}
    >
      <Icon className="h-4 w-4" />
      {label}
    </Link>
  );

  return (
    <aside className="flex h-full w-56 flex-col border-r bg-white">
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-sm font-semibold text-primary">AI-SDLC Office</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {baseNavItems.map(navLink)}
        {user?.role === "admin" && (
          <>
            <div className="mx-4 my-2 border-t" />
            {adminNavItems.map(navLink)}
          </>
        )}
      </nav>
      <div className="border-t py-2">
        {bottomNavItems.map(navLink)}
      </div>
    </aside>
  );
}
