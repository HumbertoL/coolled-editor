#!/usr/bin/env python3
"""
Riddle -- the sign, describing itself.

Three couplets, two lines at a time: I HAVE 1536 EYES / AND ONLY 8 COLORS;
I SPEAK IN FRAMES / 53 AT A TIME; I NEVER SLEEP / WHAT AM I? No answer is
given. The numbers are true of this panel: 96 x 16 LEDs, 3 bits each, and
the 53-frame device maximum this file itself uses.
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
SCREEN = 18


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        top, bottom = COUPLETS[min(len(COUPLETS) - 1, index // SCREEN)]
        k = index % SCREEN
        frame.text(top, "center", 0, C.WHITE, proportional=True)
        if k >= 4:
            question = bottom.endswith("?")
            frame.text(bottom, "center", 9, C.YELLOW if question and k % 2 else C.CYAN, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/riddle.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
