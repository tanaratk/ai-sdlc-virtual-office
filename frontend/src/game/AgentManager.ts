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

export interface AgentInfo {
  status: string;
  model: string;
  provider: string;
  current_task: string;  // step name currently being executed, "" when idle
}

export interface PipelineEvent {
  type: 'pipeline_event';
  event: 'step_running' | 'step_completed' | 'step_failed' | 'step_skipped';
  step_name: string;
  project_name: string;
  project_id: string;
  timestamp: string;
}

/** Simple map used by the legacy poller (role → status string). */
export type AgentStatusMap = Record<string, string>;

/** Richer map from WebSocket (role → {status, model, provider}). */
export type AgentInfoMap = Record<string, AgentInfo>;

// ── WebSocket client — replaces the HTTP poller ──────────────────────────────

export class AgentStatusWS {
  private ws: WebSocket | null = null;
  private stopped = false;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private onUpdate: (info: AgentInfoMap) => void) {}

  start() {
    this.stopped = false;
    this._connect();
  }

  stop() {
    this.stopped = true;
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
    this.ws = null;
  }

  private _connect() {
    if (this.stopped) return;
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    // In dev Vite proxies /ws → ws://localhost:8000, in prod use same host/port
    const url = `${proto}//${location.host}/ws/office`;

    try {
      this.ws = new WebSocket(url);
    } catch (e) {
      console.warn('[AgentStatusWS] Failed to construct WebSocket:', e);
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      console.log('[AgentStatusWS] connected');
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const msg = JSON.parse(event.data as string) as { type: string; data: AgentInfoMap };
        if (msg.type === 'agent_statuses') {
          this.onUpdate(msg.data);
        }
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onerror = () => {
      // Error is followed by onclose — let onclose handle reconnect
    };

    this.ws.onclose = () => {
      if (!this.stopped) {
        console.log('[AgentStatusWS] disconnected — reconnecting in 3s');
        this._scheduleReconnect();
      }
    };
  }

  private _scheduleReconnect() {
    if (this.stopped) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this._connect();
    }, 3000);
  }
}

// ── Legacy HTTP poller — kept as fallback reference ──────────────────────────
// Replaced by AgentStatusWS above. Left here in case WebSocket is unavailable.

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
      const res = await fetch('/api/v1/agents');
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
