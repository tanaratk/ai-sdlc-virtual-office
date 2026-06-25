import Phaser from 'phaser';
import { AGENT_CONFIG, AgentStatusWS, type AgentInfoMap } from '../AgentManager';

const TILE = 16;
const SCALE = 2;
const WORLD_TILE_W = 52;
const WORLD_TILE_H = 32;
const WORLD_W = WORLD_TILE_W * TILE * SCALE;
const WORLD_H = WORLD_TILE_H * TILE * SCALE;
const WALK_SPEED = 78;

const FRAME_SIZE = 16;
const SAFE_WALK_FRAMES = [56, 57, 58, 59];
const DIR_DOWN = 0;
const DIR_LEFT = 1;
const DIR_RIGHT = 2;
const DIR_UP = 3;
const AGENT_LABEL_Y_OFFSET = 96;
const AGENT_BUBBLE_Y_OFFSET = 120;
const AGENT_DOT_Y_OFFSET = 72;
const AGENT_GLOW_Y_OFFSET = 42;

const ROOM_TILE_COLS = 76;

type RoomKind = 'requirement' | 'meeting' | 'developer' | 'qa' | 'control';

interface RoomLayout {
  key: RoomKind;
  name: string;
  x: number;
  y: number;
  w: number;
  h: number;
  floor: number;
  wall: number;
  accent: number;
  agents: string[];
}

interface AgentObj {
  role: string;
  spriteKey: string;
  room: RoomLayout;
  img: Phaser.GameObjects.Image;
  labelBg: Phaser.GameObjects.Rectangle;
  labelText: Phaser.GameObjects.Text;
  dot: Phaser.GameObjects.Arc;
  shadow: Phaser.GameObjects.Ellipse;
  bubble: Phaser.GameObjects.Text | null;
  glow: Phaser.GameObjects.Arc | null;
  pulseTween: Phaser.Tweens.Tween | null;
  glowTween: Phaser.Tweens.Tween | null;
  walkTween: Phaser.Tweens.Tween | null;
  pathTweens: Phaser.Tweens.Tween[];
  bubbleTimer: Phaser.Time.TimerEvent | null;
  walking: boolean;
  animFrame: number;
  animDir: number;
  status: string;
  model: string;
  provider: string;
}

const ROLE_ABBR: Record<string, string> = {
  'requirement-agent': 'REQ',
  'gap-analysis-agent': 'GAP',
  'ba-agent': 'BA',
  'architect-agent': 'ARC',
  'ux-agent': 'UX',
  'technical-design-agent': 'TD',
  'developer-agent': 'DEV',
  'developer-agent-backend': 'DEB',
  'developer-agent-frontend': 'DEF',
  'developer-agent-platform': 'DEP',
  'code-review-agent': 'CRV',
  'qa-agent': 'QA',
  'devops-agent': 'OPS',
  'monitoring-agent': 'MON',
  'documentation-agent': 'DOC',
  'pm-agent': 'PM',
  'change-impact-agent': 'CI',
};

const STEP_LABELS: Record<string, string> = {
  requirement_summary: 'Analyzing requirements...',
  gap_analysis: 'Finding gaps...',
  ba_documents: 'Writing BRD and stories...',
  architecture: 'Designing architecture...',
  ux_design: 'Creating screen specs...',
  technical_design: 'Planning dev tasks...',
  code_generation: 'Generating code...',
  code_review: 'Reviewing code...',
  qa_testing: 'Writing test cases...',
  devops_pipeline: 'Preparing deployment...',
  monitoring: 'Monitoring deployment...',
  documentation: 'Compiling docs...',
  pm_summary: 'Writing project report...',
  change_impact: 'Analyzing impact...',
};

export type SelectedAgentInfo = { role: string; name: string; status: string; model: string };

function px(tile: number) {
  return tile * TILE * SCALE;
}

function frame(tx: number, ty: number) {
  return ty * ROOM_TILE_COLS + tx;
}

export class OfficeScene extends Phaser.Scene {
  private rooms: RoomLayout[] = [];
  private agents: AgentObj[] = [];
  private poller!: AgentStatusWS;
  private onAgentSelected: (info: SelectedAgentInfo) => void;

