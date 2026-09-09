#!/usr/bin/env python3
"""
Lorenz -- the butterfly attractor, drawing itself.

The classic chaotic system integrated with a plain Euler step and projected
onto the x-z plane, which is the view that shows both lobes. The panel is 6x
wider than it is tall so the wings get squashed, but the two-lobed shape and
the way the trajectory hops between them survive.

Rather than a short comet, a long stretch of path stays lit: the oldest in
blue, the recent past in cyan, the head white. The attractor is traced out
from nothing, then the tail is let go at the same rate the head advances, so
the outline stays readable instead of filling in to a solid slab -- which is
what happened at the first, longer setting. Not seamless -- chaos
does not loop -- but the reset reads as a fresh pen stroke.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53          # device maximum: a longer trace, worth it here
DELAY = 90

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.008
STEPS_PER_FRAME = 70
SETTLE_STEPS = 2000

HEAD = 12
RECENT = 90
EXPIRE = 450         # steps after which the trail is let go


def step(x, y, z):
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z
    return x + dx * DT, y + dy * DT, z + dz * DT


def trajectory(count):
    x, y, z = 0.1, 0.0, 20.0
    for _ in range(SETTLE_STEPS):
        x, y, z = step(x, y, z)
    points = []
    for _ in range(count):
        x, y, z = step(x, y, z)
        points.append((x, y, z))
    return points


def project(point, width, height):
    x, _, z = point
    px = round((x + 22.0) / 44.0 * (width - 1))
    py = round((50.0 - z) / 46.0 * (height - 1))
    return px, py


def build():
    anim = Animation(delay=DELAY)
    points = trajectory(FRAMES * STEPS_PER_FRAME)

    for index in range(FRAMES):
        frame = anim.frame()
        drawn = (index + 1) * STEPS_PER_FRAME
        for i in range(drawn):
            age = drawn - 1 - i
            if age >= EXPIRE:
                continue
            if age < HEAD:
                color = C.WHITE
            elif age < RECENT:
                color = C.CYAN
            else:
                color = C.BLUE
            frame.pixel(*project(points[i], anim.width, anim.height), color)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/lorenz.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
