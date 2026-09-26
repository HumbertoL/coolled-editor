#!/usr/bin/env python3
"""
Zipper -- a slider runs the length of the panel, meshing the teeth behind it.

Blue fabric above and below, yellow teeth that alternate top and bottom so
they interlock when closed. Ahead of the slider the two tapes splay apart in a
V, showing a red lining through the gap. The slider eases right to close it,
pauses, then eases back to open it again, so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 70
CLOSE = 22
HOLD = 4
LEFT = -3
RIGHT = 99
SPREAD = 0.22
MAX_GAP = 12


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * u)


def slider_x(index):
    if index < CLOSE:
        return LEFT + (RIGHT - LEFT) * ease(index / CLOSE)
    index -= CLOSE + HOLD
    if index < 0:
        return RIGHT
    opening = FRAMES - CLOSE - 2 * HOLD
    if index < opening:
        return RIGHT - (RIGHT - LEFT) * ease(index / opening)
    return LEFT


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        sx = slider_x(index)
        for x in range(96):
            gap = min(MAX_GAP, max(0.0, (x - sx) * SPREAD))
            up = round(gap / 2)
            down = round(gap - gap / 2)
            top_edge = 6 - up
            bottom_edge = 9 + down
            for y in range(16):
                if y < top_edge or y > bottom_edge:
                    frame.pixel(x, y, C.BLUE)
                elif top_edge + 1 < y < bottom_edge - 1:
                    frame.pixel(x, y, C.RED)
            # teeth: top ones on even columns, bottom on odd, overlapping row 7-8
            if x % 2 == 0:
                frame.vline(x, top_edge, 3 if gap < 1 else 2, C.YELLOW)
            else:
                length = 3 if gap < 1 else 2
                frame.vline(x, bottom_edge - length + 1, length, C.YELLOW)
        # the slider, with a pull tab trailing behind it
        x0 = round(sx) - 2
        frame.rect(x0, 5, 5, 6, C.WHITE, fill=True)
        frame.vline(x0 + 5, 6, 4, C.WHITE)
        frame.rect(x0 - 5, 7, 5, 2, C.CYAN, fill=True)
        frame.pixel(x0 - 4, 7, C.BLACK)
        frame.pixel(x0 - 4, 8, C.BLACK)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/zipper.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