  constructor(onAgentSelected: (info: SelectedAgentInfo) => void) {
    super({ key: 'OfficeScene' });
    this.onAgentSelected = onAgentSelected;
  }

  preload() {
    this.load.spritesheet('room_tiles', '/tilesets/Room_Builder_16x16.png', {
      frameWidth: TILE,
      frameHeight: TILE,
    });
    this.load.spritesheet('interiors', '/tilesets/Interiors_16x16.png', {
      frameWidth: TILE,
      frameHeight: TILE,
    });

    for (const cfg of AGENT_CONFIG) {
      this.load.spritesheet(cfg.spriteKey, `/sprites/${cfg.spriteKey}.png`, {
        frameWidth: FRAME_SIZE,
        frameHeight: FRAME_SIZE,
      });
    }
  }

  create() {
    this.rooms = this.createRooms();
    this.drawOffice();
    this.spawnAgents();

    this.time.addEvent({
      delay: 150,
      loop: true,
      callback: this.tickAnimations,
      callbackScope: this,
    });

    this.setupCamera();
    this.setupPoller();
  }

  private createRooms(): RoomLayout[] {
    return [
      {
        key: 'requirement',
        name: 'Requirement Room',
        x: 2,
        y: 2,
        w: 14,
        h: 10,
        floor: 0xc8d9dd,
        wall: 0x2b3942,
        accent: 0x456b79,
        agents: ['requirement-agent', 'gap-analysis-agent'],
      },
      {
        key: 'meeting',
        name: 'Meeting Room',
        x: 18,
        y: 2,
        w: 16,
        h: 10,
        floor: 0x9dcbd5,
        wall: 0x223644,
        accent: 0x3d8293,
        agents: ['ba-agent', 'architect-agent', 'ux-agent', 'technical-design-agent'],
      },
      {
        key: 'control',
        name: 'Control Room',
        x: 36,
        y: 2,
        w: 14,
        h: 10,
        floor: 0xc98b62,
        wall: 0x322c35,
        accent: 0x7b4f8f,
        agents: ['documentation-agent', 'pm-agent', 'change-impact-agent'],
      },
      {
        key: 'developer',
        name: 'Developer Room',
        x: 2,
        y: 15,
        w: 31,
        h: 15,
        floor: 0xaab7bc,
        wall: 0x1f2933,
        accent: 0x3c74a8,
        agents: [
          'developer-agent',
          'developer-agent-backend',
          'developer-agent-frontend',
          'developer-agent-platform',
          'code-review-agent',
        ],
      },
      {
        key: 'qa',
        name: 'QA Lab',
        x: 35,
        y: 15,
        w: 15,
        h: 15,
        floor: 0xd5e6dd,
        wall: 0x253742,
        accent: 0x46a36c,
        agents: ['qa-agent', 'devops-agent', 'monitoring-agent'],
      },
    ];
  }

  private drawOffice() {
    this.cameras.main.setBackgroundColor('#0d111b');

    const bg = this.add.graphics().setDepth(-20);
    bg.fillStyle(0x0d111b);
    bg.fillRect(0, 0, WORLD_W, WORLD_H);

    this.drawCorridors();
    for (const room of this.rooms) this.drawRoom(room);
    this.drawGlassHall();
    this.drawRoomNames();
  }

  private drawCorridors() {
    const g = this.add.graphics().setDepth(-5);
    g.fillStyle(0x5c6b72);
    g.fillRect(px(2), px(12), px(48), px(3));
    g.fillRect(px(16), px(12), px(2), px(18));
    g.fillRect(px(33), px(12), px(2), px(18));
    g.fillStyle(0x6d7c82, 0.5);
    for (let x = 2; x < 50; x += 2) {
      g.lineStyle(1, 0x819098, 0.32);
      g.lineBetween(px(x), px(12), px(x), px(15));
    }
    g.lineStyle(3, 0x25313a, 0.7);
    g.strokeRect(px(2), px(12), px(48), px(3));
  }

