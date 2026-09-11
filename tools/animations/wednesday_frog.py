#!/usr/bin/env python3
"""
It Is Wednesday My Dudes (2016) -- the frog.

A budgett's frog sits, blinking, and the announcement appears: IT'S
WEDNESDAY, MY DUDES. Then the scream: the frog's mouth opens, AAAAAAA fills
the second line and the whole panel shakes for the rest of the loop.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 130
SEED = 2016
FROG = [
    "..###...###..",
    ".#############",
    "#############",
    "#############",
    "#############",
    ".###########.",
    "..#########..",
]
FROG_X, FROG_Y = 0, 6
EYES = [(3, 1), (9, 1)]
MOUTH = [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4)]
SCREAM_AT = 30


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        screaming = index >= SCREAM_AT
        shake_x = rng.randint(-1, 1) if screaming else 0
        shake_y = rng.randint(-1, 1) if screaming else 0
        blink = index in (10, 11, 22)
        for r, line in enumerate(FROG):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(FROG_X + c + shake_x, FROG_Y + r + shake_y, C.GREEN)
        for ex, ey in EYES:
            frame.pixel(FROG_X + ex + shake_x, FROG_Y + ey + shake_y, C.GREEN if blink else C.BLACK)
        if screaming:
            for mx, my in MOUTH:
                frame.pixel(FROG_X + mx + shake_x, FROG_Y + my + shake_y, C.BLACK)
                frame.pixel(FROG_X + mx + shake_x, FROG_Y + my + 1 + shake_y, C.RED)
        else:
            frame.hline(FROG_X + 3 + shake_x, FROG_Y + 4 + shake_y, 7, C.BLACK)

        if index >= 4:
            frame.text("IT'S WEDNESDAY", 15 + shake_x, 0 + shake_y, C.WHITE, proportional=True)
        if 12 <= index < SCREAM_AT:
            frame.text("MY DUDES", 15, 9, C.CYAN, proportional=True)
        elif screaming:
            n = min(12, 4 + (index - SCREAM_AT))
            frame.text("A" * n, 15 + shake_x, 9 + shake_y, C.RED if index % 2 else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/wednesday_frog.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
