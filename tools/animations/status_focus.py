#!/usr/bin/env python3
"""
Focus mode -- headphones on, do not disturb.

A pair of headphones with a small equaliser bouncing between the cups, and
FOCUS MODE in magenta with a slow shine passing over it. The bars each run on
their own sine so they look like music rather than a metronome.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C, highlight  # noqa: E402

FRAMES = 24
DELAY = 120

HEADPHONES = [
    "...#####...",
    "..#.....#..",
    ".#.......#.",
    ".#.......#.",
    "##.......##",
    "##.......##",
    "##.......##",
    ".#.......#.",
]
HP_X, HP_Y = 4, 3
TEXT = "FOCUS MODE"
TEXT_X = 26


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for row, line in enumerate(HEADPHONES):
            for col, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(HP_X + col, HP_Y + row, C.WHITE)
        for i in range(5):
            height = 1 + round(1.5 + 1.5 * math.sin(2 * math.pi * (index * (2 + i % 2) / FRAMES) + i * 1.3))
            x = HP_X + 3 + i
            frame.vline(x, HP_Y + 8 - height, height, C.MAGENTA)
        head = TEXT_X - 6 + (index * (60 + 12)) // FRAMES
        frame.text(TEXT, TEXT_X, 4, highlight(C.MAGENTA, C.WHITE, head=head, half_width=1))
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/status_focus.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