  private drawRoom(room: RoomLayout) {
    const x = px(room.x);
    const y = px(room.y);
    const w = px(room.w);
    const h = px(room.h);
    const g = this.add.graphics().setDepth(0);

    g.fillStyle(0x000000, 0.28);
    g.fillRect(x + 8, y + 8, w, h);

    g.fillStyle(room.floor);
    g.fillRect(x, y, w, h);
    this.tileFloor(room);

    g.lineStyle(8, room.wall, 1);
    g.strokeRect(x, y, w, h);
    g.lineStyle(2, 0xffffff, 0.18);
    g.strokeRect(x + 6, y + 6, w - 12, h - 12);

    this.cutDoor(room);
    this.drawRoomDetail(room);
  }

  private tileFloor(room: RoomLayout) {
    const floorFrames: Record<RoomKind, number[]> = {
      requirement: [frame(0, 12), frame(1, 12), frame(0, 13), frame(1, 13)],
      meeting: [frame(36, 12), frame(37, 12), frame(36, 13), frame(37, 13)],
      developer: [frame(0, 22), frame(1, 22), frame(0, 23), frame(1, 23)],
      qa: [frame(36, 23), frame(37, 23), frame(36, 24), frame(37, 24)],
      control: [frame(21, 16), frame(22, 16)],
    };
    const frames = floorFrames[room.key] ?? floorFrames.requirement;

    for (let ty = room.y + 1; ty < room.y + room.h - 1; ty++) {
      for (let tx = room.x + 1; tx < room.x + room.w - 1; tx++) {
        const idx = frames[(tx + ty) % frames.length];
        this.add.image(px(tx) + TILE, px(ty) + TILE, 'room_tiles', idx)
          .setScale(SCALE)
          .setAlpha(0.28)
          .setDepth(1);
      }
    }

    const g = this.add.graphics().setDepth(1.5);
    g.lineStyle(1, 0xffffff, 0.08);
    for (let tx = room.x + 2; tx < room.x + room.w - 1; tx += 2) {
      g.lineBetween(px(tx), px(room.y + 1), px(tx), px(room.y + room.h - 1));
    }
    for (let ty = room.y + 2; ty < room.y + room.h - 1; ty += 2) {
      g.lineBetween(px(room.x + 1), px(ty), px(room.x + room.w - 1), px(ty));
    }
  }

  private cutDoor(room: RoomLayout) {
    const g = this.add.graphics().setDepth(2);
    const doorW = px(3);
    const dx = px(room.x + Math.floor(room.w / 2) - 1);
    const topRoom = room.y < 10;
    const dy = topRoom ? px(room.y + room.h) - 6 : px(room.y) - 4;
    g.fillStyle(0x5c6b72);
    g.fillRect(dx, dy, doorW, 18);
    g.fillStyle(0x98a8ae, 0.55);
    g.fillRect(dx + 8, dy + (topRoom ? 11 : 0), doorW - 16, 5);
    g.lineStyle(2, 0x202832, 1);
    g.lineBetween(dx, dy, dx, dy + 18);
    g.lineBetween(dx + doorW, dy, dx + doorW, dy + 18);
  }

  private drawGlassHall() {
    const g = this.add.graphics().setDepth(3);
    const x = px(18);
    const y = px(12);
    const w = px(17);
    const h = px(3);
    g.fillStyle(0x7fd5e8, 0.24);
    g.fillRect(x, y, w, h);
    g.lineStyle(2, 0xbdefff, 0.55);
    for (let i = 0; i <= 6; i++) {
      const lx = x + (w / 6) * i;
      g.lineBetween(lx, y, lx, y + h);
    }
    g.lineStyle(2, 0xffffff, 0.35);
    for (let i = 0; i < 4; i++) {
      g.lineBetween(x + i * 96, y + h - 10, x + 66 + i * 96, y + 10);
    }
  }

  private drawRoomNames() {
    for (const room of this.rooms) {
      const count = AGENT_CONFIG.filter((cfg) => cfg.room === room.name).length;
      const label = `${room.name} (${count})`;

      this.add.rectangle(px(room.x) + px(0.5), px(room.y) + px(0.5), px(room.w) - px(1), 22, room.wall, 0.86)
        .setOrigin(0, 0)
        .setDepth(9);
      this.add.text(px(room.x) + 12, px(room.y) + 5, label, {
        color: '#ecfeff',
        fontSize: '10px',
        fontStyle: 'bold',
        stroke: '#000000',
        strokeThickness: 2,
      }).setDepth(10);
    }
  }

