#!/usr/bin/env python3
"""
This Is Fine (2013) -- KC Green's dog, coffee in hand, room on fire.

The dog sits in his hat at the left with a mug, blinking occasionally, while
flames climb the right two-thirds of the panel and creep toward him. The
caption arrives late, in the panel's own words: THIS IS FINE. He takes a sip.
The fire does not stop.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 2013
DOG = [
    ".####....",
    "..##.....",
    ".#####...",
    "#.###.#..",
    ".#####...",
    "..###....",
    ".#####.#.",
    "#.....##.",
    "#######..",
    "#.....#..",
]
DOG_X, DOG_Y = 6, 4
CAPTION_AT, SIP_AT = 24, 36


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        # Flames: a column of heat per x, taller as the loop goes on and
        # closer to the dog.
        reach = 30 + index // 3
        for x in range(96 - reach, 96):
            closeness = (x - (96 - reach)) / reach
            height = 3 + round(closeness * 9) + rng.randint(-2, 2)
            for y in range(16 - height, 16):
                if rng.random() < 0.25:
                    continue
                heat = (y - (16 - height)) / max(1, height)
                frame.pixel(x, y, C.RED if heat < 0.4 and rng.random() < 0.8 else C.YELLOW if heat < 0.85 else C.WHITE)
        frame.hline(0, 15, 96, C.RED)

        blink = index in (14, 15, 44)
        sip = SIP_AT <= index < SIP_AT + 5
        for r, line in enumerate(DOG):
            for c, ch in enumerate(line):
                if ch == "#":
                    color = C.WHITE if r < 2 else C.YELLOW
                    if r == 6 and c == 7:
                        continue
                    frame.pixel(DOG_X + c, DOG_Y + r, color)
        frame.pixel(DOG_X + 2, DOG_Y + 3, C.WHITE if blink else C.BLACK)
        frame.pixel(DOG_X + 4, DOG_Y + 3, C.WHITE if blink else C.BLACK)
        mug_y = DOG_Y + 3 if sip else DOG_Y + 6
        frame.rect(DOG_X + 7, mug_y, 2, 2, C.CYAN, fill=True)
        frame.pixel(DOG_X + 9, mug_y, C.CYAN)
        if index >= CAPTION_AT:
            frame.text("THIS IS FINE.", 26, 1, C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/this_is_fine.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
