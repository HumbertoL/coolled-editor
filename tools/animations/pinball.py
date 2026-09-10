#!/usr/bin/env python3
"""
Pinball -- a ball loose among the bumpers.

Top-down table: a walled field, three round bumpers, and a ball that ricochets
between them at constant speed. A struck bumper flashes white and rings
outward for a couple of frames, and every hit adds a score pip along the top
edge. The physics is sub-stepped so the ball never tunnels through a bumper.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

BUMPERS = [
    (26, 6, 2.2, C.MAGENTA),
    (52, 10, 2.2, C.CYAN),
    (74, 4, 2.2, C.YELLOW),
]
BALL_R = 0.6
SUBSTEPS = 4


def simulate():
    """Ball state and bumper-hit frames, precomputed for the whole loop."""
    x, y = 12.0, 12.0
    vx, vy = 3.4, -1.7
    speed = math.hypot(vx, vy)
    states, hits = [], []
    for frame_index in range(FRAMES):
        frame_hits = []
        for _ in range(SUBSTEPS):
            x += vx / SUBSTEPS
            y += vy / SUBSTEPS
            if x < 2:
                x, vx = 4 - x, abs(vx)
            if x > 93:
                x, vx = 186 - x, -abs(vx)
            if y < 2:
                y, vy = 4 - y, abs(vy)
            if y > 13:
                y, vy = 26 - y, -abs(vy)
            for i, (bx, by, br, _color) in enumerate(BUMPERS):
                dx, dy = x - bx, y - by
                dist = math.hypot(dx, dy)
                if dist < br + BALL_R:
                    # Reflect about the bumper normal, keep the speed.
                    nx, ny = dx / dist, dy / dist
                    dot = vx * nx + vy * ny
                    if dot < 0:
                        vx -= 2 * dot * nx
                        vy -= 2 * dot * ny
                        norm = math.hypot(vx, vy)
                        vx, vy = vx / norm * speed, vy / norm * speed
                        x = bx + nx * (br + BALL_R + 0.1)
                        y = by + ny * (br + BALL_R + 0.1)
                        frame_hits.append(i)
        states.append((x, y))
        hits.append(frame_hits)
    return states, hits


def draw_circle(frame, cx, cy, radius, color):
    steps = max(8, int(2 * math.pi * radius * 2))
    for i in range(steps):
        a = 2 * math.pi * i / steps
        frame.pixel(round(cx + radius * math.cos(a)), round(cy + radius * math.sin(a)), color)


def build():
    anim = Animation(delay=DELAY)
    states, hits = simulate()

    # A bumper glows for 2 frames after any hit; pips accumulate.
    flash_until = [-1] * len(BUMPERS)
    total_hits = 0
    pips = []
    for index in range(FRAMES):
        frame = anim.frame()
        for bumper in hits[index]:
            flash_until[bumper] = index + 2
            total_hits += 1
        pips.append(total_hits)

        # Walls.
        frame.rect(0, 0, 96, 16, C.BLUE)

        # Bumpers.
        for i, (bx, by, br, color) in enumerate(BUMPERS):
            flashing = index <= flash_until[i]
            draw_circle(frame, bx, by, br, C.WHITE if flashing else color)
            frame.pixel(round(bx), round(by), C.WHITE if flashing else color)
            if flashing:
                draw_circle(frame, bx, by, br + 1.6, color)

        # Score pips along the top wall.
        for p in range(min(pips[index], 20)):
            frame.pixel(4 + p * 3, 0, C.YELLOW)

        # Ball with a two-step trail.
        for back, color in ((2, C.BLUE), (1, C.CYAN)):
            px, py = states[(index - back) % FRAMES]
            frame.pixel(round(px), round(py), color)
        bx, by = states[index]
        frame.pixel(round(bx), round(by), C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pinball.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
