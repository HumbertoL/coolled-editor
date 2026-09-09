#!/usr/bin/env python3
"""
Rain, with one strike of lightning.

Drops fall as three-pixel streaks -- white head, cyan body, blue tail -- which
is the palette's only way to suggest motion blur without brightness levels.
Where a drop reaches the floor it leaves a brief splash.

Two thirds of the way through, the sky flashes: the background fills blue for a
single frame behind a white bolt, then the bolt lingers one more frame in cyan
as an afterimage. That single bright frame is the whole reason the piece works
on a 16-pixel-tall panel -- there is no room for weather, so the drama has to
come from timing.

The rain loops seamlessly: drops fall 2px per frame over 16 rows, an 8-frame
cycle that divides evenly into the 24 frames. The strike happens once per loop.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

WIDTH, HEIGHT = 96, 16
FRAMES = 24
DELAY = 110
SEED = 5

FALL_SPEED = 2                 # px per frame; 16 / 2 = 8-frame cycle
DROP_COUNT = 22

FLASH_FRAME = 15               # sky lights up
AFTERGLOW_FRAME = 16           # bolt fading

STREAK = [C.WHITE, C.CYAN, C.BLUE]   # head first, upward


def make_drops():
    rng = random.Random(SEED)
    drops = []
    for _ in range(DROP_COUNT):
        drops.append(
            (
                rng.randrange(WIDTH),
                # Stagger the starts so they are not in lockstep.
                rng.randrange(HEIGHT),
            )
        )
    return drops


def bolt_path(rng):
    """A zigzag from the top edge to the floor, wandering a few px each turn."""
    x = rng.randrange(20, WIDTH - 20)
    points = [(x, 0)]
    y = 0
    while y < HEIGHT - 1:
        y = min(HEIGHT - 1, y + rng.randrange(3, 6))
        x = max(2, min(WIDTH - 3, x + rng.randrange(-5, 6)))
        points.append((x, y))
    return points


def build():
    anim = Animation(WIDTH, HEIGHT, delay=DELAY)
    drops = make_drops()
    rng = random.Random(SEED + 1)
    path = bolt_path(rng)

    for index in range(FRAMES):
        frame = anim.frame()

        # The sky, lit for exactly one frame.
        if index == FLASH_FRAME:
            frame.fill(C.BLUE)

        for x, offset in drops:
            head_y = (offset + index * FALL_SPEED) % HEIGHT
            for depth, color in enumerate(STREAK):
                frame.pixel(x, head_y - depth, color)
            # Splash on arrival.
            if head_y >= HEIGHT - 2:
                frame.pixel(x - 1, HEIGHT - 1, C.BLUE)
                frame.pixel(x + 1, HEIGHT - 1, C.BLUE)

        # The strike, drawn over the rain so it reads as nearer.
        if index in (FLASH_FRAME, AFTERGLOW_FRAME):
            color = C.WHITE if index == FLASH_FRAME else C.CYAN
            for start, end in zip(path, path[1:]):
                frame.line(start[0], start[1], end[0], end[1], color)

    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/rain.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
