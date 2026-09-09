#!/usr/bin/env python3
"""
Be right back -- a status with somebody leaving.

The message holds along the top while a stick figure walks off the right-hand
edge along the bottom, two-frame walk cycle, leaving footprints that fade.
The figure re-enters from the left when the loop restarts, which is close
enough to coming back.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 140

WALK = [
    [
        "..#..",
        ".###.",
        "..#..",
        "..#..",
        ".#.#.",
        "#...#",
    ],
    [
        "..#..",
        "..##.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
]
WALK_Y = 9
STEP = 4


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.text("BE RIGHT BACK", "center", 1, C.CYAN)
        x = STEP * index
        for k in range(1, 4):
            fx = x - k * STEP * 2
            if 0 <= fx < anim.width:
                frame.pixel(fx + (0 if k % 2 else 4), 15, C.BLUE)
        sprite = WALK[index % 2]
        for row, line in enumerate(sprite):
            for col, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(x + col, WALK_Y + row, C.YELLOW if row < 2 else C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/status_brb.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
