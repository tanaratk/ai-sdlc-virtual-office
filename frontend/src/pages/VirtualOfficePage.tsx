import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import type { SelectedAgentInfo } from '@/game/scenes/OfficeScene';

const STATUS_COLORS: Record<string, string> = {
  working: 'bg-indigo-100 text-indigo-700',
  done:    'bg-emerald-100 text-emerald-700',
  error:   'bg-red-100 text-red-700',
  waiting: 'bg-amber-100 text-amber-700',
  idle:    'bg-gray-100 text-gray-500',
};

export default function VirtualOfficePage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<SelectedAgentInfo | null>(null);

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

  // Close drawer on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedAgent(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="relative w-full" style={{ height: 'calc(100vh - 56px)' }}>
      {/* Phaser canvas container */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Glass drawer */}
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
                <span className="font-mono text-xs">{selectedAgent.model}</span>
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
