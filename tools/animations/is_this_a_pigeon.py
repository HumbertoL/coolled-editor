#!/usr/bin/env python3
"""
Is This A Pigeon? (2018, from a 1991 anime) -- the butterfly.

A butterfly flutters in from the left, wings alternating, and a hand -- well,
a pointing arrow -- comes in from the right to indicate it. The caption
asks the question. The butterfly, as ever, is not a pigeon. It flutters off
and the question hangs there.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
WINGS = [
    ["##...##", "###.###", ".##.##.", "###.###", "##...##"],
    ["..#.#..", ".##.##.", "..#.#..", ".##.##.", "..#.#.."],
]
POINT_AT, ASK_AT, LEAVE_AT = 12, 18, 40


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        if index < POINT_AT:
            bx = -8 + (46 + 8) * index / POINT_AT
        elif index < LEAVE_AT:
            bx = 46
        else:
            bx = 46 + (index - LEAVE_AT) * 6
        by = 2 + round(1.5 * math.sin(index * 0.9))
        wings = WINGS[(index // 2) % 2]
        for r, line in enumerate(wings):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(round(bx) + c, by + r, C.MAGENTA if r != 2 else C.YELLOW)
        frame.vline(round(bx) + 3, by, 5, C.WHITE)      # body

        if POINT_AT <= index < LEAVE_AT + 3:
            ax = max(round(bx) + 10, 95 - (index - POINT_AT) * 8)
            frame.hline(ax, by + 2, 96 - ax, C.WHITE)
            frame.pixel(ax + 1, by + 1, C.WHITE)
            frame.pixel(ax + 1, by + 3, C.WHITE)
        if index >= ASK_AT:
            frame.text("IS THIS A PIGEON?", "center", 9,
                       C.WHITE if index % 6 else C.YELLOW, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/is_this_a_pigeon.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
