#!/usr/bin/env python3
"""
Spirograph -- a hypotrochoid drawn by a pen in a rolling gear.

A small gear of radius r rolls inside a fixed ring of radius R with the pen at
offset d from the rolling centre; the pen traces a closed rosette. The full
curve is drawn faintly in blue for the whole loop, while a bright comet head
runs around it -- white nucleus, cyan tail -- completing exactly one lap over
the animation.

Seamless: the head parameter goes from 0 to the curve's full closing period
across the frames, and the head position is periodic in that period.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

R = 5.0              # fixed ring
r = 3.0              # rolling gear
d = 3.2              # pen offset (smaller -> a cleaner star, fewer inner loops)

CX, CY = 48.0, 8.0
SCALE_X = 3.4        # fill much of the width
SCALE_Y = 1.9        # only mildly squashed vertically, so the star survives

# The curve closes after t sweeps 2*pi * r/gcd(R,r); with R=5, r=3 that is
# 2*pi*3 (three laps of the rolling gear).
PERIOD = 2 * math.pi * 3
TAIL = 10           # comet tail length in samples


def point(t):
    k = (R - r)
    x = k * math.cos(t) + d * math.cos(k / r * t)
    y = k * math.sin(t) - d * math.sin(k / r * t)
    return CX + x * SCALE_X, CY + y * SCALE_Y


def build():
    anim = Animation(delay=DELAY)

    # Precompute the faint full curve once.
    curve = []
    steps = 900
    for i in range(steps):
        curve.append(point(PERIOD * i / steps))

    for index in range(FRAMES):
        frame = anim.frame()
        for x, y in curve:
            frame.pixel(x, y, C.BLUE)

        # Comet head advances one full period over the loop.
        head_t = PERIOD * index / FRAMES
        for k in range(TAIL):
            t = head_t - PERIOD * k / (FRAMES * 3)
            x, y = point(t)
            if k == 0:
                frame.pixel(x, y, C.WHITE)
            elif k < TAIL // 3:
                frame.pixel(x, y, C.WHITE)
            elif k < 2 * TAIL // 3:
                frame.pixel(x, y, C.CYAN)
            else:
                frame.pixel(x, y, C.BLUE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/spirograph.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
