#!/usr/bin/env python3
"""
Doppler effect -- a moving source and the wavefronts it leaves behind.

The source crosses the panel at 2.2 pixels a frame and emits a circular
wavefront every fourth frame; each front then grows at 3.2 pixels a frame
around the point it was emitted from. Ahead of the source the fronts pile up
about 4 pixels apart, behind it they trail out to 21 -- the pitch you hear
rise and fall as a siren passes. Fronts cool from white through cyan to blue
and vanish after 24 frames. The source enters and leaves off-panel, and
fronts from the previous pass are carried over, so the loop is seamless.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
WAVE_SPEED = 3.2
EMIT_EVERY = 4
MAX_AGE = 24
SOURCE_Y = 7.5


def source_x(index):
    return -10 + 116 * (index % FRAMES) / FRAMES


def fronts(index):
    """(centre x, radius, age) of every live wavefront at this frame."""
    out = []
    for age in range(1, MAX_AGE + 1):
        emitted = (index - age) % FRAMES
        if emitted % EMIT_EVERY == 0:
            out.append((source_x(emitted), WAVE_SPEED * age, age))
    return out


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for centre, radius, age in sorted(fronts(index), key=lambda f: -f[2]):
            colour = C.WHITE if age <= 5 else C.CYAN if age <= 12 else C.BLUE
            for y in range(16):
                for x in range(96):
                    distance = math.hypot(x - centre, y - SOURCE_Y)
                    if abs(distance - radius) < 0.5:
                        frame.pixel(x, y, colour)
        sx = round(source_x(index))
        frame.rect(sx - 1, 6, 3, 4, C.YELLOW, fill=True)
        frame.rect(sx, 7, 1, 2, C.RED, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/doppler.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
