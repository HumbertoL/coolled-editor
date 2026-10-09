#!/usr/bin/env python3
"""
Cyclic automaton -- spirals out of static.

Eight states, each one hungry for the next: a cell advances as soon as one of
its four neighbours is already one step ahead of it. Seeded noise, run on the
wrapping 96x16 panel for 150 steps unseen, organises into rotating spiral
cores and travelling fronts that walk the whole palette. The recorded 53
frames are one automaton step each.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
STATES = 8
WARMUP = 150
PALETTE = [C.BLACK, C.BLUE, C.CYAN, C.GREEN, C.YELLOW, C.RED, C.MAGENTA, C.WHITE]


def step(grid):
    new = [row[:] for row in grid]
    for y in range(16):
        for x in range(96):
            nxt = (grid[y][x] + 1) % STATES
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if grid[(y + dy) % 16][(x + dx) % 96] == nxt:
                    new[y][x] = nxt
                    break
    return new


def build():
    rng = random.Random(8)
    grid = [[rng.randrange(STATES) for _ in range(96)] for _ in range(16)]
    for _ in range(WARMUP):
        grid = step(grid)
    anim = Animation(delay=DELAY)
    for _ in range(FRAMES):
        frame = anim.frame()
        for y in range(16):
            for x in range(96):
                frame.pixel(x, y, PALETTE[grid[y][x]])
        grid = step(grid)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/cyclic_automaton.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
