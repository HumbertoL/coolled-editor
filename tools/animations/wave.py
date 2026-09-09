#!/usr/bin/env python3
"""
Wave -- a travelling swell with its own reflection.

Two sine components of different wavelengths sum into a crest that moves and
changes shape as they drift in and out of step, so it never looks like a rigid
shape sliding past. Below the surface the water is filled in, and a mirrored
copy above the midline gives it a reflection.

Colour comes from height rather than position: crests white, mid water cyan,
troughs blue. Seamless -- both components advance a whole number of cycles.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80


def build():
    anim = Animation(delay=DELAY)
    mid = anim.height / 2

    for index in range(FRAMES):
        turn = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for x in range(anim.width):
            swell = (
                3.0 * math.sin(2 * math.pi * x / 48 - turn)
                + 1.6 * math.sin(2 * math.pi * x / 19 + 2 * turn)
            )
            surface = mid + swell

            for y in range(anim.height):
                if y < surface - 1:
                    continue
                depth = y - surface
                if depth < 0.6:
                    color = C.WHITE          # the crest line itself
                elif depth < 3:
                    color = C.CYAN
                else:
                    color = C.BLUE
                frame.pixel(x, y, color)

            # Reflection above the surface, dimmer and only near the crest.
            mirror = round(2 * mid - surface) - 1
            if 0 <= mirror < anim.height and swell > 1.0:
                frame.pixel(x, mirror, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/wave.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
