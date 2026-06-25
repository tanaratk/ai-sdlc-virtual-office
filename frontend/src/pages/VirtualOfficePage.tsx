import { useEffect, useRef, useState } from 'react';
import { X, Activity } from 'lucide-react';
import type { SelectedAgentInfo } from '@/game/scenes/OfficeScene';
import type { PipelineEvent } from '@/game/AgentManager';

const STATUS_COLORS: Record<string, string> = {
  working: 'bg-indigo-100 text-indigo-700',
  done:    'bg-emerald-100 text-emerald-700',
  error:   'bg-red-100 text-red-700',
  waiting: 'bg-amber-100 text-amber-700',
  idle:    'bg-gray-100 text-gray-500',
};

const EVENT_COLORS: Record<string, string> = {
  step_running:   'text-indigo-400',
  step_completed: 'text-emerald-400',
  step_failed:    'text-red-400',
  step_skipped:   'text-gray-400',
};

const EVENT_ICONS: Record<string, string> = {
  step_running:   '⚙',
  step_completed: '✓',
  step_failed:    '✗',
  step_skipped:   '⤵',
};

const MAX_EVENTS = 20;

export default function VirtualOfficePage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<SelectedAgentInfo | null>(null);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [showFeed, setShowFeed] = useState(true);

  // ── Phaser game ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;
    let game: { destroy: (b: boolean) => void } | null = null;
    let active = true;

    import('@/game/config').then(({ createOfficeGame }) => {
      if (!active || !containerRef.current) return;
      game = createOfficeGame(containerRef.current, (info) => {
        setSelectedAgent(info);
      });
    });

    return () => {
      active = false;
      game?.destroy(true);
    };
  }, []);

  // ── Activity feed WebSocket (separate connection for pipeline events) ──────
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
        } catch { /* ignore */ }
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

  // ── Close drawer on Escape ────────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedAgent(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="relative w-full" style={{ height: 'calc(100vh - 56px)' }}>
      {/* Phaser canvas */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Activity Feed — bottom-left overlay */}
      <div className="absolute bottom-3 left-3 z-10 w-72">
        <div className="rounded-xl border bg-gray-950/85 backdrop-blur-md shadow-xl overflow-hidden">
          <button
            onClick={() => setShowFeed((v) => !v)}
            className="flex items-center gap-2 w-full px-3 py-2 text-xs font-semibold text-gray-300 hover:text-white border-b border-white/10"
          >
            <Activity className="h-3 w-3" />
            Pipeline Activity
            <span className="ml-auto text-gray-500">{showFeed ? '▾' : '▸'}</span>
          </button>

          {showFeed && (
            <div className="max-h-52 overflow-y-auto divide-y divide-white/5">
              {events.length === 0 ? (
                <p className="px-3 py-3 text-xs text-gray-500 italic">
                  No pipeline activity yet. Run a pipeline to see events.
                </p>
              ) : (
                events.map((ev, i) => (
                  <div key={i} className="flex items-start gap-2 px-3 py-2">
                    <span className={`text-xs mt-0.5 font-bold ${EVENT_COLORS[ev.event] ?? 'text-gray-400'}`}>
                      {EVENT_ICONS[ev.event] ?? '·'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-200 leading-tight truncate">
                        {ev.step_name.replace(/_/g, ' ')}
                      </p>
                      <p className="text-[10px] text-gray-500 truncate">{ev.project_name}</p>
                    </div>
                    <span className="text-[10px] text-gray-600 shrink-0">
                      {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Agent detail drawer — right side */}
      {selectedAgent && (
        <div className="absolute right-0 top-0 h-full w-80 border-l bg-white/80 backdrop-blur-md shadow-xl flex flex-col z-10">
          <div className="flex items-center justify-between px-4 py-3 border-b">
            <h3 className="text-sm font-semibold">Agent Detail</h3>
            <button
              onClick={() => setSelectedAgent(null)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            <div>
              <p className="text-lg font-semibold leading-tight">{selectedAgent.name}</p>
              <p className="text-xs text-muted-foreground font-mono mt-0.5">{selectedAgent.role}</p>
            </div>

            <div className="space-y-2">
              <Row label="Status">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[selectedAgent.status] ?? STATUS_COLORS.idle}`}>
                  {selectedAgent.status}
                </span>
              </Row>
              <Row label="Model">
                <span className="font-mono text-xs">{selectedAgent.model || '—'}</span>
              </Row>
            </div>
          </div>

          <div className="px-4 py-3 border-t text-xs text-muted-foreground">
            Click another agent to switch · Esc to close
          </div>
        </div>
      )}
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
