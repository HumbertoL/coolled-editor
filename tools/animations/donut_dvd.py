#!/usr/bin/env python3
"""
Donut DVD -- the bouncing screensaver, with a donut.

The DVD logo drifted diagonally, bounced off every edge, changed colour on
each bounce, and never quite hit the corner while anyone was watching. Same
here: a frosted donut with sprinkles moves at (2, 1) pixels a frame, the
frosting swaps colour at every wall, and the starting position was chosen
by search so that it comes within one pixel of a corner mid-loop and misses.
53 frames, cut back to the start.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

DONUT = [
    "....#####....",
    "..#########..",
    ".###########.",
    ".####...####.",
    "####.....####",
    ".####...####.",
    ".###########.",
    "..#########..",
    "....#####....",
]
SPRINKLES = [(3, 1), (7, 1), (10, 2), (2, 3), (11, 4), (1, 6), (5, 7), (9, 7), (6, 2)]
SPRINKLE_COLORS = [C.WHITE, C.YELLOW, C.CYAN, C.GREEN]
FROSTING = [C.MAGENTA, C.YELLOW, C.CYAN, C.GREEN, C.RED, C.WHITE]

START_X, START_Y = 40, 0          # grazes a corner by one pixel around frame 36
VX, VY = 2, 1


def build():
    anim = Animation(delay=DELAY)
    w, h = len(DONUT[0]), len(DONUT)
    x_max, y_max = anim.width - w, anim.height - h
    x, y, dx, dy = START_X, START_Y, VX, VY
    bounces = 0

    for index in range(FRAMES):
        frame = anim.frame()
        frosting = FROSTING[bounces % len(FROSTING)]
        for r, line in enumerate(DONUT):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(x + c, y + r, frosting)
        for k, (c, r) in enumerate(SPRINKLES):
            color = SPRINKLE_COLORS[(k + bounces) % len(SPRINKLE_COLORS)]
            if color != frosting:
                frame.pixel(x + c, y + r, color)

        x += dx
        y += dy
        if x <= 0 or x >= x_max:
            dx = -dx
            x = max(0, min(x_max, x))
            bounces += 1
        if y <= 0 or y >= y_max:
            dy = -dy
            y = max(0, min(y_max, y))
            bounces += 1
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/donut_dvd.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
