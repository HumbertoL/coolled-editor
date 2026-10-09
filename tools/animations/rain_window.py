#!/usr/bin/env python3
"""
Rain window -- night bus, wet glass.

Out-of-focus city lights (3x3 soft blobs in yellow, red, magenta and cyan)
pulse behind a misted pane while 18 droplets slide down it, a white head with
a cyan-then-blue trail. Each drop travels a whole number of panel heights per
loop, so every one lands back where it started and the loop is seamless.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 52
DELAY = 110
LIGHTS = [(6, 5, C.YELLOW), (17, 10, C.RED), (29, 4, C.MAGENTA), (41, 11, C.YELLOW),
          (53, 6, C.CYAN), (66, 3, C.RED), (77, 10, C.YELLOW), (89, 6, C.MAGENTA)]


def build():
    rng = random.Random(13)
    drops = []
    for _ in range(18):
        # Whole laps in the loop (k = 1..4), so each drop returns to its start.
        drops.append((rng.randrange(96), rng.randrange(16), rng.choice((1, 2, 2, 3, 4))))
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()
        # Out-of-focus city lights: 3x3 soft blobs that pulse, one dimming now and then.
        for i, (x, y, color) in enumerate(LIGHTS):
            if math.sin(2 * math.pi * (t * (1 + i % 2) + i / 8)) > -0.6:
                frame.rect(x - 1, y - 1, 3, 3, color, fill=True)
            else:
                frame.pixel(x, y, color)
        # Glass: sparse blue mist so the pane reads as wet.
        for x in range(1, 96, 6):
            for y in range(2, 16, 6):
                frame.pixel(x + (y // 6) * 3, y, C.BLUE)
        # Drops slide down leaving a trail, wrapping top to bottom.
        for x, y0, k in drops:
            head = (y0 + 16 * k * t) % 16
            frame.pixel(x, head, C.WHITE)
            for n in (1, 2, 3, 4):
                frame.pixel(x, (head - n) % 16, C.CYAN if n < 3 else C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rain_window.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
