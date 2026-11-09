#!/usr/bin/env python3
"""
The Tortoise and the Hare -- Aesop's race, run in 53 frames.

The hare bolts off the line, gets most of the way, looks back, and lies down
for a nap. The tortoise never changes pace: 1.65 pixels a frame, start to
finish. It plods past the sleeping hare, the hare wakes with a start and
sprints, and the tortoise reaches the flag first. SLOW & STEADY.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 110
GROUND = 15
NAP_X = 52
FLAG_X = 90

PALETTE = {"G": C.GREEN, "Y": C.YELLOW, "W": C.WHITE, "M": C.MAGENTA, "R": C.RED, "C": C.CYAN}

TORTOISE = [
    [
        "..GGGG....",
        ".GGYGGG.YY",
        "GGGGYGGGYY",
        ".YY..YY...",
    ],
    [
        "..GGGG....",
        ".GGYGGG.YY",
        "GGGGYGGGYY",
        "..YY..YY..",
    ],
]

HARE_RUN = [
    [
        ".......W.W.",
        ".......W.W.",
        "..WWWW.WWW.",
        ".WWWWWWWMWW",
        "WWWWWWWWWW.",
        ".WW...WW...",
        "W.......W..",
    ],
    [
        ".......W.W.",
        ".......W.W.",
        "..WWWW.WWW.",
        ".WWWWWWWMWW",
        "WWWWWWWWWW.",
        "..WW.WW....",
        "...WW......",
    ],
]

HARE_SIT = [
    ".......W.W.",
    ".......W.W.",
    ".......WWW.",
    "..WWWW.WMWW",
    ".WWWWWWWWW.",
    "WWWWWWWWW..",
    ".WW...WW...",
]

HARE_SLEEP = [
    "...........",
    "...........",
    "...........",
    "...........",
    "..WWWW.WW..",
    ".WWWWWWWWW.",
    "WWWWWWWWWMW",
]


def stamp(frame, rows, x, y, flip=False):
    width = len(rows[0])
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell != ".":
                px = width - 1 - col if flip else col
                frame.pixel(x + px, y + row, PALETTE[cell])


def scenery(frame):
    frame.hline(0, GROUND, 96, C.GREEN)
    for x in (9, 27, 44, 63, 81):
        frame.pixel(x, GROUND - 1, C.GREEN)
    # The finish: a pole with a chequered flag.
    frame.vline(FLAG_X, 4, 11, C.WHITE)
    for row in range(4):
        for col in range(5):
            if (row + col) % 2 == 0:
                frame.pixel(FLAG_X + 1 + col, 4 + row, C.WHITE)
            else:
                frame.pixel(FLAG_X + 1 + col, 4 + row, C.RED)


def tortoise_x(index):
    return min(79, round(1.65 * index))


def hare_state(index):
    """(x, sprite rows, flipped) for the hare at this frame."""
    if index < 2:
        return 10, HARE_SIT, False
    if index < 9:
        return 10 + 6 * (index - 1), HARE_RUN[index % 2], False
    if index < 11:
        return NAP_X, HARE_SIT, False
    if index < 15:
        return NAP_X, HARE_SIT, True  # a look back at the distant tortoise
    if index < 44:
        return NAP_X, HARE_SLEEP, False
    if index < 46:
        return NAP_X, HARE_SIT, False
    if index < 49:
        return NAP_X + 5 * (index - 45), HARE_RUN[index % 2], False
    return NAP_X + 15, HARE_SIT, False


def build():
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()
        scenery(frame)

        x, sprite, flip = hare_state(index)
        stamp(frame, sprite, x, GROUND - 7, flip)
        if sprite is HARE_SLEEP:
            # Zs drift up and to the right, one new one every four frames.
            nap = index - 15
            for k in range(3):
                age = nap - 4 * k
                if age >= 0:
                    step = age % 12
                    frame.small_text(
                        "Z", x + 9 + step // 2, GROUND - 9 - step * 2 // 3,
                        C.CYAN if step < 8 else C.BLUE,
                    )
        if 44 <= index < 46:
            frame.small_text("!", x + 13, GROUND - 8, C.RED)

        done = index >= 48
        stamp(frame, TORTOISE[0 if done else index % 2], tortoise_x(index), GROUND - 4)

        if done:
            colour = C.YELLOW if index % 2 == 0 else C.WHITE
            frame.small_text("SLOW & STEADY", 3, 0, colour)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/tortoise_hare.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
