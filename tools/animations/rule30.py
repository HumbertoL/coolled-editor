#!/usr/bin/env python3
"""
Rule 30 -- Wolfram's elementary cellular automaton, from a single seed.

Each generation is one row: a cell's next state depends only on itself and
its two neighbours, and rule 30 is the one that produces chaos from that. The
newest generation enters at the bottom, white, and older rows scroll up
through cyan into blue. Two generations per frame, so the triangle fills the
panel and keeps scrolling before the loop reseeds.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 120
RULE = 30
GENERATIONS_PER_FRAME = 2


def evolve(cells):
    width = len(cells)
    return [
        (RULE >> ((cells[(i - 1) % width] << 2) | (cells[i] << 1) | cells[(i + 1) % width])) & 1
        for i in range(width)
    ]


def build():
    anim = Animation(delay=DELAY)
    generations = [[0] * anim.width]
    generations[0][anim.width // 2] = 1
    while len(generations) < FRAMES * GENERATIONS_PER_FRAME + 1:
        generations.append(evolve(generations[-1]))

    for index in range(FRAMES):
        frame = anim.frame()
        newest = index * GENERATIONS_PER_FRAME + 1
        for age in range(anim.height):
            gen = newest - age
            if gen < 0:
                break
            color = C.WHITE if age == 0 else C.CYAN if age < 4 else C.BLUE
            row = anim.height - 1 - age
            for x, alive in enumerate(generations[gen]):
                if alive:
                    frame.pixel(x, row, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rule30.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
