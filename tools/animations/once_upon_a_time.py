#!/usr/bin/env python3
"""
Once upon a time -- the oldest opening line, decoded out of noise.

All fifteen character cells start as random letters, redrawn every frame in
blue and cyan. They lock in left to right, one every second frame, each with
a yellow flash, until the line reads ONCE UPON A TIME in white. A flourish
then grows outward from a diamond beneath it and a yellow glint crosses the
words, before the letters fall back into noise from the right for the loop.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, highlight  # noqa: E402

FRAMES = 53
DELAY = 100
LINE = "ONCE UPON A TIME"
CELL = 6
LEFT = (96 - (len(LINE) * CELL - 1)) // 2
TOP = 3
FIRST_LOCK = 5
ALL_LOCKED = FIRST_LOCK + 2 * (len(LINE) - 1)  # frame the last letter lands
UNLOCK = 47
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def build():
    rng = random.Random(1)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for slot, char in enumerate(LINE):
            if char == " ":
                continue
            x = LEFT + slot * CELL
            locked_at = FIRST_LOCK + 2 * slot
            # The exit runs right to left, three cells a frame.
            released = index >= UNLOCK and slot >= len(LINE) - 3 * (index - UNLOCK + 1)
            if index < locked_at or released:
                noise = rng.choice(ALPHABET.replace(char, ""))
                frame.text(noise, x, TOP, C.CYAN if (slot + index) % 3 == 0 else C.BLUE)
            elif index == locked_at:
                frame.text(char, x, TOP, C.YELLOW)
            else:
                glint = (index - ALL_LOCKED - 3) * 9
                frame.text(char, x, TOP, highlight(C.WHITE, C.YELLOW, head=glint, half_width=3))

        # The flourish: a diamond, then a rule growing out from it.
        grown = index - ALL_LOCKED - 1
        if grown >= 0 and index < UNLOCK:
            reach = min(34, grown * 5)
            frame.hline(47 - reach, 13, 2 * reach + 2, C.MAGENTA)
            for dx, dy in [(0, -1), (1, -1), (-1, 0), (2, 0), (0, 1), (1, 1), (0, 0), (1, 0)]:
                frame.pixel(47 + dx, 13 + dy, C.YELLOW)
            frame.pixel(47, 13, C.BLACK)
            frame.pixel(48, 13, C.BLACK)
            frame.pixel(47, 13, C.YELLOW)
            frame.pixel(48, 13, C.YELLOW)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/once_upon_a_time.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
