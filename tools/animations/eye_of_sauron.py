#!/usr/bin/env python3
"""
The Eye of Sauron -- lidless, wreathed in flame.

A wide ellipse of fire -- yellow toward the centre, red at the rim, flickering
every frame -- with a black vertical slit for a pupil that slides slowly from
side to side as the Eye searches. Flames lick outward past the rim. The
pupil's sweep is one full cycle per loop, so the search is seamless even
though the fire is not, and fire never is.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 666
CX, CY = 47.5, 7.5
RX, RY = 24.0, 6.5
PUPIL_SWEEP = 9.0


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES
        pupil_x = CX + PUPIL_SWEEP * math.sin(2 * math.pi * t)
        for y in range(anim.height):
            for x in range(anim.width):
                dx, dy = (x - CX) / RX, (y - CY) / RY
                r = math.hypot(dx, dy)
                if r <= 1.0:
                    # Slit pupil: narrow at the tips, two pixels wide at the middle.
                    slit = 1.2 * (1 - abs(dy) ** 1.5) + 0.2
                    if abs(x - pupil_x) < slit:
                        continue
                    heat = (1 - r) + rng.uniform(-0.25, 0.25)
                    frame.pixel(x, y, C.YELLOW if heat > 0.45 else C.RED if heat > -0.05 else C.RED)
                elif r <= 1.25 and rng.random() < (1.25 - r) * 2.2:
                    frame.pixel(x, y, C.RED if rng.random() < 0.7 else C.YELLOW)
        # Flames rising off the top rim.
        for _ in range(14):
            fx = round(CX + rng.uniform(-RX * 0.8, RX * 0.8))
            top = CY - RY * math.sqrt(max(0.0, 1 - ((fx - CX) / RX) ** 2))
            frame.pixel(fx, round(top) - rng.randint(1, 2), C.RED if rng.random() < 0.6 else C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/eye_of_sauron.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
