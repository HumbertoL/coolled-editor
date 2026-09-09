#!/usr/bin/env python3
"""
On a call -- a desk status for the doorway.

A handset rattles on the left with ring marks flickering either side of it,
ON A CALL sits in red, and a recording dot blinks at the far right. The
handset shakes by a pixel on alternate frames, which is all it takes to say
"ringing" at this size.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 24
DELAY = 120

HANDSET = [
    ".##.....##.",
    "###.....###",
    "###.....###",
    ".#########.",
    "..#######..",
]
HANDSET_X, HANDSET_Y = 4, 5


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        shake = (index % 2) if index % 8 < 4 else 0
        for row, line in enumerate(HANDSET):
            for col, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(HANDSET_X + col + shake, HANDSET_Y + row, C.WHITE)
        if index % 8 < 4:
            for side in (-1, 1):
                x = HANDSET_X + 5 + side * (7 + (index % 2))
                frame.pixel(x, HANDSET_Y + 1, C.YELLOW)
                frame.pixel(x + side, HANDSET_Y + 2, C.YELLOW)
                frame.pixel(x, HANDSET_Y + 3, C.YELLOW)
        frame.text("ON A CALL", 26, 4, C.RED)
        if index % 6 < 3:
            frame.rect(86, 6, 3, 3, C.RED, fill=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/status_on_a_call.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
