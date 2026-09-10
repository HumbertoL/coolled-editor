#!/usr/bin/env python3
"""
Gears -- a meshing gear train.

Three toothed wheels in a row, each meshing with the next so they counter-
rotate at speeds inversely proportional to their tooth counts. Each gear is a
rim, a set of radial teeth, a hub and spokes; the spokes are what make the
rotation legible on so few pixels.

Seamless: over the loop the first gear turns a whole number of times, and the
tooth-count ratios are chosen so the others do too (2, 3 and 4 turns).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90

# (cx, cy, radius, teeth, turns_over_loop, direction, rim_color, hub_color)
GEARS = [
    (24, 8, 6.5, 12, 2, +1, C.YELLOW, C.WHITE),
    (43, 8, 4.3, 8, -3, -1, C.CYAN, C.WHITE),
    (57, 8, 3.2, 6, +4, +1, C.MAGENTA, C.WHITE),
]


def dot(frame, x, y, color):
    frame.pixel(int(round(x)), int(round(y)), color)


def draw_gear(frame, cx, cy, radius, teeth, angle, rim, hub):
    # Rim.
    steps = int(2 * math.pi * radius * 2)
    for i in range(steps):
        a = 2 * math.pi * i / steps
        dot(frame, cx + radius * math.cos(a), cy + radius * math.sin(a), rim)
    # Teeth.
    for t in range(teeth):
        a = angle + 2 * math.pi * t / teeth
        for rr in (radius + 1, radius + 1.8):
            dot(frame, cx + rr * math.cos(a), cy + rr * math.sin(a), rim)
    # Hub + spokes.
    dot(frame, cx, cy, hub)
    for t in range(teeth):
        a = angle + 2 * math.pi * t / teeth
        if t % 2:
            continue
        for rr in range(1, int(radius) - 1):
            dot(frame, cx + rr * math.cos(a), cy + rr * math.sin(a), hub)


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        for cx, cy, radius, teeth, turns, _dirn, rim, hub in GEARS:
            angle = 2 * math.pi * turns * t
            draw_gear(frame, cx, cy, radius, teeth, angle, rim, hub)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/gears.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
