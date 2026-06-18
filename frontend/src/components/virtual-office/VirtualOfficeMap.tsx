import type { Agent } from "@/types/agent";
import { AgentAvatar } from "./AgentAvatar";

const ZONES = [
  "requirement_room",
  "gap_analysis_room",
  "ba_room",
  "sa_room",
  "ux_studio",
  "developer_zone",
  "qa_lab",
  "change_impact_room",
  "documentation_room",
  "pm_room",
];

const ZONE_LABELS: Record<string, string> = {
  requirement_room: "Requirement",
  gap_analysis_room: "Gap Analysis",
  ba_room: "BA",
  sa_room: "Architect",
  ux_studio: "UX Studio",
  developer_zone: "Developer",
  qa_lab: "QA Lab",
  change_impact_room: "Change Impact",
  documentation_room: "Documentation",
  pm_room: "PM",
};

interface VirtualOfficeMapProps {
  agents: Agent[];
}

export function VirtualOfficeMap({ agents }: VirtualOfficeMapProps) {
  const agentsByZone = agents.reduce<Record<string, Agent[]>>((acc, agent) => {
    const zone = agent.current_zone ?? "unknown";
    acc[zone] = acc[zone] ?? [];
    acc[zone].push(agent);
    return acc;
  }, {});

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
      {ZONES.map((zone) => (
        <div
          key={zone}
          className="flex flex-col gap-2 rounded-lg border bg-accent/40 p-3 min-h-[80px]"
        >
          <p className="text-xs font-medium text-muted-foreground">
            {ZONE_LABELS[zone] ?? zone}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {(agentsByZone[zone] ?? []).map((agent) => (
              <AgentAvatar key={agent.id} agent={agent} size="sm" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
