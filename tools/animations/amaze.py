#!/usr/bin/env python3
"""
Amaze, amaze, amaze -- Project Hail Mary.

Rocky, the five-legged Eridian, sits at the left tapping a leg while chords
rise off him as notes. The amazes arrive one at a time, then the request
that closes every good scene with him: FIST MY BUMP, with a leg raised.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120

ROCKY = [
    ".....#####.....",
    "...#########...",
    "..###########..",
    ".#############.",
    ".#############.",
    "..###########..",
    "...#########...",
]
# Five legs: (start col, direction), drawn as short diagonals under the body.
LEGS = [(1, -1), (4, -1), (7, 0), (10, 1), (13, 1)]
ROCKY_X, ROCKY_Y = 1, 2
NOTE = ["..#", "..#", "..#", "###", "###"]
TEXT_X = 20
BEATS = [6, 17, 28]        # AMAZE, AMAZE, AMAZE
BUMP_AT = 40


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        for r, line in enumerate(ROCKY):
            for c, ch in enumerate(line):
                if ch == "#":
                    frame.pixel(ROCKY_X + c, ROCKY_Y + r, C.WHITE)
        for i, (col, direction) in enumerate(LEGS):
            tap = 1 if (index + i) % 4 == 0 and index < BUMP_AT else 0
            raised = index >= BUMP_AT and i == 4
            for k in range(4):
                y = ROCKY_Y + 7 + k - tap
                x = ROCKY_X + col + direction * (k // 2)
                if raised:
                    frame.pixel(ROCKY_X + 14 + k, ROCKY_Y + 3 - k, C.WHITE)
                else:
                    frame.pixel(x, y, C.WHITE)

        # A note floats up on each beat.
        for beat in BEATS:
            age = index - beat
            if 0 <= age < 5:
                nx, ny = ROCKY_X + 15, ROCKY_Y - 1 - age
                for r, line in enumerate(NOTE):
                    for c, ch in enumerate(line):
                        if ch == "#":
                            frame.pixel(nx + c, ny + r, C.CYAN)

        if index < BUMP_AT:
            said = sum(1 for b in BEATS if index >= b)
            if said >= 1:
                top = "AMAZE" if said == 1 else "AMAZE AMAZE"
                frame.text(top, TEXT_X, 0, C.YELLOW if said < 3 else C.WHITE, proportional=True)
            if said >= 3:
                frame.text("AMAZE", TEXT_X, 9, C.YELLOW if index % 2 else C.WHITE, proportional=True)
            elif said >= 1 and index - BEATS[said - 1] < 2:
                pass
        else:
            k = index - BUMP_AT
            frame.text("FIST MY", TEXT_X, 0, C.CYAN, proportional=True)
            frame.text("BUMP", TEXT_X, 9, C.WHITE if k % 4 < 2 else C.CYAN, proportional=True)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/amaze.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
