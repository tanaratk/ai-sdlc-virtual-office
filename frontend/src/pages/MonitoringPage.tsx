import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Activity, Filter } from "lucide-react";
import { activityApi } from "@/services/activityApi";
import { projectApi } from "@/services/projectApi";

const EVENT_TYPE_LABELS: Record<string, string> = {
  task_started: "Task Started",
  task_completed: "Task Completed",
  task_failed: "Task Failed",
  agent_moved: "Agent Moved",
  document_created: "Document Created",
  document_approved: "Document Approved",
  document_rejected: "Document Rejected",
  pipeline_step_started: "Step Started",
  pipeline_step_completed: "Step Completed",
  handoff_sent: "Handoff",
  user_message: "User Message",
};

const EVENT_COLORS: Record<string, string> = {
  task_started: "bg-blue-100 text-blue-700",
  task_completed: "bg-green-100 text-green-700",
  task_failed: "bg-red-100 text-red-700",
  document_created: "bg-purple-100 text-purple-700",
  document_approved: "bg-green-100 text-green-700",
  document_rejected: "bg-red-100 text-red-700",
  pipeline_step_started: "bg-blue-100 text-blue-700",
  pipeline_step_completed: "bg-green-100 text-green-700",
  handoff_sent: "bg-yellow-100 text-yellow-700",
  user_message: "bg-gray-100 text-gray-700",
  agent_moved: "bg-gray-100 text-gray-600",
};

function TimeAgo({ iso }: { iso: string }) {
  const diff = Date.now() - new Date(iso).getTime();
  const secs = Math.floor(diff / 1000);
  const mins = Math.floor(secs / 60);
  const hours = Math.floor(mins / 60);

  let label: string;
  if (secs < 60) label = `${secs}s ago`;
  else if (mins < 60) label = `${mins}m ago`;
  else if (hours < 24) label = `${hours}h ago`;
  else label = new Date(iso).toLocaleDateString();

  return (
    <time
      dateTime={iso}
      title={new Date(iso).toLocaleString()}
      className="text-xs text-muted-foreground whitespace-nowrap"
    >
      {label}
    </time>
  );
}

export default function MonitoringPage() {
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { data: projectsData } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list(),
    staleTime: 30_000,
  });
  const projects = projectsData?.items ?? [];

  const {
    data: activityData,
    isLoading,
    isError,
    refetch,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ["activity", selectedProjectId, eventTypeFilter],
    queryFn: () =>
      activityApi.list(selectedProjectId, {
        limit: 100,
        event_type: eventTypeFilter || undefined,
      }),
    enabled: !!selectedProjectId,
    refetchInterval: autoRefresh ? 5000 : false,
  });

  const items = activityData?.items ?? [];

  return (
    <div className="space-y-4 max-w-4xl">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Activity Log
        </h2>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh (5s)
          </label>
          <button
            onClick={() => refetch()}
            disabled={!selectedProjectId}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground disabled:opacity-40"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs font-medium mb-1">Project</label>
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Select a project…</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="w-52">
          <label className="block text-xs font-medium mb-1">
            <Filter className="inline h-3 w-3 mr-1" />
            Event Type
          </label>
          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">All events</option>
            {Object.entries(EVENT_TYPE_LABELS).map(([val, label]) => (
              <option key={val} value={val}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Activity list */}
      {!selectedProjectId && (
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
          Select a project to see its activity log.
        </div>
      )}

      {selectedProjectId && isLoading && (
        <p className="text-sm text-muted-foreground py-4">Loading activity…</p>
      )}

      {selectedProjectId && isError && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/5 p-4">
          <p className="text-sm text-destructive">Failed to load activity log.</p>
        </div>
      )}

      {selectedProjectId && !isLoading && !isError && (
        <>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{activityData?.total ?? 0} events total · showing {items.length}</span>
            {dataUpdatedAt > 0 && (
              <span>Last updated: {new Date(dataUpdatedAt).toLocaleTimeString()}</span>
            )}
          </div>

          {items.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
              No activity found for this project.
            </div>
          ) : (
            <div className="rounded-lg border bg-white overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/30 text-xs text-muted-foreground">
                    <th className="px-4 py-2.5 text-left font-medium">Time</th>
                    <th className="px-4 py-2.5 text-left font-medium">Event</th>
                    <th className="px-4 py-2.5 text-left font-medium">Message</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {items.map((log) => {
                    const colorCls = EVENT_COLORS[log.event_type] ?? "bg-gray-100 text-gray-700";
                    return (
                      <tr key={log.id} className="hover:bg-muted/20">
                        <td className="px-4 py-2.5 align-top">
                          <TimeAgo iso={log.created_at} />
                        </td>
                        <td className="px-4 py-2.5 align-top">
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap ${colorCls}`}>
                            {EVENT_TYPE_LABELS[log.event_type] ?? log.event_type}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 align-top text-xs text-foreground/80 leading-relaxed">
                          {log.message}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