  private drawRoomDetail(room: RoomLayout) {
    switch (room.key) {
      case 'requirement':
        this.drawRequirement(room);
        break;
      case 'meeting':
        this.drawMeeting(room);
        break;
      case 'developer':
        this.drawDeveloper(room);
        break;
      case 'qa':
        this.drawQa(room);
        break;
      case 'control':
        this.drawControl(room);
        break;
    }
  }

  private drawRequirement(room: RoomLayout) {
    const g = this.add.graphics().setDepth(4);
    this.pixelDesk(g, room.x + 4.2, room.y + 5.7, 6.3, 2.2);
    this.pixelMonitor(g, room.x + 6.2, room.y + 4.75);
    this.pixelWhiteboard(g, room.x + 8.7, room.y + 2.3);
    this.pixelWaterCooler(g, room.x + 11.0, room.y + 6.0);
    this.pixelPlant(g, room.x + 1.8, room.y + 3.0, 0.7);
  }

  private drawMeeting(room: RoomLayout) {
    const g = this.add.graphics().setDepth(4);
    this.pixelScreen(g, room.x + 3.5, room.y + 2.0);
    this.pixelWhiteboard(g, room.x + 9.6, room.y + 2.0);
    this.pixelDesk(g, room.x + 4.2, room.y + 5.0, 7.4, 2.8);
    for (const [cx, cy] of [[3.2, 5.0], [12.2, 5.0], [3.2, 8.0], [12.2, 8.0], [7.3, 8.1]]) {
      this.pixelChair(g, room.x + cx, room.y + cy);
    }
    this.pixelPlant(g, room.x + 1.7, room.y + 7.7, 0.6);
  }

  private drawControl(room: RoomLayout) {
    const g = this.add.graphics().setDepth(4);
    this.pixelSofa(g, room.x + 3.3, room.y + 3.0);
    this.pixelCoffeeTable(g, room.x + 5.0, room.y + 6.1);
    this.pixelBookshelf(g, room.x + 1.5, room.y + 3.0);
    this.pixelArcade(g, room.x + 10.2, room.y + 2.8);
    this.pixelScreen(g, room.x + 4.0, room.y + 1.8);
  }

  private drawDeveloper(room: RoomLayout) {
    const g = this.add.graphics().setDepth(4);
    const desks = [
      [3.1, 4.0], [12.4, 4.0], [21.7, 4.0],
      [3.1, 9.6], [12.4, 9.6], [21.7, 9.6],
    ];
    for (const [tx, ty] of desks) {
      this.pixelDesk(g, room.x + tx, room.y + ty, 5.6, 2.0);
      this.pixelMonitor(g, room.x + tx + 2.0, room.y + ty - 0.8);
      this.pixelChair(g, room.x + tx + 2.0, room.y + ty + 2.25);
    }
    this.pixelServerRack(g, room.x + 28.0, room.y + 4.6);
    this.pixelServerRack(g, room.x + 28.0, room.y + 9.5);
    this.pixelPlant(g, room.x + 1.5, room.y + 12.3, 0.65);
  }

  private drawQa(room: RoomLayout) {
    const g = this.add.graphics().setDepth(4);
    this.pixelDesk(g, room.x + 2.2, room.y + 4.0, 6.4, 2.5);
    this.pixelMonitor(g, room.x + 4.3, room.y + 3.1);
    this.pixelDesk(g, room.x + 2.2, room.y + 9.8, 6.4, 2.5);
    this.pixelMonitor(g, room.x + 4.3, room.y + 8.9);
    this.pixelServerRack(g, room.x + 11.0, room.y + 4.0);
    this.pixelServerRack(g, room.x + 11.0, room.y + 9.4);
    this.pixelWhiteboard(g, room.x + 3.0, room.y + 13.0);
  }

  private pixelDesk(g: Phaser.GameObjects.Graphics, tx: number, ty: number, tw: number, th: number) {
    g.fillStyle(0x9b6235);
    g.fillRect(px(tx), px(ty), px(tw), px(th));
    g.fillStyle(0x6f4324);
    g.fillRect(px(tx) + 4, px(ty) + 4, px(tw) - 8, 5);
    g.fillStyle(0xd8b27c);
    g.fillRect(px(tx) + px(tw) - 17, px(ty) + 8, 9, 7);
  }

