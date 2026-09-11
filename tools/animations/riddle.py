#!/usr/bin/env python3
"""
Riddle -- the sign, describing itself.

Three couplets, two lines at a time: I HAVE 1536 EYES / AND ONLY 8 COLORS;
I SPEAK IN FRAMES / 53 AT A TIME; I NEVER SLEEP / WHAT AM I? Then, for the
answer, every pixel flashes through all seven colours -- which is the answer
demonstrated -- and it settles on ME.

The numbers are true of this panel: 96 x 16 LEDs, 3 bits each, and the
53-frame device maximum this file itself uses.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 160
COUPLETS = [
    ("I HAVE 1536 EYES", "AND ONLY 8 COLORS"),
    ("I SPEAK IN FRAMES", "53 AT A TIME"),
    ("I NEVER SLEEP", "WHAT AM I?"),
]
SCREEN = 12
FLASH_AT = 36
ANSWER_AT = 43
WHEEL = [C.RED, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA, C.WHITE]


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < FLASH_AT:
            top, bottom = COUPLETS[min(len(COUPLETS) - 1, index // SCREEN)]
            k = index % SCREEN
            frame.text(top, "center", 0, C.WHITE, proportional=True)
            if k >= 3:
                frame.text(bottom, "center", 9, C.CYAN if not bottom.endswith("?") or k % 2 else C.YELLOW,
                           proportional=True)
        elif index < ANSWER_AT:
            frame.fill(WHEEL[(index - FLASH_AT) % len(WHEEL)])
        else:
            k = index - ANSWER_AT
            frame.text("ME.", "center", 4, WHEEL[k % len(WHEEL)] if k < 7 else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/riddle.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
