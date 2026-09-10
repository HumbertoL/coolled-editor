#!/usr/bin/env python3
"""
Sand -- falling sand simulation with colored grains piling up.

Grains drop from the top, fall with gravity, and pile into heaps.
Different colors cycle through the spectrum. Near the end, the
piles dissolve from the bottom for a clean restart.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
SEED = 17

WIDTH = 96
HEIGHT = 16
GRAINS_PER_FRAME = 4
GRAIN_COLORS = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.MAGENTA]
CLEAR_FRAMES = 6  # last N frames used to clear


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)

    # Grid: None = empty, else a color
    grid = [[None] * WIDTH for _ in range(HEIGHT)]
    color_idx = 0

    for index in range(FRAMES):
        # Clear phase: remove bottom rows progressively
        if index >= FRAMES - CLEAR_FRAMES:
            clear_step = index - (FRAMES - CLEAR_FRAMES)
            rows_to_clear = (clear_step + 1) * HEIGHT // CLEAR_FRAMES
            for row in range(HEIGHT - 1, max(HEIGHT - 1 - rows_to_clear, -1), -1):
                for col in range(WIDTH):
                    grid[row][col] = None
            # Let remaining grains fall a few steps
            for _ in range(3):
                for y in range(HEIGHT - 2, -1, -1):
                    for x in range(WIDTH):
                        if grid[y][x] is not None and grid[y + 1][x] is None:
                            grid[y + 1][x] = grid[y][x]
                            grid[y][x] = None
        else:
            # Add new grains at the top
            for _ in range(rng.randint(3, 5)):
                x = rng.randrange(WIDTH)
                if grid[0][x] is None:
                    grid[0][x] = GRAIN_COLORS[color_idx % len(GRAIN_COLORS)]
                    color_idx += 1

            # Simulate falling -- scan bottom to top
            for _ in range(3):  # multiple sub-steps per frame for speed
                for y in range(HEIGHT - 2, -1, -1):
                    for x in range(WIDTH):
                        if grid[y][x] is None:
                            continue
                        if grid[y + 1][x] is None:
                            grid[y + 1][x] = grid[y][x]
                            grid[y][x] = None
                        else:
                            # Try diagonal
                            dirs = [-1, 1]
                            rng.shuffle(dirs)
                            for dx in dirs:
                                nx = x + dx
                                if 0 <= nx < WIDTH and grid[y + 1][nx] is None:
                                    grid[y + 1][nx] = grid[y][x]
                                    grid[y][x] = None
                                    break

        # Render
        frame = anim.frame()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if grid[y][x] is not None:
                    frame.pixel(x, y, grid[y][x])

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sand.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
