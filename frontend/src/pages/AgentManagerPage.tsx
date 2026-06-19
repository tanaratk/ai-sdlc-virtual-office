import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { agentApi } from "@/services/agentApi";
import { AgentCard } from "@/components/agent/AgentCard";
import { AgentDetailPanel } from "@/components/agent/AgentDetailPanel";

export default function AgentManagerPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    staleTime: 10_000,
  });

  const selectedAgent = agents.find((a) => a.id === selectedAgentId) ?? null;

  return (
    <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
      <aside className="space-y-2">
        <h3 className="text-sm font-semibold">Agents</h3>
        <p className="text-xs text-muted-foreground">Click an agent to view or configure</p>
        {isLoading && (
          <p className="text-sm text-muted-foreground py-2">Loading…</p>
        )}
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            isSelected={agent.id === selectedAgentId}
            onClick={() =>
              setSelectedAgentId(agent.id === selectedAgentId ? null : agent.id)
            }
          />
        ))}
      </aside>

      <main>
        {selectedAgent ? (
          <AgentDetailPanel
            agent={selectedAgent}
            onClose={() => setSelectedAgentId(null)}
          />
        ) : (
          <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">
            Select an agent from the list to view details and configure its LLM model.
          </div>
        )}
      </main>
    </div>
  );
}
