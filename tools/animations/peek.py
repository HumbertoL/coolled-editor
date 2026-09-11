#!/usr/bin/env python3
"""
Peek -- the panel is dark, and something keeps looking in.

Mostly nothing. Then a cat's head rises from the bottom edge -- just a faint
blue outline and two yellow eyes -- looks left, looks right, and sinks back
down. Dark again. Then a ghost drifts in from the right edge, hollow-eyed,
hovers, and slides away. The dark stretches are the point; the eight-second
loop means it happens rarely enough to catch people off guard.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 150

CAT = [
    "#.........#",
    "##.......##",
    "#.#.....#.#",
    "#.........#",
    "#.........#",
    "#.........#",
    ".#.......#.",
    "..#######..",
]
CAT_EYES = [(3, 4), (7, 4)]
CAT_X = 24
CAT_RISE, CAT_LOOK, CAT_SINK = 10, 15, 21     # frame each phase starts
CAT_GONE = 25

GHOST = [
    "..####..",
    ".######.",
    "##.##.##",
    "##.##.##",
    "########",
    "########",
    "########",
    "#.##.#.#",
]
GHOST_IN, GHOST_HOLD, GHOST_OUT, GHOST_GONE = 33, 38, 44, 48


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if CAT_RISE <= index < CAT_GONE:
            if index < CAT_LOOK:
                top = 16 - 2 * (index - CAT_RISE + 1)
            elif index < CAT_SINK:
                top = 16 - 2 * (CAT_LOOK - CAT_RISE)
            else:
                top = 16 - 2 * (CAT_LOOK - CAT_RISE) + 3 * (index - CAT_SINK + 1)
            for r, line in enumerate(CAT):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(CAT_X + c, top + r, C.BLUE)
            look = 0
            if CAT_LOOK <= index < CAT_SINK:
                look = -1 if index - CAT_LOOK < 3 else 1
            for ex, ey in CAT_EYES:
                frame.pixel(CAT_X + ex + look, top + ey, C.YELLOW)

        if GHOST_IN <= index < GHOST_GONE:
            if index < GHOST_HOLD:
                x = 96 - 2 * (index - GHOST_IN + 1)
            elif index < GHOST_OUT:
                x = 96 - 2 * (GHOST_HOLD - GHOST_IN)
            else:
                x = 96 - 2 * (GHOST_HOLD - GHOST_IN) + 3 * (index - GHOST_OUT + 1)
            bob = (index // 2) % 2
            for r, line in enumerate(GHOST):
                for c, ch in enumerate(line):
                    if ch == "#":
                        frame.pixel(x + c, 3 + bob + r, C.WHITE)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/peek.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
