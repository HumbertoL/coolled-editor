#!/usr/bin/env python3
"""
Sandpile -- the abelian sandpile model, grains poured on three spots.

Any cell holding four or more grains topples, sending one to each neighbour;
grains pushed off the panel's edge are lost. Pour enough and the stable piles
grow the model's famous nested diamonds, coloured by height: 0 black, 1 blue,
2 magenta, 3 yellow. The model is abelian -- the order of toppling never
matters -- so each frame adds a batch of grains and relaxes the lot.

Grains go in on a quadratic schedule, so the piles widen at a steady rate
rather than racing out and stalling, until they hit the top and bottom edges,
spread sideways and merge.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

W, H = 96, 16
FRAMES = 53
DELAY = 100
SOURCES = (16, 48, 80)
ROW = 7
GROW = 46            # frames of pouring; the rest hold the finished piles
TOTAL = 1400         # grains per source by the end of pouring
COLOURS = (C.BLACK, C.BLUE, C.MAGENTA, C.YELLOW)


def relax(grid):
    unstable = [(x, y) for y in range(H) for x in range(W) if grid[y][x] >= 4]
    while unstable:
        x, y = unstable.pop()
        if grid[y][x] < 4:
            continue
        spill, grid[y][x] = divmod(grid[y][x], 4)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H:
                grid[ny][nx] += spill
                if grid[ny][nx] >= 4:
                    unstable.append((nx, ny))


def build():
    anim = Animation(delay=DELAY)
    grid = [[0] * W for _ in range(H)]
    poured = 0
    for index in range(FRAMES):
        target = round(TOTAL * min(1.0, (index + 1) / GROW) ** 2)
        for x in SOURCES:
            grid[ROW][x] += target - poured
        poured = target
        relax(grid)
        frame = anim.frame()
        for y in range(H):
            for x in range(W):
                frame.pixel(x, y, COLOURS[grid[y][x]])
        # The pouring point glints white while sand is still falling.
        if index < GROW:
            for x in SOURCES:
                frame.pixel(x, ROW, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sandpile.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
