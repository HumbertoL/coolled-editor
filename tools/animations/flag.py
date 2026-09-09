#!/usr/bin/env python3
"""
Flag -- a rainbow flag rippling on its pole.

Six stripes of two rows each. The ripple is a sine wave in x whose amplitude
grows from nothing at the hoist to two pixels at the fly, so the flag stays
pinned to the pole and flaps at the free end. The wave travels one full
wavelength per loop, which is what makes it seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80

POLE_X = 2
FLAG_X0, FLAG_WIDTH = 4, 72
FLAG_Y0, STRIPE_ROWS = 1, 2
STRIPES = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]
WAVELENGTH = 30
AMPLITUDE = 2.2


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.vline(POLE_X, 0, anim.height, C.WHITE)
        frame.pixel(POLE_X, 0, C.YELLOW)
        phase = 2 * math.pi * index / FRAMES
        for x in range(FLAG_X0, FLAG_X0 + FLAG_WIDTH):
            along = (x - FLAG_X0) / FLAG_WIDTH
            offset = round(AMPLITUDE * along * math.sin(2 * math.pi * (x - FLAG_X0) / WAVELENGTH - phase))
            for stripe, color in enumerate(STRIPES):
                for row in range(STRIPE_ROWS):
                    frame.pixel(x, FLAG_Y0 + stripe * STRIPE_ROWS + row + offset, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/flag.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
