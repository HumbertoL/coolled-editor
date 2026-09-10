#!/usr/bin/env python3
"""
Snow -- drifting snowfall with parallax.

Three depth layers of flakes fall at different speeds and sway sideways as they
go; nearer flakes are white, farther ones cyan then blue, so depth reads through
the palette instead of size. A thin snow bank sits along the floor.

Seamless: each flake falls exactly one panel height (a whole number of heights)
over the loop and its horizontal sway completes whole cycles, so every flake
returns to where it began.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
W, H = 96, 16

# (count, fall_heights_over_loop, sway_amp, sway_cycles, color)
LAYERS = [
    (14, 1, 2.2, 1, C.WHITE),
    (18, 1, 1.6, 2, C.CYAN),
    (22, 1, 1.0, 1, C.BLUE),
]


def seed(layer_index, count):
    rng = random.Random(100 + layer_index)
    return [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, 1))
            for _ in range(count)]


def build():
    anim = Animation(delay=DELAY)
    layers = [(seed(i, cnt), fh, amp, cyc, col)
              for i, (cnt, fh, amp, cyc, col) in enumerate(LAYERS)]

    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()

        # Snow bank along the floor.
        for x in range(W):
            top = 15 - (1 if (x * 7) % 5 else 0)
            frame.pixel(x, 15, C.WHITE)
            if top < 15:
                frame.pixel(x, top, C.WHITE)

        for flakes, fall_h, amp, cyc, color in layers:
            for x0, y0, ph in flakes:
                y = (y0 + fall_h * H * t) % H
                x = (x0 + amp * math.sin(2 * math.pi * (cyc * t + ph))) % W
                if y < 15:
                    frame.pixel(x, y, color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/snow.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
