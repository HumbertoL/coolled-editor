#!/usr/bin/env python3
"""
Grumpy Cat (2012) -- Tardar Sauce, unimpressed.

The face with the downturned mouth, blinking slowly, ears flicking once, and
the caption in the two-line Impact style the pictures used: I HAD FUN ONCE.
/ IT WAS AWFUL. Then the caption clears and she just looks at you for the
rest of the loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
FACE = [
    "#.........#",
    "##.......##",
    "###########",
    "###########",
    "#..#####..#",
    "###########",
    "###########",
    ".####.####.",
    "..##.#.##..",
    "...##.##...",
]
FACE_X, FACE_Y = 4, 3
EYES = [(2, 4), (8, 4)]
FROWN = [(3, 8), (4, 7), (5, 7), (6, 7), (7, 8)]
TOP_END, BOTTOM_END, CLEAR = 16, 34, 44


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        blink = index in (12, 13, 40)
        flick = 20 <= index < 23
        for r, line in enumerate(FACE):
            for c, ch in enumerate(line):
                if ch == "#":
                    if flick and r == 0 and c == 10:
                        continue
                    frame.pixel(FACE_X + c, FACE_Y + r, C.WHITE)
        if flick:
            frame.pixel(FACE_X + 11, FACE_Y + 1, C.WHITE)
        for ex, ey in EYES:
            frame.pixel(FACE_X + ex, FACE_Y + ey, C.WHITE if blink else C.CYAN)
            if not blink:
                frame.pixel(FACE_X + ex, FACE_Y + ey - 1, C.BLUE)      # heavy brow
        for fx, fy in FROWN:
            frame.pixel(FACE_X + fx, FACE_Y + fy, C.BLACK)
        frame.pixel(FACE_X + 5, FACE_Y + 5, C.MAGENTA)                  # nose

        if index < CLEAR:
            frame.text("I HAD FUN ONCE.", 17, 0, C.WHITE, proportional=True)
            if index >= TOP_END:
                frame.text("IT WAS AWFUL.", 17, 9, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/grumpy_cat.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
