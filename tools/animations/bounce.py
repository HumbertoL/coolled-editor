#!/usr/bin/env python3
"""
Bounce -- balls with different rhythms, one wandering.

Three balls bounce in place with periods of 12, 8 and 6 frames -- all
dividing 24, so every ball is back where it started when the loop closes and
they realign once per loop, which is the moment the eye waits for. A fourth
ball rolls across and back while bouncing on the slowest rhythm.

On the floor frame a ball is drawn as a flat wide dash, the one-frame squash
that makes a bounce look springy instead of like a dot on a sine wave. Each
has a blue shadow that shrinks as it rises.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 70
FLOOR = 13

# (x, period, height, colour); the rover has a callable x.
BALLS = [
    (14, 12, 11, C.RED),
    (36, 8, 9, C.YELLOW),
    (58, 6, 7, C.GREEN),
]
ROVER = (24, 12, C.CYAN)


def rover_x(index):
    half = FRAMES // 2
    t = index / half if index < half else (FRAMES - index) / half
    return round(8 + 80 * t)


def draw_ball(frame, x, period, height, color, index):
    lift = height * abs(math.sin(math.pi * index / period))
    y = FLOOR - round(lift)
    shadow = 5 - round(4 * lift / height)
    frame.hline(x - shadow // 2, FLOOR + 1, shadow, C.CYAN)
    if index % period == 0:
        frame.rect(x - 2, FLOOR - 1, 5, 2, color, fill=True)
    else:
        frame.rect(x - 1, y - 2, 3, 3, color, fill=True)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, FLOOR + 2, anim.width, C.BLUE)
        for x, period, height, color in BALLS:
            draw_ball(frame, x, period, height, color, index)
        period, height, color = ROVER
        draw_ball(frame, rover_x(index), period, height, color, index)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/bounce.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
