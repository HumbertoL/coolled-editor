#!/usr/bin/env python3
"""
Plasma -- interfering sine waves, banded into the 8-color palette.

Three sine fields at different angles and speeds are summed and mapped onto a
cyclic color ramp. With only 8 colors the smooth field breaks into hard
contour bands, and those bands drift and fold through each other. The banding
is the point: on a continuous display this would be a soft gradient, but the
panel's quantization turns it into moving topography.

The loop is seamless. Every phase term advances by a whole multiple of 2*pi
across the frame count, so the last frame flows back into the first.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 100

# Cyclic so the ramp has no seam where it wraps.
RAMP = [C.BLUE, C.CYAN, C.WHITE, C.YELLOW, C.RED, C.MAGENTA]


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        # One full turn over the animation: the source of the seamless loop.
        phase = 2 * math.pi * index / FRAMES
        frame = anim.frame()

        def field(x, y, phase=phase):
            value = (
                math.sin(x * 0.13 + phase)
                + math.sin(y * 0.31 - phase)
                + math.sin((x + y * 2) * 0.07 + phase * 2)
            ) / 3.0
            # -1..1 into 0..1 for the ramp
            return C.ramp(RAMP, (value + 1) / 2)

        frame.each(field)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/plasma.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
