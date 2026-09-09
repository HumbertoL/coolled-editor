#!/usr/bin/env python3
"""
Metaballs -- blobs that merge and part.

Each blob contributes a field falling off as 1/distance-squared; where two
fields overlap they sum, so the blobs bulge toward each other and fuse into a
neck before separating. Thresholding that continuous field into four palette
bands turns the smooth falloff into concentric contours, which is what gives
the blobs their layered, lava-lamp look on a display with no gradients.

Seamless: every blob travels a closed elliptical path once per loop.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 95

# (centre x, centre y, x radius, y radius, turns per loop, phase, strength)
BLOBS = [
    (30, 8, 22, 5, 1, 0.0, 18),
    (62, 8, 18, 6, 1, math.pi, 15),
    (48, 8, 30, 4, 2, math.pi / 2, 11),
]

BANDS = [(1.9, C.WHITE), (1.25, C.YELLOW), (0.85, C.MAGENTA), (0.58, C.BLUE)]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        turn = 2 * math.pi * index / FRAMES
        centres = [
            (
                cx + rx * math.cos(turns * turn + phase),
                cy + ry * math.sin(turns * turn + phase),
                strength,
            )
            for cx, cy, rx, ry, turns, phase, strength in BLOBS
        ]

        frame = anim.frame()

        def field(x, y, centres=centres):
            total = 0.0
            for bx, by, strength in centres:
                # Squash x so the blobs stay round-ish on a 6:1 panel.
                dx = (x - bx) * 0.42
                dy = y - by
                total += strength / (dx * dx + dy * dy + 1.0)
            for threshold, color in BANDS:
                if total >= threshold:
                    return color
            return C.BLACK

        frame.each(field)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/metaballs.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
