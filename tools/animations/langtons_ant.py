#!/usr/bin/env python3
"""
Langton's Ant -- three ants, two rules, and a torus to argue over.

Each ant stands on a cell: if it is empty the ant turns right, if it is
painted the ant turns left; then it flips the cell and steps forward. Three
ants start spread along the panel, one each in yellow, cyan and magenta, and
paint in their own colour -- so a cell another ant painted is still "painted"
to everyone, and an ant can erase its neighbour's work. The panel wraps at
every edge. They begin slowly enough to follow each white head as it lays its
first symmetric scribbles, then speed up as the patches grow, collide and
chew into each other.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
W, H = 96, 16
# (x, y, heading, colour); heading 0=up 1=right 2=down 3=left
ANTS = [
    (16, 8, 0, C.YELLOW),
    (48, 7, 1, C.CYAN),
    (80, 8, 2, C.MAGENTA),
]
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]


def steps_for(index):
    """Slow start so the walk can be followed, then pick up the pace."""
    if index < 8:
        return 3
    if index < 20:
        return 8 + (index - 8) * 2
    return 32 + (index - 20) * 8


def build():
    cells = {}  # (x, y) -> colour of the ant that painted it
    ants = [list(a) for a in ANTS]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        if index:
            for _ in range(steps_for(index)):
                for ant in ants:
                    x, y, heading, color = ant
                    if (x, y) in cells:
                        heading = (heading - 1) % 4
                        del cells[(x, y)]
                    else:
                        heading = (heading + 1) % 4
                        cells[(x, y)] = color
                    ant[0] = (x + DX[heading]) % W
                    ant[1] = (y + DY[heading]) % H
                    ant[2] = heading
        frame = anim.frame()
        for (x, y), color in cells.items():
            frame.pixel(x, y, color)
        for x, y, _, _ in ants:
            frame.pixel(x, y, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/langtons_ant.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
