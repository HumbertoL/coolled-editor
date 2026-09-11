#!/usr/bin/env python3
"""
All Your Base (2001, from a 1991 game) -- the first meme many people met.

CATS's face -- pale, black-eyed -- glitches in with static, and the immortal
lines type out beneath it in the order they were spoken: HOW ARE YOU
GENTLEMEN, ALL YOUR BASE ARE BELONG TO US -- which gets the whole panel to
itself, centred, the face cut away for the beat -- then YOU HAVE NO CHANCE
TO SURVIVE MAKE YOUR TIME, then HA HA HA HA. The face flickers throughout
because the video always did.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
SEED = 1991
CATS = [
    "..#######..",
    ".#########.",
    "###########",
    "##.#####.##",
    "##.#####.##",
    "###########",
    "####...####",
    ".####.####.",
    "..#######..",
    "...#####...",
]
# (frame, top line, bottom line, face shown). The famous line gets the
# whole panel to itself, centred, with CATS cut away for the beat.
LINES = [
    (0, "HOW ARE YOU", "GENTLEMEN !!", True),
    (12, "ALL YOUR BASE", "ARE BELONG TO US", False),
    (26, "YOU HAVE", "NO CHANCE", True),
    (36, "TO SURVIVE", "MAKE YOUR TIME", True),
    (46, "HA HA HA HA", "", True),
]
TEXT_X = 16


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for _ in range(6):
            frame.pixel(rng.randrange(96), rng.randrange(16), C.BLUE)
        at, top, bottom, face = max((entry for entry in LINES if index >= entry[0]), key=lambda e: e[0])
        flicker = rng.random() < 0.15
        if face:
            for r, line in enumerate(CATS):
                for c, ch in enumerate(line):
                    if ch == "#" and not (flicker and r % 2):
                        frame.pixel(2 + c, 3 + r, C.CYAN if flicker else C.WHITE)
        k = index - at
        typed_top = top[:min(len(top), (k + 1) * 3)]
        x_top = TEXT_X if face else (anim.width - frame.text_width(top, proportional=True)) // 2
        frame.text(typed_top, x_top, 0, C.WHITE, proportional=True)
        if len(typed_top) == len(top) and bottom:
            typed_bottom = bottom[:max(0, (k + 1) * 3 - len(top))]
            x_bottom = TEXT_X if face else (anim.width - frame.text_width(bottom, proportional=True)) // 2
            frame.text(typed_bottom, x_bottom, 9, C.YELLOW, proportional=True)
        if top.startswith("HA") and index % 2:
            frame.text(top, TEXT_X, 0, C.RED, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/all_your_base.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
