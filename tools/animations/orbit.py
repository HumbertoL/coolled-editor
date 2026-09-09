#!/usr/bin/env python3
"""
Orbit -- a toy solar system.

Five planets circle a sun, on ellipses squashed to fit the panel's height.
Their periods are 6, 4, 3, 2 and 1 orbits per loop, which keeps Kepler
roughly honest (outer is slower) and makes the whole thing seamless. A planet
on the far half of its orbit is drawn before the sun, so it disappears behind
it; on the near half it passes in front.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 100

# (rx, ry, orbits per loop, phase, colour, size)
PLANETS = [
    (9, 2.5, 6, 0.0, C.CYAN, 1),
    (15, 4.0, 4, 1.2, C.YELLOW, 1),
    (23, 5.5, 3, 2.5, C.BLUE, 2),
    (31, 6.5, 2, 4.0, C.RED, 1),
    (44, 6.5, 1, 5.3, C.MAGENTA, 2),
]


def draw_planet(frame, x, y, color, size, ringed=False):
    if size == 1:
        frame.pixel(round(x), round(y), color)
    else:
        frame.rect(round(x) - 1, round(y) - 1, 2, 2, color, fill=True)
        if color == C.BLUE:
            frame.pixel(round(x), round(y) - 1, C.GREEN)
    if ringed:
        frame.hline(round(x) - 4, round(y), 3, C.CYAN)
        frame.hline(round(x) + 1, round(y), 3, C.CYAN)


def draw_sun(frame, cx, cy):
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if abs(dx) + abs(dy) <= 2:
                frame.pixel(cx + dx, cy + dy, C.YELLOW)
    frame.pixel(cx, cy, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    cx, cy = anim.width // 2, anim.height // 2 - 1

    for index in range(FRAMES):
        frame = anim.frame()
        near, far = [], []
        for rx, ry, orbits, phase, color, size in PLANETS:
            angle = 2 * math.pi * orbits * index / FRAMES + phase
            x = cx + rx * math.cos(angle)
            y = cy + ry * math.sin(angle)
            (near if math.sin(angle) >= 0 else far).append((x, y, color, size))
        for x, y, color, size in far:
            draw_planet(frame, x, y, color, size, ringed=color == C.MAGENTA)
        draw_sun(frame, cx, cy)
        for x, y, color, size in near:
            draw_planet(frame, x, y, color, size, ringed=color == C.MAGENTA)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/orbit.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
