#!/usr/bin/env python3
"""
The Dress (2015) -- the photo that split the internet down the middle.

A striped dress hangs at the left of the panel and the question sits beside
it. It reads BLUE & BLACK?, then flips to WHITE & GOLD?, and back, each
reading holding for less time than the last until the panel is flickering
between them in pure indecision. Then it gives up and settles on both: the
dress splits down the seam, blue and black on one side, white and gold on the
other, with both captions stacked beside it. Black lace on a black panel is
simply unlit, so the blue reading's bands show as gaps -- which is rather the
point.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
# 'b' is the dress body, 'l' the lace bands, 'h' the hanger.
DRESS = [
    "......h......",
    "...bb...bb...",
    "...bl...lb...",
    "..bbbbbbbbb..",
    "...bbbbbbb...",
    "....bbbbb....",
    "....lllll....",
    "....bbbbb....",
    "...bbbbbbb...",
    "...lllllll...",
    "..bbbbbbbbb..",
    "..bbbbbbbbb..",
    ".lllllllllll.",
    ".bbbbbbbbbbb.",
    "bbbbbbbbbbbbb",
    "lllllllllllll",
]
DRESS_X = 3
SEAM = DRESS_X + 6
BLUE_BLACK = {"b": C.BLUE, "l": C.BLACK, "h": C.WHITE}
WHITE_GOLD = {"b": C.WHITE, "l": C.YELLOW, "h": C.WHITE}
TEXT_X = 22
# How long each reading holds, shrinking into a flicker.
HOLDS = [8, 7, 5, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1]
SETTLE_AT = sum(HOLDS)


def reading_at(index):
    """0 for blue/black, 1 for white/gold, during the flipping phase."""
    elapsed = 0
    for n, hold in enumerate(HOLDS):
        elapsed += hold
        if index < elapsed:
            return n % 2
    return None


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        reading = reading_at(index)
        for r, line in enumerate(DRESS):
            for c, ch in enumerate(line):
                if ch == ".":
                    continue
                x = DRESS_X + c
                if reading is None:
                    palette = BLUE_BLACK if x < SEAM else WHITE_GOLD
                else:
                    palette = WHITE_GOLD if reading else BLUE_BLACK
                frame.pixel(x, r, palette[ch])
        if reading is None:
            # Settled: both at once, with a flash on the frame it splits.
            if index == SETTLE_AT:
                frame.vline(SEAM, 1, 15, C.MAGENTA)
            frame.text("BLUE & BLACK?", TEXT_X, 0, C.BLUE, proportional=True)
            frame.text("WHITE & GOLD?", TEXT_X, 9, C.YELLOW, proportional=True)
        elif reading == 0:
            frame.text("BLUE & BLACK?", TEXT_X, 4, C.BLUE, proportional=True)
        else:
            frame.text("WHITE & GOLD?", TEXT_X, 4, C.YELLOW, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/the_dress.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
