#!/usr/bin/env python3
"""
Sierpinski -- the chaos game.

Three corners. Start anywhere. Roll a die: move halfway toward the corner it
names, plot the point, repeat. Nothing about that rule mentions triangles,
yet after a few thousand throws the Sierpinski gasket is sitting there with
its holes in the right places. Each point is coloured by the corner it just
moved toward, so the three sub-triangles come out in three colours.

Sixty throws a frame, accumulating; the shape is squashed to the panel but
the self-similarity survives.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 3
PER_FRAME = 60
CORNERS = [(1.0, 15.0), (94.0, 15.0), (47.5, 0.0)]
COLORS = [C.RED, C.GREEN, C.CYAN]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    x, y = 30.0, 8.0
    points = []
    for _ in range(20):                       # burn in so the first points are on the gasket
        k = rng.randrange(3)
        x, y = (x + CORNERS[k][0]) / 2, (y + CORNERS[k][1]) / 2
    for index in range(FRAMES):
        for _ in range(PER_FRAME):
            k = rng.randrange(3)
            x, y = (x + CORNERS[k][0]) / 2, (y + CORNERS[k][1]) / 2
            points.append((round(x), round(y), k))
        frame = anim.frame()
        for px, py, k in points:
            frame.pixel(px, py, COLORS[k])
        # The newest point in white so the process stays visible.
        px, py, _ = points[-1]
        frame.pixel(px, py, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/sierpinski.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
