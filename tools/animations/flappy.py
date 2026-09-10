#!/usr/bin/env python3
"""
Flappy -- a little bird threading gaps in scrolling pipes.

The bird holds a fixed column while green pipes scroll in from the right, each
with a gap to clear. The world is a ring exactly as long as the scroll travels
over the loop, so the pipes stream past and wrap seamlessly. The bird's height
is a scripted bob that dips and flaps to line up with each oncoming gap, wing
beating up and down as it goes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90

W, H = 96, 16
BIRD_X = 22
GROUND_Y = 15
SCROLL = 3
RING = FRAMES * SCROLL            # world wraps after exactly one loop

# Pipes placed around the ring: (world_x, gap_center).
PIPES = [(30, 6), (85, 10), (140, 5)]
GAP = 7

# The frame at which each pipe reaches the bird's column, paired with that
# pipe's gap centre. The bird's height glides through these so it is always in
# the gap when a pipe arrives. Cyclic over FRAMES, so the loop stays seamless.
GAP_KEYS = [(3, 6), (21, 10), (39, 5)]


def bird_y(index):
    n = len(GAP_KEYS)
    for k in range(n):
        f0, y0 = GAP_KEYS[k]
        f1, y1 = GAP_KEYS[(k + 1) % n]
        span = (f1 - f0) % FRAMES
        offset = (index - f0) % FRAMES
        if offset <= span:
            t = offset / span
            t = (1 - math.cos(math.pi * t)) / 2      # ease in/out
            return y0 + (y1 - y0) * t
    return GAP_KEYS[0][1]


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        frame = anim.frame()
        scroll = index * SCROLL

        # Ground first (scrolls left).
        for x in range(0, W, 3):
            frame.pixel((x - scroll) % W, GROUND_Y, C.YELLOW)

        for world_x, gc in PIPES:
            sx = (world_x - scroll) % RING
            if sx >= W:
                continue
            for y in range(0, gc - GAP // 2):
                frame.pixel(sx, y, C.GREEN)
                frame.pixel(sx + 1, y, C.GREEN)
            for y in range(gc + GAP // 2, GROUND_Y):
                frame.pixel(sx, y, C.GREEN)
                frame.pixel(sx + 1, y, C.GREEN)

        # Bird height, pinned to the gap centres so it threads each pipe.
        biy = int(round(bird_y(index)))

        frame.pixel(BIRD_X, biy, C.YELLOW)
        frame.pixel(BIRD_X + 1, biy, C.YELLOW)
        frame.pixel(BIRD_X + 2, biy, C.RED)             # beak
        frame.pixel(BIRD_X + 1, biy - 1, C.YELLOW)      # head
        wing_up = (index % 2 == 0)
        frame.pixel(BIRD_X, biy - 1 if wing_up else biy + 1, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/flappy.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
