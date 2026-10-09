#!/usr/bin/env python3
"""
Seasons tree -- four trees, one year.

Four fractal trees (a binary recursion, each fork 0.72x shorter and 0.55 rad
apart) grow bough by bough, burst into magenta blossom and shed petals,
turn summer green, then autumn yellow and red with leaves drifting down, and
stand bare under a white ground and snow. Each tree sways on its own phase of
a two-cycle breeze.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 140
TREES = [(12, 0.0, 0.30), (36, 0.4, 0.38), (60, 0.8, 0.26), (84, 1.2, 0.34)]


def branches(x, y, length, angle, depth, sway, out, maxdepth):
    if depth > maxdepth or length < 0.8:
        return
    ex, ey = x + length * math.sin(angle), y - length * math.cos(angle)
    out.append((x, y, ex, ey, depth))
    spread = 0.55
    branches(ex, ey, length * 0.72, angle - spread + sway, depth + 1, sway, out, maxdepth)
    branches(ex, ey, length * 0.72, angle + spread + sway, depth + 1, sway, out, maxdepth)


def season(index):
    """Colours of (leaf, fall) for the phase of the year; None = bare."""
    if index < 12:
        return None, None, index / 12            # growing
    if index < 20:
        return C.MAGENTA, None, 1.0               # spring blossom
    if index < 30:
        return C.GREEN, None, 1.0                 # summer
    if index < 40:
        return C.YELLOW if index % 2 else C.RED, C.RED, 1.0   # autumn
    if index < 50:
        return None, None, 1.0                    # winter, bare, snowing
    return None, None, 1.0


def build():
    anim = Animation(delay=DELAY)
    rng = random.Random(4)
    flakes = [(rng.randrange(96), rng.randrange(16)) for _ in range(22)]
    for index in range(FRAMES):
        frame = anim.frame()
        leaf, _, grow = season(index)
        winter = index >= 40
        for tx, phase, size in TREES:
            sway = 0.12 * math.sin(2 * math.pi * (index / FRAMES) * 2 + phase)
            segs = []
            maxdepth = 1 + int(grow * 4.99)
            branches(tx, 15, 4.2 * (0.4 + 0.6 * grow), 0.0, 0, sway, segs, maxdepth)
            for x0, y0, x1, y1, depth in segs:
                frame.line(round(x0), round(y0), round(x1), round(y1), C.RED if depth < 2 else C.YELLOW)
            if leaf and grow >= 1.0:
                for x0, y0, x1, y1, depth in segs:
                    if depth >= 3:
                        color = leaf if index < 30 or (round(x1) + round(y1)) % 3 else C.RED
                        frame.pixel(round(x1), round(y1), color)
                        frame.pixel(round(x1) + 1, round(y1), color)
                        frame.pixel(round(x1), round(y1) - 1, color)
        # Ground: green, then a white blanket of snow.
        frame.hline(0, 15, 96, C.WHITE if winter else C.GREEN)
        # Falling things: petals in spring, leaves in autumn, snow in winter.
        fall_color = C.MAGENTA if 12 <= index < 20 else (C.RED if 30 <= index < 40 else (C.WHITE if winter else None))
        if fall_color:
            for i, (x, y0) in enumerate(flakes):
                fy = (y0 + index * (1 + i % 2)) % 15
                frame.pixel((x + int(2 * math.sin(index / 3 + i))) % 96, fy, fall_color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/seasons_tree.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
