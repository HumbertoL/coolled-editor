#!/usr/bin/env python3
"""
Donut DVD -- the bouncing screensaver, with a donut.

The DVD logo drifted diagonally, bounced off every edge, changed colour on
each bounce, and never quite hit the corner while anyone was watching. Same
here, with a frosted, sprinkled donut -- and this one loops seamlessly.

53 is prime, so no whole-pixel velocity brings the donut back to its start
in 53 frames. Instead its position is two triangle waves: horizontally one
out-and-back per loop, vertically four. That is ten bounces a loop, and with
five frosting colours the palette comes round too. The phases were found by
search so that it grazes a corner by one pixel mid-loop and misses.
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
SPRINKLE_COLORS = [C.WHITE, C.YELLOW, C.CYAN, C.GREEN, C.MAGENTA]
FROSTING = [C.MAGENTA, C.YELLOW, C.CYAN, C.GREEN, C.WHITE]

X_CYCLES, Y_CYCLES = 1, 4            # out-and-backs per loop
X_PHASE, Y_PHASE = 0.27, 0.18        # found by search: one-pixel corner miss


def triangle(u):
    """0 -> 1 -> 0 over one unit of u."""
    u %= 1.0
    return 2 * u if u < 0.5 else 2 - 2 * u


def bounces_by(u, start_phase):
    """How many turning points the triangle wave has passed since the start."""
    return int(2 * (u + start_phase)) - int(2 * start_phase)


def build():
    anim = Animation(delay=DELAY)
    w, h = len(DONUT[0]), len(DONUT)
    x_max, y_max = anim.width - w, anim.height - h

    for index in range(FRAMES):
        frame = anim.frame()
        ux, uy = index * X_CYCLES / FRAMES, index * Y_CYCLES / FRAMES
        x = round(triangle(ux + X_PHASE) * x_max)
        y = round(triangle(uy + Y_PHASE) * y_max)
        bounces = bounces_by(ux, X_PHASE) + bounces_by(uy, Y_PHASE)
        frosting = FROSTING[bounces % len(FROSTING)]
        for r, line in enumerate(DONUT):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(x + c, y + r, frosting)
        for k, (c, r) in enumerate(SPRINKLES):
            color = SPRINKLE_COLORS[(k + bounces) % len(SPRINKLE_COLORS)]
            if color != frosting:
                frame.pixel(x + c, y + r, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/donut_dvd.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
