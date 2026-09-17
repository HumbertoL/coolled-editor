#!/usr/bin/env python3
"""
This is where the fun begins (2005) -- Anakin, diving into a battle.

Two starfighters hold the lower band while the star streaks rip past them,
the line lands one half at a time, and then the fun does in fact begin:
cannon fire from both ships, a droid fighter coming apart, and the pair
rolling out to the right through their own debris.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jtkit import Animation, colors as C  # noqa: E402

FRAMES = 53
DELAY = 120
SEED = 1977
SKY_TOP = 8              # the words own everything above this
LINE_ONE_AT, LINE_TWO_AT = 8, 20
FIRE_AT, HIT_AT, EXIT_AT = 26, 33, 40
STARS = 22
ENEMY_X = 80

FIGHTER = [
    "..#..",
    "#####",
    ".###.",
]


def fighter(frame, x, y, color, tip=C.WHITE):
    for row, line in enumerate(FIGHTER):
        for col, cell in enumerate(line):
            if cell == "#":
                frame.pixel(x + col, y + row, color)
    frame.pixel(x + 5, y + 1, tip)     # engine glow, ahead of the nose


def build():
    rng = random.Random(SEED)
    anim = Animation(delay=DELAY)
    stars = [
        (rng.randrange(96), rng.randrange(SKY_TOP, 16), rng.choice((3, 5, 7)))
        for _ in range(STARS)
    ]

    for index in range(FRAMES):
        frame = anim.frame()

        # Star streaks, length standing in for speed since there is no
        # brightness to spend on depth.
        for x0, y, speed in stars:
            x = (x0 - index * speed) % 96
            frame.hline(x, y, speed - 1, C.BLUE)

        lead_x = 20 if index < EXIT_AT else 20 + (index - EXIT_AT) * 6
        fighter(frame, lead_x, SKY_TOP + 1, C.YELLOW)
        fighter(frame, lead_x - 9, SKY_TOP + 4 + (1 if index % 6 < 3 else 0), C.WHITE, C.CYAN)

        # The droid fighter, until it stops being one.
        if index < HIT_AT:
            frame.rect(ENEMY_X, SKY_TOP + 2, 3, 3, C.RED)
        elif index < HIT_AT + 5:
            # Coming apart: a ring of debris opening out from where it was.
            k = index - HIT_AT
            for step in range(6):
                angle = step * math.pi / 3
                frame.pixel(
                    ENEMY_X + 1 + round((k + 1) * 2.5 * math.cos(angle)),
                    SKY_TOP + 3 + round((k + 1) * 1.5 * math.sin(angle)),
                    C.YELLOW if k < 2 else C.RED,
                )
            if k < 2:
                frame.rect(ENEMY_X - k, SKY_TOP + 2 - k, 3 + k * 2, 3 + k * 2, C.WHITE)

        if FIRE_AT <= index < HIT_AT:
            # Two streams of cannon fire, one from each ship, closing on it.
            for gun, row in ((lead_x + 6, SKY_TOP + 2), (lead_x - 3, SKY_TOP + 5)):
                for spacing in (0, 14):
                    bolt = gun + (index - FIRE_AT) * 11 + spacing
                    if bolt < ENEMY_X:
                        frame.hline(bolt, row, 3, C.RED)

        if index >= LINE_TWO_AT:
            shown = "THE FUN BEGINS"[: max(1, (index - LINE_TWO_AT) * 3)]
            hot = index >= FIRE_AT and index % 4 < 2
            frame.text(shown, "center", 0, C.YELLOW if hot else C.WHITE, proportional=True)
        elif index >= LINE_ONE_AT:
            frame.text(
                "THIS IS WHERE"[: max(1, (index - LINE_ONE_AT) * 3)],
                "center", 0, C.WHITE, proportional=True,
            )
    return anim


if __name__ == "__main__":
    animation = build()
    out = Path(__file__).resolve().parents[2] / "src/sample/fun_begins.jt"
    animation.save(out)
    print(f"{out.name}: {animation.describe()}")
