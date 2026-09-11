#!/usr/bin/env python3
"""
Peek -- the panel is dark, and a cat keeps looking in.

Mostly nothing. Then a cat's head rises from the bottom edge -- just a faint
blue outline and two yellow eyes -- looks left, looks right, and sinks back
down. Dark again. Later it comes up somewhere else and does it again. The
dark stretches are the point; at eight seconds a loop it happens rarely
enough to catch people off guard.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150

CAT = [
    "#.........#",
    "##.......##",
    "#.#.....#.#",
    "#.........#",
    "#.........#",
    "#.........#",
    ".#.......#.",
    "..#######..",
]
CAT_EYES = [(3, 4), (7, 4)]
# (x, rise, look, sink, gone): two appearances, different places.
PEEKS = [(22, 8, 13, 20, 24), (66, 34, 39, 46, 50)]

def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for cat_x, rise, look, sink, gone in PEEKS:
            if not rise <= index < gone:
                continue
            if index < look:
                top = 16 - 2 * (index - rise + 1)
            elif index < sink:
                top = 16 - 2 * (look - rise)
            else:
                top = 16 - 2 * (look - rise) + 3 * (index - sink + 1)
            for r, line in enumerate(CAT):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(cat_x + c, top + r, C.BLUE)
            glance = 0
            if look <= index < sink:
                glance = -1 if index - look < 3 else 1
            for ex, ey in CAT_EYES:
                frame.pixel(cat_x + ex + glance, top + ey, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/peek.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
