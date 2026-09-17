#!/usr/bin/env python3
"""
I am the Senate (2005).

Mace stands on the left, Palpatine hunched in his chair on the right, and
the argument plays out a line at a time above them: THE SENATE WILL DECIDE
YOUR FATE -- I AM THE SENATE -- NOT YET. The Chancellor's eyes come up
yellow on his line, and on IT'S TREASON THEN both blades light: purple for
Mace, red from the sleeve of a man who was only ever a frail old politician.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150
SENATE_AT = 16          # I AM THE SENATE
NOT_YET_AT = 30
TREASON_AT = 38

MACE_X, PALPATINE_X, FLOOR = 10, 76, 15

MACE = [
    ".#.",
    "###",
    ".#.",
    ".#.",
    "#.#",
]
HOOD = [
    ".###.",
    "#...#",
    "#...#",
    ".###.",
    ".###.",
    "#...#",
]


def sprite(frame, rows, x, y, color):
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, y + row, color)


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        frame.hline(0, FLOOR, 96, C.BLUE)

        sprite(frame, MACE, MACE_X, FLOOR - 5, C.CYAN)
        sprite(frame, HOOD, PALPATINE_X, FLOOR - 6, C.BLUE)
        # The eyes: dark while he is still pretending, yellow once he stops.
        eyes = C.YELLOW if index >= SENATE_AT else C.BLACK
        frame.pixel(PALPATINE_X + 1, FLOOR - 5, eyes)
        frame.pixel(PALPATINE_X + 3, FLOOR - 5, eyes)

        if index >= TREASON_AT:
            # Short blades on purpose: the words own the top half.
            reach = min(4, (index - TREASON_AT) * 2 + 1)
            frame.vline(MACE_X + 3, FLOOR - 4 - reach, reach, C.MAGENTA)
            frame.vline(PALPATINE_X - 2, FLOOR - 4 - reach, reach, C.RED)

        if index >= TREASON_AT:
            shown = "IT'S TREASON THEN"[: max(1, (index - TREASON_AT) * 4)]
            frame.text(shown, "center", 0, C.CYAN, proportional=True)
        elif index >= NOT_YET_AT:
            frame.text("NOT YET.", "center", 1, C.CYAN, proportional=True)
        elif index >= SENATE_AT:
            age = index - SENATE_AT
            color = C.WHITE if age % 4 < 2 else C.YELLOW
            frame.text("I AM THE SENATE"[: max(1, age * 4)], "center", 1, color,
                       proportional=True)
        else:
            frame.text("THE SENATE WILL"[: max(1, index * 3)], 2, 0, C.CYAN,
                       proportional=True)
            if index >= 6:
                frame.text("DECIDE YOUR FATE"[: max(1, (index - 6) * 3)], 2, 8,
                           C.CYAN, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/i_am_the_senate.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
