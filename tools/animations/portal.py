#!/usr/bin/env python3
"""
Portal -- a companion cube on an infinite loop.

A blue portal on the left, an orange one on the right, and a cube sliding
between them. It enters the orange portal on the right and emerges from the
blue one on the left at the same moment, clipped at each ring, so it never
leaves the room. The portals shimmer between their two colours. Because the
cube's position is one crossing per loop, it is seamless -- which is also
the joke.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
LEFT_X, RIGHT_X = 10, 85
SPAN = RIGHT_X - LEFT_X
CUBE = ["####", "#..#", "#..#", "####"]
FLOOR = 14


def portal(frame, cx, outer, inner, tick):
    for y in range(FLOOR - 12, FLOOR + 1):
        dy = (y - (FLOOR - 6)) / 6.5
        hw = 2.4 * math.sqrt(max(0.0, 1 - dy * dy))
        for x in (round(cx - hw), round(cx + hw)):
            frame.pixel(x, y, outer if (y + tick) % 3 else inner)
        if abs(dy) < 0.98:
            for x in range(round(cx - hw) + 1, round(cx + hw)):
                if (x + y + tick) % 4 == 0:
                    frame.pixel(x, y, inner)


def cube(frame, x, y, clip_min, clip_max):
    for r, line in enumerate(CUBE):
        for c, ch in enumerate(line):
            px = x + c
            if clip_min <= px < clip_max:
                if ch == "#":
                    frame.pixel(px, y + r, C.WHITE)
                elif (r, c) in ((1, 1), (1, 2), (2, 1), (2, 2)):
                    frame.pixel(px, y + r, C.MAGENTA)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES
        frame.hline(0, FLOOR + 1, anim.width, C.BLUE)
        portal(frame, LEFT_X, C.BLUE, C.CYAN, index)
        portal(frame, RIGHT_X, C.RED, C.YELLOW, index)
        bob = round(math.sin(2 * math.pi * 3 * t))
        y = FLOOR - 4 + bob
        x = LEFT_X + SPAN * t
        cube(frame, round(x), y, LEFT_X, RIGHT_X)
        cube(frame, round(x - SPAN), y, LEFT_X, RIGHT_X)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/portal.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
