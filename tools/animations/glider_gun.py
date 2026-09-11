#!/usr/bin/env python3
"""
Glider gun -- Gosper's, the first pattern proven to grow without limit.

Conway's Life again, but instead of soup, the famous gun: two shuttles
bouncing between blocks, colliding every thirty generations to throw off a
glider. The gliders march away down and to the right and leave the panel. The
world is simulated unbounded and the panel is just a window onto it, so
nothing at the edge can reflect back and break the gun. Two generations a frame, so three gliders are launched per loop.

Colour by age as in the other Life: born white, survived cyan, older blue.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
GENS_PER_FRAME = 2
WIDTH, HEIGHT = 96, 16
GUN = [
    "........................#...........",
    "......................#.#...........",
    "............##......##............##",
    "...........#...#....##............##",
    "##........#.....#...##..............",
    "##........#...#.##....#.#...........",
    "..........#.....#.......#...........",
    "...........#...#....................",
    "............##......................",
]
GUN_X, GUN_Y = 1, 0


def step(alive):
    counts = {}
    for x, y in alive:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    counts[(x + dx, y + dy)] = counts.get((x + dx, y + dy), 0) + 1
    return {cell for cell, n in counts.items() if n == 3 or (n == 2 and cell in alive)}


def build():
    alive = {(GUN_X + c, GUN_Y + r) for r, line in enumerate(GUN) for c, ch in enumerate(line) if ch == "#"}
    age = {cell: 2 for cell in alive}
    anim = Animation(delay=DELAY)
    for _ in range(FRAMES):
        frame = anim.frame()
        for (x, y), a in age.items():
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                frame.pixel(x, y, C.WHITE if a == 0 else C.CYAN if a == 1 else C.BLUE)
        for _ in range(GENS_PER_FRAME):
            nxt = step(alive)
            age = {cell: (age[cell] + 1 if cell in age else 0) for cell in nxt}
            alive = nxt
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/glider_gun.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
