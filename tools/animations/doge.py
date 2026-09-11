#!/usr/bin/env python3
"""
Doge (2013) -- wow. such pixel. very LED.

A Shiba face on the left, eyebrows going, and the Comic Sans captions
popping in around the panel in the meme's rainbow of colours, each holding a
couple of seconds before the next: WOW, SUCH PIXEL, VERY LED, MUCH SIGN,
SO BRIGHT, WOW. The dog's eyes glance toward each new word.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
SHIBA = [
    "#.........#",
    "##.......##",
    "###.....###",
    "###########",
    "###########",
    "#.#######.#",
    "###########",
    "####.#.####",
    ".#########.",
    "...#####...",
]
FACE_X, FACE_Y = 3, 3
EYES = [(2, 5), (8, 5)]
CAPTIONS = [
    (0, "WOW", 30, 1, C.MAGENTA),
    (8, "SUCH PIXEL", 38, 0, C.GREEN),
    (17, "VERY LED", 24, 9, C.CYAN),
    (26, "MUCH SIGN", 44, 9, C.YELLOW),
    (35, "SO BRIGHT", 28, 0, C.RED),
    (44, "WOW", 70, 5, C.WHITE),
]
HOLD = 9


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        current = [c for c in CAPTIONS if c[0] <= index < c[0] + HOLD]
        for r, line in enumerate(SHIBA):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(FACE_X + c, FACE_Y + r, C.YELLOW)
        look = 0
        if current:
            look = 1 if current[-1][2] > 40 else 0
        for ex, ey in EYES:
            frame.pixel(FACE_X + ex + look, FACE_Y + ey, C.BLACK)
        frame.pixel(FACE_X + 5, FACE_Y + 7, C.BLACK)
        brow = (index // 3) % 2
        for ex, _ in EYES:
            frame.pixel(FACE_X + ex, FACE_Y + 3 - brow, C.WHITE)
        for at, text, x, y, color in current:
            k = index - at
            frame.text(text, x, y, C.WHITE if k == 0 else color, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/doge.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
