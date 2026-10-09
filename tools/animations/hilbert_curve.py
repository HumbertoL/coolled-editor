#!/usr/bin/env python3
"""
Hilbert curve -- a space-filling curve drawing itself across the panel.

Six order-3 Hilbert curves, one per 16x16 tile at a 2px pitch, chained end to
start so they form one unbroken path of 384 points. Each tile's curve enters
top-left and leaves top-right, so a single 2px step joins it to the next.
A white head draws the path in about five seconds; then colour bands stream
along the finished curve, showing how a path that never crosses itself still
visits every point of the square.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
ORDER = 8            # points per side of one tile: 2**3
DRAW_FRAMES = 36
BAND = 6             # points per colour band
RAINBOW = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]


def d2xy(n, d):
    """Point ``d`` along an order-log2(n) Hilbert curve, from (0,0) to (n-1,0)."""
    x = y = 0
    s, t = 1, d
    while s < n:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        t //= 4
        s *= 2
    return x, y


def path():
    points = []
    for tile in range(6):
        for d in range(ORDER * ORDER):
            x, y = d2xy(ORDER, d)
            points.append((tile * 16 + 2 * x, 2 * y))
    return points


def build():
    points = path()
    total = len(points)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < DRAW_FRAMES:
            head = round(total * (index + 1) / DRAW_FRAMES)
            shift = 0
        else:
            head = total
            shift = (index - DRAW_FRAMES) * 3
        for i in range(1, head):
            colour = RAINBOW[((i - shift) // BAND) % len(RAINBOW)] if index >= DRAW_FRAMES else C.BLUE
            if index < DRAW_FRAMES and head - i < 24:
                colour = C.CYAN
            frame.line(*points[i - 1], *points[i], colour)
        if index < DRAW_FRAMES:
            frame.pixel(*points[head - 1], C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hilbert_curve.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