  private pixelMonitor(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x1c2430);
    g.fillRect(px(tx), px(ty), 34, 24);
    g.fillStyle(0x67e8f9);
    g.fillRect(px(tx) + 4, px(ty) + 4, 26, 14);
    g.fillStyle(0x2f3a48);
    g.fillRect(px(tx) + 14, px(ty) + 22, 8, 7);
  }

  private pixelChair(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x2c3e50);
    g.fillRect(px(tx), px(ty), 24, 21);
    g.fillStyle(0x415a70);
    g.fillRect(px(tx) + 4, px(ty) + 4, 16, 9);
  }

  private pixelPlant(g: Phaser.GameObjects.Graphics, tx: number, ty: number, scale = 1) {
    const x = px(tx);
    const y = px(ty);
    g.fillStyle(0x2f7d32);
    g.fillCircle(x + 14 * scale, y + 8 * scale, 14 * scale);
    g.fillStyle(0x59b85f);
    g.fillCircle(x + 4 * scale, y + 2 * scale, 8 * scale);
    g.fillCircle(x + 22 * scale, y + 3 * scale, 9 * scale);
    g.fillStyle(0x7a4a2a);
    g.fillRect(x + 8 * scale, y + 21 * scale, 12 * scale, 12 * scale);
  }

  private pixelWaterCooler(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x9be7ff, 0.8);
    g.fillRect(px(tx), px(ty), 22, 28);
    g.fillStyle(0xe5edf3);
    g.fillRect(px(tx) + 2, px(ty) + 26, 18, 30);
  }

  private pixelScreen(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0xf8fafc);
    g.fillRect(px(tx), px(ty), px(4.5), px(2.2));
    g.fillStyle(0x43a047);
    g.fillCircle(px(tx) + 18, px(ty) + 16, 10);
    g.fillStyle(0xe07a5f);
    g.fillRect(px(tx) + 34, px(ty) + 10, 28, 8);
    g.fillStyle(0x4e79a7);
    g.fillRect(px(tx) + 34, px(ty) + 22, 42, 8);
  }

  private pixelWhiteboard(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0xf4f8fb);
    g.fillRect(px(tx), px(ty), px(4), px(2.4));
    g.lineStyle(2, 0xb7c2cc);
    g.strokeRect(px(tx), px(ty), px(4), px(2.4));
  }

  private pixelSofa(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x6c7a89);
    g.fillRoundedRect(px(tx), px(ty), px(7), px(2.2), 5);
    g.fillStyle(0x516170);
    g.fillRect(px(tx) + 8, px(ty) + 8, px(6), px(1));
  }

  private pixelCoffeeTable(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x8b5a2b);
    g.fillRoundedRect(px(tx), px(ty), px(4), px(2), 4);
    g.fillStyle(0xfff7ed);
    g.fillRect(px(tx) + 18, px(ty) + 10, 10, 8);
  }

  private pixelBookshelf(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x6b4423);
    g.fillRect(px(tx), px(ty), px(2), px(4.8));
    for (let i = 0; i < 5; i++) {
      g.fillStyle([0xe76f51, 0x2a9d8f, 0xe9c46a, 0x8ab17d][i % 4]);
      g.fillRect(px(tx) + 5, px(ty) + 8 + i * 12, 22, 6);
    }
  }

  private pixelArcade(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x4c1d95);
    g.fillRect(px(tx), px(ty), px(2.2), px(4));
    g.fillStyle(0x67e8f9);
    g.fillRect(px(tx) + 8, px(ty) + 10, 24, 16);
    g.fillStyle(0xf472b6);
    g.fillCircle(px(tx) + 14, px(ty) + 46, 4);
    g.fillCircle(px(tx) + 24, px(ty) + 46, 4);
  }

  private pixelServerRack(g: Phaser.GameObjects.Graphics, tx: number, ty: number) {
    g.fillStyle(0x17202a);
    g.fillRect(px(tx), px(ty), px(2.2), px(4.5));
    for (let i = 0; i < 4; i++) {
      g.fillStyle(0x2f3a48);
      g.fillRect(px(tx) + 4, px(ty) + 8 + i * 14, 26, 8);
      g.fillStyle(i % 2 ? 0x22c55e : 0x38bdf8);
      g.fillRect(px(tx) + 8, px(ty) + 10 + i * 14, 5, 4);
    }
  }

  private spawnAgents() {
    const byRoom: Record<string, typeof AGENT_CONFIG[number][]> = {};
    for (const cfg of AGENT_CONFIG) (byRoom[cfg.room] ??= []).push(cfg);

    for (const room of this.rooms) {
      const cfgs = byRoom[room.name] ?? [];
      cfgs.forEach((cfg, idx) => {
        const { x, y } = this.agentStartPos(room, idx, cfgs.length);
        const shadow = this.add.ellipse(x, y - 7, 54, 18, 0x000000, 0.26).setDepth(18);
        const img = this.add.image(x, y, cfg.spriteKey, SAFE_WALK_FRAMES[0]).setOrigin(0.5, 1).setScale(4.5).setDepth(22);
        img.setInteractive({ useHandCursor: true });

        const abbr = ROLE_ABBR[cfg.role] ?? cfg.role.slice(0, 3).toUpperCase();
        const labelBg = this.add.rectangle(x, y - AGENT_LABEL_Y_OFFSET, abbr.length * 10 + 16, 18, 0x101827, 0.88).setDepth(30);
        const labelText = this.add.text(x, y - AGENT_LABEL_Y_OFFSET, abbr, {
          fontSize: '11px',
          color: '#ffffff',
          fontStyle: 'bold',
        }).setOrigin(0.5, 0.5).setDepth(31);
        const dot = this.add.arc(x + 31, y - AGENT_DOT_Y_OFFSET, 5, 0, 360, false, 0xffffff, 0.55).setDepth(31);

        const agentObj: AgentObj = {
          role: cfg.role,
          spriteKey: cfg.spriteKey,
          room,
          img,
          labelBg,
          labelText,
          dot,
          shadow,
          bubble: null,
          glow: null,
          pulseTween: null,
          glowTween: null,
          walkTween: null,
          pathTweens: [],
          bubbleTimer: null,
          walking: false,
          animFrame: 0,
          animDir: DIR_DOWN,
          status: 'idle',
          model: '',
          provider: '',
        };

        img.on('pointerdown', () => this.onAgentSelected({
          role: cfg.role,
          name: cfg.role.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          status: agentObj.status,
          model: agentObj.model || agentObj.provider || 'ollama',
        }));

        this.agents.push(agentObj);
        this.scheduleWalk(agentObj);
      });
    }
  }

  private agentStartPos(room: RoomLayout, idx: number, _total: number) {
    const points = this.roomWalkPoints(room);
    return points[idx % points.length];
  }

  private roomWalkPoints(room: RoomLayout) {
    const t = (x: number, y: number) => ({ x: px(room.x + x), y: px(room.y + y) });

    switch (room.key) {
      case 'requirement':
        return [t(3.0, 8.2), t(7.0, 8.6), t(10.7, 7.8), t(7.0, 10.2)];
      case 'meeting':
        return [t(3.1, 8.9), t(6.5, 8.8), t(11.8, 8.8), t(13.0, 5.2), t(7.7, 10.0)];
      case 'control':
        return [t(3.0, 8.5), t(6.8, 8.9), t(10.4, 8.1), t(9.2, 10.0), t(6.5, 10.1)];
      case 'developer':
        return [
          t(2.4, 13.1), t(7.2, 7.6), t(16.5, 7.6), t(25.8, 7.6),
          t(7.2, 13.0), t(16.5, 13.0), t(25.8, 13.0), t(14.5, 14.1),
        ];
      case 'qa':
        return [t(2.4, 13.1), t(5.2, 7.7), t(5.2, 13.0), t(9.6, 7.6), t(9.2, 12.6)];
      default:
        return [t(room.w / 2, room.h / 2)];
    }
  }

  private roomDoorPoint(room: RoomLayout) {
    return {
      x: px(room.x + Math.floor(room.w / 2) + 0.5),
      y: room.y < 10 ? px(room.y + room.h + 1.1) : px(room.y - 0.8),
    };
  }

  private corridorPointFor(room: RoomLayout) {
    const door = this.roomDoorPoint(room);
    return {
      x: door.x,
      y: room.y < 10 ? px(13.4) : px(13.8),
    };
  }

  private randomWalkPoint(room: RoomLayout) {
    return Phaser.Utils.Array.GetRandom(this.roomWalkPoints(room));
  }

  private stopAgentTweens(agent: AgentObj) {
    agent.walkTween?.stop();
    agent.walkTween = null;
    for (const tween of agent.pathTweens) tween.stop();
    agent.pathTweens = [];
  }

  private directionTo(agent: AgentObj, point: { x: number; y: number }) {
    const dx = point.x - agent.img.x;
    const dy = point.y - agent.img.y;
    return Math.abs(dx) >= Math.abs(dy)
      ? (dx > 0 ? DIR_RIGHT : DIR_LEFT)
      : (dy > 0 ? DIR_DOWN : DIR_UP);
  }

  private moveAgentPath(agent: AgentObj, points: { x: number; y: number }[], onComplete: () => void) {
    const next = points.shift();
    if (!next) {
      agent.walking = false;
      agent.animDir = DIR_DOWN;
      onComplete();
      return;
    }

    agent.animDir = this.directionTo(agent, next);
    agent.walking = true;
    const dist = Phaser.Math.Distance.Between(agent.img.x, agent.img.y, next.x, next.y);
    const tween = this.tweens.add({
      targets: agent.img,
      x: next.x,
      y: next.y,
      duration: Math.max(360, (dist / WALK_SPEED) * 1000),
      ease: 'Linear',
      onComplete: () => {
        agent.pathTweens = agent.pathTweens.filter((tweenItem) => tweenItem !== tween);
        this.moveAgentPath(agent, points, onComplete);
      },
    });
    agent.pathTweens.push(tween);
  }

  private scheduleWalk(agent: AgentObj) {
    this.time.delayedCall(Phaser.Math.Between(1400, 4600), () => {
      if (!agent.img.active) return;
      if (agent.status === 'working') {
        agent.walking = false;
        agent.animDir = DIR_DOWN;
        this.scheduleWalk(agent);
        return;
      }

      this.stopAgentTweens(agent);
      const shouldChangeRoom = Phaser.Math.Between(1, 100) <= 20;

      if (shouldChangeRoom && this.rooms.length > 1) {
        const targetRoom = Phaser.Utils.Array.GetRandom(this.rooms.filter((room) => room.key !== agent.room.key));
        const path = [
          this.roomDoorPoint(agent.room),
          this.corridorPointFor(agent.room),
          this.corridorPointFor(targetRoom),
          this.roomDoorPoint(targetRoom),
          this.randomWalkPoint(targetRoom),
        ];
        this.moveAgentPath(agent, path, () => {
          agent.room = targetRoom;
          this.scheduleWalk(agent);
        });
        return;
      }

      this.moveAgentPath(agent, [this.randomWalkPoint(agent.room)], () => this.scheduleWalk(agent));
    });
  }

  private tickAnimations() {
    for (const a of this.agents) {
      a.animFrame = a.walking ? (a.animFrame + 1) % SAFE_WALK_FRAMES.length : 0;
      const frameIdx = SAFE_WALK_FRAMES[a.animFrame] ?? SAFE_WALK_FRAMES[0];
      try {
        a.img.setFrame(frameIdx);
      } catch {
        // Ignore unexpected third-party sheet layout changes.
      }
    }
  }

  setAgentStatuses(info: AgentInfoMap) {
    for (const a of this.agents) {
      const entry = info[a.role];
      const s = entry?.status ?? 'idle';
      if (entry) {
        a.model = entry.model ?? '';
        a.provider = entry.provider ?? '';
      }
      if (s === a.status) continue;

      const prev = a.status;
      a.status = s;
      this.applyStatusDot(a);

      if (s === 'working') {
        this.stopAgentTweens(a);
        a.walking = false;
        a.animDir = DIR_DOWN;
        this.startGlow(a);
        const task = entry?.current_task ?? '';
        this.showBubble(a, STEP_LABELS[task] ?? 'Working...', 0x2563eb);
      } else {
        this.stopGlow(a);
        if (prev === 'working') {
          const msg = s === 'error' ? 'Error!' : 'Done';
          this.showBubble(a, msg, s === 'error' ? 0xdc2626 : 0x059669, 3500);
        }
      }
    }
  }

  private showBubble(a: AgentObj, text: string, bgColor: number, duration = 0) {
    a.bubbleTimer?.remove(false);
    a.bubbleTimer = null;
    a.bubble?.destroy();
    a.bubble = null;

    const bubble = this.add.text(a.img.x, a.img.y - AGENT_BUBBLE_Y_OFFSET, text, {
      fontSize: '10px',
      color: '#ffffff',
      backgroundColor: `#${bgColor.toString(16).padStart(6, '0')}`,
      padding: { x: 6, y: 4 },
      wordWrap: { width: 140 },
      align: 'center',
    }).setOrigin(0.5, 1).setDepth(40).setAlpha(0.96);

    a.bubble = bubble;
    a.bubbleTimer = this.time.delayedCall(duration > 0 ? duration : 6000, () => {
      if (!a.bubble) return;
      this.tweens.add({
        targets: a.bubble,
        alpha: 0,
        duration: 600,
        ease: 'Power1',
        onComplete: () => {
          a.bubble?.destroy();
          a.bubble = null;
          a.bubbleTimer = null;
        },
      });
    });
  }

  private applyStatusDot(a: AgentObj) {
    a.pulseTween?.stop();
    a.pulseTween = null;
    a.dot.setAlpha(1);

    const colors: Record<string, number> = {
      working: 0x38bdf8,
      done: 0x34d399,
      error: 0xef4444,
      waiting: 0xf59e0b,
    };
    a.dot.setFillStyle(colors[a.status] ?? 0xffffff, a.status === 'idle' ? 0.45 : 1);
    if (a.status === 'working') {
      a.pulseTween = this.tweens.add({
        targets: a.dot,
        alpha: 0.25,
        duration: 700,
        yoyo: true,
        repeat: -1,
      });
    }
  }

  private startGlow(a: AgentObj) {
    this.stopGlow(a);
    a.glow = this.add.arc(a.img.x, a.img.y - AGENT_GLOW_Y_OFFSET, 42, 0, 360, false, 0x38bdf8, 0.2).setDepth(19);
    a.glowTween = this.tweens.add({
      targets: a.glow,
      alpha: { from: 0.16, to: 0.4 },
      scaleX: { from: 1, to: 1.35 },
      scaleY: { from: 1, to: 1.35 },
      duration: 850,
      yoyo: true,
      repeat: -1,
    });
  }

  private stopGlow(a: AgentObj) {
    a.glowTween?.stop();
    a.glowTween = null;
    a.glow?.destroy();
    a.glow = null;
  }

  private setupCamera() {
    const cam = this.cameras.main;
    cam.setBounds(0, 0, WORLD_W, WORLD_H);
    const zoom = Math.min(cam.width / WORLD_W, cam.height / WORLD_H);
    cam.setZoom(zoom);
    cam.centerOn(WORLD_W / 2, WORLD_H / 2);
  }

  private setupPoller() {
    this.poller = new AgentStatusWS((info) => this.setAgentStatuses(info));
    this.poller.start();
  }

  update() {
    for (const a of this.agents) {
      const ix = a.img.x;
      const iy = a.img.y;
      a.shadow.setPosition(ix, iy - 8);
      a.labelBg.setPosition(ix, iy - AGENT_LABEL_Y_OFFSET);
      a.labelText.setPosition(ix, iy - AGENT_LABEL_Y_OFFSET);
      a.dot.setPosition(ix + 31, iy - AGENT_DOT_Y_OFFSET);
      if (a.glow) a.glow.setPosition(ix, iy - AGENT_GLOW_Y_OFFSET);
      if (a.bubble) a.bubble.setPosition(ix, iy - AGENT_BUBBLE_Y_OFFSET);
    }
  }

  shutdown() {
    this.poller?.stop();
    for (const a of this.agents) {
      this.stopAgentTweens(a);
      a.pulseTween?.stop();
      a.bubbleTimer?.remove(false);
      this.stopGlow(a);
      a.bubble?.destroy();
      a.bubble = null;
    }
  }
}
