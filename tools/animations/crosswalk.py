#!/usr/bin/env python3
"""
Crosswalk -- a pedestrian signal and the people who obey it, mostly.

On the left, the signal head: a steady red hand, then the white walking
figure, then the flashing hand with a countdown from 9. On the right, a side
view of the street: one pedestrian waits at the kerb, tapping a foot, and
strolls across on WALK; at 6 a latecomer in yellow sprints across and makes
the far kerb at 0. On the steady hand a red car rushes through.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402
from jtkit.font import FONT_5X7  # noqa: E402

FRAMES = 53
DELAY = 110
WALK = (10, 29)          # frames showing the walking figure
COUNT_FROM = 30          # countdown 9..0, two frames a digit
STEADY = COUNT_FROM + 20
KERB_L, KERB_R = 40, 86

HAND = [
    "..#.#.#..",
    "..#.#.#.#",
    "..#.#.#.#",
    "#.#.#.#.#",
    "#.#######",
    "#########",
    ".########",
    ".#######.",
    "..######.",
    "..#####..",
    "..#####..",
]
WALKER = [
    "...##..",
    "...##..",
    ".......",
    "..###..",
    ".#.##..",
    "#..###.",
    "...##.#",
    "...##..",
    "..#.#..",
    ".#...#.",
    ".#...#.",
    "#.....#",
]


def bitmap(frame, rows, x, y, colour):
    for dy, row in enumerate(rows):
        for dx, cell in enumerate(row):
            if cell == "#":
                frame.pixel(x + dx, y + dy, colour)


def big_digit(frame, digit, x, y, colour):
    for dy, row in enumerate(FONT_5X7[str(digit)]):
        for dx, cell in enumerate(row):
            if cell == "#":
                frame.rect(x + 2 * dx, y + 2 * dy, 2, 2, colour, fill=True)


def person(frame, x, stride, shirt):
    """A 3px-wide figure with feet on row 14; stride 0 together, 1 apart."""
    frame.pixel(x + 1, 6, C.WHITE)
    frame.hline(x, 7, 3, shirt)
    frame.vline(x + 1, 8, 3, shirt)
    frame.pixel(x + 1, 11, C.BLUE)
    if stride:
        frame.pixel(x, 12, C.BLUE)
        frame.pixel(x + 2, 12, C.BLUE)
        frame.pixel(x, 13, C.BLUE)
        frame.pixel(x + 2, 13, C.BLUE)
        frame.pixel(x - 1 if stride > 1 else x, 14, C.WHITE)
        frame.pixel(x + 3 if stride > 1 else x + 2, 14, C.WHITE)
    else:
        frame.vline(x + 1, 12, 2, C.BLUE)
        frame.pixel(x + 1, 14, C.WHITE)


def street(frame):
    frame.hline(32, 15, KERB_L - 32, C.CYAN)
    frame.hline(KERB_R, 15, 96 - KERB_R, C.CYAN)
    for x in range(KERB_L + 1, KERB_R - 1, 4):
        frame.hline(x, 15, 2, C.WHITE)
    # Lamp post at the far kerb.
    frame.vline(92, 2, 13, C.BLUE)
    frame.hline(89, 2, 4, C.BLUE)
    frame.pixel(89, 3, C.YELLOW)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.rect(0, 0, 31, 16, C.BLUE)
        street(frame)
        if WALK[0] <= index <= WALK[1]:
            bitmap(frame, WALKER, 5, 2, C.WHITE)
        elif COUNT_FROM <= index < STEADY:
            digit = 9 - (index - COUNT_FROM) // 2
            if index % 2 == 0:
                bitmap(frame, HAND, 3, 2, C.RED)
            big_digit(frame, digit, 15, 1, C.YELLOW)
        else:
            bitmap(frame, HAND, 3, 2, C.RED)

        # The patient one: waits, taps, strolls across, then steps off right.
        if index < WALK[0]:
            person(frame, 34, 1 if index % 4 == 1 else 0, C.GREEN)
        else:
            x = 34 + round((index - WALK[0]) * 2.6)
            if x < 96:
                person(frame, x, (index // 2) % 2, C.GREEN)
        # The latecomer: in at 6, a full sprint.
        late_from = COUNT_FROM + 6
        if index >= late_from:
            x = 33 + (index - late_from) * 4
            if x < 96:
                person(frame, x, 2 if index % 2 else 0, C.YELLOW)
                frame.pixel(x - 2, 9, C.WHITE)
                frame.pixel(x - 4, 10, C.WHITE)
        # Steady hand: the traffic moves.
        if index >= STEADY:
            cx = 36 + (index - STEADY) * 22
            frame.rect(cx + 2, 10, 6, 2, C.RED, fill=True)
            frame.rect(cx, 12, 11, 2, C.RED, fill=True)
            frame.pixel(cx + 5, 10, C.CYAN)
            frame.pixel(cx + 10, 12, C.YELLOW)
            frame.pixel(cx + 2, 14, C.WHITE)
            frame.pixel(cx + 8, 14, C.WHITE)
            for k in range(3):
                frame.hline(cx - 6 - 3 * k, 11 + k, 3, C.BLUE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/crosswalk.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
