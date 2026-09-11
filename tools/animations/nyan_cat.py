#!/usr/bin/env python3
"""
Nyan Cat (2011) -- Pop-Tart body, rainbow trail, stars going past.

The cat bobs up and down in place while the rainbow streams out behind it in
six stripes that ripple with the bob, and stars fly past from right to left
at three speeds. The bob, the rainbow ripple and the star speeds all complete
whole cycles per loop, so it is seamless -- as the original was, for ten
hours.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 90
SEED = 2011
CAT_X = 58
RAINBOW = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]
BODY = [
    ".##########.",
    "#..........#",
    "#.#..#..#..#",
    "#..#.....#.#",
    "#....#.#...#",
    "#..........#",
    ".##########.",
]
HEAD = [
    "#.....#",
    "#######",
    "#.#.#.#",
    "#######",
    "#.###.#",
    ".#####.",
]
BOB = [0, 0, 1, 1, 0, 0, -1, -1]


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    stars = [(rng.randrange(96), rng.randrange(16), rng.choice((1, 2, 3))) for _ in range(14)]
    for index in range(FRAMES):
        frame = anim.frame()
        t = index / FRAMES
        bob = BOB[index % len(BOB)]
        body_y = 4 + bob

        for sx, sy, laps in stars:
            x = round((sx - laps * 96 * t) % 96)
            frame.pixel(x, sy, C.WHITE)
            if laps == 3:
                frame.pixel((x + 1) % 96, sy, C.WHITE)

        for x in range(0, CAT_X + 1):
            ripple = round(math.sin(2 * math.pi * (x / 16 + 3 * t)))
            for i, color in enumerate(RAINBOW):
                frame.pixel(x, 4 + i + ripple, color)

        for r, line in enumerate(BODY):
            for c, ch in enumerate(line):
                frame.pixel(CAT_X + c, body_y + r, C.MAGENTA if ch == "." else C.YELLOW)
        for r, line in enumerate(HEAD):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(CAT_X + 10 + c, body_y + 1 + r, C.WHITE)
        # Eyes and cheeks.
        frame.pixel(CAT_X + 12, body_y + 3, C.BLACK)
        frame.pixel(CAT_X + 14, body_y + 3, C.BLACK)
        frame.pixel(CAT_X + 11, body_y + 4, C.MAGENTA)
        frame.pixel(CAT_X + 15, body_y + 4, C.MAGENTA)
        # Legs, alternating.
        for i in range(4):
            frame.pixel(CAT_X + 1 + i * 3 + (index % 2), body_y + 7, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/nyan_cat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
