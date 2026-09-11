#!/usr/bin/env python3
"""
Badger Badger Badger (2003) -- Weebl's Flash loop, the earworm.

A row of badgers bounce in time to the chant along the top, BADGER twelve
times, then a mushroom rises up in the middle (MUSHROOM MUSHROOM), then the
badgers again, then the snake appears -- SNAKE! A SNAKE! -- and it starts
over. The badgers are striped black and white, so on a black panel they are
white with a dark stripe down the face.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
BADGER = [
    "##..##.",
    ".#####.",
    "#.###.#",
    ".#####.",
    "..###..",
    "..#.#..",
]
MUSHROOM = [
    "..#####..",
    ".#######.",
    "#########",
    "...###...",
    "...###...",
    "...###...",
]
SNAKE = [
    "###......",
    "...#.....",
    "....##...",
    "......#..",
    "......#.#",
    ".....##.#",
]
BADGER_END, MUSHROOM_END, BADGER2_END = 22, 32, 44


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        badgers = index < BADGER_END or MUSHROOM_END <= index < BADGER2_END
        if badgers:
            beat = index % 2
            frame.text("BADGER BADGER", "center", 0, C.WHITE if beat else C.YELLOW, proportional=True)
            for i in range(7):
                x = 4 + i * 13
                y = 9 - ((i + index) % 2)
                for r, line in enumerate(BADGER):
                    for c, ch in enumerate(line):
                        if ch == "#":
                            frame.pixel(x + c, y + r, C.WHITE)
                frame.pixel(x + 3, y + 2, C.BLACK)
        elif index < MUSHROOM_END:
            k = index - BADGER_END
            frame.text("MUSHROOM", "center", 0, C.RED if k % 4 < 2 else C.WHITE, proportional=True)
            rise = max(0, 5 - k)
            for r, line in enumerate(MUSHROOM):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(44 + c, 9 + r + rise, C.RED if r < 3 else C.WHITE)
            frame.pixel(46, 10, C.WHITE)
            frame.pixel(50, 11, C.WHITE)
        else:
            k = index - BADGER2_END
            frame.text("SNAKE! A SNAKE!", "center", 0, C.GREEN if k % 2 else C.WHITE, proportional=True)
            slide = max(0, 30 - k * 6)
            for r, line in enumerate(SNAKE):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(30 + c * 4 + slide, 9 + r, C.GREEN)
                        frame.pixel(31 + c * 4 + slide, 9 + r, C.GREEN)
            frame.pixel(30 + slide, 9, C.RED)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/badger_badger.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
