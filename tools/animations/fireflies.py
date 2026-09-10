#!/usr/bin/env python3
"""
Fireflies -- glowing insects drifting over a grass silhouette.

~12 fireflies float with gentle random walks, each pulsing through
the GLOW ramp on its own staggered cycle. A dark green grass line
runs along the bottom. Seamless loop at 53 frames.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 31

WIDTH = 96
HEIGHT = 16
NUM_FIREFLIES = 12
# Glow cycle: up and down through BLACK -> BLUE -> CYAN -> WHITE -> CYAN -> BLUE -> BLACK
# 7 steps, but we want seamless so use a period that divides into the motion.
# The glow ramp as a full up-and-down cycle:
GLOW_CYCLE = [C.BLACK, C.BLUE, C.CYAN, C.WHITE, C.CYAN, C.BLUE]
GLOW_PERIOD = len(GLOW_CYCLE)  # 6 steps per cycle


def make_grass(rng):
    """Generate an irregular grass silhouette along the bottom."""
    grass = []
    for x in range(WIDTH):
        # Base height 2, occasional taller blades
        h = 2
        r = rng.random()
        if r < 0.12:
            h = 4
        elif r < 0.25:
            h = 3
        grass.append(h)
    return grass


def build():
    rng = random.Random(SEED)

    grass = make_grass(rng)

    # Initialize fireflies: x, y, vx, vy, phase_offset
    fireflies = []
    for i in range(NUM_FIREFLIES):
        x = rng.uniform(4, WIDTH - 4)
        y = rng.uniform(1, HEIGHT - 5)
        vx = rng.uniform(-0.4, 0.4)
        vy = rng.uniform(-0.3, 0.3)
        phase = i * GLOW_PERIOD / NUM_FIREFLIES  # staggered evenly
        fireflies.append([x, y, vx, vy, phase])

    # Pre-generate all positions for seamless looping by running
    # the random walk with a fixed seed per frame
    walk_rng = random.Random(SEED + 100)

    # Record all frame states
    all_states = []
    for f_idx in range(FRAMES):
        state = []
        for ff in fireflies:
            x, y, vx, vy, phase = ff
            state.append((x, y, phase))

            # Update velocity with small random nudges
            vx += walk_rng.uniform(-0.15, 0.15)
            vy += walk_rng.uniform(-0.1, 0.1)
            # Damping
            vx *= 0.92
            vy *= 0.92
            # Clamp speed
            max_v = 0.6
            vx = max(-max_v, min(max_v, vx))
            vy = max(-max_v, min(max_v, vy))
            # Move
            x += vx
            y += vy
            # Soft bounce off edges
            if x < 1:
                x = 1
                vx = abs(vx) * 0.5
            elif x > WIDTH - 2:
                x = WIDTH - 2
                vx = -abs(vx) * 0.5
            if y < 0:
                y = 0
                vy = abs(vy) * 0.5
            elif y > HEIGHT - 5:
                y = HEIGHT - 5
                vy = -abs(vy) * 0.5

            ff[:] = [x, y, vx, vy, phase]
        all_states.append(state)

    anim = Animation(delay=DELAY)
    for f_idx in range(FRAMES):
        frame = anim.frame()

        # Draw grass
        for x in range(WIDTH):
            h = grass[x]
            for dy in range(h):
                frame.pixel(x, HEIGHT - 1 - dy, C.GREEN)

        # Draw fireflies
        for ff_idx, (fx, fy, phase) in enumerate(all_states[f_idx]):
            # Glow cycle position
            cycle_pos = (f_idx + phase) % GLOW_PERIOD
            glow_idx = int(cycle_pos) % len(GLOW_CYCLE)
            color = GLOW_CYCLE[glow_idx]

            if color != C.BLACK:
                px, py = int(round(fx)), int(round(fy))
                frame.pixel(px, py, color)
                # When at peak brightness, add a subtle halo
                if color == C.WHITE:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        hx, hy = px + dx, py + dy
                        if 0 <= hx < WIDTH and 0 <= hy < HEIGHT - grass[min(hx, WIDTH - 1)]:
                            if frame.get(hx, hy) == C.BLACK:
                                frame.pixel(hx, hy, C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fireflies.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
