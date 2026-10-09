#!/usr/bin/env python3
"""
Paper plane -- a dart tracing a figure eight across a night sky.

The plane follows x = 48 + 36 sin(t), y = 8 + 4 sin(2t) over one loop of 53
frames, so the path closes exactly. It faces the way it is going, and a trail
of its last few positions fades cyan to blue. Clouds drift left at 96 pixels
per loop, so they wrap seamlessly as well.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 80
SPRITE = [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (2, 0), (3, 0), (2, 2), (3, 2)]
CLOUDS = [(8, 12), (36, 14), (70, 11)]


def position(index):
    theta = 2 * math.pi * index / FRAMES
    return 48 + 36 * math.sin(theta), 8 + 4 * math.sin(2 * theta), math.cos(theta)


def draw_clouds(frame, index):
    shift = round(96 * index / FRAMES)
    for base_x, y in CLOUDS:
        x = (base_x - shift) % 96
        for dx, dy in [(0, 0), (1, 0), (2, 0), (3, -1), (4, 0), (5, 0)]:
            frame.pixel(x + dx, y + dy, C.BLUE)


def draw_sprite(frame, x, y, facing):
    for dx, dy in SPRITE:
        px = dx if facing > 0 else 4 - dx
        frame.pixel(round(x) - 2 + px, round(y) - 1 + dy, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        draw_clouds(frame, index)
        for back in range(8, 0, -1):
            tx, ty, _ = position(index - back)
            colour = C.CYAN if back <= 3 else C.BLUE
            frame.pixel(round(tx), round(ty), colour)
        x, y, facing = position(index)
        draw_sprite(frame, x, y, facing)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/paper_plane.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
