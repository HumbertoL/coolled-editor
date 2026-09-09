#!/usr/bin/env python3
"""
Tunnel -- the demoscene classic, flying down a checkered pipe.

Each pixel's colour comes from its polar coordinates: depth is 1/r, angle is
split into sectors, and a checkerboard on (depth, sector) gives the walls.
Advancing depth each frame flies forward; advancing the sector spins the
tunnel. Both advance an even number of cells over the loop, which keeps the
checker parity intact so the loop is seamless.

The vertical axis is stretched so the tunnel mouth is round on a 6:1 panel,
and the far end fades to black rather than blue because there is no darker
colour to hand.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 70

SECTORS = 12
DEPTH_SCALE = 64.0
STRETCH = 2.6
HOLE = 3.0
FAR = 5.5
FLY_CELLS = 2      # depth cells travelled per loop (even, for parity)
SPIN_CELLS = 2     # sectors turned per loop (even, for parity)


def build():
    anim = Animation(delay=DELAY)
    cx, cy = (anim.width - 1) / 2, (anim.height - 1) / 2

    for index in range(FRAMES):
        frame = anim.frame()
        fly = FLY_CELLS * index / FRAMES
        spin = SPIN_CELLS * index / FRAMES

        def color_at(x, y):
            dx, dy = x - cx, (y - cy) * STRETCH
            r = math.hypot(dx, dy)
            if r < HOLE:
                return C.BLACK
            angle = (math.atan2(dy, dx) / (2 * math.pi)) % 1.0
            d = math.floor(DEPTH_SCALE / r + fly)
            s = math.floor(angle * SECTORS + spin)
            even = (d + s) % 2 == 0
            if r < FAR:
                return C.BLUE if even else C.BLACK
            if d % 4 == 0 and even:
                return C.WHITE
            return C.CYAN if even else C.BLUE

        frame.each(color_at)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tunnel.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
