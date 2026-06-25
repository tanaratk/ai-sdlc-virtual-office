import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FolderOpen,
  Bot,
  Building2,
  Radio,
  Cpu,
  Database,
  Plug,
  Users,
  GitBranch,
  Activity,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

type NavItem = { to: string; icon: React.ElementType; label: string };

const workspaceItems: NavItem[] = [
  { to: "/",         icon: LayoutDashboard, label: "Operations Hub" },
  { to: "/projects", icon: FolderOpen,      label: "Projects"       },
  { to: "/office",   icon: Building2,       label: "Virtual Office" },
];

const deliveryItems: NavItem[] = [
  { to: "/pipeline-runs", icon: Radio,     label: "Pipeline Control" },
  { to: "/documents",     icon: FileText,  label: "Documents"        },
  { to: "/traceability",  icon: GitBranch, label: "Traceability"     },
  { to: "/monitoring",    icon: Activity,  label: "Monitoring"       },
];

const systemItems: NavItem[] = [
  { to: "/agents",   icon: Bot,      label: "Agent Management" },
  { to: "/settings", icon: Cpu,      label: "AI Models"        },
  { to: "/rag",      icon: Database, label: "Knowledge Base"   },
  { to: "/mcp",      icon: Plug,     label: "Connectors"       },
];

const adminItems: NavItem[] = [
  { to: "/users",          icon: Users,    label: "Users"          },
  { to: "/admin/projects", icon: Settings, label: "Admin Projects" },
];

type SidebarProps = {
  collapsed: boolean;
  onToggle: () => void;
};

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { pathname } = useLocation();
  const { user } = useAuth();

  const isActive = (to: string) =>
    to === "/" ? pathname === "/" : pathname.startsWith(to);

  const NavLink = ({ to, icon: Icon, label }: NavItem) => (
    <Link
      key={to}
      to={to}
      title={collapsed ? label : undefined}
      className={cn(
        "flex items-center rounded-md py-2 text-sm transition-colors hover:bg-accent",
        collapsed
          ? "mx-2 justify-center px-2"
          : "mx-2 gap-3 px-3",
        isActive(to)
          ? "bg-accent font-medium text-primary"
          : "text-muted-foreground"
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {!collapsed && label}
    </Link>
  );

  const SectionLabel = ({ label }: { label: string }) =>
    collapsed ? (
      <hr className="mx-3 my-2 border-border/50" />
    ) : (
      <p className="mx-4 mb-1 mt-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
        {label}
      </p>
    );

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r bg-white transition-all duration-200",
        collapsed ? "w-14" : "w-64"
      )}
    >
      {collapsed ? (
        <div className="flex h-16 flex-col items-center justify-center gap-1 border-b">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-3.5 w-3.5" />
          </div>
          <button
            onClick={onToggle}
            className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            title="Expand sidebar"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      ) : (
        <div className="flex h-16 items-center border-b px-3 gap-2">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-4 w-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-foreground truncate">Agentic Software</p>
            <p className="text-[11px] text-muted-foreground truncate">Factory · agent workspace</p>
          </div>
          <button
            onClick={onToggle}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors flex-shrink-0"
            title="Collapse sidebar"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto py-2">
        <SectionLabel label="Workspace" />
        {workspaceItems.map((item) => <NavLink key={item.to} {...item} />)}

        <SectionLabel label="Delivery" />
        {deliveryItems.map((item) => <NavLink key={item.to} {...item} />)}

        <SectionLabel label="AI Platform" />
        {systemItems.map((item) => <NavLink key={item.to} {...item} />)}

        {user?.role === "admin" && (
          <>
            <SectionLabel label="Administration" />
            {adminItems.map((item) => <NavLink key={item.to} {...item} />)}
          </>
        )}
      </nav>

      {!collapsed && (
        <div className="border-t p-4">
          <div className="rounded-lg bg-secondary p-3 text-secondary-foreground">
            <p className="text-xs font-semibold">12-agent pipeline</p>
            <p className="mt-1 text-[11px] text-secondary-foreground/70">
              Business, design, delivery, review, deploy.
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
