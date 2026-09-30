#!/usr/bin/env python3
"""
Hypno Spiral -- two eyes' worth of spirals turning in opposite directions.

Each of two spirals, centred on its own half of the panel, is computed per
pixel from a polar function: the arm phase is the angle plus the radius, so
the bands curl into the middle. The left one winds clockwise and the right
one the other way, and the eight-color palette slides through the bands as
they turn. A slow pulse squeezes and relaxes the arm spacing. Every term is
periodic in the frame count, so the loop has no seam.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90
ARMS = 2
CENTERS = [(24.0, 7.5, 1), (72.0, 7.5, -1)]
# Black is in the cycle so every lap has a dark band between the bright ones.
PALETTE = [C.BLACK, C.BLUE, C.CYAN, C.WHITE, C.YELLOW, C.RED, C.MAGENTA, C.GREEN]


def shade(x, y, t):
    # Nearest spiral owns the pixel; the seam between them is at x = 48.
    cx, cy, spin = CENTERS[0] if x < 48 else CENTERS[1]
    dx, dy = x + 0.5 - cx, y + 0.5 - cy
    radius = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    pulse = 1.0 + 0.2 * math.sin(2 * math.pi * t)
    # Phase is in color steps: the angle winds it, the radius unwinds it.
    phase = ARMS * angle / (2 * math.pi) * spin * 4 + radius * 0.5 * pulse
    phase -= spin * t * 8        # eight steps per loop, so the palette laps once
    index = int(math.floor(phase)) % 8
    return PALETTE[index]


def build():
    anim = Animation(delay=DELAY)
    for i in range(FRAMES):
        t = i / FRAMES
        frame = anim.frame()
        frame.each(lambda x, y, t=t: shade(x, y, t))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hypno_spiral.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
