import type { Agent } from "@/types/agent";
import type { PipelineRun, PipelineStep } from "@/types/workflow";
import { RoomCard, type RoomConfig } from "./RoomCard";

const ROOMS: RoomConfig[] = [
  { zone: "requirement_room",   label: "Requirement",    stepNames: ["requirement_summary", "gap_analysis"], navPath: "intake" },
  { zone: "gap_analysis_room",  label: "Gap Analysis",   stepNames: ["gap_analysis"],                       navPath: "intake" },
  { zone: "ba_room",            label: "BA",             stepNames: ["ba_documents"],                        navPath: "documents" },
  { zone: "sa_room",            label: "Architect",      stepNames: ["sa_documents"],                        navPath: "documents" },
  { zone: "ux_studio",          label: "UX Studio",      stepNames: ["ux_documents"],                        navPath: "documents" },
  { zone: "developer_zone",     label: "Developer",      stepNames: ["dev_tasks"],                           navPath: "documents" },
  { zone: "qa_lab",             label: "QA Lab",         stepNames: ["test_cases"],                          navPath: "documents" },
  { zone: "traceability_room",  label: "Traceability",   stepNames: [],                                      navPath: "traceability" },
  { zone: "change_impact_room", label: "Change Impact",  stepNames: ["change_impact"],                       navPath: "change-impact" },
  { zone: "control_room",       label: "Control Room",   stepNames: [],                                      navPath: "agents" },
];

interface VirtualOfficeMapProps {
  agents: Agent[];
  projectId?: string;
  activeRun?: PipelineRun | null;
  steps?: PipelineStep[];
  onAgentClick?: (agent: Agent) => void;
}

export function VirtualOfficeMap({
  agents,
  projectId,
  activeRun,
  steps,
  onAgentClick,
}: VirtualOfficeMapProps) {
  const agentsByZone = agents.reduce<Record<string, Agent[]>>((acc, agent) => {
    const zone = agent.current_zone ?? agent.home_zone ?? "control_room";
    acc[zone] = acc[zone] ?? [];
    acc[zone].push(agent);
    return acc;
  }, {});

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
      {ROOMS.map((room) => (
        <RoomCard
          key={room.zone}
          room={room}
          agents={agentsByZone[room.zone] ?? []}
          projectId={projectId}
          activeRun={activeRun}
          steps={steps}
          onAgentClick={onAgentClick}
        />
      ))}
    </div>
  );
}
