#!/usr/bin/env python3
"""
Fire -- a heat field rising and cooling.

The classic demo-scene effect: seed the bottom row with random heat, then each
step take every cell from the average of the three cells below it minus a
random cooling amount. Heat maps onto the only ramp the palette offers for
this -- red, yellow, white -- with magenta embers at the very coolest lit
level, which reads as the dull glow at the edge of a flame.

Not seamless, and it does not need to be: the field is chaotic enough that the
loop point is invisible. The simulation is warmed up before the first captured
frame so it starts already burning rather than igniting.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

WIDTH, HEIGHT = 96, 16
FRAMES = 24
DELAY = 70
SEED = 17
WARMUP = 30

MAX_HEAT = 36
# Thresholds are deliberately uneven: a narrow white core, a broad red body.
HEAT_COLORS = [(30, C.WHITE), (20, C.YELLOW), (7, C.RED), (3, C.MAGENTA)]


def color_for(heat):
    for threshold, color in HEAT_COLORS:
        if heat >= threshold:
            return color
    return None


def step(heat, rng):
    """One rise-and-cool pass. Row 0 is the floor, so the flame climbs it."""
    nxt = [[0] * WIDTH for _ in range(HEIGHT)]

    # Floor: a few roaring hotspots rather than uniform heat, so the flame
    # develops distinct tongues.
    for x in range(WIDTH):
        roll = rng.random()
        if roll < 0.30:
            nxt[0][x] = rng.randint(MAX_HEAT - 6, MAX_HEAT)
        elif roll < 0.62:
            nxt[0][x] = rng.randint(MAX_HEAT // 2, MAX_HEAT - 8)
        else:
            nxt[0][x] = rng.randint(0, MAX_HEAT // 3)

    for y in range(1, HEIGHT):
        for x in range(WIDTH):
            below = (
                heat[y - 1][(x - 1) % WIDTH]
                + heat[y - 1][x]
                + heat[y - 1][(x + 1) % WIDTH]
            )
            # Divide by slightly more than 3 so heat decays with altitude.
            nxt[y][x] = max(0, below // 3 - rng.randint(2, 7))
    return nxt


def build():
    rng = random.Random(SEED)
    heat = [[0] * WIDTH for _ in range(HEIGHT)]
    for _ in range(WARMUP):
        heat = step(heat, rng)

    anim = Animation(WIDTH, HEIGHT, delay=DELAY)
    for _ in range(FRAMES):
        heat = step(heat, rng)
        frame = anim.frame()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = color_for(heat[y][x])
                if color:
                    # Flip vertically: the simulation grows upward, the panel
                    # addresses rows downward.
                    frame.pixel(x, HEIGHT - 1 - y, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fire.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
