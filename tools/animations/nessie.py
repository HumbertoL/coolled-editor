#!/usr/bin/env python3
"""
Nessie -- the loch, three humps, and the photograph.

A rippling surface, calm to start with. Three humps break it one after
another from the right, each pushing out a ring, and then the neck comes up
on the left and the head turns. That is the cue for the 1934 Surgeon's
Photograph: one frame of pure white, two more where the whole scene is
flattened to white -- an overexposed plate rather than a picture -- and by
the time it clears she is on her way back down, humps sinking in the order
they surfaced. The last thing to go is the ripple.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
WATER_Y = 11

# Scene beats, by frame index.
HUMP_AT = (7, 11, 15)   # right to left, one ring apiece
NECK_AT = 20            # the neck starts up
NECK_UP = 29            # fully up, and looking around
FLASH_AT = 34           # the plate is exposed
AFTER_TO = 36           # and takes two frames to clear
SINK_AT = 38

NECK_X = 22
HUMPS = (66, 52, 38)
HUMP_HALF = 5


def surface(x, phase):
    return WATER_Y + round(math.sin(2 * math.pi * (x / 24 + phase)))


def draw_water(frame, phase, rings):
    for x in range(96):
        top = surface(x, phase)
        frame.pixel(x, top, C.CYAN)
        for y in range(top + 1, 16):
            if (x + y * 3 + round(phase * 8)) % 5:
                continue
            frame.pixel(x, y, C.BLUE)
    for center, radius in rings:
        for side in (-1, 1):
            x = center + side * radius
            frame.pixel(x, surface(x, phase) + 1, C.CYAN)
            frame.pixel(x, surface(x, phase), C.WHITE)


def draw_hump(frame, center, phase, height):
    for dx in range(-HUMP_HALF, HUMP_HALF + 1):
        lift = height * math.sqrt(max(0.0, 1 - (dx / (HUMP_HALF + 0.5)) ** 2))
        top = surface(center + dx, phase) - round(lift)
        frame.vline(center + dx, top, surface(center + dx, phase) - top + 1, C.GREEN)


def draw_neck(frame, phase, extent, looking):
    """A neck curving back over the water, with the head at the top."""
    base_y = surface(NECK_X, phase)
    top_y = base_y - round(extent * (base_y - 2))
    for y in range(top_y, base_y + 1):
        t = (base_y - y) / max(1, base_y - top_y)
        x = NECK_X - round(4 * t * t)
        frame.pixel(x, y, C.GREEN)
        frame.pixel(x + 1, y, C.GREEN)
    if extent < 0.6:
        return
    head_x = NECK_X - round(4) - (1 if looking else 0)
    frame.rect(head_x - 2, top_y - 1, 5, 3, C.GREEN, fill=True)
    frame.pixel(head_x - 3, top_y, C.GREEN)
    frame.pixel(head_x - (1 if looking else 0), top_y - 1, C.WHITE)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        phase = 4 * index / FRAMES  # four whole cycles, so the water wraps

        if index == FLASH_AT:
            frame.fill(C.WHITE)
            continue

        rings = [
            (center, (index - at) * 4)
            for center, at in zip(HUMPS, HUMP_AT)
            if 0 <= index - at < 4
        ]
        draw_water(frame, phase, rings)

        for order, (center, at) in enumerate(zip(HUMPS, HUMP_AT)):
            if index < at:
                continue
            rising = min(1.0, (index - at) / 3)
            sinking = 1.0
            if index >= SINK_AT:
                sinking = max(0.0, 1 - (index - SINK_AT - order * 3) / 4)
            height = 4 * rising * sinking
            if height > 0.2:
                draw_hump(frame, center, phase, height)

        if index >= NECK_AT:
            if index < SINK_AT:
                extent = min(1.0, (index - NECK_AT) / (NECK_UP - NECK_AT))
            else:
                extent = max(0.0, 1 - (index - SINK_AT) / 5)
            if extent > 0.05:
                draw_neck(frame, phase, extent, looking=index % 6 < 3)

        if FLASH_AT < index <= AFTER_TO:
            # The plate is still clearing: shape, but no colour left in it.
            frame.map(lambda x, y, color: C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/nessie.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
