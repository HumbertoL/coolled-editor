#!/usr/bin/env python3
"""
Sonar -- rings expanding from the centre.

Rings are drawn on an ellipse stretched horizontally, because a true circle
larger than eight pixels would run off a 16-pixel-tall panel immediately. The
stretch lets three or four rings be in flight at once across the full width.

Age sets the colour, using the palette's one usable brightness ramp: a new
ring is white, then cyan, then blue as it widens and fades. A pinging dot sits
at the origin. Seamless -- ring radius is a sawtooth in the frame index.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 85

CENTER_X, CENTER_Y = 48, 8
RINGS = 3
X_SQUASH = 0.30      # <1 stretches the ring horizontally
# With that squash, a ring of radius r reaches r / X_SQUASH pixels sideways,
# so anything past ~15 is already off the end of a 96-wide panel.
MAX_RADIUS = 16
THICKNESS = 0.9


def ring_color(fraction):
    if fraction < 0.35:
        return C.WHITE
    if fraction < 0.7:
        return C.CYAN
    return C.BLUE


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        progress = index / FRAMES

        for ring in range(RINGS):
            # Evenly spaced phases, wrapping -> a continuous stream of rings.
            fraction = (progress + ring / RINGS) % 1.0
            radius = fraction * MAX_RADIUS
            if radius < 1:
                continue
            color = ring_color(fraction)

            for x in range(anim.width):
                for y in range(anim.height):
                    dx = (x - CENTER_X) * X_SQUASH
                    dy = y - CENTER_Y
                    if abs(math.hypot(dx, dy) - radius) < THICKNESS:
                        frame.pixel(x, y, color)

        # The emitter, blinking as each ring is launched.
        frame.pixel(CENTER_X, CENTER_Y, C.WHITE if index % 8 < 4 else C.CYAN)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sonar.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
