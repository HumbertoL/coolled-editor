#!/usr/bin/env python3
"""
Lightning -- a storm at night.

A ragged cloud base sits along the top in blue. Every so often a bolt walks
down from it: a random walk that jags sideways as it falls, with a couple of
short branches. The strike frame is white and lights the cloud up with it;
the next two frames show the bolt cooling through cyan to blue, then dark.

The first bolt flickers -- two strike frames back to back -- because real ones
do, and one flicker in three sells it more than making them all flash.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 80
SEED = 3

CLOUD_ROWS = 2
STRIKES = [(3, 0), (4, 0), (11, 1), (17, 2), (18, 2)]   # (frame, bolt id)
BOLT_STARTS = [30, 72, 52]


def make_bolt(rng, x):
    points = []
    y = CLOUD_ROWS
    while y < 16:
        points.append((x, y))
        x += rng.choice((-2, -1, -1, 0, 0, 1, 1, 2))
        if rng.random() < 0.3:
            points.append((x, y))
        y += 1
    # A couple of side branches off the upper half.
    for _ in range(2):
        bx, by = points[rng.randrange(2, len(points) // 2)]
        direction = rng.choice((-1, 1))
        for k in range(rng.randrange(3, 6)):
            bx += direction
            by += 1 if k % 2 else 0
            points.append((bx, by))
    return points


def build():
    rng = random.Random(SEED)
    bolts = [make_bolt(rng, x) for x in BOLT_STARTS]
    cloud_depth = [rng.choice((1, 1, 2, 2, 3)) for _ in range(96)]
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()
        flash = any(index == f for f, _ in STRIKES)
        for x, depth in enumerate(cloud_depth):
            for y in range(depth):
                frame.pixel(x, y, C.WHITE if flash and y == depth - 1 else
                            C.CYAN if flash else C.BLUE)
        for strike_frame, bolt_id in STRIKES:
            age = index - strike_frame
            if age == 0:
                color = C.WHITE
            elif age == 1:
                color = C.CYAN
            elif age == 2:
                color = C.BLUE
            else:
                continue
            for x, y in bolts[bolt_id]:
                frame.pixel(x, y, color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lightning.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
