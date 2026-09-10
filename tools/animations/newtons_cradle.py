#!/usr/bin/env python3
"""
Newton's cradle -- five balls, one swing each way per loop.

The end ball swings out and back on one side, the impulse passes through the
row, and the far ball swings out on the other. One sine drives both: while it
is negative the left ball is displaced, while positive the right, and the
middle three never move -- which is the whole point of the toy. A white flash
on the middle ball marks each click. Seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
BALLS = 5
PITCH = 4
PIVOT_Y = 1
LENGTH = 10.0
SWING = 0.95        # radians


def build():
    anim = Animation(delay=DELAY)
    centre = (anim.width - 1) / 2
    pivots = [centre + (i - (BALLS - 1) / 2) * PITCH for i in range(BALLS)]

    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(round(pivots[0]) - 6, PIVOT_Y, PITCH * (BALLS - 1) + 13, C.BLUE)
        s = math.sin(2 * math.pi * index / FRAMES)
        angles = [0.0] * BALLS
        if s < 0:
            angles[0] = SWING * s
        else:
            angles[-1] = SWING * s
        click = abs(s) < 0.12

        for i, (px, a) in enumerate(zip(pivots, angles)):
            bx = px + LENGTH * math.sin(a)
            by = PIVOT_Y + LENGTH * math.cos(a)
            frame.line(px, PIVOT_Y + 1, bx, by - 1, C.BLUE)
            moving = a != 0.0
            color = C.YELLOW if moving else (C.WHITE if click and i == BALLS // 2 else C.CYAN)
            frame.rect(round(bx) - 1, round(by) - 1, 3, 3, color, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/newtons_cradle.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
