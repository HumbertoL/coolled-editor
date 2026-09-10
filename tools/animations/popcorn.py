#!/usr/bin/env python3
"""
Popcorn -- kernels over heat.

A pan sits on a flickering red element. Kernels jiggle in it, launch on
staggered phases, and pop into a white starburst at the top of their arc
before dropping back in. Each kernel's cycle length divides the loop, so it
runs seamlessly.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 48
DELAY = 90

PAN_LEFT, PAN_RIGHT, PAN_Y = 24, 72, 13

# (x, launch phase, arc height, horizontal drift)
KERNELS = [
    (30, 0.00, 9, +2),
    (38, 0.42, 11, -1),
    (44, 0.13, 12, +1),
    (50, 0.71, 10, -2),
    (56, 0.29, 12, +2),
    (62, 0.55, 9, -1),
    (66, 0.85, 11, +1),
    (35, 0.63, 10, +2),
]

FLIGHT = 0.55  # fraction of the cycle spent airborne


def build():
    anim = Animation(delay=DELAY)

    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()

        # The pan and its handle.
        frame.hline(PAN_LEFT, PAN_Y + 1, PAN_RIGHT - PAN_LEFT, C.WHITE)
        frame.vline(PAN_LEFT, PAN_Y - 1, 3, C.WHITE)
        frame.vline(PAN_RIGHT - 1, PAN_Y - 1, 3, C.WHITE)
        frame.hline(PAN_RIGHT, PAN_Y - 1, 8, C.CYAN)

        # Heat: element flicker under the pan.
        for x in range(PAN_LEFT + 2, PAN_RIGHT - 2):
            if (x * 7 + index * 3) % 5 < 2:
                frame.pixel(x, PAN_Y + 2, C.RED)
            if (x * 5 + index * 3) % 9 == 0:
                frame.pixel(x, PAN_Y + 3, C.YELLOW)

        for kx, phase, height, drift in KERNELS:
            age = (t - phase) % 1.0
            if age >= FLIGHT:
                # In the pan, jiggling with the heat.
                jiggle = 1 if (index + kx) % 4 < 2 else 0
                frame.pixel(kx, PAN_Y - jiggle, C.YELLOW)
                continue
            # Airborne: a parabola from pan lip back to pan lip.
            u = age / FLIGHT
            y = PAN_Y - height * 4 * u * (1 - u)
            x = kx + drift * math.sin(math.pi * u)
            px, py = round(x), round(y)
            if 0.38 < u < 0.62:
                # The pop: a starburst around a yellow heart.
                frame.pixel(px, py, C.YELLOW)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    frame.pixel(px + dx, py + dy, C.WHITE)
                if 0.45 < u < 0.55:
                    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
                        frame.pixel(px + dx, py + dy, C.CYAN)
            else:
                frame.pixel(px, py, C.YELLOW if u < 0.38 else C.WHITE)
                if u >= 0.62:
                    frame.pixel(px + 1, py, C.WHITE)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/popcorn.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
