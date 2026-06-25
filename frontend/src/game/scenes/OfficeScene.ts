import Phaser from 'phaser';
import { AGENT_CONFIG, AgentStatusWS, type AgentInfoMap } from '../AgentManager';

// ── Layout constants ──────────────────────────────────────────────────────────

const HDR_H      = 22;   // header bar height (px)
const GAP        = 12;   // gap between rooms
const MARGIN     = 12;   // edge margin
const WALK_SPEED = 55;   // px / sec

// LimeZu Premade Characters: 896×656 px → 56 cols × 41 rows @ 16×16 per frame
const FRAME_SIZE     = 16;
const SPRITE_COLS    = 56;   // 896 / 16 = 56 columns per row
const FRAMES_PER_DIR = 3;    // 3 walk frames per direction
const DIR_DOWN  = 0;
const DIR_LEFT  = 1;
const DIR_RIGHT = 2;
const DIR_UP    = 3;

// ── Colors ────────────────────────────────────────────────────────────────────

const ROOM_COLORS: Record<string, { floor: number; carpet: number; header: number }> = {
  'Requirement Room': { floor: 0xf5e6c8, carpet: 0xe8c99a, header: 0x6366f1 },
  'Meeting Room':     { floor: 0xd4edda, carpet: 0xa8d5b5, header: 0x10b981 },
  'Control Room':     { floor: 0xd0e8f0, carpet: 0x9ec5d4, header: 0x8b5cf6 },
  'Developer Room':   { floor: 0xddd5f0, carpet: 0xb5a8e8, header: 0x3b82f6 },
  'QA Lab':           { floor: 0xf0e8d0, carpet: 0xd4c49a, header: 0xf59e0b },
};

