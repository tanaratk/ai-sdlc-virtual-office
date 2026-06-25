import { useEffect, useRef, useState } from 'react';
import { Activity, Building2, X } from 'lucide-react';
import type { SelectedAgentInfo } from '@/game/scenes/OfficeScene';
import type { PipelineEvent } from '@/game/AgentManager';

const STATUS_COLORS: Record<string, string> = {
  working: 'bg-blue-100 text-blue-700',
  done: 'bg-emerald-100 text-emerald-700',
  error: 'bg-red-100 text-red-700',
  waiting: 'bg-amber-100 text-amber-700',
  idle: 'bg-slate-100 text-slate-500',
};

const EVENT_COLORS: Record<string, string> = {
  step_running: 'text-blue-300',
  step_completed: 'text-emerald-300',
  step_failed: 'text-red-300',
  step_skipped: 'text-slate-400',
};

const EVENT_ICONS: Record<string, string> = {
  step_running: 'RUN',
  step_completed: 'OK',
  step_failed: 'ERR',
  step_skipped: 'SKIP',
};

const MAX_EVENTS = 50;

export default function VirtualOfficePage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<SelectedAgentInfo | null>(null);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [showFeed, setShowFeed] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;
    let game: { destroy: (removeCanvas: boolean) => void } | null = null;
    let active = true;

    import('@/game/config').then(({ createOfficeGame }) => {
      if (!active || !containerRef.current) return;
      game = createOfficeGame(containerRef.current, setSelectedAgent);
    });

    return () => {
      active = false;
      game?.destroy(true);
    };
  }, []);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let stopped = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      if (stopped) return;
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(`${proto}//${location.host}/ws/office`);

      ws.onmessage = (e: MessageEvent) => {
        try {
          const msg = JSON.parse(e.data as string) as { type: string } & PipelineEvent;
          if (msg.type === 'pipeline_event') {
            setEvents((prev) => [msg as PipelineEvent, ...prev].slice(0, MAX_EVENTS));
          }
        } catch {
          // Ignore malformed websocket messages.
        }
      };

      ws.onclose = () => {
        if (!stopped) reconnectTimer = setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedAgent(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div
      className="grid w-full grid-cols-[minmax(0,1fr)_20rem] overflow-hidden rounded-lg border bg-slate-950 shadow-sm"
      style={{ height: 'calc(100vh - 8rem)' }}
    >
      <div className="relative min-w-0 overflow-hidden">
        <div className="absolute left-3 top-3 z-10 max-w-72 rounded-md border border-white/10 bg-slate-950/75 px-3 py-2 text-white shadow-lg backdrop-blur-md">
          <div className="flex items-center gap-2">
            <Building2 className="h-3.5 w-3.5 text-blue-300" />
            <p className="text-xs font-semibold">AI-SDLC Pixel Office</p>
          </div>
          <p className="mt-0.5 text-[10px] text-slate-400">
            Live rooms, walking agents, and status bubbles.
          </p>
        </div>

        <div ref={containerRef} className="h-full w-full" />

        {selectedAgent && (
          <div className="absolute bottom-4 left-4 z-20 flex w-80 flex-col rounded-lg border bg-white/90 shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between border-b px-4 py-3">
              <h3 className="text-sm font-semibold">Agent Detail</h3>
              <button
                onClick={() => setSelectedAgent(null)}
                className="text-muted-foreground hover:text-foreground"
                aria-label="Close agent detail"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-4 px-4 py-4">
              <div>
                <p className="text-lg font-semibold leading-tight">{selectedAgent.name}</p>
                <p className="mt-0.5 font-mono text-xs text-muted-foreground">{selectedAgent.role}</p>
              </div>

              <div className="space-y-2">
                <Row label="Status">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[selectedAgent.status] ?? STATUS_COLORS.idle}`}>
                    {selectedAgent.status}
                  </span>
                </Row>
                <Row label="Model">
                  <span className="font-mono text-xs">{selectedAgent.model || '-'}</span>
                </Row>
              </div>
            </div>

            <div className="border-t px-4 py-3 text-xs text-muted-foreground">
              Click another agent to switch. Press Esc to close.
            </div>
          </div>
        )}
      </div>

      <aside className="min-w-0 border-l border-white/10 bg-slate-950/95">
        <div className="flex h-full flex-col overflow-hidden">
          <button
            onClick={() => setShowFeed((v) => !v)}
            className="flex w-full items-center gap-2 border-b border-white/10 px-4 py-3 text-xs font-semibold text-slate-300 hover:text-white"
          >
            <Activity className="h-3.5 w-3.5" />
            Agent Feed
            <span className="ml-auto text-slate-500">{events.length} entries</span>
          </button>

          {showFeed && (
            <div className="min-h-0 flex-1 overflow-y-auto divide-y divide-white/5">
              {events.length === 0 ? (
                <p className="px-4 py-4 text-xs italic text-slate-500">
                  No pipeline activity yet. Run a pipeline to see events here.
                </p>
              ) : (
                events.map((ev, index) => (
                  <div key={`${ev.timestamp}-${index}`} className="flex items-start gap-3 px-4 py-3">
                    <span className={`mt-0.5 rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-bold ${EVENT_COLORS[ev.event] ?? 'text-slate-400'}`}>
                      {EVENT_ICONS[ev.event] ?? 'LOG'}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs leading-tight text-slate-200">
                        {ev.step_name.replace(/_/g, ' ')}
                      </p>
                      <p className="truncate text-[10px] text-slate-500">{ev.project_name}</p>
                    </div>
                    <span className="shrink-0 text-[10px] text-slate-600">
                      {new Date(ev.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                      })}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
