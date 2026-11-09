#!/usr/bin/env python3
"""
Whale -- a blue whale rising to breathe.

The whale holds the middle of the panel while plankton drifts past it, so it
reads as swimming. Its depth follows one cosine per loop: deep at the ends,
breaking the surface in the middle, where the back shows above the waterline
and a white spout goes up for nine frames. The flukes beat four times a
loop, the swell runs twice round and the plankton wraps exactly once, so
frame 53 is frame 0.
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
SURFACE = 5
WHALE_X = 34
PALETTE = {"B": C.BLUE, "C": C.CYAN, "W": C.WHITE}

BODY = [
    "...............BBBBBBBBBBB....",
    "...........BBBBBBBBBBBBBBBBB..",
    "........BBBBBBBBBBBBBBBBBBBBB.",
    ".....BBBBBBBBBBBBBBBBBBBBBWBBB",
    "..BBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBBCCCCCCCCCCCCCCCC",
    "....BBBBBBBCCCCCCCCCCCCCCCCCC.",
    "...........CCCCCCCCCCCCCCCC...",
    "................BBB...........",
]
# Flukes, drawn to the left of the body; rows line up with BODY's.
FLUKES = [
    [".......", "B......", "BB.....", ".BBB...", "..BBBB.", "....BBB", ".......", ".......", "......."],
    [".......", ".......", ".......", "B......", "BBB....", ".BBBBBB", "BBB....", "B......", "......."],
    [".......", ".......", ".......", ".......", ".......", "....BBB", "..BBBB.", ".BBB...", "BB....."],
]
BLOWHOLE = 23  # column of BODY the spout rises from


def stamp(frame, rows, x, y):
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell != ".":
                frame.pixel(x + col, y + row, PALETTE[cell])


def build():
    rng = random.Random(8)
    plankton = [(rng.randrange(96), rng.randrange(SURFACE + 2, 16), rng.choice([C.GREEN, C.CYAN])) for _ in range(16)]
    stars = [(rng.randrange(96), rng.randrange(0, 3)) for _ in range(7)]
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        t = index / FRAMES
        frame = anim.frame()

        for x, y in stars:
            frame.pixel(x, y, C.WHITE)
        for x, y, colour in plankton:
            frame.pixel((x - round(96 * t)) % 96, y, colour)

        rise = (1 - math.cos(2 * math.pi * t)) / 2  # 0 deep, 1 at the surface
        top = 8 - round(4 * rise)
        beat = math.sin(2 * math.pi * 4 * t)
        flukes = FLUKES[0 if beat > 0.4 else 2 if beat < -0.4 else 1]
        stamp(frame, flukes, WHALE_X - 6, top)
        stamp(frame, BODY, WHALE_X, top)

        # The swell, drawn over the whale so its back sits in the water.
        for x in range(96):
            crest = math.sin(2 * math.pi * (x / 24 - 2 * t)) > 0.55
            y = SURFACE - (1 if crest else 0)
            if frame.get(x, y) == C.BLACK or y > top:
                frame.pixel(x, y, C.CYAN)

        if rise > 0.86:
            sx = WHALE_X + BLOWHOLE
            age = sum(1 for k in range(index) if (1 - math.cos(2 * math.pi * k / FRAMES)) / 2 > 0.86)
            height = min(4, 1 + age)
            for h in range(1, height + 1):
                spread = 0 if h < 3 else h - 2
                frame.pixel(sx - spread, top - h, C.WHITE)
                frame.pixel(sx + spread, top - h, C.WHITE)
            if age % 2:
                frame.pixel(sx - 3, top - 2, C.CYAN)
                frame.pixel(sx + 3, top - 2, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/whale.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
