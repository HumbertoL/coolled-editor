#!/usr/bin/env python3
"""
Peanut Butter Jelly Time (2002) -- the dancing banana.

A banana with arms and legs, swaying side to side with its arms up, while the
chant cycles beneath it: PEANUT BUTTER JELLY TIME, then WHERE HE AT, then
THERE HE GO, then DO THE PEANUT BUTTER JELLY, then back round, in the
original's yellow. A second banana joins at the far side for the second half.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
BANANA = [
    [
        "#....#..",
        ".#..##..",
        "..###...",
        "..###...",
        "..###...",
        "..###...",
        ".##.##..",
        "##...##.",
        ".#...#..",
    ],
    [
        "..#....#",
        "..##..#.",
        "...###..",
        "...###..",
        "...###..",
        "...###..",
        "..##.##.",
        ".##...##",
        "..#...#.",
    ],
]
CHANT = [
    "PEANUT BUTTER", "JELLY TIME!", "PEANUT BUTTER", "JELLY TIME!",
    "WHERE HE AT?", "THERE HE GO!", "DO THE PEANUT", "BUTTER JELLY",
]
CHANT_EVERY = 6


def banana(frame, x, y, pose, color):
    for r, line in enumerate(BANANA[pose]):
        for c, ch in enumerate(line):
            if ch == "#":
                frame.pixel(x + c, y + r, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        pose = (index // 2) % 2
        banana(frame, 4 + (index % 2), 3, pose, C.YELLOW)
        if index >= FRAMES // 2:
            banana(frame, 84 - (index % 2), 3, 1 - pose, C.YELLOW)
        line = CHANT[(index // CHANT_EVERY) % len(CHANT)]
        color = C.YELLOW if (index // CHANT_EVERY) % 2 == 0 else C.MAGENTA
        frame.text(line, "center", 4, color if index % CHANT_EVERY else C.WHITE, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/pb_jelly_time.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
