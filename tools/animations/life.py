#!/usr/bin/env python3
"""
Conway's Game of Life, on a 96x16 torus.

Four gliders are launched into a patch of random soup. They collide with it,
scatter, and the mess settles into still lifes and blinkers -- the usual
trajectory, but a 96x16 world is small enough that the whole thing reads as
one event rather than a field of unrelated activity.

Cells are colored by age, which is the part that makes it worth watching on a
panel with no brightness control: a cell born this generation is white, one
that has survived a generation is cyan, and anything older is blue. Active
regions flicker white while settled structures sink to blue, so you can see
where the computation is still happening.

The loop is deliberately not seamless -- Life does not return to its seed.
The jump back reads as a reseed, which suits it.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

WIDTH, HEIGHT = 96, 16
FRAMES = 24
DELAY = 180
SEED = 11           # fixed so the file is reproducible
SOUP_DENSITY = 0.32

GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

AGE_COLORS = [C.WHITE, C.CYAN]   # age 0, age 1
OLD_COLOR = C.BLUE               # age 2+


def seed_world():
    rng = random.Random(SEED)
    alive = set()

    # A band of soup in the middle third, left clear at the edges so the
    # gliders have room to travel before they hit anything.
    for x in range(34, 64):
        for y in range(2, HEIGHT - 2):
            if rng.random() < SOUP_DENSITY:
                alive.add((x, y))

    # Gliders heading inward from both ends.
    for origin_x, origin_y, flip in [(4, 2, False), (8, 9, False),
                                     (88, 3, True), (84, 10, True)]:
        for dx, dy in GLIDER:
            x = origin_x - dx if flip else origin_x + dx
            alive.add((x % WIDTH, (origin_y + dy) % HEIGHT))

    return alive


def step(alive):
    """One generation, wrapping at every edge."""
    counts = {}
    for x, y in alive:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbour = ((x + dx) % WIDTH, (y + dy) % HEIGHT)
                counts[neighbour] = counts.get(neighbour, 0) + 1

    return {
        cell
        for cell, count in counts.items()
        if count == 3 or (count == 2 and cell in alive)
    }


def build():
    anim = Animation(WIDTH, HEIGHT, delay=DELAY)
    alive = seed_world()
    age = {cell: 0 for cell in alive}

    for _ in range(FRAMES):
        frame = anim.frame()
        for cell in alive:
            years = age.get(cell, 0)
            color = AGE_COLORS[years] if years < len(AGE_COLORS) else OLD_COLOR
            frame.pixel(cell[0], cell[1], color)

        following = step(alive)
        # Survivors get older; newcomers start at zero.
        age = {
            cell: (age[cell] + 1 if cell in age else 0)
            for cell in following
        }
        alive = following

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/life.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
