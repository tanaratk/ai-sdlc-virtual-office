import { useQuery } from "@tanstack/react-query";
import { agentApi } from "@/services/agentApi";
import { VirtualOfficeMap } from "@/components/virtual-office/VirtualOfficeMap";

export default function VirtualOfficePage() {
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: agentApi.list,
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Virtual Office</h2>
      <p className="text-sm text-muted-foreground">
        2D Phaser.js office coming in MVP 4. Current view: agent zone status.
      </p>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading agents…</p>
      ) : (
        <VirtualOfficeMap agents={agents} />
      )}
    </div>
  );
}
