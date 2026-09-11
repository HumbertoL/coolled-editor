#!/usr/bin/env python3
"""
DFTBA -- Don't Forget To Be Awesome.

The five letters sit spaced across the top. One at a time each lights gold
and its word appears beneath: DON'T, FORGET, TO, BE, AWESOME. On the last
one the whole line goes gold and AWESOME flashes, then it holds for a beat.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
LETTERS = "DFTBA"
WORDS = ["DON'T", "FORGET", "TO", "BE", "AWESOME"]
LETTER_XS = [12, 29, 46, 63, 80]
STEP = 9
START = 3


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        current = min(len(WORDS) - 1, (index - START) // STEP) if index >= START else -1
        finished = index >= START + STEP * len(WORDS) - 2
        for i, (ch, x) in enumerate(zip(LETTERS, LETTER_XS)):
            if finished or i == current:
                color = C.YELLOW
            elif i < current:
                color = C.WHITE
            else:
                color = C.BLUE
            frame.text(ch, x, 0, color)
        if current >= 0:
            word = WORDS[current]
            flash = finished and index % 2 == 0
            frame.text(word, "center", 9, C.WHITE if flash else C.YELLOW if finished else C.CYAN,
                       proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/dftba.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
