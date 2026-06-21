export interface AgentConfig {
  role: string;
  spriteKey: string;
  room: string;
  startTile: { tx: number; ty: number };
}

// Updated for 2-row layout:
// Row 1 (ty=2..16): Requirement(tx=2..19)  Meeting(tx=22..39)  Control(tx=42..59)
// Row 2 (ty=19..35): Developer(tx=2..28)   QA Lab(tx=31..59)
export const AGENT_CONFIG: AgentConfig[] = [
  { role: 'requirement-agent',        spriteKey: 'agent_REQ', room: 'Requirement Room', startTile: { tx: 7,  ty: 7  } },
  { role: 'gap-analysis-agent',       spriteKey: 'agent_GAP', room: 'Requirement Room', startTile: { tx: 14, ty: 10 } },
  { role: 'ba-agent',                 spriteKey: 'agent_BA',  room: 'Meeting Room',     startTile: { tx: 26, ty: 7  } },
  { role: 'architect-agent',          spriteKey: 'agent_AC',  room: 'Meeting Room',     startTile: { tx: 35, ty: 7  } },
  { role: 'ux-agent',                 spriteKey: 'agent_UX',  room: 'Meeting Room',     startTile: { tx: 31, ty: 11 } },
  { role: 'technical-design-agent',   spriteKey: 'agent_TD',  room: 'Meeting Room',     startTile: { tx: 26, ty: 11 } },
  { role: 'developer-agent',          spriteKey: 'agent_DA1', room: 'Developer Room',   startTile: { tx: 6,  ty: 24 } },
  { role: 'developer-agent-backend',  spriteKey: 'agent_DAB', room: 'Developer Room',   startTile: { tx: 11, ty: 24 } },
  { role: 'developer-agent-frontend', spriteKey: 'agent_DAF', room: 'Developer Room',   startTile: { tx: 16, ty: 24 } },
  { role: 'developer-agent-platform', spriteKey: 'agent_DAP', room: 'Developer Room',   startTile: { tx: 21, ty: 24 } },
  { role: 'code-review-agent',        spriteKey: 'agent_RV',  room: 'Developer Room',   startTile: { tx: 9,  ty: 30 } },
  { role: 'qa-agent',                 spriteKey: 'agent_QA',  room: 'QA Lab',           startTile: { tx: 36, ty: 24 } },
  { role: 'devops-agent',             spriteKey: 'agent_DEO', room: 'QA Lab',           startTile: { tx: 44, ty: 24 } },
  { role: 'monitoring-agent',         spriteKey: 'agent_MON', room: 'QA Lab',           startTile: { tx: 36, ty: 30 } },
  { role: 'documentation-agent',      spriteKey: 'agent_DOC', room: 'Control Room',     startTile: { tx: 46, ty: 7  } },
  { role: 'pm-agent',                 spriteKey: 'agent_PM',  room: 'Control Room',     startTile: { tx: 55, ty: 7  } },
  { role: 'change-impact-agent',      spriteKey: 'agent_CI',  room: 'Control Room',     startTile: { tx: 50, ty: 11 } },
];

export type AgentStatusMap = Record<string, string>;

export class AgentStatusPoller {
  private timer: ReturnType<typeof setInterval> | null = null;
  private lastStatuses: AgentStatusMap = {};

  constructor(private onUpdate: (statuses: AgentStatusMap) => void) {}

  start() {
    this.poll();
    this.timer = setInterval(() => this.poll(), 3000);
  }

  stop() {
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  private async poll() {
    try {
      const res = await fetch('/api/agents');
      if (!res.ok) return;
      const agents: { role: string; status: string }[] = await res.json();
      const statuses: AgentStatusMap = {};
      for (const a of agents) statuses[a.role] = a.status;

      const changed = Object.keys(statuses).some(
        (role) => statuses[role] !== this.lastStatuses[role]
      );
      if (changed) {
        this.lastStatuses = statuses;
        this.onUpdate(statuses);
      }
    } catch {
      // backend offline — ignore
    }
  }
}
