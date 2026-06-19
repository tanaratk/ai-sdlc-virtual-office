import { useState } from "react";
import { Monitor, GitBranch, ChevronDown, ChevronRight, Tag, User, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ScreenField {
  name: string;
  type: string;
  required: boolean;
  validation: string;
  description: string;
}

interface Screen {
  id: string;
  name: string;
  description: string;
  userRole: string;
  requirementRefs: string[];
  fields: ScreenField[];
  actions: string[];
  navigation: string[];
}

interface UserFlow {
  id: string;
  name: string;
  requirementRef: string;
  steps: string[];
}

interface ParsedScreenSpec {
  totalScreens: number;
  totalFlows: number;
  screens: Screen[];
  flows: UserFlow[];
}

// ── Parser ────────────────────────────────────────────────────────────────────

function parseScreenSpec(markdown: string): ParsedScreenSpec {
  const screens: Screen[] = [];
  const flows: UserFlow[] = [];

  // Extract totals from header
  const totalScreensMatch = markdown.match(/\*\*Total Screens:\*\*\s*(\d+)/);
  const totalFlowsMatch = markdown.match(/\*\*Total User Flows:\*\*\s*(\d+)/);

  // Split into sections
  const section2Start = markdown.indexOf("## 2. Screen Specifications");
  const section3Start = markdown.indexOf("## 3. User Interaction Flows");

  const screenSection =
    section2Start !== -1
      ? markdown.slice(section2Start, section3Start !== -1 ? section3Start : undefined)
      : "";

  const flowSection = section3Start !== -1 ? markdown.slice(section3Start) : "";

  // Parse screens — split on ### UI-
  const screenChunks = screenSection.split(/(?=###\s+UI-)/);
  for (const chunk of screenChunks) {
    const headerMatch = chunk.match(/###\s+(UI-\d+)\s*[–—-]+\s*(.+)/);
    if (!headerMatch) continue;

    const id = headerMatch[1].trim();
    const name = headerMatch[2].trim();

    const roleMatch = chunk.match(/\*\*User Role:\*\*\s*(.+)/);
    const refsMatch = chunk.match(/\*\*Requirement Refs:\*\*\s*(.+)/);

    // Description: text between header metadata and "**Fields:**"
    const descMatch = chunk.match(/\*\*Requirement Refs:\*\*[^\n]*\n+([^*\n][^*]*?)\n*\*\*Fields:/s);
    const description = descMatch ? descMatch[1].trim() : "";

    // Fields: rows from the markdown table
    const fields: ScreenField[] = [];
    const fieldTableMatch = chunk.match(/\| Field \| Type \|.*?\n\|[-|]+\|\n([\s\S]*?)(?=\n\*\*Actions|\n>)/);
    if (fieldTableMatch) {
      const rows = fieldTableMatch[1].split("\n").filter((r) => r.trim().startsWith("|"));
      for (const row of rows) {
        const cols = row.split("|").map((c) => c.trim()).filter(Boolean);
        if (cols.length >= 5) {
          fields.push({
            name: cols[0].replace(/`/g, ""),
            type: cols[1],
            required: cols[2].toLowerCase() === "yes",
            validation: cols[3] === "—" ? "" : cols[3],
            description: cols[4],
          });
        }
      }
    }

    // Actions
    const actionsMatch = chunk.match(/\*\*Actions:\*\*\n+([\s\S]*?)(?=\n\*\*Navigation)/);
    const actions: string[] = [];
    if (actionsMatch) {
      actionsMatch[1].match(/`([^`]+)`/g)?.forEach((m) => actions.push(m.replace(/`/g, "")));
    }

    // Navigation
    const navMatch = chunk.match(/\*\*Navigation:\*\*\n+([\s\S]*?)(?=\n---|\n###|$)/);
    const navigation: string[] = [];
    if (navMatch) {
      navMatch[1]
        .split("\n")
        .filter((l) => l.trim().startsWith("-"))
        .forEach((l) => navigation.push(l.replace(/^-\s*/, "").trim()));
    }

    screens.push({
      id,
      name,
      description,
      userRole: roleMatch ? roleMatch[1].trim() : "",
      requirementRefs: refsMatch
        ? refsMatch[1]
            .split(",")
            .map((r) => r.trim())
            .filter(Boolean)
        : [],
      fields,
      actions,
      navigation,
    });
  }

  // Parse flows — split on ### FLOW-
  const flowChunks = flowSection.split(/(?=###\s+FLOW-)/);
  for (const chunk of flowChunks) {
    const headerMatch = chunk.match(/###\s+(FLOW-\d+)(?:\s*[✦·]\s*([^\s—–-][^—–]*?))?\s*[—–-]+\s*(.+)/);
    if (!headerMatch) continue;

    const id = headerMatch[1].trim();
    const reqRef = headerMatch[2]?.trim() ?? "";
    const name = headerMatch[3].trim();

    const steps: string[] = chunk
      .split("\n")
      .filter((l) => /^\d+\./.test(l.trim()))
      .map((l) => l.trim());

    flows.push({ id, name, requirementRef: reqRef, steps });
  }

  return {
    totalScreens: totalScreensMatch ? parseInt(totalScreensMatch[1]) : screens.length,
    totalFlows: totalFlowsMatch ? parseInt(totalFlowsMatch[1]) : flows.length,
    screens,
    flows,
  };
}

// ── Field type badge ──────────────────────────────────────────────────────────

const FIELD_TYPE_COLORS: Record<string, string> = {
  text: "bg-blue-50 text-blue-700",
  textarea: "bg-blue-50 text-blue-700",
  number: "bg-purple-50 text-purple-700",
  date: "bg-orange-50 text-orange-700",
  dropdown: "bg-teal-50 text-teal-700",
  checkbox: "bg-yellow-50 text-yellow-700",
  file: "bg-pink-50 text-pink-700",
  password: "bg-red-50 text-red-700",
};

function FieldTypeBadge({ type }: { type: string }) {
  return (
    <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-mono font-medium", FIELD_TYPE_COLORS[type] ?? "bg-gray-100 text-gray-600")}>
      {type}
    </span>
  );
}

// ── Screen Card ───────────────────────────────────────────────────────────────

function ScreenCard({ screen }: { screen: Screen }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-muted/30"
      >
        <Monitor className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-muted-foreground">{screen.id}</span>
            <span className="text-sm font-semibold">{screen.name}</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {screen.fields.length} fields
            </span>
          </div>
          <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
            {screen.userRole && (
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {screen.userRole}
              </span>
            )}
            {screen.requirementRefs.length > 0 && (
              <span className="flex items-center gap-1">
                <Tag className="h-3 w-3" />
                {screen.requirementRefs.join(", ")}
              </span>
            )}
          </div>
          {!expanded && screen.description && (
            <p className="mt-1 text-xs text-muted-foreground line-clamp-1">{screen.description}</p>
          )}
        </div>
        {expanded ? (
          <ChevronDown className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
        )}
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="border-t px-4 py-4 space-y-4">
          {screen.description && (
            <p className="text-sm text-muted-foreground">{screen.description}</p>
          )}

          {/* Fields */}
          {screen.fields.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Input Fields
              </h4>
              <div className="overflow-hidden rounded-md border">
                <table className="w-full text-xs">
                  <thead className="bg-muted/30">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium">Field</th>
                      <th className="px-3 py-2 text-left font-medium">Type</th>
                      <th className="px-3 py-2 text-left font-medium">Req</th>
                      <th className="px-3 py-2 text-left font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {screen.fields.map((f) => (
                      <tr key={f.name} className="hover:bg-muted/10">
                        <td className="px-3 py-2 font-mono">{f.name}</td>
                        <td className="px-3 py-2">
                          <FieldTypeBadge type={f.type} />
                        </td>
                        <td className="px-3 py-2">
                          {f.required ? (
                            <span className="text-red-500">●</span>
                          ) : (
                            <span className="text-muted-foreground">○</span>
                          )}
                        </td>
                        <td className="px-3 py-2 text-muted-foreground">{f.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Actions + Navigation side by side */}
          <div className="grid grid-cols-2 gap-4">
            {screen.actions.length > 0 && (
              <div>
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Actions
                </h4>
                <div className="space-y-1">
                  {screen.actions.map((a) => (
                    <div key={a} className="rounded-md bg-primary/5 px-2.5 py-1.5 text-xs font-medium text-primary">
                      {a}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {screen.navigation.length > 0 && (
              <div>
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Navigates To
                </h4>
                <div className="space-y-1">
                  {screen.navigation.map((n) => (
                    <div key={n} className="flex items-center gap-1 text-xs text-muted-foreground">
                      <ArrowRight className="h-3 w-3 flex-shrink-0" />
                      {n}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Flow Card ─────────────────────────────────────────────────────────────────

function FlowCard({ flow }: { flow: UserFlow }) {
  return (
    <div className="rounded-lg border bg-white p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground">{flow.id}</span>
            <span className="text-sm font-semibold">{flow.name}</span>
          </div>
          {flow.requirementRef && (
            <span className="mt-1 inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Tag className="h-3 w-3" />
              {flow.requirementRef}
            </span>
          )}
        </div>
        <span className="flex-shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {flow.steps.length} steps
        </span>
      </div>

      <ol className="space-y-1.5">
        {flow.steps.map((step, i) => (
          <li key={i} className="flex gap-2.5 text-sm">
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">
              {i + 1}
            </span>
            <span className="text-muted-foreground leading-snug pt-0.5">
              {step.replace(/^\d+\.\s*/, "")}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface ScreenSpecViewerProps {
  markdown: string;
}

export function ScreenSpecViewer({ markdown }: ScreenSpecViewerProps) {
  const [tab, setTab] = useState<"screens" | "flows">("screens");
  const data = parseScreenSpec(markdown);

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-lg border bg-white px-4 py-2.5">
          <Monitor className="h-4 w-4 text-primary" />
          <div>
            <p className="text-lg font-bold leading-none">{data.totalScreens}</p>
            <p className="text-xs text-muted-foreground">Screens</p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-lg border bg-white px-4 py-2.5">
          <GitBranch className="h-4 w-4 text-primary" />
          <div>
            <p className="text-lg font-bold leading-none">{data.totalFlows}</p>
            <p className="text-xs text-muted-foreground">User Flows</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg border bg-muted/30 p-1 w-fit">
        <button
          onClick={() => setTab("screens")}
          className={cn(
            "rounded-md px-4 py-1.5 text-sm font-medium transition-colors",
            tab === "screens" ? "bg-white shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Monitor className="inline h-3.5 w-3.5 mr-1.5" />
          Screens
        </button>
        <button
          onClick={() => setTab("flows")}
          className={cn(
            "rounded-md px-4 py-1.5 text-sm font-medium transition-colors",
            tab === "flows" ? "bg-white shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <GitBranch className="inline h-3.5 w-3.5 mr-1.5" />
          User Flows
        </button>
      </div>

      {/* Content */}
      {tab === "screens" && (
        <div className="space-y-2">
          {data.screens.length === 0 ? (
            <p className="text-sm text-muted-foreground">No screens parsed.</p>
          ) : (
            data.screens.map((screen) => <ScreenCard key={screen.id} screen={screen} />)
          )}
        </div>
      )}

      {tab === "flows" && (
        <div className="space-y-3">
          {data.flows.length === 0 ? (
            <p className="text-sm text-muted-foreground">No user flows parsed.</p>
          ) : (
            data.flows.map((flow) => <FlowCard key={flow.id} flow={flow} />)
          )}
        </div>
      )}
    </div>
  );
}
