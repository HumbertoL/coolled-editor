#!/usr/bin/env python3
"""
Lava lamp -- three wax blobs rising and sinking in a glowing base.

Each blob is a metaball: the sum of r^2 / distance^2 over all blobs gives a
field, and the field is quantized onto the palette, so the edge of the wax is
RED, its body MAGENTA and its hot core YELLOW. Every blob's height and sway are
sinusoids of one period over the 53 frames, so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
HEIGHT = 16
# (x0, phase, sway, radius) per blob; heights come from the shared period.
BLOBS = [(20, 0.0, 4.0, 3.6), (46, 2.1, 5.0, 4.2), (72, 4.0, 3.0, 3.2)]


def centres(index):
    theta = 2 * math.pi * index / FRAMES
    out = []
    for x0, phase, sway, radius in BLOBS:
        cx = x0 + sway * math.sin(2 * theta + phase)
        cy = 8 + 6 * math.sin(theta + phase)
        out.append((cx, cy, radius))
    return out


def colour_at(x, y, blobs):
    if y >= HEIGHT - 1:
        return C.BLUE
    total = 0.0
    for cx, cy, radius in blobs:
        d2 = (x - cx) ** 2 + (y - cy) ** 2 + 0.5
        total += radius * radius / d2
    if total < 0.7:
        return C.BLACK
    if total < 1.1:
        return C.RED
    if total < 1.8:
        return C.MAGENTA
    return C.YELLOW


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        blobs = centres(index)
        frame = anim.frame()
        frame.each(lambda x, y, blobs=blobs: colour_at(x, y, blobs))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lava_lamp.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