const ROOM_ICONS: Record<string, string> = {
  'Requirement Room': '📋', 'Meeting Room': '🤝', 'Control Room': '⚙️',
  'Developer Room': '💻',  'QA Lab': '🧪',
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface RoomLayout {
  name: string; icon: string;
  x: number; y: number; w: number; h: number;
  headerColor: number; floorColor: number; carpetColor: number;
}

interface AgentObj {
  role: string; spriteKey: string; room: RoomLayout;
  img:       Phaser.GameObjects.Image;
  labelBg:   Phaser.GameObjects.Rectangle;
  labelText: Phaser.GameObjects.Text;
  dot:       Phaser.GameObjects.Arc;
  bubble:    Phaser.GameObjects.Text | null;   // chat bubble shown on status change
  glow:      Phaser.GameObjects.Arc | null;
  pulseTween:  Phaser.Tweens.Tween | null;
  glowTween:   Phaser.Tweens.Tween | null;
  walkTween:   Phaser.Tweens.Tween | null;
  bubbleTween: Phaser.Tweens.Tween | null;
  walking:    boolean;
  animFrame:  number;
  animDir:    number;
  status:     string;
  model:      string;
  provider:   string;
}

const ROLE_ABBR: Record<string, string> = {
  'requirement-agent':        'REQ', 'gap-analysis-agent':       'GAP',
  'ba-agent':                 'BA',  'architect-agent':          'ARC',
  'ux-agent':                 'UX',  'technical-design-agent':   'TD',
  'developer-agent':          'DEV', 'developer-agent-backend':  'DEB',
  'developer-agent-frontend': 'DEF', 'developer-agent-platform': 'DEP',
  'code-review-agent':        'CRV', 'qa-agent':                 'QA',
  'devops-agent':             'OPS', 'monitoring-agent':         'MON',
  'documentation-agent':      'DOC', 'pm-agent':                 'PM',
  'change-impact-agent':      'CI',
};

// Human-readable labels for pipeline step names (shown in chat bubbles)
const STEP_LABELS: Record<string, string> = {
  requirement_summary: 'Analyzing requirements...',
  gap_analysis:        'Finding gaps...',
  ba_documents:        'Writing BRD & User Stories...',
  architecture:        'Designing architecture...',
  ux_design:           'Creating screen specs...',
  technical_design:    'Planning dev tasks...',
  code_generation:     'Generating code...',
  code_review:         'Reviewing code...',
  qa_testing:          'Writing test cases...',
  devops_pipeline:     'Setting up DevOps...',
  monitoring:          'Monitoring deployment...',
  documentation:       'Compiling docs...',
  pm_summary:          'Writing project report...',
  change_impact:       'Analyzing impact...',
};

export type SelectedAgentInfo = { role: string; name: string; status: string; model: string };

// ── Scene ─────────────────────────────────────────────────────────────────────

export class OfficeScene extends Phaser.Scene {
  private rooms:   RoomLayout[] = [];
  private agents:  AgentObj[]   = [];
  private poller!: AgentStatusWS;
  private W = 800;
  private H = 600;
  private onAgentSelected: (info: SelectedAgentInfo) => void;

  constructor(onAgentSelected: (info: SelectedAgentInfo) => void) {
    super({ key: 'OfficeScene' });
    this.onAgentSelected = onAgentSelected;
  }

  // ── Preload ───────────────────────────────────────────────────────────────

  preload() {
    this.load.on('loaderror', (f: Phaser.Loader.File) =>
      console.error(`[Phaser] ✗ ${f.key} → ${f.src}`)
    );

    // FIX 2: try 48×48 frames (LimeZu Premade Characters vertical strip)
    for (const cfg of AGENT_CONFIG) {
      this.load.spritesheet(cfg.spriteKey, `/sprites/${cfg.spriteKey}.png`, {
        frameWidth: FRAME_SIZE, frameHeight: FRAME_SIZE,
      });
    }
  }

  // ── Create ────────────────────────────────────────────────────────────────

  create() {
    this.W = this.cameras.main.width;
    this.H = this.cameras.main.height;

    // Verify sprite dimensions (expect 896×656 = 56×41 @ 16×16)
    const firstKey = AGENT_CONFIG[0]?.spriteKey;
    if (firstKey) {
      const src = this.textures.get(firstKey).source[0];
      console.log(
        `[Phaser] ${firstKey}: ${src.width}×${src.height} px → ` +
        `${Math.floor(src.width / FRAME_SIZE)} cols × ${Math.floor(src.height / FRAME_SIZE)} rows ` +
        `= ${this.textures.get(firstKey).frameTotal} frames @ ${FRAME_SIZE}×${FRAME_SIZE}`
      );
    }

    this.rooms = this.computeLayout();
    this.drawMap();
    this.spawnAgents();

    this.time.addEvent({
      delay: 150, loop: true,
      callback: this.tickAnimations, callbackScope: this,
    });

    this.setupCamera();
    this.setupPoller();
  }

  // ── FIX 3: Dynamic layout — fits entire viewport ──────────────────────────

  private computeLayout(): RoomLayout[] {
    const W = this.W, H = this.H;
    const ROOM_W = Math.floor((W - MARGIN * 2 - GAP * 2) / 3);
    const ROOM_H = Math.floor((H - MARGIN * 2 - GAP) / 2) - 10;
    const DEV_W  = Math.floor(ROOM_W * 1.5);
    const QA_W   = W - MARGIN * 2 - DEV_W - GAP;
    const ROW2_Y = MARGIN + ROOM_H + GAP;

    const defs = [
      { name: 'Requirement Room', x: MARGIN,                      y: MARGIN,  w: ROOM_W, h: ROOM_H },
      { name: 'Meeting Room',     x: MARGIN + ROOM_W + GAP,       y: MARGIN,  w: ROOM_W, h: ROOM_H },
      { name: 'Control Room',     x: MARGIN + (ROOM_W + GAP) * 2, y: MARGIN,  w: ROOM_W, h: ROOM_H },
      { name: 'Developer Room',   x: MARGIN,                      y: ROW2_Y,  w: DEV_W,  h: ROOM_H },
      { name: 'QA Lab',           x: MARGIN + DEV_W + GAP,        y: ROW2_Y,  w: QA_W,   h: ROOM_H },
    ];

    return defs.map((d) => {
      const clr = ROOM_COLORS[d.name] ?? { floor: 0xf0f0e8, carpet: 0xd4d4b8, header: 0x666699 };
      return {
        ...d,
        icon: ROOM_ICONS[d.name] ?? '🏢',
        headerColor: clr.header,
        floorColor:  clr.floor,
        carpetColor: clr.carpet,
      };
    });
  }

  // ── Map ───────────────────────────────────────────────────────────────────

  private drawMap() {
    const bg = this.add.graphics().setDepth(-2);
    bg.fillStyle(0x1a1a2e);
    bg.fillRect(0, 0, this.W, this.H);

    // Corridor strip between row 1 and row 2
    const top = this.rooms[0], bot = this.rooms[3];
    if (top && bot) {
      const cg = this.add.graphics().setDepth(-1);
      cg.fillStyle(0x252542);
      cg.fillRect(MARGIN, top.y + top.h, this.W - MARGIN * 2, bot.y - (top.y + top.h));
    }

    const furG = this.add.graphics().setDepth(2);
    for (const room of this.rooms) {
      this.drawRoom(room, furG);
    }
  }

  private drawRoom(room: RoomLayout, furG: Phaser.GameObjects.Graphics) {
    const { x, y, w, h } = room;

    // Drop shadow
    const sg = this.add.graphics().setDepth(-1);
    sg.fillStyle(0x000000, 0.20);
    sg.fillRect(x + 4, y + 4, w, h);

    // Floor + carpet
    const fg = this.add.graphics().setDepth(0);
    fg.fillStyle(room.floorColor);
    fg.fillRect(x, y, w, h);
    const pad = 16;
    fg.fillStyle(room.carpetColor, 0.50);
    fg.fillRect(x + pad, y + HDR_H + pad, w - pad * 2, h - HDR_H - pad * 2);

    // Border + inner shadow
    const og = this.add.graphics().setDepth(3);
    og.lineStyle(1.5, 0x6366f1, 0.45);
    og.strokeRect(x, y, w, h);
    og.lineStyle(3, 0x000000, 0.10);
    og.strokeRect(x + 2, y + 2, w - 4, h - 4);

    // Header
    const hg = this.add.graphics().setDepth(4);
    hg.fillStyle(room.headerColor, 0.92);
    hg.fillRect(x, y, w, HDR_H);

    const agentCount = AGENT_CONFIG.filter((c) => c.room === room.name).length;
    const pillW = 22;
    hg.fillStyle(0xffffff, 0.20);
    hg.fillRoundedRect(x + w - pillW - 4, y + 3, pillW, HDR_H - 6, 3);

    this.add.text(x + 8, y + HDR_H / 2, `${room.icon} ${room.name}`, {
      color: '#ffffff', fontSize: '10px', fontStyle: 'bold',
      stroke: '#00000066', strokeThickness: 1,
    }).setOrigin(0, 0.5).setDepth(5);

    this.add.text(x + w - pillW / 2 - 4, y + HDR_H / 2, `${agentCount}`, {
      color: '#ffffffbb', fontSize: '8px',
    }).setOrigin(0.5, 0.5).setDepth(5);

    // FIX 1: Graphics furniture
    this.placeFurniture(furG, room);
  }

  // ── FIX 1: Graphics furniture ─────────────────────────────────────────────

  private fur(
    g: Phaser.GameObjects.Graphics,
    x: number, y: number,
    type: 'desk' | 'computer' | 'chair' | 'plant' | 'server',
  ) {
    switch (type) {
      case 'desk':
        g.fillStyle(0x8B6914);
        g.fillRect(x, y, 40, 24);
        g.fillStyle(0x6B4F0F);
        g.fillRect(x + 2, y + 2, 36, 4);
        break;

      case 'computer':
        g.fillStyle(0x2a2a3a);
        g.fillRect(x + 8, y - 18, 24, 16);
        g.fillStyle(0x0088cc, 0.85);
        g.fillRect(x + 10, y - 16, 20, 10);
        g.fillStyle(0x444455);
        g.fillRect(x + 18, y - 2, 4, 4);
        break;

      case 'chair':
        g.fillStyle(0x4a6fa5);
        g.fillRect(x, y, 18, 18);
        g.fillStyle(0x3a5585);
        g.fillRect(x + 2, y + 2, 14, 8);
        break;

      case 'plant':
        g.fillStyle(0x2d5a27);
        g.fillCircle(x + 8, y + 4, 10);
        g.fillStyle(0x3d7a35);
        g.fillCircle(x + 3, y, 6);
        g.fillCircle(x + 13, y + 1, 7);
        g.fillStyle(0x5c3d1e);
        g.fillRect(x + 5, y + 12, 6, 8);
        break;

      case 'server':
        g.fillStyle(0x1a1a2e);
        g.fillRect(x, y, 20, 40);
        g.fillStyle(0x2a2a42);
        g.fillRect(x + 2, y + 2, 16, 36);
        g.fillStyle(0x00ff88);
        g.fillRect(x + 4,  y + 6,  4, 4);
        g.fillRect(x + 4,  y + 14, 4, 4);
        g.fillRect(x + 4,  y + 22, 4, 4);
        g.fillStyle(0x0088ff);
        g.fillRect(x + 10, y + 6,  4, 4);
        g.fillRect(x + 10, y + 14, 4, 4);
        break;
    }
  }

  private placeFurniture(g: Phaser.GameObjects.Graphics, room: RoomLayout) {
    const { x, y, w, h } = room;
    const iy = y + HDR_H + 18;

    switch (room.name) {
      case 'Requirement Room':
        this.fur(g, x + 14,         iy,            'desk');
        this.fur(g, x + 14,         iy,            'computer');
        this.fur(g, x + w - 58,     iy,            'desk');
        this.fur(g, x + w - 58,     iy,            'computer');
        this.fur(g, x + w - 26,     y + h - 38,    'plant');
        break;

      case 'Meeting Room': {
        const cx = x + w / 2 - 40;
        const cy = y + HDR_H + h * 0.35;
        g.fillStyle(0x7a5910);
        g.fillRect(cx, cy, 80, 32);
        g.fillStyle(0x5a3e0a);
        g.fillRect(cx + 2, cy + 2, 76, 5);
        this.fur(g, cx + 6,  cy - 26, 'chair');
        this.fur(g, cx + 50, cy - 26, 'chair');
        this.fur(g, cx + 6,  cy + 38, 'chair');
        this.fur(g, cx + 50, cy + 38, 'chair');
        break;
      }

      case 'Developer Room': {
        const desks = 4;
        const spacing = Math.floor((w - 40) / desks);
        for (let i = 0; i < desks; i++) {
          const dx = x + 14 + i * spacing;
          this.fur(g, dx, iy, 'desk');
          this.fur(g, dx, iy, 'computer');
        }
        this.fur(g, x + w - 28, y + HDR_H + h * 0.50, 'server');
        break;
      }

      case 'QA Lab':
        this.fur(g, x + 14,         iy, 'desk');
        this.fur(g, x + 14,         iy, 'computer');
        this.fur(g, x + w / 2 - 20, iy, 'desk');
        this.fur(g, x + w / 2 - 20, iy, 'computer');
        this.fur(g, x + w - 28,     y + HDR_H + h * 0.50, 'server');
        break;

      case 'Control Room':
        this.fur(g, x + 14,         iy,            'desk');
        this.fur(g, x + 14,         iy,            'computer');
        this.fur(g, x + w - 58,     iy,            'desk');
        this.fur(g, x + w - 58,     iy,            'computer');
        this.fur(g, x + 14,         y + HDR_H + h * 0.50, 'server');
        this.fur(g, x + 40,         y + HDR_H + h * 0.50, 'server');
        this.fur(g, x + w - 26,     y + h - 38,    'plant');
        break;
    }
  }

  // ── Animation ticker ──────────────────────────────────────────────────────

  private tickAnimations() {
    for (const a of this.agents) {
      a.animFrame = a.walking ? (a.animFrame + 1) % FRAMES_PER_DIR : 0;
      // 896×656 sheet, 56 cols/row: frameIndex = dir * 56 + animFrame
      const frameIdx = a.animDir * SPRITE_COLS + a.animFrame;
      try { a.img.setFrame(frameIdx); } catch { /* frame out of range */ }
    }
  }

  // ── FIX 2: Spawn agents ───────────────────────────────────────────────────

  private spawnAgents() {
    const byRoom: Record<string, typeof AGENT_CONFIG[number][]> = {};
    for (const cfg of AGENT_CONFIG) {
      (byRoom[cfg.room] ??= []).push(cfg);
    }

    for (const room of this.rooms) {
      const cfgs = byRoom[room.name] ?? [];
      cfgs.forEach((cfg, idx) => {
        const { x: px, y: py } = this.agentStartPos(room, idx, cfgs.length);

        if (idx === 0) {
          const tex = this.textures.get(cfg.spriteKey);
          const src = tex.source[0];
          console.log(
            `[${room.name}] ${cfg.spriteKey}: ${src.width}×${src.height}px, ` +
            `frames=${tex.frameTotal}`
          );
        }

        // 16×16 frame, scale 3 → 48×48 on screen; anchor at feet
        const img = this.add.image(px, py, cfg.spriteKey, 0);
        img.setOrigin(0.5, 1).setScale(3).setDepth(5);
        img.setInteractive({ useHandCursor: true });

        const abbr = ROLE_ABBR[cfg.role] ?? cfg.role.slice(0, 3).toUpperCase();
        const bw   = abbr.length * 7 + 8;

        // Badge sits above the 48px sprite (feet at py, head at py-48)
        const labelBg = this.add.rectangle(px, py - 54, bw, 14, room.headerColor, 0.90)
          .setDepth(8);
        const labelText = this.add.text(px, py - 54, abbr, {
          fontSize: '9px', color: '#ffffff', fontStyle: 'bold',
        }).setOrigin(0.5, 0.5).setDepth(9);
        const dot = this.add.arc(px + 18, py - 36, 4, 0, 360, false, 0xffffff, 0.40)
          .setDepth(9);

        const agentObj: AgentObj = {
          role: cfg.role, spriteKey: cfg.spriteKey, room,
          img, labelBg, labelText, dot,
          bubble: null, glow: null,
          pulseTween: null, glowTween: null, walkTween: null, bubbleTween: null,
          walking: false, animFrame: 0, animDir: DIR_DOWN,
          status: 'idle', model: '', provider: '',
        };

        img.on('pointerdown', () => this.onAgentSelected({
          role:   cfg.role,
          name:   cfg.role.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          status: agentObj.status,
          model:  agentObj.model || agentObj.provider || 'ollama',
        }));

        this.agents.push(agentObj);
        this.scheduleWalk(agentObj);
      });
    }
  }

  private agentStartPos(room: RoomLayout, idx: number, total: number) {
    const cols   = Math.ceil(Math.sqrt(total));
    const rows   = Math.ceil(total / cols);
    const col    = idx % cols;
    const row    = Math.floor(idx / cols);
    const pad    = 28;
    const innerW = room.w - pad * 2;
    const innerH = room.h - HDR_H - pad * 2;
    return {
      x: room.x + pad + (col + 0.5) * (innerW / cols),
      y: room.y + HDR_H + pad + (row + 0.5) * (innerH / rows),
    };
  }

  // ── Walk ──────────────────────────────────────────────────────────────────

  private roomWalkBounds(room: RoomLayout) {
    const pad = 32;
    return {
      minX: room.x + pad,
      maxX: room.x + room.w - pad,
      minY: room.y + HDR_H + pad,
      maxY: room.y + room.h - pad,
    };
  }

  private scheduleWalk(agent: AgentObj) {
    this.time.delayedCall(Phaser.Math.Between(2000, 6000), () => {
      if (agent.status === 'working') {
        agent.walking = false; agent.animDir = DIR_DOWN;
        this.scheduleWalk(agent); return;
      }
      const b  = this.roomWalkBounds(agent.room);
      const tx = Phaser.Math.Between(b.minX, b.maxX);
      const ty = Phaser.Math.Between(b.minY, b.maxY);
      const dx = tx - agent.img.x, dy = ty - agent.img.y;

      agent.animDir = Math.abs(dx) >= Math.abs(dy)
        ? (dx > 0 ? DIR_RIGHT : DIR_LEFT)
        : (dy > 0 ? DIR_DOWN  : DIR_UP);
      agent.walking = true;

      const dist = Phaser.Math.Distance.Between(agent.img.x, agent.img.y, tx, ty);
      agent.walkTween?.stop();
      agent.walkTween = this.tweens.add({
        targets: agent.img, x: tx, y: ty,
        duration: (dist / WALK_SPEED) * 1000, ease: 'Linear',
        onComplete: () => {
          agent.walking = false; agent.walkTween = null;
          agent.animDir = DIR_DOWN;
          this.scheduleWalk(agent);
        },
      });
    });
  }

  // ── Status ────────────────────────────────────────────────────────────────

  setAgentStatuses(info: AgentInfoMap) {
    for (const a of this.agents) {
      const entry = info[a.role];
      const s = entry?.status ?? 'idle';
      if (entry) {
        a.model    = entry.model    ?? '';
        a.provider = entry.provider ?? '';
      }
      if (s !== a.status) {
        const prev = a.status;
        a.status = s;
        this.applyStatusDot(a);
        if (s === 'working') {
          a.walkTween?.stop(); a.walking = false; a.animDir = DIR_DOWN;
          this.startGlow(a);
          const task = entry?.current_task ?? '';
          this.showBubble(a, STEP_LABELS[task] ?? 'Working...', 0x4f46e5);
        } else {
          this.stopGlow(a);
          if (prev === 'working') {
            const msg = s === 'error' ? 'Error!' : 'Done ✓';
            const color = s === 'error' ? 0xef4444 : 0x059669;
            this.showBubble(a, msg, color, 3500);
          }
        }
      }
    }
  }

  private showBubble(a: AgentObj, text: string, bgColor: number, duration = 0) {
    // Destroy existing bubble
    a.bubbleTween?.stop(); a.bubbleTween = null;
    a.bubble?.destroy(); a.bubble = null;

    const bubble = this.add.text(a.img.x, a.img.y - 72, text, {
      fontSize: '8px',
      color: '#ffffff',
      backgroundColor: `#${bgColor.toString(16).padStart(6, '0')}`,
      padding: { x: 5, y: 3 },
      wordWrap: { width: 90 },
      align: 'center',
    }).setOrigin(0.5, 1).setDepth(20).setAlpha(0.95);

    a.bubble = bubble;

    // Auto-fade out: immediately if duration=0 means indefinite (fade after 6s), else use duration
    const fadeAfter = duration > 0 ? duration : 6000;
    a.bubbleTween = this.time.delayedCall(fadeAfter, () => {
      if (!a.bubble) return;
      a.bubbleTween = this.tweens.add({
        targets: a.bubble, alpha: 0, duration: 600, ease: 'Power1',
        onComplete: () => { a.bubble?.destroy(); a.bubble = null; a.bubbleTween = null; },
      });
    }) as unknown as Phaser.Tweens.Tween;
  }

  private applyStatusDot(a: AgentObj) {
    a.pulseTween?.stop(); a.pulseTween = null; a.dot.setAlpha(1);
    const clr: Record<string, number> = {
      working: 0x6366f1, done: 0x34d399, error: 0xef4444, waiting: 0xf59e0b,
    };
    const color = a.status === 'idle' ? 0xffffff : (clr[a.status] ?? 0xffffff);
    const alpha = a.status === 'idle' ? 0.35 : 1;
    a.dot.setFillStyle(color, alpha);
    if (a.status === 'working') {
      a.pulseTween = this.tweens.add({
        targets: a.dot, alpha: 0.3, duration: 800, yoyo: true, repeat: -1,
      });
    }
  }

  private startGlow(a: AgentObj) {
    this.stopGlow(a);
    a.glow = this.add.arc(a.img.x, a.img.y, 22, 0, 360, false, 0x6366f1, 0.18).setDepth(4);
    a.glowTween = this.tweens.add({
      targets: a.glow,
      alpha:  { from: 0.18, to: 0.38 },
      scaleX: { from: 1.0,  to: 1.30 },
      scaleY: { from: 1.0,  to: 1.30 },
      duration: 900, yoyo: true, repeat: -1,
    });
  }

  private stopGlow(a: AgentObj) {
    a.glowTween?.stop(); a.glowTween = null;
    a.glow?.destroy();   a.glow      = null;
  }

  // ── Camera (FIX 3: zoom=1, no scroll — everything fits on screen) ─────────

  private setupCamera() {
    const cam = this.cameras.main;
    cam.setBounds(0, 0, this.W, this.H);
    cam.setZoom(1);
    cam.setBackgroundColor('#1a1a2e');
  }

  // ── Poller ────────────────────────────────────────────────────────────────

  private setupPoller() {
    this.poller = new AgentStatusWS((info) => this.setAgentStatuses(info));
    this.poller.start();
  }

  // ── Update ────────────────────────────────────────────────────────────────

  update() {
    for (const a of this.agents) {
      const { x: ix, y: iy } = a.img;  // iy = feet position (origin 0.5, 1)
      a.labelBg.setPosition(ix, iy - 54);
      a.labelText.setPosition(ix, iy - 54);
      a.dot.setPosition(ix + 18, iy - 36);
      if (a.glow)   a.glow.setPosition(ix, iy - 24);
      if (a.bubble) a.bubble.setPosition(ix, iy - 72);
    }
  }

  // ── Cleanup ───────────────────────────────────────────────────────────────

  shutdown() {
    this.poller?.stop();
    for (const a of this.agents) {
      a.walkTween?.stop(); a.pulseTween?.stop();
      this.stopGlow(a);
      a.bubble?.destroy(); a.bubble = null;
    }
  }
}
