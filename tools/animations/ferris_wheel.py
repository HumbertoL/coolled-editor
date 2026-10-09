#!/usr/bin/env python3
"""
Ferris wheel -- a night fairground ride turning over a small skyline.

Eight cabins ride a wheel that turns one cabin-spacing across the loop, so the
set of cabins is the same at the end as at the start and the loop is seamless.
Cabins stay upright, as they do on a real wheel. White bulbs chase round the
rim, two steps a frame, and stars twinkle over the city on a fixed schedule.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 90
CX, CY, R = 24, 8, 6.5
CABINS = 8
BULBS = 16
CABIN_COLORS = [C.YELLOW, C.MAGENTA, C.CYAN, C.RED, C.GREEN, C.WHITE, C.YELLOW, C.MAGENTA]


def point(angle, radius=R):
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def draw_city(frame, rng):
    frame.hline(0, 15, 96, C.GREEN)
    x = 44
    while x < 96:
        width = rng.randint(4, 7)
        height = rng.randint(4, 11)
        frame.rect(x, 15 - height, width, height, C.BLUE, fill=True)
        for wy in range(15 - height + 2, 14, 3):
            for wx in range(x + 1, x + width - 1, 2):
                if rng.random() < 0.5:
                    frame.pixel(wx, wy, C.YELLOW)
        x += width + 1


def draw_stars(frame, index, stars):
    for k, (sx, sy) in enumerate(stars):
        if (index + k) % 6 < 3:
            frame.pixel(sx, sy, C.WHITE)


def draw_wheel(frame, index):
    spin = 2 * math.pi * index / (FRAMES * CABINS)
    for i in range(32):
        x, y = point(2 * math.pi * i / 32)
        frame.pixel(x, y, C.BLUE)
    for i in range(BULBS):
        x, y = point(2 * math.pi * i / BULBS, R + 1)
        if (i - 2 * index) % 4 == 0:
            frame.pixel(x, y, C.WHITE)
    frame.pixel(CX, CY, C.YELLOW)
    for k in range(CABINS):
        angle = 2 * math.pi * k / CABINS + spin
        x0, y0 = point(angle, 0)
        x1, y1 = point(angle)
        frame.line(round(x0), round(y0), round(x1), round(y1), C.BLUE)
    for k in range(CABINS):
        x, y = point(2 * math.pi * k / CABINS + spin)
        frame.rect(round(x) - 1, round(y) - 1, 2, 2, CABIN_COLORS[k], fill=True)


def build():
    rng = random.Random(7)
    stars = [(rng.randint(46, 94), rng.randint(0, 5)) for _ in range(9)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_stars(frame, index, stars)
        draw_city(frame, random.Random(3))
        draw_wheel(frame, index)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/ferris_wheel.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
