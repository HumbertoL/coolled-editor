#!/usr/bin/env python3
"""
Aquarium -- fish, bubbles, weed. The calm one.

Five fish cross at their own speeds in both directions, each flicking its
tail every few frames. Bubbles rise from the sand and drift a pixel side to
side; seaweed sways on a slow sine. Every speed is a whole number of panel
crossings per loop and the weed completes whole cycles, so it is seamless --
which matters for something meant to sit in the corner of a room all day.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 4

FISH = [
    "...##...",
    ".#####.#",
    "########",
    ".#####.#",
    "...##...",
]
FISH_W = len(FISH[0])
LAP = 96 + FISH_W

# (lane y, laps per loop (negative = leftward), phase, colour)
SCHOOL = [
    (1, 1, 0.0, C.YELLOW),
    (6, 2, 0.35, C.CYAN),
    (3, -1, 0.6, C.MAGENTA),
    (8, -2, 0.1, C.GREEN),
    (5, 1, 0.75, C.WHITE),
]
SAND_Y = 15
WEED_X = [10, 30, 58, 82]


def draw_fish(frame, x, y, color, facing_right, flick):
    for r, line in enumerate(FISH):
        cells = line if facing_right else line[::-1]
        for c, ch in enumerate(cells):
            if ch != "#":
                continue
            # The tail is the lone pixel at the back; flick it up or down.
            is_tail = (c == 7 and facing_right and r in (1, 3)) or (c == 0 and not facing_right and r in (1, 3))
            if is_tail and flick and r == 1:
                continue
            frame.pixel(x + c, y + r, color)
    eye_x = x + 6 if facing_right else x + 1
    frame.pixel(eye_x, y + 1, C.BLACK)


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    bubbles = [(rng.randrange(6, 90), rng.random(), rng.choice((1, 2))) for _ in range(9)]

    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES

        frame.hline(0, SAND_Y, 96, C.YELLOW)
        for wx in WEED_X:
            for k in range(6):
                sway = round(1.6 * math.sin(2 * math.pi * (2 * t) + k * 0.6 + wx))
                frame.pixel(wx + sway, SAND_Y - 1 - k, C.GREEN)

        for bx, phase, cycles in bubbles:
            y = (SAND_Y - 1) - ((t * cycles + phase) % 1.0) * 17
            wob = round(math.sin(y * 0.9))
            if 0 <= y < SAND_Y:
                frame.pixel(bx + wob, round(y), C.CYAN if int(y) % 3 else C.WHITE)

        for lane, laps, phase, color in SCHOOL:
            pos = ((t * laps + phase) % 1.0) * LAP - FISH_W
            if laps < 0:
                pos = 96 - pos - FISH_W
            draw_fish(frame, round(pos), lane, color, laps > 0, (index // 3) % 2 == 0)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/aquarium.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
