import React, { useCallback, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { getColorFromChunk } from './helpers/colors';
import { GRID_HEIGHT, GRID_WIDTH } from './helpers/constants';

const SQUARE = 12;
const GAP = 1;
const PITCH = SQUARE + GAP;
const RADIUS = 2;
// Room around a cell for its glow to spill into.
const GLOW = 5;

const WIDTH = GRID_WIDTH * PITCH - GAP;
const HEIGHT = GRID_HEIGHT * PITCH - GAP;

const BACKGROUND = '#0a0a0f';
const UNLIT = '#000000';

const GridContainer = styled.div`
  margin-top: 20px;
  padding: 12px;
  background: ${BACKGROUND};
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 0 40px rgba(0, 0, 0, 0.5),
    inset 0 0 30px rgba(0, 0, 0, 0.3);
  line-height: 0;
`;

const GridCanvas = styled.canvas`
  display: block;
  cursor: crosshair;
  touch-action: none;
`;

const roundedRect = (ctx, x, y, size, radius) => {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + size, y, x + size, y + size, radius);
  ctx.arcTo(x + size, y + size, x, y + size, radius);
  ctx.arcTo(x, y + size, x, y, radius);
  ctx.arcTo(x, y, x + size, y, radius);
  ctx.closePath();
};

/**
 * The unlit board, drawn once and blitted each frame.
 *
 * Every frame starts from this, so only lit cells cost anything per frame.
 */
const buildBase = (scale) => {
  const base = document.createElement('canvas');
  base.width = WIDTH * scale;
  base.height = HEIGHT * scale;
  const ctx = base.getContext('2d');
  ctx.scale(scale, scale);
  ctx.fillStyle = BACKGROUND;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = UNLIT;
  for (let column = 0; column < GRID_WIDTH; column++) {
    for (let row = 0; row < GRID_HEIGHT; row++) {
      roundedRect(ctx, column * PITCH, row * PITCH, SQUARE, RADIUS);
      ctx.fill();
    }
  }
  return base;
};

/**
 * One lit cell, with its glow baked in.
 *
 * Drawing a shadow per cell per frame is what made this expensive as DOM.
 * There are only eight colours, so each is rendered once and stamped
 * thereafter -- a blit rather than a shadow pass.
 */
const buildSprite = (color, scale) => {
  const size = SQUARE + GLOW * 2;
  const sprite = document.createElement('canvas');
  sprite.width = size * scale;
  sprite.height = size * scale;
  const ctx = sprite.getContext('2d');
  ctx.scale(scale, scale);

  ctx.shadowColor = `${color}80`;
  ctx.shadowBlur = 4;
  ctx.fillStyle = color;
  roundedRect(ctx, GLOW, GLOW, SQUARE, RADIUS);
  ctx.fill();
  // A second, tighter pass to match the two-shadow look of the old CSS.
  ctx.shadowBlur = 1;
  ctx.fill();
  return sprite;
};

const Grid = ({
  pixelArray,
  onClick,
  onMouseDown,
  onMouseUp,
  onMouseEnter,
}) => {
  const canvasRef = useRef(null);
  const baseRef = useRef(null);
  const spritesRef = useRef(new Map());
  const scaleRef = useRef(1);
  // Which cell the pointer was last over, so a drag paints once per cell
  // rather than once per mouse event.
  const lastCellRef = useRef(-1);

  const spriteFor = useCallback((color) => {
    const cache = spritesRef.current;
    if (!cache.has(color)) {
      cache.set(color, buildSprite(color, scaleRef.current));
    }
    return cache.get(color);
  }, []);

  // Redraw whenever the frame changes. This is the whole render path: one
  // blit for the board, then one stamp per lit cell.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !pixelArray) {
      return;
    }

    const scale = window.devicePixelRatio || 1;
    if (scale !== scaleRef.current || !baseRef.current) {
      scaleRef.current = scale;
      spritesRef.current = new Map();
      baseRef.current = buildBase(scale);
      canvas.width = WIDTH * scale;
      canvas.height = HEIGHT * scale;
      canvas.style.width = `${WIDTH}px`;
      canvas.style.height = `${HEIGHT}px`;
    }

    const ctx = canvas.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(baseRef.current, 0, 0);
    ctx.scale(scale, scale);

    const count = Math.min(pixelArray.length, GRID_WIDTH * GRID_HEIGHT);
    for (let index = 0; index < count; index++) {
      const color = getColorFromChunk(pixelArray[index]);
      if (color === UNLIT) {
        continue;
      }
      const column = Math.floor(index / GRID_HEIGHT);
      const row = index % GRID_HEIGHT;
      ctx.drawImage(
        spriteFor(color),
        column * PITCH - GLOW,
        row * PITCH - GLOW,
        SQUARE + GLOW * 2,
        SQUARE + GLOW * 2,
      );
    }
  }, [pixelArray, spriteFor]);

  const cellFromEvent = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const column = Math.floor((event.clientX - rect.left) / PITCH);
    const row = Math.floor((event.clientY - rect.top) / PITCH);
    if (column < 0 || column >= GRID_WIDTH || row < 0 || row >= GRID_HEIGHT) {
      return -1;
    }
    // Column-major, matching how the old CSS grid flowed its children.
    return column * GRID_HEIGHT + row;
  };

  const handlePointerDown = (event) => {
    const cell = cellFromEvent(event);
    if (cell < 0) {
      return;
    }
    lastCellRef.current = cell;
    onMouseDown();
    onClick(cell);
  };

  const handlePointerMove = (event) => {
    const cell = cellFromEvent(event);
    if (cell < 0 || cell === lastCellRef.current) {
      return;
    }
    lastCellRef.current = cell;
    // App decides whether this paints, based on its dragging state.
    onMouseEnter(cell);
  };

  const handlePointerUp = () => {
    lastCellRef.current = -1;
    onMouseUp();
  };

  if (!pixelArray) {
    return <div>Please upload a file</div>;
  }

  return (
    <GridContainer>
      <GridCanvas
        ref={canvasRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      />
    </GridContainer>
  );
};

export default Grid;
