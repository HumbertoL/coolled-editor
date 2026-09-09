#!/usr/bin/env python3
"""
Helix -- two strands winding round each other, with rungs between.

Both strands are the same sine wave a half-period apart, so they cross twice
per wavelength. The rungs joining them are drawn only where the strands are
far enough apart to have something to join, which is what makes it read as
three-dimensional: the ladder appears to twist edge-on and vanish at each
crossing.

Depth cue: whichever strand is currently in front is drawn white, the other
blue, and they swap at every crossing. Rungs are cyan. Seamless -- the phase
advances one whole turn across the frame count.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 85

WAVELENGTH = 32
AMPLITUDE = 6.0
RUNG_SPACING = 4
RUNG_MIN_GAP = 3


def build():
    anim = Animation(delay=DELAY)
    mid = (anim.height - 1) / 2

    for index in range(FRAMES):
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        for x in range(anim.width):
            angle = 2 * math.pi * x / WAVELENGTH + phase
            a = mid + AMPLITUDE * math.sin(angle)
            b = mid + AMPLITUDE * math.sin(angle + math.pi)

            # cos tells us which strand is nearer the viewer.
            front, back = (a, b) if math.cos(angle) >= 0 else (b, a)

            if x % RUNG_SPACING == 0 and abs(a - b) >= RUNG_MIN_GAP:
                lo, hi = sorted((a, b))
                for y in range(math.ceil(lo), math.floor(hi) + 1):
                    frame.pixel(x, y, C.CYAN)

            frame.pixel(x, round(back), C.BLUE)
            frame.pixel(x, round(front), C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/helix.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
