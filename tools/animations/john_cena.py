#!/usr/bin/env python3
"""
You Can't See Me -- the hand goes up, the face goes away, the horns arrive.

John Cena's taunt taken literally: a face waits in the middle of the panel, a
flat palm waves across it, and with every pass more of the face is gone --
dithered out pixel by pixel with a fixed seed, so it dissolves rather than
cutting. By the time the hand drops there is nothing behind it. Then the
fanfare: AND HIS NAME IS types itself across the full width, and JOHN CENA
lands on the fifth note with a burst of horns radiating from behind it.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 100
SEED = 2005  # the year the theme first played

# Scene beats, by frame index.
WAVE_FROM, WAVE_TO = 4, 22   # the palm passes back and forth
HAND_DROP = 27               # it leaves, and the face does not come back
NAME_AT = 28                 # "AND HIS NAME IS" starts typing
CENA_AT = 39                 # the horns

FACE = [
    "..#####..",
    ".#######.",
    "#########",
    "#########",
    "#########",
    "#########",
    "#########",
    ".#######.",
    "..#####..",
]
FACE_X, FACE_Y = 40, 3
EYES = [(3, 3), (5, 3)]
PALM = [
    "#.#.#",
    "#####",
    "#####",
    "#####",
    ".####",
    "..###",
    "...##",
]
#: Trumpet beats, relative to CENA_AT: do -- do -- do -- do -- dooooo.
FANFARE = (0, 2, 4, 6, 9)


def face_order(rng):
    """Every face pixel, shuffled -- the order it dissolves in."""
    cells = [
        (column, row)
        for row, line in enumerate(FACE)
        for column, cell in enumerate(line)
        if cell == "#"
    ]
    rng.shuffle(cells)
    return cells


def draw_face(frame, cells, visible):
    """Draw the first ``visible`` cells of the dissolve order."""
    kept = set(cells[:visible])
    for column, row in kept:
        frame.pixel(FACE_X + column, FACE_Y + row, C.YELLOW)
    for eye in EYES:
        if eye in kept:
            frame.pixel(FACE_X + eye[0], FACE_Y + eye[1], C.BLACK)
    for offset in range(3):
        mouth = (3 + offset, 6)
        if mouth in kept:
            frame.pixel(FACE_X + mouth[0], FACE_Y + mouth[1], C.BLACK)


def draw_palm(frame, x, y):
    for row, line in enumerate(PALM):
        for column, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + column, y + row, C.WHITE)


def draw_horns(frame, spread):
    """
    Speed lines blasting out either side of the wordmark.

    They stay clear of the letters -- the name is the point -- so they start
    at the text's own edges and grow outward on each hit of the fanfare.
    """
    left, right = 21, 75
    for row in (1, 3, 5, 11, 13, 15):
        length = spread if row in (3, 13) else max(0, spread - 2)
        frame.hline(left - length, row, length, C.YELLOW)
        frame.hline(right, row, length, C.YELLOW)


def build():
    rng = random.Random(SEED)
    cells = face_order(rng)
    anim = Animation(delay=DELAY)
    for index in range(FRAMES):
        frame = anim.frame()

        if index < HAND_DROP:
            if index < WAVE_FROM:
                remaining = len(cells)
            elif index < WAVE_TO:
                gone = (index - WAVE_FROM) / (WAVE_TO - WAVE_FROM)
                remaining = round(len(cells) * (1 - gone))
            else:
                remaining = 0
            draw_face(frame, cells, remaining)

            if index >= WAVE_FROM:
                swing = math.sin(2 * math.pi * (index - WAVE_FROM) / 4)
                x = round(FACE_X + 2 + 8 * swing)
                fall = 0 if index < WAVE_TO else (index - WAVE_TO + 1) ** 2
                draw_palm(frame, x, 4 + fall)
        elif index >= CENA_AT:
            beat = index - CENA_AT
            hit = max((b for b in FANFARE if b <= beat), default=0)
            draw_horns(frame, max(0, 14 - 4 * (beat - hit)))
            loud = beat in FANFARE
            frame.text("JOHN CENA", "center", 5, C.WHITE if loud else C.RED)
        elif index >= NAME_AT:
            typed = min(15, (index - NAME_AT + 1) * 2)
            frame.text("AND HIS NAME IS"[:typed], 3, 5, C.CYAN)
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/john_cena.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
