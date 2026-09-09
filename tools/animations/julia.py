#!/usr/bin/env python3
"""
Julia -- a fractal morphing as its parameter circles the origin.

For each pixel, iterate z = z^2 + c and colour by how many steps it takes to
escape. Sweeping c round a circle of radius 0.74 walks through the classic
family: connected blobs, dendrites, near-dust and back -- a little inside
the textbook 0.7885 so the thin end of the cycle still shows something. A full circle per loop
makes it seamless.

The panel is much wider than tall, so the complex plane is sampled with a
different scale on each axis -- the set is squashed vertically, but its
filaments and bands read far better than a thin horizontal slice would.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53          # device maximum, so the morph is as smooth as it gets
DELAY = 80

RADIUS = 0.74
MAX_ITER = 22
SCALE_X = 30.0
SCALE_Y = 10.0
DARK_BELOW = 5      # escapes this fast are left black

BANDS = [C.BLUE, C.BLUE, C.BLUE, C.CYAN, C.CYAN, C.GREEN, C.GREEN,
         C.YELLOW, C.YELLOW, C.RED, C.RED, C.MAGENTA, C.MAGENTA, C.WHITE]


def build():
    anim = Animation(delay=DELAY)
    cx, cy = (anim.width - 1) / 2, (anim.height - 1) / 2

    for index in range(FRAMES):
        frame = anim.frame()
        angle = 2 * math.pi * index / FRAMES
        c = complex(RADIUS * math.cos(angle), RADIUS * math.sin(angle))

        def color_at(x, y):
            z = complex((x - cx) / SCALE_X, (cy - y) / SCALE_Y)
            n = 0
            while n < MAX_ITER and (z.real * z.real + z.imag * z.imag) < 4.0:
                z = z * z + c
                n += 1
            if n >= MAX_ITER or n < DARK_BELOW:
                return C.BLACK
            return BANDS[min(n - DARK_BELOW, len(BANDS) - 1)]

        frame.each(color_at)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/julia.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
