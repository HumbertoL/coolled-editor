#!/usr/bin/env python3
"""
Flip-disc display -- a 48x8 board of yellow/black discs, flipping in waves.

Each disc is 2x2 pixels. A flip takes two frames: edge-on it shows as a thin
blue sliver, then lands on its new face. Four pictures, four different wave
shapes carrying the change: a sweep from the left, a ripple out from the
centre, a diagonal, and a scatter in seeded random order. The last picture
flips back to the first, so the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
COLS, ROWS = 48, 8
SEGMENT = 13  # 4 segments of 13 = 52, plus a final frame equal to the first
WAVE = 8


def picture_rings(c, r):
    d = math.hypot((c - 23.5) / 2.0, r - 3.5)
    return int(d) % 2 == 0


def picture_checks(c, r):
    return (c // 2 + r // 2) % 2 == 0


def picture_hearts(c, r):
    heart = ["_##_##_", "#######", "#######", "_#####_", "__###__", "___#___"]
    cx = c % 12 - 2
    ry = r - 1
    return 0 <= ry < 6 and 0 <= cx < 7 and heart[ry][cx] == "#"


def picture_diagonals(c, r):
    return (c + r) % 6 < 3


PICTURES = [picture_rings, picture_checks, picture_hearts, picture_diagonals]


def orders():
    rng = random.Random(5)
    scatter = {(c, r): rng.random() for c in range(COLS) for r in range(ROWS)}
    return [
        lambda c, r: c / (COLS - 1),
        lambda c, r: math.hypot((c - 23.5) / 2.0, r - 3.5) / 12.2,
        lambda c, r: (c + (ROWS - 1 - r) * 2) / (COLS - 1 + (ROWS - 1) * 2),
        lambda c, r: scatter[(c, r)],
    ]


def build():
    anim = Animation(delay=DELAY)
    waves = orders()
    for index in range(FRAMES):
        frame = anim.frame()
        seg = (index // SEGMENT) % 4
        local = index % SEGMENT if index < 52 else 0
        before = PICTURES[seg]
        after = PICTURES[(seg + 1) % 4]
        if index == 52:
            before = after = PICTURES[0]
        for c in range(COLS):
            for r in range(ROWS):
                start = round(waves[seg](c, r) * WAVE) + 2
                old, new = before(c, r), after(c, r)
                if local < start or old == new:
                    face = old
                elif local == start:
                    face = None
                else:
                    face = new
                x, y = c * 2, r * 2
                if face is None:
                    frame.vline(x + 1, y, 2, C.BLUE)
                elif face:
                    frame.rect(x, y, 2, 2, C.YELLOW, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/flip_disc.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
