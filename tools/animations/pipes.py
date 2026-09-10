#!/usr/bin/env python3
"""
Pipes -- the Windows 95 screensaver, translated to 96x16.

Four coloured pipes grow one segment per frame. Each has an 18% chance to
turn 90 degrees; on the edge or into an occupied cell, the pipe respawns at a
random empty location with a fresh direction. There is no depth or shading --
the palette has neither -- so the interest is entirely in the routing.

Not seamless: the field fills up. But it also self-resets: once all four
pipes have collided into stuck corners, the whole board wipes to black on the
last frame and starts over, so replaying the loop feels continuous.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 4

PIPE_COLORS = [C.RED, C.GREEN, C.MAGENTA, C.CYAN]
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
TURN_CHANCE = 0.18


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=110)

    # (x, y, dx, dy, color) per pipe. Start each on a different edge.
    pipes = []
    starts = [(0, 8, 1, 0), (95, 4, -1, 0), (48, 0, 0, 1), (60, 15, 0, -1)]
    for (x, y, dx, dy), color in zip(starts, PIPE_COLORS):
        pipes.append([x, y, dx, dy, color])

    grid = {}   # (x, y) -> color; persistent across frames

    def respawn(pipe):
        # Find an empty cell for the new head, keep the same colour so the
        # network of that colour keeps its identity.
        color = pipe[4]
        for _ in range(60):
            x = rng.randrange(1, 95)
            y = rng.randrange(1, 15)
            if (x, y) not in grid:
                dx, dy = rng.choice(DIRS)
                pipe[:] = [x, y, dx, dy, color]
                return
        # Board is basically full; nothing more we can do this frame.

    def step(pipe):
        x, y, dx, dy, color = pipe
        # Lay the current head cell.
        grid[(x, y)] = color
        # Chance to turn 90 degrees.
        if rng.random() < TURN_CHANCE:
            dx, dy = (-dy, dx) if rng.random() < 0.5 else (dy, -dx)
        nx, ny = x + dx, y + dy
        # Blocked by wall or a laid segment -> respawn.
        if not (0 <= nx < 96 and 0 <= ny < 16) or (nx, ny) in grid:
            respawn(pipe)
            return
        pipe[:] = [nx, ny, dx, dy, color]

    for index in range(FRAMES):
        # Full wipe on the last frame so the sample loops cleanly.
        if index == FRAMES - 1:
            grid.clear()
            frame = anim.frame()
            continue

        for pipe in pipes:
            step(pipe)

        frame = anim.frame()
        for (x, y), color in grid.items():
            frame.pixel(x, y, color)
        # Draw heads brighter so the eye follows them.
        for x, y, _dx, _dy, _color in pipes:
            frame.pixel(x, y, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pipes.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
