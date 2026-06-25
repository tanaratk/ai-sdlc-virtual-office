import Phaser from 'phaser';
import { OfficeScene, type SelectedAgentInfo } from './scenes/OfficeScene';

export function createOfficeGame(
  container: HTMLElement,
  onAgentSelected: (info: SelectedAgentInfo) => void,
): Phaser.Game {
  const scene = new OfficeScene(onAgentSelected);

  return new Phaser.Game({
    type: Phaser.AUTO,
    width: container.clientWidth || 800,
    height: container.clientHeight || 600,
    backgroundColor: '#1a1a2e',
    pixelArt: true,
    roundPixels: true,
    parent: container,
    physics: {
      default: 'arcade',
      arcade: { debug: false },
    },
    scene,
  });
}
