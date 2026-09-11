#!/usr/bin/env python3
"""
Stonks (2019) -- Meme Man and the line that only goes up.

A jagged chart climbs across the panel, drawn one point at a time, dipping
now and then just enough to worry you before resuming. Meme Man's featureless
head watches from the corner. When the line clears the top, STONKS flashes,
with the upward arrow. The line comes down for the loop, which is the only
time it ever does.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
SEED = 2019
HEAD = [
    ".#####.",
    "#######",
    "#######",
    "#######",
    "#######",
    ".#####.",
    "..###..",
]
HEAD_X, HEAD_Y = 2, 1
REVEAL_FRAMES = 42


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    points = []
    y = 14.0
    for x in range(12, 96):
        y += rng.uniform(-0.85, 0.6)
        y = max(2.0, min(14.5, y))
        points.append((x, round(y)))
    for index in range(FRAMES):
        frame = anim.frame()
        for r, line in enumerate(HEAD):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(HEAD_X + c, HEAD_Y + r, C.WHITE)
        frame.pixel(HEAD_X + 2, HEAD_Y + 3, C.BLACK)
        frame.pixel(HEAD_X + 4, HEAD_Y + 3, C.BLACK)
        frame.rect(HEAD_X, HEAD_Y + 7, 7, 3, C.BLUE, fill=True)          # the suit
        frame.pixel(HEAD_X + 3, HEAD_Y + 8, C.RED)                       # the tie

        shown = min(len(points), round(len(points) * (index + 1) / REVEAL_FRAMES))
        prev = None
        for i in range(shown):
            p = points[i]
            if prev:
                frame.line(prev[0], prev[1], p[0], p[1], C.GREEN)
            prev = p
        if shown < len(points):
            frame.pixel(*points[shown - 1], C.WHITE)
        frame.hline(12, 15, 84, C.BLUE)
        if index >= REVEAL_FRAMES:
            k = index - REVEAL_FRAMES
            frame.text("STONKS", 12, 1, C.YELLOW if k % 2 else C.WHITE, proportional=True)
            frame.glyph("+ARROW_U", 48, 1, C.GREEN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/stonks.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
