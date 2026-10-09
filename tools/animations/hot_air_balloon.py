#!/usr/bin/env python3
"""
Hot-air balloon -- a striped balloon bobbing over rolling hills.

The balloon sways a pixel side to side and bobs up and down on one 53-frame
period, so the loop is seamless. Its envelope is red and yellow bands shaded
by distance from the middle, with a basket on ropes below. Clouds drift past
at 96 pixels per loop and the hills stay put, so the scene reads as the
balloon moving against the wind.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
RX, RY = 6.0, 6.0
CLOUDS = [(10, 3), (44, 1), (74, 4)]


def draw_sky(frame, index):
    shift = round(96 * index / FRAMES)
    for base_x, y in CLOUDS:
        x = (base_x - shift) % 96
        for dx in range(6):
            frame.pixel(x + dx, y + (1 if dx in (0, 5) else 0), C.WHITE)
    for x in range(96):
        height = 2 + round(2 * math.sin(x / 9.0) + 1.5 * math.sin(x / 4.0 + 1))
        frame.vline(x, 16 - height, height, C.GREEN)


def draw_balloon(frame, index):
    theta = 2 * math.pi * index / FRAMES
    cx = 30 + round(6 * math.sin(theta))
    cy = 5 + round(1.2 * math.sin(theta + 0.8))
    for y in range(cy - 6, cy + 2):
        for x in range(cx - 7, cx + 8):
            dx = (x - cx) / RX
            dy = (y - cy) / RY
            if dx * dx + dy * dy > 1.0:
                continue
            band = int((x - (cx - 7)) / 3.5) % 2
            shade = dx * dx + dy * dy > 0.6
            colour = C.MAGENTA if shade else (C.RED if band == 0 else C.YELLOW)
            frame.pixel(x, y, colour)
    frame.rect(cx - 2, cy + 2, 5, 3, C.BLUE, fill=True)
    frame.pixel(cx - 2, cy + 2, C.YELLOW)
    frame.pixel(cx + 2, cy + 2, C.YELLOW)
    frame.vline(cx - 3, cy + 1, 1, C.WHITE)
    frame.vline(cx + 3, cy + 1, 1, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_sky(frame, index)
        draw_balloon(frame, index)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/hot_air_balloon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
