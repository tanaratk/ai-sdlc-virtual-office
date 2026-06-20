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
  Code2,
  Database,
  Wrench,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

type NavItem = { to: string; icon: React.ElementType; label: string };

const mainItems: NavItem[] = [
  { to: "/",        icon: LayoutDashboard, label: "Dashboard" },
  { to: "/projects",icon: FolderOpen,      label: "Projects" },
  { to: "/intake",  icon: Upload,          label: "Requirements" },
];

const deliveryItems: NavItem[] = [
  { to: "/pipeline-runs",   icon: Radio,     label: "Pipeline Runs" },
  { to: "/documents",       icon: FileText,  label: "Documents" },
  { to: "/code-workspace",  icon: Code2,     label: "Code Workspace" },
  { to: "/traceability",    icon: GitBranch, label: "Traceability" },
  { to: "/office",          icon: Building2, label: "Virtual Office" },
  { to: "/monitoring",      icon: Activity,  label: "Monitoring" },
];

const platformItems: NavItem[] = [
  { to: "/agents",   icon: Bot,      label: "Agents" },
  { to: "/rag",      icon: Database, label: "RAG Knowledge Base" },
  { to: "/mcp",      icon: Wrench,   label: "Tool Registry" },
  { to: "/settings", icon: Cpu,      label: "AI Model Settings" },
];

const adminItems: NavItem[] = [
  { to: "/users",         icon: Users,      label: "User Management" },
  { to: "/admin/projects",icon: FolderOpen, label: "Project Management" },
];

export function Sidebar() {
  const { pathname } = useLocation();
  const { user } = useAuth();

  const isActive = (to: string) =>
    to === "/" ? pathname === "/" : pathname.startsWith(to);

  const NavLink = ({ to, icon: Icon, label }: NavItem) => (
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
      <Icon className="h-4 w-4 flex-shrink-0" />
      {label}
    </Link>
  );

  const SectionLabel = ({ label }: { label: string }) => (
    <p className="mx-4 mb-1 mt-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
      {label}
    </p>
  );

  return (
    <aside className="flex h-full w-56 flex-col border-r bg-white">
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-sm font-semibold text-primary">AI-SDLC Office</span>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        <SectionLabel label="Main" />
        {mainItems.map((item) => <NavLink key={item.to} {...item} />)}

        <SectionLabel label="Delivery" />
        {deliveryItems.map((item) => <NavLink key={item.to} {...item} />)}

        <SectionLabel label="AI Platform" />
        {platformItems.map((item) => <NavLink key={item.to} {...item} />)}

        {user?.role === "admin" && (
          <>
            <SectionLabel label="Administration" />
            {adminItems.map((item) => <NavLink key={item.to} {...item} />)}
          </>
        )}
      </nav>
    </aside>
  );
}
